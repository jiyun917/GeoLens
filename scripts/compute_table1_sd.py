"""Compute 5-replicate mean ± sample SD for all 25 model×backend cells of
the v2 unified2 matrix (24 core cells + Gemini long_context).

Produces two artifacts in data/eval/results/:
  - table1_full_sd.md — 25 rows × 5 core metrics (Step Acc, Hall Rate,
    Loop Rate, Latency, Cost). Paper Table 1 in compact form.
  - Goal Comp appendix table appended to the same file.

Also cross-checks the recomputed cells against the existing
final_unified2_table.md and prints any mismatches to stderr.

Statistical unit = replicate (n=5). Each replicate's value is the mean
across the 2 scenarios (survey_setup + 3d_visualization). SD is sample
SD (n-1 denominator) — matches final_unified2_table.md convention.

For Qwen cost, uses mean_cost_usd_effective (cloud-equivalent, time-based)
per scripts/qwen_cost_convert.py — self-hosted marginal is $0.
"""

from __future__ import annotations

import glob
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent

MODELS = ["gemini", "claude", "gpt", "qwen"]
CORE_BACKENDS = ["no_rag", "vanilla_vector", "graph_only",
                 "vision_only", "full_system", "state_path"]

# Display labels for the 25 cells (model, backend) — long_context only for gemini.
CELLS = [(m, b) for m in MODELS for b in CORE_BACKENDS] + [("gemini", "long_context")]

CORE_METRICS = [
    ("step_accuracy",      "Step Acc",  "%"),
    ("hallucination_rate", "Hall Rate", "%"),
    ("loop_rate",          "Loop Rate", "%"),
    ("mean_latency_sec",   "Latency",   "s"),
    ("mean_cost_usd",      "Cost/step", "$"),
]
GOAL_METRIC = ("goal_completion_rate", "Goal Comp", "%")


def per_replicate_values(model: str, backend: str, mkey: str) -> list[float]:
    """Collect one value per replicate for (model, backend, metric).

    Value = mean across scenarios in that replicate.
    """
    if backend == "long_context":
        pattern = f"data/eval/results/run_{model}_longctx_r*_*.json"
    else:
        pattern = f"data/eval/results/run_{model}_unified2_r*_*.json"
    files = sorted(glob.glob(str(ROOT / pattern)))
    out: list[float] = []
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        scenarios = d.get("scenarios", []) or []
        per_scen: list[float] = []
        for scen in scenarios:
            b = (scen.get("backends") or {}).get(backend)
            if not b or "error" in b:
                continue
            # Qwen cost: use effective (cloud-equivalent) value, else raw.
            if mkey == "mean_cost_usd" and model == "qwen":
                v = b.get("mean_cost_usd_effective")
            else:
                v = b.get(mkey)
            if v is None:
                continue
            per_scen.append(v)
        if per_scen:
            out.append(sum(per_scen) / len(per_scen))
    return out


def fmt(vals: list[float], unit: str) -> str:
    if not vals:
        return "n/a"
    mean = statistics.mean(vals)
    sd = statistics.stdev(vals) if len(vals) >= 2 else 0.0
    if unit == "%":
        return f"{mean*100:.1f}±{sd*100:.1f}"
    if unit == "s":
        return f"{mean:.1f}±{sd:.1f}"
    if unit == "$":
        return f"${mean*1000:.2f}±{sd*1000:.2f}m"
    return f"{mean:.3f}±{sd:.3f}"


def build_row(model: str, backend: str, metrics: list) -> tuple[str, list[str]]:
    label = f"{model} / {backend}"
    cells = []
    for mkey, _, unit in metrics:
        vals = per_replicate_values(model, backend, mkey)
        cells.append(fmt(vals, unit))
    return label, cells


def render_table(title: str, metrics: list, note: str = "") -> str:
    lines = [f"## {title}", ""]
    if note:
        lines.append(note)
        lines.append("")
    header = ["Cell (Model / Backend)"] + [f"{lbl} ({u}) {'↑' if mkey in ('step_accuracy','goal_completion_rate') else '↓'}"
                                            for mkey, lbl, u in metrics]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for model, backend in CELLS:
        label, cells = build_row(model, backend, metrics)
        lines.append("| " + " | ".join([label] + cells) + " |")
    lines.append("")
    return "\n".join(lines)


# ---- Cross-check against existing final_unified2_table.md ---------------

CELL_RE = re.compile(r"^\| ([\w\s/()%$↑↓]+) \| (.+) \|$")


def parse_final_table(path: Path) -> dict:
    """Returns {(model, backend, mkey) : "mean±sd" string} from existing doc."""
    text = path.read_text(encoding="utf-8")
    out: dict = {}
    current_model = None
    header_backends: list[str] = []
    metric_label_to_key = {
        "Step Acc":  "step_accuracy",
        "Hall Rate": "hallucination_rate",
        "Loop Rate": "loop_rate",
        "Goal Comp": "goal_completion_rate",
        "Latency":   "mean_latency_sec",
        "Cost/step": "mean_cost_usd",
    }
    for line in text.splitlines():
        m = re.match(r"^## (\w+)$", line.strip())
        if m:
            current_model = m.group(1).lower()
            header_backends = []
            continue
        if current_model and line.startswith("| metric |"):
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            header_backends = parts[1:]
            continue
        if current_model and header_backends and line.startswith("|") and "±" in line:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            metric_cell = parts[0]
            # e.g. "Step Acc (%) ↑" -> "Step Acc"
            base = metric_cell.split("(")[0].strip()
            mkey = metric_label_to_key.get(base)
            if not mkey:
                continue
            for i, backend in enumerate(header_backends):
                if i + 1 < len(parts):
                    out[(current_model, backend, mkey)] = parts[i + 1]
    return out


