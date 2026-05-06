from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Request as FastAPIRequest
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai import OpenAI
from google import genai
from google.genai import types
import os

from ..utils.stream import stream_text
from ..utils.gemini import convert_openai_to_gemini, stream_gemini
from ..services.rag import get_manual_context
from ..services.rag_router import get_rag_router

import anthropic
import base64 as b64module
import json
import uuid
import time

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class MessagesRequest(BaseModel):
    messages: List[Any]


class StepRequest(BaseModel):
    messages: List[Any]
    manual_ids: Optional[List[str]] = None
    session_state: Optional[dict] = None  # mode, visited_node_ids, active_workflow_id, etc.


class AnnotateRequest(BaseModel):
    image: str
    data_type: str = "other"
    description: str = ""
    topic: str = ""


def _claude_stream_response(messages, model="claude-opus-4-20250514"):
    """Create a Claude streaming response for report/analysis tasks."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    client = anthropic.Anthropic(api_key=api_key)

    # Extract system message
    system_text = ""
    claude_messages = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        if role == "system":
            if isinstance(content, str):
                system_text = content
            elif isinstance(content, list):
                system_text = " ".join(p.get("text", "") for p in content if p.get("type") == "text")
            continue

        # Convert content to Claude format
        if isinstance(content, str):
            claude_messages.append({"role": role, "content": content})
        elif isinstance(content, list):
            claude_parts = []
            for part in content:
                if part.get("type") == "text":
                    claude_parts.append({"type": "text", "text": part["text"]})
                elif part.get("type") == "image_url":
                    image_url = part.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image/"):
                        try:
                            header, data = image_url.split(",", 1)
                            mime_type = header.split(";")[0].split(":")[1]
                            claude_parts.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": data,
                                },
                            })
                        except Exception:
                            pass
            if claude_parts:
                claude_messages.append({"role": role, "content": claude_parts})

    if not claude_messages:
        return None

    start_time = time.time()

    def stream_claude():
        def format_sse(payload: dict) -> str:
            return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"

        message_id = f"msg-{uuid.uuid4().hex}"
        text_started = False
        full_text = ""

        yield format_sse({"type": "start", "messageId": message_id})

        try:
            with client.messages.stream(
                model=model,
                max_tokens=16384,
                system=system_text,
                messages=claude_messages,
            ) as stream:
                for text in stream.text_stream:
                    full_text += text
                    if not text_started:
                        yield format_sse({"type": "text-start", "id": "text-1"})
                        text_started = True
                        print(f"[claude] Time to first chunk: {(time.time() - start_time) * 1000:.0f}ms")
                    yield format_sse({"type": "text-delta", "id": "text-1", "delta": text})

            if text_started:
                yield format_sse({"type": "text-end", "id": "text-1"})

            yield format_sse({"type": "finish"})
            print(f"[claude] Total: {(time.time() - start_time) * 1000:.0f}ms | {len(full_text)} chars")
        except Exception as e:
            print(f"[claude] Error: {e}")
            if not text_started:
                yield format_sse({"type": "text-start", "id": "text-1"})
            yield format_sse({"type": "text-delta", "id": "text-1", "delta": f"Error: {str(e)}"})
            yield format_sse({"type": "text-end", "id": "text-1"})
            yield format_sse({"type": "finish"})

        yield "data: [DONE]\n\n"

    return StreamingResponse(stream_claude(), media_type="text/event-stream")


def _claude_review_report(report_text: str, topic: str) -> str:
    """Use Claude Opus to verify and enhance a Gemini-generated report."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or not report_text.strip():
        return report_text

    try:
        client = anthropic.Anthropic(api_key=api_key)
        result = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=16384,
            messages=[{
                "role": "user",
                "content": (
                    f"Topic: {topic}\n\n"
                    "You are a senior geoscience peer reviewer with 20+ years of experience. "
                    "Critically review and IMPROVE this geological interpretation report.\n\n"
                    "## Review Checklist (check EVERY item)\n"
                    "1. **Terminology**: Fix incorrect terms. Use standard geology terms (림싱크라인 not 퀼싱크라인, clinoform not just curved reflector).\n"
                    "2. **Tectonic consistency**: Do structural interpretations match the tectonic setting?\n"
                    "   - Extensional basin (F3, Viking Graben): expect normal faults, salt diapirs, clinoforms — NOT compressional folds\n"
                    "   - Clinoforms ≠ anticlines. Differential compaction ≠ tectonic folding.\n"
                    "3. **Evidence-based**: Every interpretation MUST cite a specific visual observation with LOCATION.\n"
                    "   - REJECT: '단층이 존재한다' → FIX: '단면 중앙부에서 반사면의 불연속이 관찰되며 정단층으로 해석된다'\n"
                    "4. **Relative descriptions**: Add relative spatial comparisons where missing:\n"
                    "   - Position: '단면 중앙에서 약간 우측', symmetry: '좌측이 우측보다 깊다'\n"
                    "   - Thickness: '돔 정상부에서 측면부로 갈수록 얇아진다'\n"
                    "5. **Draping vs Onlap**: Distinguish correctly. Draping = passive burial after structure. Onlap = syn-tectonic sedimentation.\n"
                    "6. **Fault checklist**: For each fault claim, verify: offset visible? termination? dip direction?\n"
                    "7. **Key horizons**: Describe boundary reflectors with amplitude, continuity, shape.\n"
                    "8. **Confidence tags**: EVERY bullet MUST end with [신뢰도: 높음/중간/낮음] or [Confidence: High/Medium/Low]. Add ALL missing tags. Most should be 중간/Medium.\n"
                    "9. **No hallucination**: Remove features not supported by the described observations.\n"
                    "10. **Completeness**: Add any important observations or interpretations that are missing.\n\n"
                    "## Rules\n"
                    "- Keep the same markdown format, language, and section structure\n"
                    "- Do NOT remove existing correct content — only correct, enhance, and add\n"
                    "- Keep all ```structures blocks unchanged\n"
                    "- Output the improved report only. No meta-commentary. No preamble.\n\n"
                    f"Report to review:\n{report_text}"
                ),
            }],
        )
        reviewed = result.content[0].text.strip()
        print(f"[CLAUDE] Report review complete: {len(report_text)} → {len(reviewed)} chars")
        return reviewed
    except Exception as e:
        print(f"[CLAUDE] Report review failed: {e}")
        return report_text


