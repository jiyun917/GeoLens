"""Probe: reproduce a full_system + Gemini API call for a specific
scenario step and DUMP everything about the raw response — finish_reason,
safety_ratings, prompt_feedback, candidates structure — so we can pin
down WHY the bench got empty strings.

Usage:
    .venv/Scripts/python.exe scripts/probe_empty_response.py \\
        --scenario opendtect__3d_visualization__01 \\
        --step 3 \\
        --repeats 3
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env.local")
except ImportError:
    pass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _load_scenario(sid: str) -> dict:
    p = ROOT / "data" / "eval" / "scenarios" / f"{sid}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _build_full_system_messages(scen: dict, step_index: int):
    """Reconstruct exactly what backend_full_system would send to the LLM."""
    from api.services.bench_backends import _load_screenshot_b64, _build_messages
    from api.services.rag_router import get_rag_router

    screenshot_b64 = _load_screenshot_b64(scen, step_index)
    visited: list[str] = []
    if step_index > 0:
        from api.services.guide_pipeline import get_guide_pipeline
        pipeline = get_guide_pipeline()
        for j in range(step_index):
            prev_b64 = _load_screenshot_b64(scen, j)
            if not prev_b64:
                continue
            vs = pipeline.recognize_visual_state(prev_b64)
            loc = pipeline.localize_to_graph(
                vs, None, screenshot_b64=prev_b64,
                manual_ids=[scen["manual_id"]],
                user_goal=scen.get("goal", ""),
                visited_node_ids=list(visited),
            )
            n = loc.get("node")
            if n and n["id"] not in visited:
                visited.append(n["id"])

    session_state = {"mode": "guide", "visited_node_ids": visited}
    result = get_rag_router().route(
        user_message=scen.get("goal", ""),
        screenshot_b64=screenshot_b64,
        session_state=session_state,
        manual_ids=[scen["manual_id"]],
    )
    context_block = result.get("context_block", "") or ""
    prior_responses = [f"placeholder step {i}" for i in range(step_index)]
    messages = _build_messages(scen, step_index, prior_responses, context_block=context_block)
    return messages, context_block


def _call_gemini_raw(messages, model="gemini-2.5-pro"):
    import os
    gkey = os.environ.get("GEMINI_API_KEY")
    if not gkey:
        return {"error": "GEMINI_API_KEY not set"}
    from google import genai
    from google.genai import types
    from api.routers.task import convert_openai_to_gemini

    client = genai.Client(api_key=gkey, http_options=types.HttpOptions(timeout=120_000))
    sys_text = ""
    non_sys = []
    for m in messages:
        if m["role"] == "system":
            c = m["content"]
            sys_text = c if isinstance(c, str) else " ".join(
                p.get("text", "") for p in c if p.get("type") == "text"
            )
        else:
            non_sys.append(m)
    contents = convert_openai_to_gemini(non_sys)

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=types.Content(
                parts=[types.Part.from_text(text=sys_text)]
            ) if sys_text else None,
        ),
    )

    dump = {
        "text_property": resp.text,
        "text_property_len": len(resp.text or ""),
        "sys_text_len": len(sys_text),
        "candidates_count": len(resp.candidates or []),
    }
    if resp.candidates:
        cand_dumps = []
        for i, c in enumerate(resp.candidates):
            cd = {
                "index": i,
                "finish_reason": str(getattr(c, "finish_reason", None)),
                "finish_message": str(getattr(c, "finish_message", None)),
                "safety_ratings": [
                    {"category": str(getattr(r, "category", None)),
                     "probability": str(getattr(r, "probability", None)),
                     "blocked": getattr(r, "blocked", None)}
                    for r in (getattr(c, "safety_ratings", None) or [])
                ],
            }
            content = getattr(c, "content", None)
            if content is not None:
                parts = getattr(content, "parts", None) or []
                cd["parts_count"] = len(parts)
                cd["parts_preview"] = [
                    {"text": (getattr(p, "text", None) or "")[:300],
                     "text_len": len(getattr(p, "text", None) or "")}
                    for p in parts
                ]
            cand_dumps.append(cd)
        dump["candidates"] = cand_dumps
    pf = getattr(resp, "prompt_feedback", None)
    if pf is not None:
        dump["prompt_feedback"] = {
            "block_reason": str(getattr(pf, "block_reason", None)),
            "safety_ratings": [
                {"category": str(getattr(r, "category", None)),
                 "probability": str(getattr(r, "probability", None))}
                for r in (getattr(pf, "safety_ratings", None) or [])
            ],
        }
    um = getattr(resp, "usage_metadata", None)
    if um is not None:
        dump["usage_metadata"] = {
            "prompt_token_count": getattr(um, "prompt_token_count", None),
            "candidates_token_count": getattr(um, "candidates_token_count", None),
            "total_token_count": getattr(um, "total_token_count", None),
        }
    return dump


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="opendtect__3d_visualization__01")
    ap.add_argument("--step", type=int, default=3)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--model", default="gemini-2.5-pro")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    scen = _load_scenario(args.scenario)
    print(f"[probe] scenario={args.scenario} step={args.step} model={args.model} repeats={args.repeats}")
    messages, context_block = _build_full_system_messages(scen, args.step)
    sys_chars = sum(
        len(m["content"]) if isinstance(m["content"], str) else sum(
            len(p.get("text", "")) for p in m["content"] if p.get("type") == "text"
        )
        for m in messages if m["role"] == "system"
    )
    print(f"[probe] built messages: {len(messages)} turns, context_block={len(context_block)} chars, system_msg={sys_chars} chars")

    results = []
    for r in range(1, args.repeats + 1):
        print(f"\n--- attempt {r}/{args.repeats} ---")
        try:
            dump = _call_gemini_raw(messages, model=args.model)
        except Exception as e:
            dump = {"error": f"{type(e).__name__}: {e}"}
        dump["_attempt"] = r
        results.append(dump)
        print(json.dumps(dump, ensure_ascii=False, indent=2, default=str)[:2500])

    out_path = ROOT / "data" / "eval" / "results" / (args.out or f"probe_{args.scenario}_step{args.step}.json")
    out_path.write_text(json.dumps({
        "scenario_id": args.scenario,
        "step_index": args.step,
        "model": args.model,
        "context_block_chars": len(context_block),
        "system_message_chars": sys_chars,
        "results": results,
    }, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n[probe] Full dump written: {out_path}")


if __name__ == "__main__":
    main()
