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

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class MessagesRequest(BaseModel):
    messages: List[Any]


class StepRequest(BaseModel):
    messages: List[Any]
    manual_ids: Optional[List[str]] = None


class AnnotateRequest(BaseModel):
    image: str
    data_type: str = "other"
    description: str = ""
    topic: str = ""


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
        model="gemini-2.5-pro",
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

        # Use goal + recent steps as the RAG query
        query = " ".join(query_parts[-3:]) if query_parts else ""
        print(f"[STEP] RAG query: {query[:150]}")

        if query:
            context = get_manual_context(body.manual_ids, query)
            if context:
                # Prepend manual context to the system message
                context_block = (
                    "\n\n--- Reference Manual Context ---\n"
                    f"{context}\n"
                    "--- End Reference Manual Context ---\n"
                )
                # Find system message and append context
                for msg in messages:
                    if msg.get("role") == "system":
                        if isinstance(msg["content"], str):
                            msg["content"] += context_block
                        elif isinstance(msg["content"], list):
                            msg["content"].append({"type": "text", "text": context_block})
                        break
                else:
                    # No system message found, add one
                    messages.insert(0, {"role": "system", "content": context_block})

    # Use Gemini (vision-capable) as primary, local LLM as fallback
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

    # Extract topic + capture descriptions for precise Graph RAG query
    topic_parts = []
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
                        topic_parts.append(part.get("text", ""))

    query = " ".join(topic_parts) if topic_parts else ""
    print(f"[REPORT] Graph RAG query: {query[:200]}")

    if query:
        context = get_manual_context(body.manual_ids or [], query, top_k=10)
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

    # Report generation needs vision for screenshot analysis
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

ANNOTATE_PROMPT = """You are an expert geoscientist. Detect and precisely locate geological features in this {data_type} image.
Context: {topic} — {description}
{data_type_hint}

## Coordinate System (CRITICAL — follow exactly)
Normalized 0.0 to 1.0:
- (0.0, 0.0) = top-left corner, (1.0, 1.0) = bottom-right corner
- (0.5, 0.5) = exact center of image
- x increases left→right, y increases top→bottom

## How to locate features precisely
For each feature, think step by step:
1. What fraction of the image width (0.0-1.0) is the feature's LEFT edge? RIGHT edge?
2. What fraction of the image height (0.0-1.0) is the feature's TOP? BOTTOM?
3. For lines: trace 8-12 points along the feature. At curves, place points closer together.
4. Double-check: a feature at the image center should have coords near (0.5, 0.5).

## Geometry types
- "line": array of 8-12 {{x,y}} points. Geological features are usually CURVED — capture the curvature with well-placed points.
- "bbox": x, y (top-left corner), width, height
- "point": x, y

feature_type: fault, horizon, unconformity, anomaly, stratigraphic_boundary, fold, intrusion, contact, fracture_zone, amplitude_anomaly, velocity_anomaly, well_marker, formation_top, log_anomaly

Output format:
{{"annotations": [{{"id":"h1","feature_type":"horizon","label":"Horizon H1","confidence":"high",
"geometry":{{"type":"line","points":[{{"x":0.05,"y":0.40}},{{"x":0.15,"y":0.38}},{{"x":0.30,"y":0.34}},{{"x":0.40,"y":0.32}},{{"x":0.50,"y":0.33}},{{"x":0.60,"y":0.36}},{{"x":0.75,"y":0.41}},{{"x":0.90,"y":0.44}}]}},
"description":"Curved reflector with synclinal geometry"}}]}}

Rules: max 5 features, only CLEARLY visible ones, coordinates strictly 0.0-1.0.
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
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        return {"annotations": []}

    try:
        client = genai.Client(api_key=gemini_api_key)

        hint = _DATA_TYPE_HINTS.get(body.data_type, "Detect geological features.")

        prompt = ANNOTATE_PROMPT.format(
            data_type=body.data_type,
            topic=body.topic or "geological interpretation",
            description=body.description or "no description",
            data_type_hint=hint,
        )

        import base64 as b64mod
        image_data = body.image
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        image_bytes = b64mod.b64decode(image_data)

        # Resize large images to speed up API call (coordinates are normalized so this is safe)
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_bytes))
            max_dim = 1536
            if max(img.size) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                image_bytes = buf.getvalue()
        except Exception:
            pass

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

        import json
        result = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=contents,
            config=config,
        )

        parsed = json.loads(result.text)
        raw_annotations = parsed.get("annotations", [])
        annotations = _validate_annotations(raw_annotations)
        print(f"[ANNOTATE] Detected {len(annotations)} features (raw: {len(raw_annotations)}) for {body.data_type}")
        return {"annotations": annotations}

    except Exception as e:
        print(f"[ANNOTATE] Error: {e}")
        return {"annotations": []}


@router.post("/api/coordinates")
@limiter.limit("15/minute;200/hour")
async def handle_coordinate_chat(request: FastAPIRequest, body: MessagesRequest):
    # Coordinates locates UI elements - needs vision
    response = _gemini_stream_response(body.messages)
    if response:
        return response
    return _local_llm_response(body.messages)
