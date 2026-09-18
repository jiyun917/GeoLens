"""Task 5 (v3): enumerate every readable on-screen label for each scenario
screenshot with a vision model at temperature 0, and produce a REVIEW file
that diffs the enumeration against the current visible_elements ground
truth. Nothing is written back to the scenario JSONs — the user reviews
the diff first.

Procedure (identical for all 24 screenshots, OpendTect 16 + QGIS 8):
  1. Send the screenshot with a fixed enumeration prompt (dialog/window
     titles, menu items, buttons, tabs, field labels, list/tree entries,
     checkbox/radio labels, status-bar text) to GT_VISION_MODEL
     (default gemini-2.5-pro), temperature 0, JSON output.
  2. Store the raw enumeration per step (gt_visible_elements_enum_v3.json).
  3. Diff against the scenario's visual_state_gt.visible_elements using the
     v3 scorer's loose canonical containment, and list per step:
     - candidates to ADD (seen by the model, not covered by current GT)
     - current GT entries NOT seen by the model (to be checked by a human)
Model response logs from any benchmark run are never consulted.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
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

PROMPT = """You are transcribing the user interface shown in this screenshot of a desktop application.
List EVERY piece of text that a user could read on screen, grouped by kind. Copy labels verbatim (keep capitalisation, hyphens, brackets, numbers). Do not guess hidden items; do not describe; do not interpret. Ignore the GeoLens chat window if present.

Return JSON only:
{
  "window_titles": ["title-bar text of every visible window/dialog"],
  "menu_items": ["visible menu-bar entries and open context-menu/submenu entries"],
  "buttons": ["push buttons, toolbar buttons with text, OK/Cancel/Next/... "],
  "tabs": ["tab labels"],
  "field_labels": ["labels of text fields, dropdowns, spinboxes, incl. their current value in parentheses if readable"],
  "list_or_tree_entries": ["entries in lists, trees, tables (e.g. tree nodes, layer names)"],
  "checkbox_radio_labels": ["checkbox / radio-button labels with state if visible"],
  "other_text": ["status-bar text, headings, panel titles, tooltips, anything else readable"]
}"""


def canon(s: str) -> str:
    return re.sub(r"[^a-z0-9가-힣]+", "", (s or "").lower())


def covered(item: str, gt_list: list) -> bool:
    c = canon(item)
    if len(c) < 2:
        return True
    for g in gt_list:
        gc = canon(g)
        if c in gc or (len(gc) >= 3 and gc in c):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("GT_VISION_MODEL", "gemini-2.5-pro"))
    ap.add_argument("--scenarios", nargs="*", default=None)
    args = ap.parse_args()
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=120_000))
    cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    enum_out = {}
    review = [f"# GT visible_elements review — vision enumeration ({args.model}, temperature 0), {time.strftime('%Y-%m-%d')}", "",
              "For each step: A = labels the vision model read that the current GT does not cover (candidate additions); "
              "B = current GT entries the model did not read (human check: hidden/absent, or paraphrase?). "
              "Coverage uses the v3 loose canonical containment. Nothing has been applied to the scenario files.", ""]
    for f in sorted(glob.glob(str(ROOT / "data/eval/scenarios/*.json"))):
        scen = json.load(open(f, encoding="utf-8"))
        sid = scen.get("scenario_id")
        if not sid or sid == "EXAMPLE_PLACEHOLDER" or (args.scenarios and sid not in args.scenarios):
            continue
        review.append(f"## {sid}")
        for step in scen["steps"]:
            i = step["step_index"]
            img = open(ROOT / step["screenshot_path"], "rb").read()
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=PROMPT),
                                                          types.Part.from_bytes(data=img, mime_type="image/jpeg")])]
            raw = ""
            for attempt in range(3):
                try:
                    r = client.models.generate_content(model=args.model, contents=contents, config=cfg)
                    raw = (r.text or "").strip()
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
            missing = [g for g in gt if not covered(g, seen)]
            review.append(f"### step {i} — {step['screenshot_path']}")
            review.append(f"- current GT ({len(gt)}): " + " | ".join(gt))
            review.append(f"- vision read ({len(seen)}): " + " | ".join(seen))
            review.append(f"- **A. candidate additions ({len(add)})**: " + (" | ".join(add) if add else "(none)"))
            review.append(f"- **B. GT not read by vision ({len(missing)})**: " + (" | ".join(missing) if missing else "(none)"))
            review.append("")
            print(f"{sid} s{i}: seen={len(seen)} gt={len(gt)} add={len(add)} missing={len(missing)}", flush=True)
    (ROOT / "data/eval/results/gt_visible_elements_enum_v3.json").write_text(json.dumps(enum_out, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "data/eval/results/gt_visible_elements_review_v3.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    print("saved review + enum json")


if __name__ == "__main__":
    main()
