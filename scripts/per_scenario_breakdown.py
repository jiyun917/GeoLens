"""Per-scenario breakdown of unified3 results.

Motivation: the professor's requirement (1) was to add a complex scenario
(attribute_computation, 8 steps, cross-workflow) and verify whether the
hybrid full_system advantage grows or shrinks with complexity. The
aggregate 25-cell table averages all three scenarios and cannot answer
this question directly. This script splits the table by scenario.

Two artifacts under data/eval/results/:
  - per_scenario_unified3.md — per-scenario means for all 25 cells
  - complexity_gap_unified3.md — narrow table on full - vanilla and
    full - no_rag deltas by scenario, per model, for step_accuracy,
    hallucination_rate, goal_completion_rate.

Statistical unit remains the replicate (n=5); scenario-level means are
computed per replicate before averaging.
"""

from __future__ import annotations

import os
import argparse
import glob
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "eval" / "results"

MODELS = [m.strip() for m in os.environ.get("BENCH_MODELS", "gemini,claude,gpt").split(",") if m.strip()]  # v3: Qwen excluded (VL serving unavailable); set BENCH_MODELS=gemini,claude,gpt,qwen for unified2/3/4 tags
BACKENDS = ["no_rag", "vanilla_vector", "vanilla_budget", "graph_only",
            "vision_only", "full_system", "state_path"]

SCENARIOS = [
    ("opendtect__survey_setup__01",        "survey_setup",     "Low",  4),
    ("opendtect__3d_visualization__01",    "3d_visualization", "Low",  4),
    ("opendtect__attribute_computation__01", "attribute_computation", "**High**", 8),
]


def load_per_scenario(tag: str) -> dict:
    """Returns {(model, backend, scen_id, metric): [per_replicate_value]}."""
    out: dict = defaultdict(list)
    for model in MODELS:
        pattern = str(ROOT / f"data/eval/results/run_{model}_{tag}_r*_*.json")
        for f in sorted(glob.glob(pattern)):
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            for scen in d.get("scenarios", []) or []:
                sid = scen.get("scenario_id")
                for bname, b in (scen.get("backends") or {}).items():
                    if not b or "error" in b or bname not in BACKENDS:
                        continue
                    for mkey in ("step_accuracy", "hallucination_rate",
                                 "goal_completion_rate", "mean_latency_sec"):
                        v = b.get(mkey)
                        if v is not None:
                            out[(model, bname, sid, mkey)].append(float(v))
    return out


def fmt_pct(vals: list[float]) -> str:
    if not vals:
        return "—"
    m = statistics.fmean(vals)
    sd = statistics.stdev(vals) if len(vals) >= 2 else 0.0
    return f"{m*100:.1f}±{sd*100:.1f}"


