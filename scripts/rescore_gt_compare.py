"""Re-score stored run JSONs with the OLD and NEW scenario GT and report the deltas
(v3 GT review, 2026-09-18). Scorer = v3 (GEOLENS_SCORER=v3), unchanged; only the GT
fields differ (visible_elements, data_state, current_action, QGIS step-3 pattern/keywords).

OLD GT = scenario files at --old-rev (git), NEW GT = working tree. Nothing is written
back into the run JSONs.

Usage: .venv/Scripts/python.exe scripts/rescore_gt_compare.py [--old-rev 44fa1ab~1] [--globs ...]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ["GEOLENS_SCORER"] = "v3"

SIDS = ["opendtect__survey_setup__01", "opendtect__3d_visualization__01", "opendtect__attribute_computation__01", "qgis__vector_buffer__01"]


def load_gt(rev: str | None):
    out = {}
    for sid in SIDS:
        if rev:
            txt = subprocess.run(["git", "show", f"{rev}:data/eval/scenarios/{sid}.json"], capture_output=True, text=True, encoding="utf-8").stdout
            out[sid] = json.loads(txt)
        else:
            out[sid] = json.load(open(f"data/eval/scenarios/{sid}.json", encoding="utf-8"))
    return out


def model_of(name: str) -> str:
    for m in ("gemini", "claude", "gpt", "qwen"):
        if m in name:
            return m
    return "?"


def group_of(name: str) -> str:
    for g in ("unified4", "dev_iter0", "dev_iter1", "dev_iter4", "latency_baseline", "qgis_pilot"):
        if g in name:
            return g
    return name.split("_")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-rev", default="44fa1ab~1")
    ap.add_argument("--globs", nargs="*", default=[
        "data/eval/results/run_*unified4*_r*.json",
        "data/eval/results/dev_iter0_v2mech_gemini_r*.json",
        "data/eval/results/dev_iter1_v3_gemini_r*.json",
        "data/eval/results/latency_baseline_survey_iter1_r*.json",
        "data/eval/results/dev_iter4_v3_*_r*.json",
        "../GeoLens-paper-wt-iter2/data/eval/results/dev_iter4_v3_*_r*.json",
    ])
    ap.add_argument("--out", default="data/eval/results/rescore_gt_compare_v3.md")
    args = ap.parse_args()
    from api.services.evaluation import step_match, hallucinated_elements

    old_gt, new_gt = load_gt(args.old_rev), load_gt(None)
    files = []
    for g in args.globs:
        files += sorted(glob.glob(g))
    agg = defaultdict(lambda: {"n": 0, "m_old": 0, "m_new": 0, "h_old": 0, "h_new": 0})
    flips = []
    for f in files:
        run = json.load(open(f, encoding="utf-8"))
        name = os.path.basename(f)
        grp, model = group_of(name), model_of(name)
        for sc in run.get("scenarios", []):
            sid = sc.get("scenario_id")
            if sid not in old_gt:
                continue
            goal_o, goal_n = old_gt[sid].get("goal", ""), new_gt[sid].get("goal", "")
            for b, m in (sc.get("backends") or {}).items():
                for ps in m.get("per_step", []):
                    si = ps.get("step_index")
                    resp = ps.get("response") or ""
                    so, sn = old_gt[sid]["steps"][si], new_gt[sid]["steps"][si]
                    mo, mn = bool(step_match(resp, so)), bool(step_match(resp, sn))
                    ho = bool(hallucinated_elements(resp, (so.get("visual_state_gt") or {}).get("visible_elements", []), step_gt=so, goal=goal_o))
                    hn = bool(hallucinated_elements(resp, (sn.get("visual_state_gt") or {}).get("visible_elements", []), step_gt=sn, goal=goal_n))
                    a = agg[(grp, model, b)]
                    a["n"] += 1; a["m_old"] += mo; a["m_new"] += mn; a["h_old"] += ho; a["h_new"] += hn
                    if mo != mn or ho != hn:
                        flips.append((grp, model, b, name, sid.replace("opendtect__", ""), si, mo, mn, ho, hn, resp[:90].replace("\n", " ")))
    lines = [f"# Re-score with old vs new GT (v3 scorer) — old = {args.old_rev}, new = working tree", "",
             f"Files: {len(files)}. Metrics per (group, model, backend): step matches and hallucination flags summed over scenarios × steps × replicates.", "",
             "| group | model | backend | n steps | step_acc old → new | Δpp | hall rate old → new | Δpp |", "|---|---|---|---|---|---|---|---|"]
    for key in sorted(agg):
        a = agg[key]
        n = a["n"] or 1
        lines.append(f"| {key[0]} | {key[1]} | {key[2]} | {a['n']} | {a['m_old']/n:.3f} → {a['m_new']/n:.3f} | {100*(a['m_new']-a['m_old'])/n:+.1f} | "
                     f"{a['h_old']/n:.3f} → {a['h_new']/n:.3f} | {100*(a['h_new']-a['h_old'])/n:+.1f} |")
    lines += ["", f"## Flipped step results ({len(flips)})", "", "| group | model | backend | file | scenario | step | match old→new | hall old→new | response |", "|---|---|---|---|---|---|---|---|---|"]
    for r in flips:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {'✓' if r[6] else '✗'}→{'✓' if r[7] else '✗'} | {'✓' if r[8] else '✗'}→{'✓' if r[9] else '✗'} | `{r[10]}` |")
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:80]))
    print("written:", args.out, "| flips:", len(flips))


if __name__ == "__main__":
    main()
