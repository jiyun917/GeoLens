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
import base64 as _b64
import json
import uuid
import time

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Runtime-settable capture scenario. Overrides EVAL_CAPTURE_SCENARIO env var
# when set. Lets the eval helper script switch scenarios without restarting
# the dev server.
_active_eval_scenario: Optional[str] = None


def _save_capture_for_eval(screenshot_data_url: str, scenario_id: str, step_index: int) -> None:
    """When EVAL_CAPTURE_SCENARIO env is set, persist the inbound screenshot
    to data/eval/screenshots/{scenario_id}/step_{i}.png so it can be replayed
    by bench_runner offline."""
    if not screenshot_data_url or not scenario_id:
        return
    try:
        if "," not in screenshot_data_url:
            return
        header, data = screenshot_data_url.split(",", 1)
        ext = "png" if "png" in header.lower() else "jpg"
        out_dir = os.path.join("data", "eval", "screenshots", scenario_id)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"step_{step_index}.{ext}")
        with open(out_path, "wb") as f:
            f.write(_b64.b64decode(data))
        print(f"[EVAL-CAPTURE] saved {out_path}")
    except Exception as e:
        print(f"[EVAL-CAPTURE] save failed: {e}")


class MessagesRequest(BaseModel):
    messages: List[Any]


class StepRequest(BaseModel):
    messages: List[Any]
    manual_ids: Optional[List[str]] = None
    session_state: Optional[dict] = None  # mode, visited_node_ids, active_workflow_id, etc.