def _get_llm_client():
    """Return an OpenAI-compatible client. Uses local LLM if LOCAL_LLM_URL is set."""
    local_llm_url = os.environ.get("LOCAL_LLM_URL")
    if local_llm_url:
        return OpenAI(base_url=f"{local_llm_url}/v1", api_key="not-needed"), "local"
    else:
        return OpenAI(), "gpt-5-mini-2025-08-07"


def _filter_text_messages(messages):
    """Filter out image content for text-only LLMs."""
    text_messages = []
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            text_parts = [p.get("text", "") for p in content if p.get("type") == "text"]
            if text_parts:
                text_messages.append({"role": msg["role"], "content": " ".join(text_parts)})
        else:
            text_messages.append(msg)
    return text_messages


def _gemini_stream_response(messages):
    """Create a Gemini streaming response from OpenAI-format messages."""
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        return None

    client = genai.Client(api_key=gemini_api_key)

    # Extract system instruction
    system_instruction_parts = []
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content")
            if isinstance(content, str):
                system_instruction_parts.append(types.Part.from_text(text=content))
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        system_instruction_parts.append(
                            types.Part.from_text(text=part.get("text"))
                        )

    system_instruction = (
        types.Content(parts=system_instruction_parts)
        if system_instruction_parts
        else None
    )

    contents = convert_openai_to_gemini(messages)

    generate_content_config = types.GenerateContentConfig(
        system_instruction=system_instruction,
    )

    stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
        config=generate_content_config,
    )

    return StreamingResponse(
        stream_gemini(stream),
        media_type="text/event-stream",
    )


def _local_llm_response(messages):
    """Fallback: stream response from local text-only LLM."""
    client, model_name = _get_llm_client()
    messages = _filter_text_messages(messages)

    stream = client.chat.completions.create(
        messages=messages,
        model=model_name,
        stream=True,
    )

    return StreamingResponse(
        stream_text(stream, {}),
        media_type="text/event-stream",
    )