def render_full_breakdown(data: dict) -> str:
    lines = [
        "# Per-scenario breakdown — unified3",
        "",
        "Cells report mean ± sample SD over n=5 replicates. Each scenario "
        "value is the mean over that scenario's steps.",
        "",
    ]
    metrics = [
        ("step_accuracy",        "Step Acc"),
        ("hallucination_rate",   "Hall Rate"),
        ("goal_completion_rate", "Goal Comp"),
    ]
    for mkey, mlabel in metrics:
        lines.append(f"## {mlabel} (%) by scenario")
        lines.append("")
        header = ["Model / Backend"] + [f"{lbl} ({cx}, {n}st)"
                                         for _, lbl, cx, n in SCENARIOS]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join(["---"] * len(header)) + "|")
        for model in MODELS:
            for bname in BACKENDS:
                cells = [f"{model} / {bname}"]
                for sid, _, _, _ in SCENARIOS:
                    vals = data.get((model, bname, sid, mkey), [])
                    cells.append(fmt_pct(vals))
                lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_complexity_gap(data: dict) -> str:
    """Show full - vanilla and full - no_rag by scenario, per model, on Step Acc.

    Also compute the aggregate "complexity gap widening" quantity:
      Δ_complex - Δ_simple  (simple = mean of survey_setup and 3d_viz).
    """
    lines = [
        "# Complexity-vs-gap analysis — unified3",
        "",
        "Pre-registered prediction (see `v2_pre_registration.md § attribute "
        "prediction`): vanilla_vector should underperform on the complex "
        "attribute_computation scenario because retrieval will drift toward "
        "the theory pages (§1.5.1) instead of the procedure pages (§1.5.1a). "
        "full_system should recover via workflow routing. If the prediction "
        "is confirmed, the full − vanilla gap on step_accuracy should be "
        "**larger** on attribute_computation than on the two 4-step "
        "scenarios.",
        "",
        "This table restricts to the two contrasts most relevant to the "
        "prediction: **full − vanilla** and **full − no_rag**, on "
        "step_accuracy (higher = better). Numbers are percentage points; "
        "positive means full wins. `Δ complex − simple` is the widening: "
        "attribute − mean(survey_setup, 3d_viz).",
        "",
    ]

    def gap(model, contrast_A, contrast_B, sid, mkey):
        a = data.get((model, contrast_A, sid, mkey), [])
        b = data.get((model, contrast_B, sid, mkey), [])
        if not a or not b:
            return None
        return (statistics.fmean(a) - statistics.fmean(b)) * 100

    for contrast in ("vanilla_vector", "no_rag"):
        lines.append(f"## full_system − {contrast} on Step Acc (pp)")
        lines.append("")
        header = ["Model", "survey_setup", "3d_viz", "attribute (complex)",
                  "Δ complex − simple"]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join(["---"] * len(header)) + "|")
        for model in MODELS:
            g_ss = gap(model, "full_system", contrast,
                       "opendtect__survey_setup__01", "step_accuracy")
            g_3d = gap(model, "full_system", contrast,
                       "opendtect__3d_visualization__01", "step_accuracy")
            g_at = gap(model, "full_system", contrast,
                       "opendtect__attribute_computation__01", "step_accuracy")
            cells = [model]
            for g in (g_ss, g_3d, g_at):
                cells.append("—" if g is None else f"{g:+.1f}")
            if g_ss is not None and g_3d is not None and g_at is not None:
                widening = g_at - (g_ss + g_3d) / 2
                cells.append(f"{widening:+.1f}")
            else:
                cells.append("—")
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    # Same for hallucination_rate (lower better, so we invert sign)
    lines.append("## full_system − vanilla_vector on Hall Rate (pp, lower = better)")
    lines.append("")
    lines.append("Same as above but on hallucination rate. Because "
                 "lower is better, we report **vanilla − full** so positive "
                 "still means full wins.")
    lines.append("")
    header = ["Model", "survey_setup", "3d_viz", "attribute (complex)",
              "Δ complex − simple"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for model in MODELS:
        def hg(model, sid):
            a = data.get((model, "vanilla_vector", sid, "hallucination_rate"), [])
            b = data.get((model, "full_system", sid, "hallucination_rate"), [])
            if not a or not b:
                return None
            return (statistics.fmean(a) - statistics.fmean(b)) * 100
        g_ss = hg(model, "opendtect__survey_setup__01")
        g_3d = hg(model, "opendtect__3d_visualization__01")
        g_at = hg(model, "opendtect__attribute_computation__01")
        cells = [model]
        for g in (g_ss, g_3d, g_at):
            cells.append("—" if g is None else f"{g:+.1f}")
        if g_ss is not None and g_3d is not None and g_at is not None:
            widening = g_at - (g_ss + g_3d) / 2
            cells.append(f"{widening:+.1f}")
        else:
            cells.append("—")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("## Interpretation guide")
    lines.append("")
    lines.append("- **Δ complex − simple > 0** on the full − vanilla row = "
                 "hybrid advantage widens with complexity (**prediction "
                 "confirmed** for that model).")
    lines.append("- **Δ complex − simple ≈ 0** = flat effect (prediction "
                 "unconfirmed, hybrid gives constant lift).")
    lines.append("- **Δ complex − simple < 0** = hybrid narrows on complex "
                 "workloads (prediction **refuted**).")
    lines.append("")
    lines.append("The direction across the 4 models is the primary "
                 "quantity of interest — a single model can flip due to "
                 "small-n noise; a majority of models moving in the same "
                 "direction is the pre-registered confirmation criterion.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="unified3")
    args = ap.parse_args()
    data = load_per_scenario(args.tag)
    print(f"Loaded {len(data)} (model, backend, scen, metric) cells", file=sys.stderr)

    full = render_full_breakdown(data)
    (RESULTS / f"per_scenario_{args.tag}.md").write_text(full, encoding="utf-8")
    print(f"saved: per_scenario_{args.tag}.md", file=sys.stderr)

    gap = render_complexity_gap(data)
    (RESULTS / f"complexity_gap_{args.tag}.md").write_text(gap, encoding="utf-8")
    print(f"saved: complexity_gap_{args.tag}.md", file=sys.stderr)

    print(gap)


if __name__ == "__main__":
    main()
