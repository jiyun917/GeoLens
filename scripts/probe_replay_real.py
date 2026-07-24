"""Probe #2: replay the exact failing step by loading the REAL prior
responses from a previously-recorded bench run. First probe used
fabricated placeholders and succeeded — suggesting the real prior
responses are what breaks Gemini. This script confirms.
"""

from __future__ import annotations

import argparse
import glob
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


def _find_real_prior_responses(scenario_id: str, backend: str, model: str, step_index: int):
    """Find a bench run that captured this scenario/backend/model and extract
    the actual prior responses used at `step_index`."""
    pattern = str(ROOT / "data" / "eval" / "results" / f"run_{model}_r*_*.json")
    for f in sorted(glob.glob(pattern)):
        if "norag" in f or "flash" in f:
            continue
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for scen in d.get("scenarios") or []:
            if scen.get("scenario_id") != scenario_id:
                continue
            b = scen.get("backends", {}).get(backend)
            if not b or "per_step" not in b:
                continue
            per = b["per_step"]
            if len(per) < step_index:
                continue
            # prior_responses are the previous steps' responses
            prior = [per[i].get("response", "") for i in range(step_index)]
            failed_step = per[step_index] if step_index < len(per) else None
            return {
                "prior_responses": prior,
                "failed_step_summary": {
                    "response": (failed_step or {}).get("response", ""),
                    "latency_sec": (failed_step or {}).get("latency_sec"),
                    "output_tokens": (failed_step or {}).get("output_tokens"),
                    "input_tokens": (failed_step or {}).get("input_tokens"),
                },
                "source_file": Path(f).name,
            }
    return None


def _build(scen, step_index, prior_responses):
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
    messages = _build_messages(scen, step_index, prior_responses, context_block=context_block)
    return messages, context_block


def _call_gemini_raw(messages, model="gemini-2.5-pro", max_output_tokens=None):
    import os
    gkey = os.environ["GEMINI_API_KEY"]
    from google import genai
    from google.genai import types
    from api.routers.task import convert_openai_to_gemini

    client = genai.Client(api_key=gkey, http_options=types.HttpOptions(timeout=180_000))
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

    cfg_kwargs = {
        "system_instruction": types.Content(
            parts=[types.Part.from_text(text=sys_text)]
        ) if sys_text else None,
    }
    if max_output_tokens is not None:
        cfg_kwargs["max_output_tokens"] = max_output_tokens
    config = types.GenerateContentConfig(**cfg_kwargs)

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    dump = {
        "text_property": resp.text,
        "text_property_len": len(resp.text or ""),
        "candidates_count": len(resp.candidates or []),
    }
    if resp.candidates:
        c = resp.candidates[0]
        dump["candidate_0"] = {
            "finish_reason": str(getattr(c, "finish_reason", None)),
            "finish_message": str(getattr(c, "finish_message", None)),
            "safety_ratings_count": len(getattr(c, "safety_ratings", None) or []),
            "parts_count": len(getattr(getattr(c, "content", None), "parts", None) or []),
        }
    pf = getattr(resp, "prompt_feedback", None)
    if pf is not None:
        dump["prompt_feedback"] = {
            "block_reason": str(getattr(pf, "block_reason", None)),
        }
    um = getattr(resp, "usage_metadata", None)
    if um is not None:
        dump["usage_metadata"] = {
            "prompt_token_count": getattr(um, "prompt_token_count", None),
            "candidates_token_count": getattr(um, "candidates_token_count", None),
            "total_token_count": getattr(um, "total_token_count", None),
            "thoughts_token_count": getattr(um, "thoughts_token_count", None),
        }
    return dump


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="opendtect__3d_visualization__01")
    ap.add_argument("--backend", default="full_system")
    ap.add_argument("--model", default="gemini")
    ap.add_argument("--step", type=int, default=3)
    ap.add_argument("--max-output", type=int, default=None, help="Set explicit max_output_tokens")
    args = ap.parse_args()

    real = _find_real_prior_responses(args.scenario, args.backend, args.model, args.step)
    if not real:
        print(f"No prior_responses found for {args.scenario}/{args.backend}/{args.model}/step={args.step}")
        return
    print(f"[replay] source: {real['source_file']}")
    print(f"[replay] failed step summary: {json.dumps(real['failed_step_summary'], ensure_ascii=False)}")
    print("[replay] prior responses:")
    for i, r in enumerate(real["prior_responses"]):
        print(f"  step {i}: {r[:120]!r}")

    scen = _load_scenario(args.scenario)
    messages, context_block = _build(scen, args.step, real["prior_responses"])
    print(f"\n[replay] context_block={len(context_block)} chars")

    # Test 1: baseline (no max_output set — what bench uses)
    print("\n=== TRIAL A: default max_output_tokens (mimics bench) ===")
    try:
        d = _call_gemini_raw(messages, model="gemini-2.5-pro", max_output_tokens=None)
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(f"error: {e}")

    # Test 2: with explicit max_output_tokens=1024
    print("\n=== TRIAL B: max_output_tokens=1024 ===")
    try:
        d = _call_gemini_raw(messages, model="gemini-2.5-pro", max_output_tokens=1024)
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(f"error: {e}")


if __name__ == "__main__":
    main()