@router.post("/api/step")
@limiter.limit("20/minute;300/hour")
async def handle_step_chat(request: FastAPIRequest, body: StepRequest):
    print(f"[STEP] Received request with {len(body.messages)} messages, manual_ids={body.manual_ids}")
    messages = body.messages

    # Enrich system prompt with manual context if manual_ids provided
    if body.manual_ids:
        # Extract goal from system prompt + last assistant message (current step context)
        query_parts = []
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "")
                if isinstance(content, str) and "# Goal" in content:
                    try:
                        start = content.index("# Goal") + len("# Goal\n")
                        end = content.index("\n#", start) if "\n#" in content[start:] else start + 200
                        query_parts.append(content[start:end].strip())
                    except ValueError:
                        pass
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, str):
                    query_parts.append(content)

        # Use goal + recent steps as RAG query
        raw_query = " ".join(query_parts[-3:]) if query_parts else ""
        query = raw_query
        print(f"[STEP] RAG query: {query[:150]}")

        # Extract latest screenshot from messages for Graph-RAG localization
        latest_screenshot = None
        for msg in reversed(messages):
            content = msg.get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "image_url":
                        latest_screenshot = part.get("image_url", {}).get("url")
                        if latest_screenshot:
                            break
            if latest_screenshot:
                break

        # Use RAG Router (graph-aware) if screenshot available, else plain vector
        context_block = ""
        router_result: Optional[dict] = None
        # Merge frontend-provided session state (do NOT override explicit mode)
        session_state = dict(body.session_state or {})
        # Guide endpoint defaults to "guide" mode only if caller did not specify
        session_state.setdefault("mode", "guide")
        try:
            if latest_screenshot:
                router_result = get_rag_router().route(
                    user_message=query,
                    screenshot_b64=latest_screenshot,
                    session_state=session_state,
                    manual_ids=body.manual_ids,
                )
                context_block = router_result.get("context_block", "")
                raw = router_result.get("raw_output") or {}
                current_node = raw.get("current_node") if isinstance(raw, dict) else None
                print(f"[STEP] RAG router mode={router_result.get('mode')}, context={len(context_block)}chars, node={current_node.get('id') if current_node else None}")
            elif query:
                ctx = get_manual_context(body.manual_ids, query)
                if ctx:
                    context_block = f"--- Reference Manual Context ---\n{ctx}\n--- End Reference Manual Context ---"
        except Exception as e:
            print(f"[STEP] RAG error, falling back to plain vector: {e}")
            if query:
                ctx = get_manual_context(body.manual_ids, query)
                if ctx:
                    context_block = f"--- Reference Manual Context ---\n{ctx}\n--- End Reference Manual Context ---"

        # Text-based post-completion fallback: if the current dialog name
        # appears in a recent assistant message, the user is back on a
        # screen they were already instructed about → inject dismiss hint.
        # This works even when the workflow node localization returns None.
        try:
            current_dialog = ""
            if latest_screenshot and isinstance(router_result, dict):
                vs = (router_result.get("raw_output") or {}).get("visual_state") or {}
                current_dialog = (vs.get("current_dialog") or "").strip()
        except Exception:
            current_dialog = ""

        if current_dialog and len(current_dialog) >= 4:
            # Check the last 6 assistant messages for the dialog name
            recent_assistant_text = []
            count = 0
            for m in reversed(messages):
                if m.get("role") == "assistant":
                    content = m.get("content")
                    if isinstance(content, str):
                        recent_assistant_text.append(content)
                    elif isinstance(content, list):
                        recent_assistant_text.extend(
                            p.get("text", "") for p in content if p.get("type") == "text"
                        )
                    count += 1
                    if count >= 6:
                        break
            joined = "\n".join(recent_assistant_text).lower()
            dialog_lc = current_dialog.lower()
            if dialog_lc in joined:
                hint = (
                    "\n\n--- POST-COMPLETION DETECTED ---\n"
                    f"The current dialog \"{current_dialog}\" was already the subject of a previous instruction "
                    "in this session. The action you previously gave on this dialog has finished — the dialog "
                    "is just lingering. DO NOT repeat any instruction targeting this dialog. "
                    "Instead, instruct the user to DISMISS it (Close / Finish / Done / OK / Cancel / X).\n"
                    "--- End ---"
                )
                context_block = (context_block or "") + hint
                print(f"[STEP] post-completion text-fallback fired for dialog='{current_dialog}'")

        if context_block:
            block = f"\n\n--- GeoLens RAG Context ---\n{context_block}\n--- End Context ---\n"
            for msg in messages:
                if msg.get("role") == "system":
                    if isinstance(msg["content"], str):
                        msg["content"] += block
                    elif isinstance(msg["content"], list):
                        msg["content"].append({"type": "text", "text": block})
                    break
            else:
                messages.insert(0, {"role": "system", "content": block})

    # Claude Sonnet 4 for best visual grounding (fewer "phantom button"
    # hallucinations than Gemini Flash). Fall back to Gemini Flash, then
    # local LLM if Anthropic key missing or service down.
    response = _claude_stream_response(messages, model="claude-sonnet-4-6")
    if response:
        return response
    response = _gemini_stream_response(messages)
    if response:
        return response
    return _local_llm_response(messages)


