"""Direction consistency counter — sees ALL comparisons that matter for
paper A/B/C judgment, not just full_system vs vanilla_vector.

Adds two axes the pre-registration flagged:
  1. graph_only vs full_system on faithfulness — is graph_only unexpectedly
     the faithfulness winner? (Gemini v2 preview showed graph_only=2.5,
     full_system=5.0)
  2. graph_only vs vanilla_vector on faithfulness — does workflow-only
     retrieval beat pure vector retrieval? Ablation implication.

Direction consistency = fraction of models (out of 4) where a given
backend beats another on a given metric, in the correct direction. This
is the primary judgment quantity when n=5 makes p-values underpowered.

Usage:
    .venv/Scripts/python.exe scripts/direction_consistency.py --tag unified2
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


MODELS = ["gemini", "claude", "gpt", "qwen"]
BACKENDS = ["no_rag", "vanilla_vector", "graph_only",
            "vision_only", "full_system", "state_path"]
METRICS = [
    ("step_accuracy",        "higher"),
    ("faithfulness",         "higher"),
    ("hallucination_rate",   "lower"),
    ("goal_completion_rate", "higher"),
    ("mean_latency_sec",     "lower"),
    ("mean_cost_usd",        "lower"),
]

# The pairs we score for direction consistency. Each pair is (A, B): we
# count "yes" when A wins (in the metric's better direction) over B for
# a given model.
PAIRS = [
    ("full_system",  "vanilla_vector"),   # our main hypothesis
    ("full_system",  "no_rag"),           # RAG vs zero-shot
    ("vanilla_vector", "no_rag"),         # baseline RAG vs zero-shot
    ("graph_only",   "vanilla_vector"),   # workflow-only vs vector-only
    ("graph_only",   "full_system"),      # ablation: does full add over graph?
    ("state_path",   "full_system"),      # novel path vs standard hybrid
]


def load(tag: str) -> dict:
    """(model, backend, metric) -> [replicate_agg_across_scenarios, ...]"""
    out: dict = defaultdict(list)
    for f in sorted(glob.glob(str(ROOT / f"data/eval/results/run_*_{tag}_r*_*.json"))):
        m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", Path(f).name)
        if not m:
            continue
        model = m.group(1)
        if model not in MODELS:
            continue
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        # Aggregate metric per backend, averaging across scenarios in the replicate
        per_bkn: dict = defaultdict(lambda: defaultdict(list))
        for scen in d.get("scenarios", []) or []:
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b:
                    continue
                for mkey, _ in METRICS:
                    v = b.get(mkey)
                    if v is not None:
                        per_bkn[bname][mkey].append(float(v))
        for bname in BACKENDS:
            for mkey, _ in METRICS:
                vs = per_bkn[bname].get(mkey, [])
                if vs:
                    out[(model, bname, mkey)].append(sum(vs) / len(vs))
    return out


def report(data: dict) -> str:
    lines = []
    lines.append("# Direction consistency — v2 unified matrix\n")
    lines.append("For each metric and each candidate pair (A vs B), we count "
                 "how many of the 4 models have A winning over B in the metric's "
                 "correct direction. **4/4 = universal**, **3/4 = majority**, "
                 "**2/4 = mixed**, **≤1/4 = A loses**.\n")
    lines.append("Statistical unit = replicate. Each cell in the underlying "
                 "table is a per-model mean over 5 replicates; the winner per "
                 "model is decided by comparing those means (no per-model "
                 "significance requirement — that's the point of direction "
                 "consistency at small n).\n")

    for metric, direction in METRICS:
        lines.append(f"\n## {metric} ({'higher better' if direction=='higher' else 'lower better'})\n")
        lines.append("| pair | " + " | ".join(MODELS) + " | direction consistency |")
        lines.append("|---|" + "|".join(["---"] * len(MODELS)) + "|---|")
        for A, B in PAIRS:
            row = [f"{A} vs {B}"]
            wins = 0
            n_valid = 0
            for model in MODELS:
                a = data.get((model, A, metric), [])
                b = data.get((model, B, metric), [])
                if not a or not b:
                    row.append("—")
                    continue
                mA, mB = statistics.fmean(a), statistics.fmean(b)
                if direction == "higher":
                    A_wins = mA > mB
                    tie = mA == mB
                else:
                    A_wins = mA < mB
                    tie = mA == mB
                marker = "=" if tie else ("A" if A_wins else "B")
                # Format the actual numbers so it's auditable
                row.append(f"{marker} ({mA:.2f}/{mB:.2f})")
                if not tie:
                    n_valid += 1
                    if A_wins:
                        wins += 1
            summary = f"{wins}/{n_valid} models: A wins"
            if n_valid == len(MODELS):
                if wins == n_valid:
                    summary += " — **universal**"
                elif wins >= n_valid * 0.75:
                    summary += " — majority"
                elif wins <= n_valid * 0.25:
                    summary += " — A loses"
                else:
                    summary += " — mixed"
            row.append(summary)
            lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## Note on goal_completion_rate interpretation\n")
    lines.append("The 3d_visualization scenario captures the *penultimate* state "
                 "(In-line + Cross-line displayed, Z-slice not yet added). Its "
                 "final visual_state does NOT indicate goal-reached, so under "
                 "the 3-gate check, no backend can achieve goal_completion for "
                 "that scenario. Effectively goal_completion_rate is a "
                 "**single-scenario measurement** on survey_setup only — n=5 "
                 "per (model, backend) instead of n=10. This is a scenario "
                 "capture limitation, not a metric flaw. Any goal_completion "
                 "differences observed should be interpreted with this reduced "
                 "power in mind.\n")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="unified2")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    data = load(args.tag)
    if not data:
        print(f"no data for tag={args.tag}")
        return
    md = report(data)
    print(md)
    out = ROOT / "data" / "eval" / "results" / (args.out or f"direction_{args.tag}.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
