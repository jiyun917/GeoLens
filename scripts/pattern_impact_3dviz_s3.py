"""Decision material for the 3d_visualization step-3 allowed-alternative pattern
(the element-mention alternative '(?i)\\b(In[- ]?line|Cross[- ]?line|Z[- ]?slice|3D Scene|Elements)\\b').

Re-scores step 3 of opendtect__3d_visualization__01 in stored run JSONs with the
scenario's current patterns (A) and with that alternative removed (B), per
model × backend × replicate, and reports every cell whose match flips.
No pattern is changed on disk.

Usage: .venv/Scripts/python.exe scripts/pattern_impact_3dviz_s3.py [--glob "data/eval/results/run_*unified4*_r*.json"] ...
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ.setdefault("GEOLENS_SCORER", "v3")

SID = "opendtect__3d_visualization__01"
ALT_NOTE = "Ground-truth element mention"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--globs", nargs="*", default=[
        "data/eval/results/dev_iter0_v2mech_gemini_r*.json",
        "data/eval/results/dev_iter1_v3_gemini_r*.json",
        "data/eval/results/run_*unified4*_r*.json",
    ])
    ap.add_argument("--out", default="data/eval/results/pattern_impact_3dviz_s3.md")
    args = ap.parse_args()
    from api.services.evaluation import step_match

    scen = json.load(open(f"data/eval/scenarios/{SID}.json", encoding="utf-8"))
    step_a = scen["steps"][3]
    step_b = copy.deepcopy(step_a)
    step_b["allowed_alternatives"] = [a for a in (step_b.get("allowed_alternatives") or []) if ALT_NOTE not in (a.get("note") or "")]
    assert len(step_b["allowed_alternatives"]) == len(step_a.get("allowed_alternatives") or []) - 1, "alternative not found"

    files = []
    for g in args.globs:
        files += sorted(glob.glob(g))
    rows = []
    agg = defaultdict(lambda: [0, 0, 0])  # (group, model, backend) -> [n, matched_A, matched_B]
    for f in files:
        run = json.load(open(f, encoding="utf-8"))
        name = os.path.basename(f)
        group = "unified4" if "unified4" in name else ("dev_iter0" if "dev_iter0" in name else ("dev_iter1" if "dev_iter1" in name else name.split("_")[0]))
        model = "gemini" if "gemini" in name else ("claude" if "claude" in name else ("gpt" if "gpt" in name else ("qwen" if "qwen" in name else "?")))
        for sc in run.get("scenarios", []):
            if sc.get("scenario_id") != SID:
                continue
            for b, m in (sc.get("backends") or {}).items():
                for ps in m.get("per_step", []):
                    if ps.get("step_index") != 3:
                        continue
                    resp = ps.get("response") or ""
                    a = bool(step_match(resp, step_a))
                    bm = bool(step_match(resp, step_b))
                    key = (group, model, b)
                    agg[key][0] += 1
                    agg[key][1] += a
                    agg[key][2] += bm
                    if a != bm:
                        rows.append((group, model, b, name, resp[:120].replace("\n", " "), a, bm))
    lines = ["# 3d_visualization step 3 — impact of the element-mention allowed alternative", "",
             f"A = current patterns (sentinel + 2 alternatives); B = without the alternative noted '{ALT_NOTE}'. Files: {len(files)}.", "",
             "## Cells whose step-3 match changes (A → B)", "",
             "| group | model | backend | file | response (head) | A | B |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | `{r[4]}` | {'✓' if r[5] else '✗'} | {'✓' if r[6] else '✗'} |")
    if not rows:
        lines.append("| — | — | — | — | no change | | |")
    lines += ["", "## Step-3 match counts per model × backend (n replicates): A → B", "",
              "| group | model | backend | n | matched A | matched B |", "|---|---|---|---|---|---|"]
    for key in sorted(agg):
        n, a, b = agg[key]
        lines.append(f"| {key[0]} | {key[1]} | {key[2]} | {n} | {a} | {b} |")
    # what B removes: responses that matched ONLY via the element mention
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("written:", args.out)


if __name__ == "__main__":
    main()