@router.post("/api/help")
@limiter.limit("8/minute;100/hour")
async def handle_help_chat(request: FastAPIRequest, body: MessagesRequest):
    # Help is text-only Q&A, local LLM is sufficient
    response = _gemini_stream_response(body.messages)
    if response:
        return response
    return _local_llm_response(body.messages)


@router.post("/api/check")
@limiter.limit("30/minute;500/hour")
async def handle_check_chat(request: FastAPIRequest, body: MessagesRequest):
    print(f"[CHECK] Received request with {len(body.messages)} messages")
    # Check compares before/after screenshots - needs vision
    response = _gemini_stream_response(body.messages)
    if response:
        return response
    return _local_llm_response(body.messages)


@router.post("/api/report")
@limiter.limit("5/minute;50/hour")
async def handle_report_chat(request: FastAPIRequest, body: StepRequest):
    print(f"[REPORT] Received request with {len(body.messages)} messages, manual_ids={body.manual_ids}")
    messages = body.messages

    # Extract topic + capture descriptions + data types for precise Graph RAG query
    topic_parts = []
    data_types = set()
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content", "")
            if isinstance(content, str) and "# Topic" in content:
                try:
                    start = content.index("# Topic") + len("# Topic\n")
                    end = content.index("\n", start)
                    topic_parts.append(content[start:end].strip())
                except ValueError:
                    pass
        if msg.get("role") == "user":
            content = msg.get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        text = part.get("text", "")
                        topic_parts.append(text)
                        # Extract data type from capture labels like "[Capture 1 (seismic): ...]"
                        import re
                        dt_matches = re.findall(r'\((\w+)\):', text)
                        data_types.update(dt_matches)

    detected_types = list(data_types) if data_types else None
    print(f"[REPORT] Detected data types: {detected_types}")

    raw_query = " ".join(topic_parts) if topic_parts else ""
    query = raw_query
    print(f"[REPORT] Graph RAG query: {query[:200]}")

    if query:
        context = get_manual_context(body.manual_ids or [], query, top_k=10, data_types=detected_types)
        if context:
            context_block = (
                "\n\n--- Reference Context (Knowledge Graph + Manuals) ---\n"
                f"{context}\n"
                "--- End Reference Context ---\n"
            )
            for msg in messages:
                if msg.get("role") == "system":
                    if isinstance(msg["content"], str):
                        msg["content"] += context_block
                    elif isinstance(msg["content"], list):
                        msg["content"].append({"type": "text", "text": context_block})
                    break

    # Report generation: Gemini Pro (image analysis + draft) → Gemini fallback
    print("[REPORT] Using Gemini Pro for report generation (image analysis)...")
    response = _gemini_stream_response(messages)
    if response:
        return response
    return _local_llm_response(messages)


_DATA_TYPE_HINTS = {
    "seismic": "Seismic section: x=distance, y=time/depth(down). Horizons=curved reflectors(line), faults=discontinuities(line), amplitude anomalies=bbox.",
    "well_log": "Well log: y=depth(down), x=log values. Formation tops=point, log anomaly zones=bbox.",
    "gpr": "GPR: x=distance, y=depth(down). Reflectors=line, hyperbolas=point at apex, anomaly zones=bbox.",
    "gravity": "Gravity: anomaly highs/lows=bbox, gradients/lineaments=line.",
    "magnetic": "Magnetic: anomaly regions=bbox, linear anomalies=line.",
    "resistivity": "Resistivity: high/low zones=bbox, boundaries=line.",
    "geological_map": "Geological map: contacts/faults=line, structural points=point, intrusions=bbox.",
}