def norm_num(s: str) -> tuple[float, float] | None:
    """Parse '57.5±11.2' or '$0.70±0.01m' -> (mean, sd) as floats.

    Cost strings are in milli-USD; we compare numerically.
    """
    s = s.strip().lstrip("$").rstrip("m")
    m = re.match(r"^(-?\d+\.?\d*)±(-?\d+\.?\d*)$", s)
    if not m:
        return None
    return float(m.group(1)), float(m.group(2))


def crosscheck(existing_path: Path) -> list[str]:
    """Recompute all cells for the same 6 metrics and diff against existing
    final_unified2_table.md. Returns list of mismatch descriptions.

    Tolerance: 0.05 absolute on printed value (accounts for rounding).
    """
    existing = parse_final_table(existing_path)
    diffs: list[str] = []
    metrics_map = {
        "step_accuracy":        ("%", 1.0),   # 0.05 pp in printed units
        "hallucination_rate":   ("%", 1.0),
        "loop_rate":            ("%", 1.0),
        "goal_completion_rate": ("%", 1.0),
        "mean_latency_sec":     ("s", 1.0),
        "mean_cost_usd":        ("$", 1000.0),
    }
    tolerance = 0.15
    for model in MODELS:
        for backend in CORE_BACKENDS:
            for mkey, (unit, scale) in metrics_map.items():
                vals = per_replicate_values(model, backend, mkey)
                if not vals:
                    continue
                rec_mean = statistics.mean(vals) * (100 if unit == "%" else scale)
                rec_sd = (statistics.stdev(vals) if len(vals) >= 2 else 0.0) * (100 if unit == "%" else scale)
                exp = existing.get((model, backend, mkey))
                if exp is None:
                    diffs.append(f"MISSING existing entry: {model}/{backend} {mkey}")
                    continue
                parsed = norm_num(exp)
                if parsed is None:
                    diffs.append(f"UNPARSEABLE existing entry: {model}/{backend} {mkey} = '{exp}'")
                    continue
                exp_mean, exp_sd = parsed
                if abs(rec_mean - exp_mean) > tolerance or abs(rec_sd - exp_sd) > tolerance:
                    diffs.append(
                        f"MISMATCH {model}/{backend} {mkey}: "
                        f"existing {exp_mean:.2f}±{exp_sd:.2f}  "
                        f"recomputed {rec_mean:.2f}±{rec_sd:.2f}"
                    )
    return diffs


def main():
    # 1. Cross-check against existing table
    existing_path = ROOT / "data" / "eval" / "results" / "final_unified2_table.md"
    if existing_path.exists():
        print("=== Cross-check vs final_unified2_table.md ===", file=sys.stderr)
        diffs = crosscheck(existing_path)
        if not diffs:
            print("  no mismatches (tolerance 0.15 on printed units).", file=sys.stderr)
        else:
            print(f"  {len(diffs)} mismatch(es):", file=sys.stderr)
            for d in diffs:
                print("   -", d, file=sys.stderr)
        print("", file=sys.stderr)
    else:
        print(f"[warn] {existing_path} not found — skipping cross-check", file=sys.stderr)

    # 2. Build the two tables
    header = (
        "# Paper Table 1 — full mean ± sample SD for all 25 cells\n\n"
        "Statistical unit = replicate (n=5 per cell). Each replicate value "
        "is the mean across the 2 scenarios (survey_setup + 3d_visualization). "
        "SD is sample SD (n-1 denominator).\n\n"
        "Cells: 4 models × 6 backends + Gemini × long_context = 25.\n"
        "long_context runs Gemini only because the manual (~226K tokens) "
        "exceeds the 128K–200K context windows of the other three models.\n\n"
        "Qwen cost uses the cloud-equivalent (time-based) `mean_cost_usd_effective` "
        "value; the self-hosted marginal cost is $0 and would be misleading.\n\n"
    )

    core_note = (
        "5 core metrics reported here. Goal Completion is reported "
        "separately below (Appendix A) because its effective n differs — "
        "see the footnote on that table."
    )
    core_table = render_table(
        "Table 1 (compact) — core metrics",
        CORE_METRICS,
        core_note,
    )

    goal_note = (
        "**Effective n footnote**: 3d_visualization captures the "
        "penultimate state, so no backend can pass the 3-gate check on that "
        "scenario. Goal Completion in each replicate is therefore effectively "
        "a survey_setup-only measurement (n=5 per cell, not n=10). Interpret "
        "differences with reduced power in mind."
    )
    goal_table = render_table(
        "Appendix A — Goal Completion",
        [GOAL_METRIC],
        goal_note,
    )

    out_text = header + core_table + "\n" + goal_table
    out_path = ROOT / "data" / "eval" / "results" / "table1_full_sd.md"
    out_path.write_text(out_text, encoding="utf-8")
    print(out_text)
    print(f"\nsaved: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
