"""Task A (v3): apply the vision-enumerated labels to visible_elements.

Rule (fixed before the development loop, applied identically to all 24
steps, OpendTect and QGIS): every label the vision model read (category
A in gt_visible_elements_review_v3.md, i.e. not already covered by the
current GT under the v3 loose containment) is appended to
visual_state_gt.visible_elements. Existing entries are kept. Labels
shorter than 3 characters (after canonicalisation) are kept but the scorer
grounds them by exact match only (evaluation._hallucinated_elements_impl).

Also writes gt_review_B_and_samples.md: the 25 current-GT entries the
vision model did not read (category B, human decision) and three sample
steps with their full applied lists for spot checking.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SAMPLES = [("opendtect__survey_setup__01", 0), ("opendtect__attribute_computation__01", 3), ("qgis__vector_buffer__01", 3)]


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
    enum = json.load(open(ROOT / "data/eval/results/gt_visible_elements_enum_v3.json", encoding="utf-8"))
    review = ["# GT review — B items (current GT not read by vision) + 3 applied samples", "",
              "Category A (vision-read labels not covered by the old GT) has been applied to every step. "
              "B entries are kept in the GT unless you strike them; decide per line.", ""]
    total_added = 0; b_items = []
    for f in sorted((ROOT / "data/eval/scenarios").glob("*.json")):
        scen = json.load(open(f, encoding="utf-8"))
        sid = scen.get("scenario_id")
        if not sid or sid == "EXAMPLE_PLACEHOLDER":
            continue
        for step in scen["steps"]:
            i = step["step_index"]; key = f"{sid}#{i}"
            seen = []
            for k, v in (enum.get(key) or {}).items():
                if isinstance(v, list):
                    seen += [str(x).strip() for x in v if str(x).strip()]
            vs = step.setdefault("visual_state_gt", {})
            gt = list(vs.get("visible_elements") or [])
            add = []
            for s in seen:
                if not covered(s, gt + add):
                    add.append(s)
            missing = [g for g in gt if not covered(g, seen)]
            for g in missing:
                b_items.append((sid, i, step["screenshot_path"], g))
            vs["visible_elements"] = gt + add
            vs["_gt_provenance"] = f"v3: {len(gt)} authored + {len(add)} vision-enumerated (gemini-2.5-pro, temperature 0, 2026-09-18)"
            total_added += len(add)
            if (sid, i) in SAMPLES:
                review.append(f"## SAMPLE {sid} step {i} — {step['screenshot_path']}")
                review.append("applied visible_elements (" + str(len(vs["visible_elements"])) + "): " + " | ".join(vs["visible_elements"]))
                review.append("")
        json.dump(scen, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"{sid}: applied")
    review.append(f"## B items ({len(b_items)}) — current GT entries the vision model did not read")
    review.append("| scenario | step | screenshot | GT entry | keep? |"); review.append("|---|---|---|---|---|")
    for sid, i, path, g in b_items:
        review.append(f"| {sid} | {i} | {path} | {g} | |")
    review.append("")
    review.append("Also for decision (patterns, not GT): survey_setup step 0 has no text label on the Add button (models write '+ 아이콘'); "
                  "QGIS step 3 expects 'Input layer' selection but the captured dialog may already show roads_33S. Patterns were NOT changed.")
    (ROOT / "data/eval/results/gt_review_B_and_samples.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    print(f"total added {total_added}; B items {len(b_items)}; review -> data/eval/results/gt_review_B_and_samples.md")


if __name__ == "__main__":
    main()
