"""Aggregate replicate bench runs into paper-ready mean ± std tables.

Discovers all data/eval/results/run_<model>_r<rep>_*.json files, groups by
(model, backend), and computes mean ± std for every metric across replicates.

Writes:
  data/eval/results/aggregate_by_backend.md
  data/eval/results/aggregate_by_backend.csv
  data/eval/results/aggregate_by_model.md

Usage:
    .venv/Scripts/python.exe scripts/aggregate_results.py
"""

from __future__ import annotations

import csv
import glob
import json
import math
import os
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "data" / "eval" / "results"


# Metrics the paper reports. faithfulness = 1 − hallucination_rate; loop_rate
# is preferred over dwell_loop_rate for readability.
PAPER_QUALITY = ["step_accuracy", "faithfulness", "goal_completion_rate", "loop_rate"]
PAPER_EFFICIENCY = ["mean_latency_sec", "mean_cost_usd"]
PAPER_METRICS = PAPER_QUALITY + PAPER_EFFICIENCY


RE_FILENAME = re.compile(r"^run_(?P<model>[a-z]+)_r(?P<rep>\d+)_\d+T\d+\.json$")


def discover_runs() -> Dict[str, List[Path]]:
    """model -> list of replicate JSON paths"""
    by_model: Dict[str, List[Path]] = defaultdict(list)
    for p in sorted(RESULTS_DIR.glob("run_*_r*_*.json")):
        m = RE_FILENAME.match(p.name)
        if m:
            by_model[m.group("model")].append(p)
    return by_model


def _mean_std(values: List[float]) -> Tuple[float, float]:
    vals = [v for v in values if v is not None]
    if not vals:
        return (float("nan"), float("nan"))
    if len(vals) == 1:
        return (vals[0], 0.0)
    return (statistics.fmean(vals), statistics.stdev(vals))


def _active_scenario_ids() -> set:
    """Read data/eval/scenarios/opendtect__*.json to know which scenarios
    are currently active. Any per-scenario data from OTHER scenario_ids
    in existing run files is filtered out — so re-organising the
    scenario set doesn't require a bench rerun."""
    from pathlib import Path as _P
    scen_dir = _P(__file__).resolve().parent.parent / "data" / "eval" / "scenarios"
    out = set()
    for p in scen_dir.glob("opendtect__*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            sid = d.get("scenario_id")
            if sid:
                out.add(sid)
        except Exception:
            continue
    return out


def collect_by_backend(runs: Dict[str, List[Path]]) -> Dict[Tuple[str, str, str], List[Dict]]:
    """(model, backend, metric) -> list of replicate values.
    Recomputes per-run aggregate from the `scenarios[]` list, filtering to
    only the currently-active scenario IDs. This lets us drop a scenario
    from the analysis without rerunning the bench."""
    active = _active_scenario_ids()
    print(f"Active scenario filter: {sorted(active)}")
    bucket: Dict[Tuple[str, str, str], List[float]] = defaultdict(list)
    for model, paths in runs.items():
        for p in paths:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[SKIP] {p.name}: {e}")
                continue
            # Recompute per-backend mean-over-scenarios using ONLY active
            # scenario_ids from this run.
            per_backend: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
            for scen in data.get("scenarios") or []:
                sid = scen.get("scenario_id")
                if active and sid not in active:
                    continue
                for bname, bmetrics in (scen.get("backends") or {}).items():
                    if not bmetrics or "error" in bmetrics:
                        continue
                    for metric in PAPER_METRICS:
                        v = bmetrics.get(metric)
                        if v is not None:
                            per_backend[bname][metric].append(float(v))
            for bname, metric_lists in per_backend.items():
                for metric, vs in metric_lists.items():
                    if vs:
                        bucket[(model, bname, metric)].append(statistics.fmean(vs))
    return bucket


def render_backend_table(bucket) -> str:
    """Table: rows = (model × backend), cols = paper metrics with mean ± std."""
    header = ["model", "backend"] + PAPER_METRICS
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]

    keys = sorted({(m, b) for (m, b, _) in bucket.keys()})
    for model, backend in keys:
        row = [model, backend]
        for metric in PAPER_METRICS:
            vals = bucket.get((model, backend, metric), [])
            mean, std = _mean_std(vals)
            if math.isnan(mean):
                row.append("—")
            else:
                if metric in ("mean_cost_usd",):
                    row.append(f"${mean:.5f} ± {std:.5f}")
                elif metric in ("mean_latency_sec",):
                    row.append(f"{mean:.2f}s ± {std:.2f}")
                else:
                    row.append(f"{mean:.3f} ± {std:.3f}")
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines) + "\n"


def render_model_table(bucket) -> str:
    """Model-level table (average across backends × replicates)."""
    header = ["model"] + PAPER_METRICS
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]

    models = sorted({m for (m, _, _) in bucket.keys()})
    for model in models:
        row = [model]
        for metric in PAPER_METRICS:
            vals: List[float] = []
            for (m, _b, _metric), lst in bucket.items():
                if m == model and _metric == metric:
                    vals.extend(lst)
            mean, std = _mean_std(vals)
            if math.isnan(mean):
                row.append("—")
            else:
                if metric in ("mean_cost_usd",):
                    row.append(f"${mean:.5f} ± {std:.5f}")
                elif metric in ("mean_latency_sec",):
                    row.append(f"{mean:.2f}s ± {std:.2f}")
                else:
                    row.append(f"{mean:.3f} ± {std:.3f}")
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines) + "\n"


def write_csv(bucket, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "backend", "metric", "n_replicates", "mean", "std", "values"])
        for (model, backend, metric), vals in sorted(bucket.items()):
            mean, std = _mean_std(vals)
            w.writerow([
                model, backend, metric, len(vals),
                f"{mean:.6f}" if not math.isnan(mean) else "",
                f"{std:.6f}" if not math.isnan(std) else "",
                ";".join(f"{v:.6f}" for v in vals),
            ])


def main():
    runs = discover_runs()
    if not runs:
        print("No replicate runs found. Expected data/eval/results/run_<model>_r<rep>_*.json")
        sys.exit(1)

    print("Runs discovered per model:")
    for m, paths in runs.items():
        print(f"  {m:<8} {len(paths)} replicate(s)")

    bucket = collect_by_backend(runs)

    backend_md = render_backend_table(bucket)
    model_md = render_model_table(bucket)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "aggregate_by_backend.md").write_text(
        "# Aggregate — model × backend\n\n" + backend_md, encoding="utf-8"
    )
    (RESULTS_DIR / "aggregate_by_model.md").write_text(
        "# Aggregate — model level\n\n" + model_md, encoding="utf-8"
    )
    write_csv(bucket, RESULTS_DIR / "aggregate_by_backend.csv")

    print("\n=== BACKEND-LEVEL TABLE ===")
    print(backend_md)
    print("\n=== MODEL-LEVEL TABLE ===")
    print(model_md)

    print(f"\nWrote:")
    print(f"  {RESULTS_DIR / 'aggregate_by_backend.md'}")
    print(f"  {RESULTS_DIR / 'aggregate_by_backend.csv'}")
    print(f"  {RESULTS_DIR / 'aggregate_by_model.md'}")


if __name__ == "__main__":
    main()
