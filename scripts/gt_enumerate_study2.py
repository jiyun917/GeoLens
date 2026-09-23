"""Study 2 GT enumeration — identical procedure to scripts/gt_enumerate_visible_elements.py
(same PROMPT, same model gemini-2.5-pro, temperature 0, JSON output, same loose-containment
diff), but reads the study-2 scenario drafts from --dir and writes study-2 output files so the
v3 artefacts (gt_visible_elements_enum_v3.json / _review_v3.md) are never overwritten.
Model response logs from any benchmark run are never consulted.

Usage: .venv/Scripts/python.exe scripts/gt_enumerate_study2.py [--dir data/eval/study2/scenarios_draft]
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT))
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
from gt_enumerate_visible_elements import PROMPT, covered  # noqa: E402  (same prompt and diff rule as v3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("GT_VISION_MODEL", "gemini-2.5-pro"))
    ap.add_argument("--dir", default="data/eval/study2/scenarios_draft")
    ap.add_argument("--out-prefix", default="data/eval/study2/gt_visible_elements")
    args = ap.parse_args()
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=120_000))
    cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    enum_out = {}
    review = [f"# Study 2 GT visible_elements — vision enumeration ({args.model}, temperature 0), {time.strftime('%Y-%m-%d')}", "",
              "Same procedure as v3 (gt_enumerate_visible_elements.py). The drafts have no visible_elements yet, so every label read is a candidate (A). "
              "Nothing has been applied to the scenario files.", ""]
    usage = {"prompt": 0, "candidates": 0, "thoughts": 0}
    for f in sorted(glob.glob(str(ROOT / args.dir / "*.json"))):
        scen = json.load(open(f, encoding="utf-8"))
        sid = scen.get("scenario_id")
        review.append(f"## {sid}")
        for step in scen["steps"]:
            i = step["step_index"]
            if not (ROOT / step["screenshot_path"]).exists():
                print(f"{sid} s{i}: screenshot missing - skipped", flush=True); continue
            img = open(ROOT / step["screenshot_path"], "rb").read()
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=PROMPT),
                                                          types.Part.from_bytes(data=img, mime_type="image/jpeg")])]
            raw = ""
            for attempt in range(3):
                try:
                    r = client.models.generate_content(model=args.model, contents=contents, config=cfg)
                    raw = (r.text or "").strip()
                    um = getattr(r, "usage_metadata", None)
                    if um:
                        usage["prompt"] += int(getattr(um, "prompt_token_count", 0) or 0)
                        usage["candidates"] += int(getattr(um, "candidates_token_count", 0) or 0)
                        usage["thoughts"] += int(getattr(um, "thoughts_token_count", 0) or 0)
                    break
                except Exception as e:
                    print("retry", sid, i, e); time.sleep(5)
            try:
                enum = json.loads(raw)
            except Exception:
                m = re.search(r"\{[\s\S]*\}", raw); enum = json.loads(m.group()) if m else {}
            enum_out[f"{sid}#{i}"] = enum
            seen = []
            for k, v in (enum or {}).items():
                if isinstance(v, list):
                    seen += [str(x) for x in v if str(x).strip()]
            gt = list((step.get("visual_state_gt") or {}).get("visible_elements") or [])
            add = [s for s in seen if not covered(s, gt)]
            review.append(f"### step {i} — {step['screenshot_path']}")
            review.append(f"- vision read ({len(seen)}): " + " | ".join(seen))
            review.append(f"- **A. candidate additions ({len(add)})**: " + (" | ".join(add) if add else "(none)"))
            review.append("")
            print(f"{sid} s{i}: seen={len(seen)} add={len(add)}", flush=True)
    Path(ROOT / f"{args.out_prefix}_enum_study2.json").write_text(json.dumps(enum_out, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(ROOT / f"{args.out_prefix}_review_study2.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    cost = usage["prompt"] / 1e6 * 1.25 + (usage["candidates"] + usage["thoughts"]) / 1e6 * 10.0
    print(f"saved; tokens prompt={usage['prompt']} out={usage['candidates']} thoughts={usage['thoughts']} ≈ ${cost:.2f}")


if __name__ == "__main__":
    main()
