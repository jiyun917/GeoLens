import json
import time
import traceback
import uuid
import base64
from typing import Any, List, Optional
from google.genai import types


def convert_openai_to_gemini(messages: List[Any]) -> List[types.Content]:
    gemini_messages = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        # Map OpenAI roles to Gemini roles
        # OpenAI: system, user, assistant, tool
        # Gemini: system (via config), user, model
        if role == "system":
            continue

        gemini_role = "user" if role == "user" else "model"

        parts = []
        if isinstance(content, str):
            parts.append(types.Part.from_text(text=content))
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    parts.append(types.Part.from_text(text=part.get("text")))
                elif part.get("type") == "image_url":
                    image_url = part.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image/"):
                        # Handle base64 image
                        try:
                            header, data = image_url.split(",", 1)
                            mime_type = header.split(";")[0].split(":")[1]
                            parts.append(
                                types.Part.from_bytes(
                                    data=base64.b64decode(data), mime_type=mime_type
                                )
                            )
                        except Exception:
                            print(
                                f"Error parsing base64 image: {traceback.format_exc()}"
                            )
                    elif image_url.startswith("gs://"):
                        # Handle Cloud Storage URI
                        parts.append(
                            types.Part.from_uri(
                                file_uri=image_url, mime_type="image/png"
                            )
                        )
                    else:
                        pass

        if parts:
            gemini_messages.append(types.Content(role=gemini_role, parts=parts))

    return gemini_messages


def stream_gemini(
    stream,
    endpoint_name: Optional[str] = None,
    start_time: Optional[float] = None,
):
    try:
        if start_time is None:
            start_time = time.time()
        first_chunk_logged = False

        def format_sse(payload: dict) -> str:
            return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"

        message_id = f"msg-{uuid.uuid4().hex}"
        text_stream_id = "text-1"
        text_started = False
        text_finished = False
        full_response_text = ""

        yield format_sse({"type": "start", "messageId": message_id})

        for chunk in stream:
            if not first_chunk_logged:
                first_chunk_logged = True
                print(
                    f"[{endpoint_name or 'gemini-stream'}] Time to first chunk: {(time.time() - start_time) * 1000:.2f}ms"
                )

            if chunk.text:
                full_response_text += chunk.text
                if not text_started:
                    yield format_sse({"type": "text-start", "id": text_stream_id})
                    text_started = True
                yield format_sse(
                    {
                        "type": "text-delta",
                        "id": text_stream_id,
                        "delta": chunk.text,
                    }
                )

        if text_started and not text_finished:
            yield format_sse({"type": "text-end", "id": text_stream_id})
            text_finished = True

        finish_metadata = {}

        yield format_sse(
            {"type": "finish", "messageMetadata": finish_metadata}
            if finish_metadata
            else {"type": "finish"}
        )

        print(
            f"[{endpoint_name or 'gemini-stream'}] Total stream time: {(time.time() - start_time) * 1000:.2f}ms | Response: {full_response_text[:200]}"
        )

        yield "data: [DONE]\n\n"
    except Exception:
        traceback.print_exc()
        raise
