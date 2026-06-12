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