ANNOTATE_PROMPT = """You are an expert geoscientist performing precise geological feature detection.
Context: {topic} — {description}
Data type: {data_type}
{data_type_hint}

## ██ ACCURACY FIRST — READ BEFORE ANNOTATING ██
1. ONLY annotate features you can CLEARLY and UNAMBIGUOUSLY see in the image.
2. If a feature is uncertain or ambiguous, DO NOT include it. Fewer accurate labels > many inaccurate ones.
3. For EACH feature, verify: Can I trace this feature's exact path/boundary in the image? If not, skip it.

## Coordinate System (CRITICAL — relative to FULL IMAGE)
Normalized 0.0 to 1.0 relative to the FULL IMAGE (including any borders, axes, toolbars):
- (0.0, 0.0) = top-left corner of the ENTIRE image
- (1.0, 1.0) = bottom-right corner of the ENTIRE image
- (0.5, 0.5) = exact center of the ENTIRE image

## How to locate features precisely
For each feature, think step by step:
1. Look at where the feature is in the FULL image (not just the data area)
2. Estimate x: how far from the LEFT edge (0.0) to the RIGHT edge (1.0)?
3. Estimate y: how far from the TOP edge (0.0) to the BOTTOM edge (1.0)?
4. For lines: trace 8-12 points ALONG THE VISIBLE FEATURE path
5. VERIFY each coordinate: mentally place a dot at (x, y) on the image — does it land on the feature?

## Geometry types
- "line": array of 8-12 {{x,y}} points tracing the feature. Follow the ACTUAL visible path, not a schematic.
- "bbox": x, y (top-left), width, height — for zones/areas
- "point": x, y — for point features

## Feature types
fault, horizon, unconformity, anomaly, stratigraphic_boundary, fold, intrusion, contact, fracture_zone, amplitude_anomaly, velocity_anomaly, well_marker, formation_top, log_anomaly

## Labels
- Use descriptive, specific labels: "Main Horizon (strong reflector)" not just "Horizon"
- Include observable characteristics: "Normal Fault (30ms throw)" not just "Fault"

Output format:
{{"annotations": [{{"id":"h1","feature_type":"horizon","label":"Strong continuous reflector","confidence":"high",
"geometry":{{"type":"line","points":[{{"x":0.05,"y":0.40}},{{"x":0.15,"y":0.38}},{{"x":0.30,"y":0.34}},{{"x":0.50,"y":0.33}},{{"x":0.75,"y":0.41}},{{"x":0.90,"y":0.44}}]}},
"description":"Continuous high-amplitude reflector traceable across section"}}]}}

Rules:
- Max 5 features — quality over quantity
- ONLY clearly visible features — when in doubt, leave it out
- Coordinates strictly 0.0-1.0, relative to DATA AREA only
- Confidence: "high" only for unambiguous features, "medium" for most, "low" for subtle
"""


def _validate_annotations(annotations: list) -> list:
    """Validate and clamp annotation coordinates to 0.0-1.0 range."""
    valid = []
    for a in annotations:
        geom = a.get("geometry", {})
        geom_type = geom.get("type")

        if geom_type == "line":
            points = geom.get("points", [])
            if len(points) < 2:
                continue
            geom["points"] = [
                {
                    "x": round(max(0.0, min(1.0, float(p.get("x", 0)))), 4),
                    "y": round(max(0.0, min(1.0, float(p.get("y", 0)))), 4),
                }
                for p in points
            ]
        elif geom_type == "bbox":
            x = max(0.0, min(1.0, float(geom.get("x", 0))))
            y = max(0.0, min(1.0, float(geom.get("y", 0))))
            bw = float(geom.get("width", 0))
            bh = float(geom.get("height", 0))
            if bw <= 0.005 or bh <= 0.005:
                continue
            geom["x"] = round(x, 4)
            geom["y"] = round(y, 4)
            geom["width"] = round(min(bw, 1.0 - x), 4)
            geom["height"] = round(min(bh, 1.0 - y), 4)
        elif geom_type == "point":
            geom["x"] = round(max(0.0, min(1.0, float(geom.get("x", 0)))), 4)
            geom["y"] = round(max(0.0, min(1.0, float(geom.get("y", 0)))), 4)
        else:
            continue

        a["geometry"] = geom
        valid.append(a)

    return valid


