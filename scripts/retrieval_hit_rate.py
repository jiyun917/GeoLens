"""Compute retrieval hit rate on the v2 unified matrix.

For each step of each scenario, we know which workflow node SHOULD have been
routed to (encoded in this script's SCENARIO_STEP_EXPECTED map — the same
ground-truth mapping used by scripts/routing_dryrun.py).

Retrieval hit rate = fraction of steps where the picked node matches the
expected workflow AND (optionally) the expected step number within a
tolerance.

Metrics per (model, backend, scenario):
    workflow_hit_rate  — picked_workflow_id == expected
    step_hit_rate      — picked step_number == expected (±1 tolerance)
    fallback_rate      — how often did the confidence gate fire

This exists so that v2's Table 2 (ablation) has a "why does each backend
score what it scores" story: full_system routes correctly N% of the time
and falls back M% of the time; graph_only routes correctly N'% but has no
fallback, etc.

Usage:
    .venv/Scripts/python.exe scripts/retrieval_hit_rate.py --tag unified2
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# Expected workflow_id and step_number per (scenario, step_index).
# Step_number is best-guess mapping to the workflow node we authored.
SCENARIO_STEP_EXPECTED = {
    "opendtect__survey_setup__01": {
        0: ("survey_setup", 1),   # open Survey Setup and Selection
        1: ("survey_setup", 2),   # Create New Survey dialog
        2: ("survey_setup", 3),   # choose initial setup
        3: ("survey_setup", 5),   # Main Window loaded
    },
    "opendtect__3d_visualization__01": {
        0: ("d3_visualization", 1),  # main_window_ready
        1: ("d3_visualization", 2),  # add_inline
        2: ("d3_visualization", 3),  # add_crossline
        3: ("d3_visualization", 4),  # add_zslice
    },
}

STEP_TOLERANCE = 1  # ±1 step counts as a hit


def collect(tag: str) -> dict:
    """Load per-step routing telemetry from all v2 files with the given tag."""
    files = sorted(glob.glob(str(ROOT / f"data/eval/results/run_*_{tag}_r*_*.json")))
    rows = []
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", Path(f).name)
        if not m:
            continue
        model, rep = m.group(1), int(m.group(2))
        for scen in d.get("scenarios", []) or []:
            sid = scen.get("scenario_id")
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b:
                    continue
                per_step = b.get("per_step") or []
                for ps in per_step:
                    if not ps.get("route_method"):
                        continue  # non-routed backend, skip
                    idx = ps.get("step_index")
                    exp = SCENARIO_STEP_EXPECTED.get(sid, {}).get(idx)
                    if not exp:
                        continue
                    exp_wf, exp_step = exp
                    picked_wf = ps.get("picked_workflow_id")
                    picked_node = ps.get("picked_node_id") or ""
                    # Extract step number from node id if formatted as workflow_NN_...
                    picked_step = None
                    mm = re.match(r"[a-z_]+_(\d+)_[a-z_]+", picked_node)
                    if mm:
                        picked_step = int(mm.group(1))
                    wf_hit = (picked_wf == exp_wf)
                    step_hit = (
                        picked_step is not None
                        and abs(picked_step - exp_step) <= STEP_TOLERANCE
                        and wf_hit
                    )
                    rows.append({
                        "model": model,
                        "rep": rep,
                        "scenario": sid,
                        "backend": bname,
                        "step_index": idx,
                        "expected_wf": exp_wf,
                        "expected_step": exp_step,
                        "picked_wf": picked_wf,
                        "picked_step": picked_step,
                        "confidence": ps.get("route_confidence", 0.0),
                        "fallback": bool(ps.get("fallback_activated")),
                        "wf_hit": wf_hit,
                        "step_hit": step_hit,
                    })
    return rows


def report(rows: list) -> str:
    by_mb: dict = defaultdict(lambda: {"wf_hit": 0, "step_hit": 0,
                                         "fallback": 0, "n": 0,
                                         "conf_sum": 0.0})
    for r in rows:
        k = (r["model"], r["backend"])
        by_mb[k]["n"] += 1
        by_mb[k]["wf_hit"] += int(r["wf_hit"])
        by_mb[k]["step_hit"] += int(r["step_hit"])
        by_mb[k]["fallback"] += int(r["fallback"])
        by_mb[k]["conf_sum"] += float(r["confidence"] or 0)

    lines = []
    lines.append("# Retrieval hit rate — v2 unified matrix\n")
    lines.append("Only backends that route through guide_pipeline "
                 "(full_system, state_path) produce non-trivial numbers here. "
                 "Others show '—'.\n")
    lines.append("Step hit: picked workflow AND picked step within ±1 of expected.\n")
    lines.append("| model | backend | n steps | workflow hit | step hit | fallback rate | mean conf |")
    lines.append("|---|---|---|---|---|---|---|")
    for (mdl, bkn), agg in sorted(by_mb.items()):
        n = agg["n"]
        if n == 0:
            continue
        lines.append(
            f"| {mdl} | {bkn} | {n} | "
            f"{100*agg['wf_hit']/n:.0f}% | "
            f"{100*agg['step_hit']/n:.0f}% | "
            f"{100*agg['fallback']/n:.0f}% | "
            f"{agg['conf_sum']/n:.2f} |"
        )
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="unified2")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    rows = collect(args.tag)
    if not rows:
        print(f"no routed steps found for tag={args.tag}")
        return
    md = report(rows)
    print(md)
    out = ROOT / "data" / "eval" / "results" / (args.out or f"retrieval_hits_{args.tag}.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
