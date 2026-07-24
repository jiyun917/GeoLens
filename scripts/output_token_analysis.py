"""Output token distribution — validates the cost paradox mechanism.

Hypothesis (from v1): full_system is cheaper than vanilla_vector on API-
priced models because the workflow context makes the generator emit
tighter, shorter instructions. i.e., cost = tokens × price, and hybrid
saves on tokens even though it injects a larger prompt.

To validate: per-backend output token distribution. If hypothesis holds:
    output_tokens[full_system] < output_tokens[vanilla_vector]

Also reports input tokens so the full cost breakdown is auditable —
hybrid injects more context (larger input) but saves via smaller output.
Whether the net is positive depends on the model's in/out price ratio.

Usage:
    .venv/Scripts/python.exe scripts/output_token_analysis.py --tag unified2
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


def load(tag: str) -> dict:
    """(model, backend) -> {'in': [...], 'out': [...], 'cost': [...]} per step."""
    out: dict = defaultdict(lambda: {"in": [], "out": [], "cost": []})
    for f in sorted(glob.glob(str(ROOT / f"data/eval/results/run_*_{tag}_r*_*.json"))):
        m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", Path(f).name)
        if not m:
            continue
        model = m.group(1)
        if model not in MODELS:
            continue
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for scen in d.get("scenarios", []) or []:
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b or bname not in BACKENDS:
                    continue
                for ps in b.get("per_step") or []:
                    it = ps.get("input_tokens")
                    ot = ps.get("output_tokens")
                    ct = ps.get("cost_usd")
                    if it is not None:
                        out[(model, bname)]["in"].append(int(it))
                    if ot is not None:
                        out[(model, bname)]["out"].append(int(ot))
                    if ct is not None:
                        out[(model, bname)]["cost"].append(float(ct))
    return out


def _stats(vs: list) -> dict:
    if not vs:
        return {"n": 0}
    return {
        "n":     len(vs),
        "mean":  statistics.fmean(vs),
        "median": statistics.median(vs),
        "std":   statistics.stdev(vs) if len(vs) >= 2 else 0.0,
        "min":   min(vs),
        "max":   max(vs),
    }


def report(data: dict) -> str:
    lines = []
    lines.append("# Output token distribution — v2 unified matrix\n")
    lines.append("Per-step input/output token distribution and cost, aggregated "
                 "across all scenarios × replicates for each (model, backend).\n")
    lines.append("The cost paradox hypothesis: `output_tokens[full_system] < "
                 "output_tokens[vanilla_vector]` on generator-costly models. "
                 "If true, workflow context makes the generator emit tighter "
                 "responses, and the net effect (input growth vs output "
                 "shrinkage) is favorable for hybrid on models where "
                 "output tokens are priced high (Claude, GPT, Gemini).\n")

    for model in MODELS:
        lines.append(f"\n## {model}\n")
        lines.append("| backend | n | input mean | output mean | output median | cost mean ($) |")
        lines.append("|---|---|---|---|---|---|")
        for backend in BACKENDS:
            cell = data.get((model, backend), {"in": [], "out": [], "cost": []})
            si = _stats(cell["in"])
            so = _stats(cell["out"])
            sc = _stats(cell["cost"])
            if si.get("n", 0) == 0:
                continue
            lines.append(
                f"| {backend} | {si['n']} | "
                f"{si['mean']:.0f}±{si['std']:.0f} | "
                f"{so['mean']:.0f}±{so['std']:.0f} | "
                f"{so['median']:.0f} | "
                f"{sc['mean']*1000:.3f}m |"
            )

        # Cost paradox verdict for this model
        vc = data.get((model, "vanilla_vector"))
        fc = data.get((model, "full_system"))
        if vc and fc and vc["out"] and fc["out"]:
            v_out = statistics.fmean(vc["out"])
            f_out = statistics.fmean(fc["out"])
            v_in = statistics.fmean(vc["in"])
            f_in = statistics.fmean(fc["in"])
            v_cost = statistics.fmean(vc["cost"])
            f_cost = statistics.fmean(fc["cost"])
            out_ratio = f_out / v_out if v_out else float("nan")
            in_ratio = f_in / v_in if v_in else float("nan")
            cost_ratio = f_cost / v_cost if v_cost else float("nan")
            verdict = "✓ hybrid cheaper" if f_cost < v_cost else "✗ hybrid pricier"
            output_verdict = ("✓ hybrid emits shorter output"
                              if f_out < v_out else "✗ hybrid emits longer output")
            lines.append(
                f"\n**Cost paradox check ({model})**:  "
                f"full_system input × {in_ratio:.2f}, output × {out_ratio:.2f}, "
                f"cost × {cost_ratio:.2f}. {output_verdict}. {verdict}."
            )

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
    out = ROOT / "data" / "eval" / "results" / (args.out or f"output_tokens_{args.tag}.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
