"""Build the FINAL 4-model × 3-backend × 6-metric table with mean±std
across the 5 replicates of the unified matrix.

Each replicate contributes one aggregate per backend (mean across the two
scenarios), so n=5 per (model, backend) cell. Statistical unit = replicate.

Outputs a markdown table to stdout and to
data/eval/results/final_unified_table.md.
"""

from __future__ import annotations

import glob
import json
import sys
import statistics
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent

MODELS = ["gemini", "claude", "gpt", "qwen"]
DEFAULT_BACKENDS = ["no_rag", "vanilla_vector", "graph_only",
                    "vision_only", "full_system", "state_path"]
METRICS = [
    ("step_accuracy",        "Step Acc",   "%", "higher"),
    ("hallucination_rate",   "Hall Rate",  "%", "lower"),
    ("loop_rate",            "Loop Rate",  "%", "lower"),
    ("goal_completion_rate", "Goal Comp",  "%", "higher"),
    ("mean_latency_sec",     "Latency",    "s", "lower"),
    ("mean_cost_usd",        "Cost/step",  "$", "lower"),
]


def collect(tag: str = "unified", backends: list | None = None) -> dict:
    """Returns {(model, backend, metric_key) : [per_replicate_agg_value, ...]}."""
    _backends = backends or DEFAULT_BACKENDS
    out: dict = defaultdict(list)
    for model in MODELS:
        pattern = f"data/eval/results/run_{model}_{tag}_r*_*.json"
        files = sorted(glob.glob(str(ROOT / pattern)))
        if not files:
            print(f"[warn] no files for model {model} tag={tag}", file=sys.stderr)
            continue
        for f in files:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            # Prefer aggregate section if present (rescore_results updates it);
            # else fall back to computing across scenarios.
            scenarios = d.get("scenarios", []) or []
            for backend in _backends:
                metrics_for_scenarios = []
                for scen in scenarios:
                    b = (scen.get("backends") or {}).get(backend)
                    if not b or "error" in b:
                        continue
                    metrics_for_scenarios.append(b)
                if not metrics_for_scenarios:
                    continue
                # Per-replicate mean across scenarios for each metric.
                # For Qwen, prefer the effective (cloud-equivalent) cost that
                # scripts/qwen_cost_convert.py stamped onto the JSON — that
                # avoids the misleading $0.0000 self-hosted marginal cost.
                for mkey, _, _, _ in METRICS:
                    if mkey == "mean_cost_usd" and model == "qwen":
                        vals = [m.get("mean_cost_usd_effective") for m in metrics_for_scenarios]
                        vals = [v for v in vals if v is not None]
                    else:
                        vals = [m[mkey] for m in metrics_for_scenarios
                                if m.get(mkey) is not None]
                    if not vals:
                        continue
                    out[(model, backend, mkey)].append(sum(vals) / len(vals))
    return out


def fmt(vals: list, unit: str) -> str:
    if not vals:
        return "—"
    mean = statistics.mean(vals)
    sd = statistics.stdev(vals) if len(vals) >= 2 else 0.0
    if unit == "%":
        return f"{mean*100:.1f}±{sd*100:.1f}"
    if unit == "s":
        return f"{mean:.1f}±{sd:.1f}"
    if unit == "$":
        return f"${mean*1000:.2f}±{sd*1000:.2f}m"  # milli-USD per step
    return f"{mean:.3f}±{sd:.3f}"


def render(data: dict, backends: list) -> str:
    lines = []
    lines.append(f"# Final 4-Model × {len(backends)}-Backend Matrix (n=5 replicates each)")
    lines.append("")
    lines.append("Statistical unit = replicate. Each cell reports mean ± std "
                 "across 5 replicates, where each replicate averages the 2 "
                 "scenarios (survey_setup + 3d_visualization).")
    lines.append("")
    lines.append("Goal completion uses the 3-gate check: sentinel + grounded "
                 "+ visual_state confirms goal-reached.")
    lines.append("")
    lines.append("**Goal Comp footnote**: 3d_visualization captures the "
                 "penultimate state (In-line + Cross-line displayed, Z-slice "
                 "not yet added). Its final visual_state does NOT indicate "
                 "goal-reached, so no backend can achieve goal_completion on "
                 "that scenario under the 3-gate check. Consequently the Goal "
                 "Comp column is effectively a single-scenario measurement "
                 "on survey_setup only — n=5 per (model, backend), not n=10. "
                 "This is a scenario-capture limitation, not a metric flaw. "
                 "Interpret Goal Comp differences with this reduced power in "
                 "mind.")
    lines.append("")

    for model in MODELS:
        lines.append(f"## {model}")
        lines.append("")
        head = ["metric"] + backends
        lines.append("| " + " | ".join(head) + " |")
        lines.append("|" + "|".join(["---"] * len(head)) + "|")
        for mkey, label, unit, direction in METRICS:
            row = [f"{label} ({unit}) {'↑' if direction=='higher' else '↓'}"]
            for backend in backends:
                row.append(fmt(data.get((model, backend, mkey), []), unit))
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="unified",
                    help="Filename tag between model and r<N> (default: unified)")
    ap.add_argument("--backends", nargs="*", default=None,
                    help="Subset of backends (default: all 6)")
    ap.add_argument("--out", default=None,
                    help="Output markdown filename inside data/eval/results/")
    args = ap.parse_args()
    backends = args.backends or DEFAULT_BACKENDS
    data = collect(tag=args.tag, backends=backends)
    if not data:
        print(f"no data for tag={args.tag}")
        return
    text = render(data, backends)
    print(text)
    out_name = args.out or f"final_{args.tag}_table.md"
    out = ROOT / "data" / "eval" / "results" / out_name
    out.write_text(text, encoding="utf-8")
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