def _claude_stream_response(messages, model="claude-opus-4-20250514"):
    """Create a Claude streaming response."""
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

    # Eval capture mode: save inbound screenshot to disk indexed by
    # assistant-message count. Each /step call represents step N where
    # N = number of assistant messages already in the conversation.
    # Step 0 is the initial screen before any AI action. Runtime-set
    # scenario (via /api/eval/capture-scenario) takes priority over env.
    eval_scenario = _active_eval_scenario or os.environ.get("EVAL_CAPTURE_SCENARIO")
    if eval_scenario:
        step_index = sum(1 for m in messages if m.get("role") == "assistant")
        capture_screenshot = None
        for m in reversed(messages):
            c = m.get("content")
            if isinstance(c, list):
                for part in c:
                    if part.get("type") == "image_url":
                        capture_screenshot = part.get("image_url", {}).get("url")
                        if capture_screenshot:
                            break
            if capture_screenshot:
                break
        if capture_screenshot:
            _save_capture_for_eval(capture_screenshot, eval_scenario, step_index)

    # Enrich system prompt with manual context if manual_ids provided
    if body.manual_ids:
        # Build RAG query: ALWAYS include the goal (the high-level user intent)
        # plus the last 2 assistant messages (current local state). Earlier code
        # dropped the goal once 5+ messages accumulated, which caused RAG to
        # search only on recent actions ("clicked Survey → clicked Import")
        # instead of the user's actual objective (e.g. "3차원 시각화" / "3D
        # visualization" — Korean user scenarios are the KO deployment target,
        # see README §7 Language policy).
        goal_text = ""
        assistant_texts: List[str] = []
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "")
                if isinstance(content, str) and "# Goal" in content and not goal_text:
                    try:
                        start = content.index("# Goal") + len("# Goal\n")
                        end = content.index("\n#", start) if "\n#" in content[start:] else start + 200
                        goal_text = content[start:end].strip()
                    except ValueError:
                        pass
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, str):
                    assistant_texts.append(content)

        query_pieces: List[str] = []
        if goal_text:
            # Weight goal 2x so retrieval stays anchored to the user's overall
            # intent even when local actions accumulate.
            query_pieces.append(goal_text)
            query_pieces.append(goal_text)
        # Only include recent assistant text in the early phase. Deep into a
        # workflow (>3 steps) those messages describe local UI actions
        # ("Click Next", "Click Import") and drift RAG away from the goal —
        # the graph-RAG router's screenshot already carries the local context.
        if len(assistant_texts) <= 3:
            query_pieces.extend(assistant_texts[-2:])
        raw_query = " ".join(query_pieces)
        query = raw_query
        print(f"[STEP] RAG query (n_asst={len(assistant_texts)}): {query[:150]}")

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
            # Scan a much wider assistant-message window (was 6). At step 15+
            # the offending "Click Next" instruction that opened the current
            # dialog is often 5-10 turns back and was falling outside the
            # window, so this fallback never fired.
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
                    if count >= 15:
                        break
            joined = "\n".join(recent_assistant_text).lower()
            dialog_lc = current_dialog.lower()
            # Fuzzy match: full dialog title OR any significant token (>=4 chars)
            # from it. E.g. "Import SEG-Y Data" matches "SEG-Y" or "Import"
            # even when the model paraphrased the dialog name in prior turns.
            tokens = [t for t in dialog_lc.replace("-", " ").split() if len(t) >= 4]
            matched = dialog_lc in joined or any(t in joined for t in tokens)
            if matched:
                # Hint is PREPENDED (not appended) so it appears BEFORE the
                # RAG chunks. Previously the hint sat at the bottom of the
                # system context, after ~3k chars of manual chunks that
                # explicitly instruct "click Next → click Import → click
                # Close". The model followed the manual literally and
                # ignored the tail-hint. Placing the hint first + wrapping
                # it in explicit override language makes it dominate.
                hint = (
                    "\n\n"
                    "╔══════════════════════════════════════════════════════════════╗\n"
                    "║ ██ MANDATORY POST-COMPLETION OVERRIDE — READ BEFORE MANUAL ██ ║\n"
                    "╚══════════════════════════════════════════════════════════════╝\n"
                    f"The current dialog \"{current_dialog}\" was already the subject "
                    "of a previous instruction in this session. The action you gave "
                    "on this dialog earlier has finished — the dialog is just "
                    "lingering as a residual/post-completion state.\n"
                    "\n"
                    "HARD RULES (override everything below including manual RAG chunks):\n"
                    "1. DO NOT instruct any button click that would ADVANCE this dialog "
                    "(no Next, no Import, no OK on this dialog, no re-entering fields).\n"
                    "2. IGNORE any manual-context sentence that says to press Next/Import/OK "
                    "on this dialog — those describe the FIRST time through the dialog, "
                    "not this repeat visit.\n"
                    "3. Instruct the user to DISMISS the dialog. Look for one of these buttons "
                    "in the screenshot: Close, Finish, Done, X in the title bar, or Cancel "
                    "(only if no other dismiss option exists).\n"
                    "4. Your entire response must target the dismiss button. One instruction only.\n"
                    "═══════════════════════════════════════════════════════════════\n\n"
                )
                # Prepend to context_block so it comes BEFORE RAG chunks.
                context_block = hint + (context_block or "")
                print(f"[STEP] post-completion text-fallback fired for dialog='{current_dialog}' (hint prepended)")

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

    # Architecture: Gemini 2.5 Pro as PRIMARY agent for /step (main step
    # generation) — best cost/latency trade-off with strong visual grounding
    # at Pro tier. Claude Sonnet 4.6 as SUB-AGENT (Anthropic fallback) for
    # cases where Gemini quota/health fails or an alternative reasoning path
    # is desired. Local LLM as last-resort text-only fallback.
    response = _gemini_stream_response(messages)
    if response:
        return response
    response = _claude_stream_response(messages, model="claude-sonnet-4-6")
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


class CaptureScenarioRequest(BaseModel):
    scenario_id: Optional[str] = None  # null = stop capturing


@router.post("/api/eval/capture-scenario")
async def set_capture_scenario(body: CaptureScenarioRequest):
    """Set/clear the active capture scenario at runtime. Overrides env var."""
    global _active_eval_scenario
    _active_eval_scenario = body.scenario_id
    print(f"[EVAL-CAPTURE] active scenario set to: {_active_eval_scenario!r}")
    return {"scenario_id": _active_eval_scenario}


@router.get("/api/eval/capture-scenario")
async def get_capture_scenario():
    """Inspect current active capture scenario."""
    env_val = os.environ.get("EVAL_CAPTURE_SCENARIO")
    return {"scenario_id": _active_eval_scenario, "env_fallback": env_val}