@router.post("/api/annotate")
@limiter.limit("10/minute;100/hour")
async def handle_annotate(request: FastAPIRequest, body: AnnotateRequest):
    hint = _DATA_TYPE_HINTS.get(body.data_type, "Detect geological features.")
    prompt = ANNOTATE_PROMPT.format(
        data_type=body.data_type,
        topic=body.topic or "geological interpretation",
        description=body.description or "no description",
        data_type_hint=hint,
    )

    image_data = body.image
    if "," in image_data:
        header_part, b64_data = image_data.split(",", 1)
        mime_type = header_part.split(";")[0].split(":")[1] if ":" in header_part else "image/jpeg"
    else:
        b64_data = image_data
        mime_type = "image/jpeg"

    # Resize large images
    try:
        from PIL import Image
        import io
        image_bytes = b64module.b64decode(b64_data)
        img = Image.open(io.BytesIO(image_bytes))
        max_dim = 2048
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            image_bytes = buf.getvalue()
            b64_data = b64module.b64encode(image_bytes).decode()
            mime_type = "image/jpeg"
    except Exception:
        pass

    # Gemini for annotation (better spatial/coordinate accuracy)
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        return {"annotations": []}

    try:
        gclient = genai.Client(api_key=gemini_api_key)
        image_bytes = b64module.b64decode(b64_data)
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                ],
            )
        ]
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
            thinking_config=types.ThinkingConfig(thinking_budget=1024),
        )
        result = gclient.models.generate_content(model="gemini-2.5-pro", contents=contents, config=config)
        parsed = json.loads(result.text)
        raw_annotations = parsed.get("annotations", [])
        annotations = _validate_annotations(raw_annotations)
        print(f"[ANNOTATE] Gemini detected {len(annotations)} features for {body.data_type}")
        return {"annotations": annotations}
    except Exception as e:
        print(f"[ANNOTATE] Gemini error: {e}")
        return {"annotations": []}


class ReviewRequest(BaseModel):
    report: str
    topic: str


@router.post("/api/report/review")
@limiter.limit("5/minute;30/hour")
async def handle_report_review(request: FastAPIRequest, body: ReviewRequest):
    """GPT reviews and enhances a Claude-generated report."""
    print(f"[REVIEW] Reviewing report: {len(body.report)} chars, topic: {body.topic[:50]}")
    reviewed = _claude_review_report(body.report, body.topic)
    return {"reviewed_report": reviewed}


@router.post("/api/coordinates")
@limiter.limit("15/minute;200/hour")
async def handle_coordinate_chat(request: FastAPIRequest, body: MessagesRequest):
    # Coordinates: synchronous call for simple "x,y" output, wrapped as SSE
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if gemini_api_key:
        import time as _t, random as _r
        client = genai.Client(
            api_key=gemini_api_key,
            http_options=types.HttpOptions(timeout=20_000),
        )

        system_instruction_parts = []
        for msg in body.messages:
            if msg.get("role") == "system":
                content = msg.get("content")
                if isinstance(content, str):
                    system_instruction_parts.append(types.Part.from_text(text=content))

        system_instruction = (
            types.Content(parts=system_instruction_parts)
            if system_instruction_parts
            else None
        )

        contents = convert_openai_to_gemini(body.messages)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
        )

        # Retry on transient errors so a single 503 burst doesn't 500 the endpoint.
        text = "None"
        MAX_RETRY = 3
        for attempt in range(MAX_RETRY + 1):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=contents,
                    config=config,
                )
                text = response.text.strip() if response.text else "None"
                if attempt > 0:
                    print(f"[coordinates] recovered on retry {attempt}")
                break
            except Exception as e:
                msg = str(e)
                transient = any(m in msg for m in (
                    "503", "429", "500", "504", "UNAVAILABLE",
                    "RESOURCE_EXHAUSTED", "DEADLINE_EXCEEDED", "timed out", "Timeout"
                ))
                if not transient or attempt >= MAX_RETRY:
                    print(f"[coordinates] failed: {e}")
                    text = "None"
                    break
                delay = 1.0 * (2 ** attempt) + _r.uniform(0, 0.5)
                print(f"[coordinates] transient; retry {attempt + 1}/{MAX_RETRY} after {delay:.1f}s")
                _t.sleep(delay)
        print(f"[coordinates] Result: {text}")

        import uuid, json as json_mod
        msg_id = f"msg-{uuid.uuid4().hex}"

        def sse_wrap():
            yield f'data: {json_mod.dumps({"type":"start","messageId":msg_id})}\n\n'
            yield f'data: {json_mod.dumps({"type":"text-start","id":"text-1"})}\n\n'
            yield f'data: {json_mod.dumps({"type":"text-delta","id":"text-1","delta":text})}\n\n'
            yield f'data: {json_mod.dumps({"type":"text-end","id":"text-1"})}\n\n'
            yield f'data: {json_mod.dumps({"type":"finish"})}\n\n'
            yield "data: [DONE]\n\n"

        return StreamingResponse(sse_wrap(), media_type="text/event-stream")
    return _local_llm_response(body.messages)
