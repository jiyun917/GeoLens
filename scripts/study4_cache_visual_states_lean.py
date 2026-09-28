# -*- coding: utf-8 -*-
"""Lean variant of study4_cache_visual_states.py: the SAME vision call as GuideRAGPipeline.recognize_visual_state
(gemini-2.5-flash, prompt v3 per software profile, JSON, temperature 0, AUX_THINKING_BUDGET thinking config) made
directly with the google-genai client, WITHOUT instantiating the pipeline (no ChromaDB / CLIP initialisation, which
stalls while three benchmark processes hold the stores). Output format identical to the full script.
Usage: .venv/Scripts/python.exe scripts/study4_cache_visual_states_lean.py --dirs data/eval/study4/scenarios_draft
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, re, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass
os.environ.setdefault("AUX_THINKING_BUDGET", "0")
os.environ.setdefault("VISION_PROMPT_VERSION", "v3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", required=True); ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    from api.services.guide_pipeline import _build_visual_state_prompt, _aux_thinking_config, _extract_json
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=60_000))
    out_root = ROOT / "data/eval/study4/visual_states"
    n_call = n_skip = 0
    for d in args.dirs.split(","):
        for f in sorted(glob.glob(str(ROOT / d / "*.json"))):
            sc = json.load(open(f, encoding="utf-8")); sid = sc["scenario_id"]
            software = "qgis" if sid.startswith("qgis") else "opendtect"
            prompt = _build_visual_state_prompt(software)
            (out_root / sid).mkdir(parents=True, exist_ok=True)
            for st in sc["steps"]:
                i = st["step_index"]; sp = ROOT / st["screenshot_path"]; out = out_root / sid / f"step_{i}.json"
                if not sp.exists():
                    print(f"{sid} s{i}: screenshot missing"); continue
                raw = sp.read_bytes(); sha = hashlib.sha256(raw).hexdigest()
                if out.exists() and not args.force:
                    try:
                        if json.load(open(out, encoding="utf-8")).get("sha256") == sha:
                            n_skip += 1; continue
                    except Exception:
                        pass
                contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt), types.Part.from_bytes(data=raw, mime_type="image/jpeg")])]
                config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0, thinking_config=_aux_thinking_config(types))
                vs = {}
                for attempt in range(4):
                    try:
                        r = client.models.generate_content(model="gemini-2.5-flash", contents=contents, config=config)
                        vs = _extract_json(r.text) or {}
                        if vs:
                            break
                    except Exception as e:
                        print(f"  retry {sid} s{i}: {str(e)[:80]}", flush=True)
                    time.sleep(3 + 3 * attempt)
                out.write_text(json.dumps({"scenario_id": sid, "step_index": i, "screenshot_path": st["screenshot_path"], "sha256": sha,
                                           "software_id": software, "vision_prompt": "v3", "visual_state": vs}, ensure_ascii=False, indent=1), encoding="utf-8")
                n_call += 1
                print(f"{sid} s{i}: {'ok' if vs else 'EMPTY'} dialog={str(vs.get('current_dialog'))[:50]!r}", flush=True)
    print(f"done: calls={n_call} skipped={n_skip}")


if __name__ == "__main__":
    main()
