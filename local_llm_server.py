"""Simple OpenAI-compatible API server using transformers + torch."""
import json
import uuid
from threading import Thread

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Any, List, Optional
import uvicorn

app = FastAPI()

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
print(f"Loading {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
print("Model loaded!")


class ChatRequest(BaseModel):
    messages: List[Any]
    model: Optional[str] = None
    stream: Optional[bool] = True
    max_tokens: Optional[int] = 2048
    temperature: Optional[float] = 0.7


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    text = tokenizer.apply_chat_template(
        request.messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    if request.stream:
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        gen_kwargs = {
            **inputs,
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
            "do_sample": request.temperature > 0,
            "streamer": streamer,
        }
        thread = Thread(target=model.generate, kwargs=gen_kwargs)
        thread.start()

        def generate_stream():
            msg_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
            for token_text in streamer:
                chunk = {
                    "id": msg_id,
                    "object": "chat.completion.chunk",
                    "choices": [{"index": 0, "delta": {"content": token_text}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(chunk)}\n\n"
            yield f"data: {json.dumps({'id': msg_id, 'object': 'chat.completion.chunk', 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    else:
        outputs = model.generate(**inputs, max_new_tokens=request.max_tokens, temperature=request.temperature, do_sample=request.temperature > 0)
        response_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": response_text}, "finish_reason": "stop"}],
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11434)
