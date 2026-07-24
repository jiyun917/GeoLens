"""Claude asymmetry re-check — v1 vs v2 hallucination Δ per model.

Question: v1 observation was that Claude (uniquely) showed hybrid full_system
raising hallucination by +12.5 pp vs vanilla_vector, while gemini/gpt/qwen
showed hybrid REDUCING hallucination. If this v1 pattern was a byproduct
of the broken workflow coverage (routing to irrelevant nodes), v2 should
show the asymmetry gone — Claude joins the other 3 models with hybrid
helping (or at least not hurting).

If v2 still shows Claude-only hybrid worsening hallucination, then this
IS a robust model-family difference (probably about how Claude handles
irrelevant workflow context) and belongs in discussion.

Computes for each model: full_system hall_rate − vanilla_vector hall_rate
(negative = hybrid helps, positive = hybrid hurts). Then flags Claude as
outlier if its Δ is meaningfully positive while other 3 are ≤ 0.

Usage:
    .venv/Scripts/python.exe scripts/claude_asymmetry_check.py --tag unified2
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


def load_hall_rates(tag: str) -> dict:
    """(model, backend) -> [per_replicate_agg_hall_rate, ...]"""
    out: dict = defaultdict(list)
    for f in sorted(glob.glob(str(ROOT / f"data/eval/results/run_*_{tag}_r*_*.json"))):
        m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", Path(f).name)
        if not m:
            continue
        model = m.group(1)
        if model not in MODELS:
            continue
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        # replicate aggregate = mean across scenarios
        per_bkn: dict = defaultdict(list)
        for scen in d.get("scenarios", []) or []:
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b:
                    continue
                h = b.get("hallucination_rate")
                if h is not None:
                    per_bkn[bname].append(float(h))
        for bname, vs in per_bkn.items():
            if vs:
                out[(model, bname)].append(sum(vs) / len(vs))
    return out


def report(v1_data: dict, v2_data: dict) -> str:
    def _delta(data: dict, model: str) -> tuple[float, float, float]:
        full = data.get((model, "full_system"), [])
        van  = data.get((model, "vanilla_vector"), [])
        if not full or not van:
            return (float("nan"), float("nan"), float("nan"))
        mf = statistics.fmean(full)
        mv = statistics.fmean(van)
        return (mf, mv, mf - mv)

    lines = []
    lines.append("# Claude hallucination asymmetry — v1 vs v2 re-check\n")
    lines.append("Δ = hall_rate[full_system] − hall_rate[vanilla_vector] "
                 "(negative → hybrid helps, positive → hybrid hurts).\n")
    lines.append("| model | v1 full | v1 vanilla | v1 Δ | v2 full | v2 vanilla | v2 Δ | Δ shift |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for model in MODELS:
        v1_f, v1_v, v1_d = _delta(v1_data, model)
        v2_f, v2_v, v2_d = _delta(v2_data, model)
        shift = v2_d - v1_d if not (v1_d != v1_d or v2_d != v2_d) else float("nan")

        def _fmt(x): return "—" if x != x else f"{x*100:+.1f}pp"  # NaN check
        def _fmt2(x): return "—" if x != x else f"{x:.3f}"
        lines.append(
            f"| {model} | "
            f"{_fmt2(v1_f)} | {_fmt2(v1_v)} | {_fmt(v1_d)} | "
            f"{_fmt2(v2_f)} | {_fmt2(v2_v)} | {_fmt(v2_d)} | "
            f"{_fmt(shift)} |"
        )

    lines.append("\n## Verdict\n")
    v2_deltas = {m: _delta(v2_data, m)[2] for m in MODELS}
    valid = {m: d for m, d in v2_deltas.items() if not (d != d)}
    if len(valid) == len(MODELS):
        claude_pos = v2_deltas["claude"] > 0
        others_nonpos = all(v2_deltas[m] <= 0 for m in MODELS if m != "claude")
        if claude_pos and others_nonpos:
            lines.append(
                "**v2 CONFIRMS asymmetry**: Claude is the only model where "
                "hybrid raises hallucination while all 3 others show hybrid "
                "helping or neutral. This is now a robust model-family "
                "observation. Reserve a discussion paragraph on "
                "'model-specific sensitivity to hybrid workflow context'."
            )
        elif claude_pos and not others_nonpos:
            lines.append(
                "**v2 partial confirmation**: Claude still shows hybrid > "
                "vanilla in hall_rate, but the asymmetry is less clean — "
                "other models also mixed. Flag as 'observed in both v1 and "
                "v2' without pushing the isolated-Claude claim."
            )
        elif not claude_pos:
            lines.append(
                "**v2 REJECTS asymmetry**: Claude no longer shows hybrid > "
                "vanilla in hall_rate. The v1 observation was likely a "
                "byproduct of workflow coverage gap. Drop from discussion, "
                "cite in methodology audit as a fixed-in-v2 artifact."
            )
    else:
        lines.append("Insufficient data — some model's v2 data missing.")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1-tag", default="unified")
    ap.add_argument("--v2-tag", default="unified2")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    v1 = load_hall_rates(args.v1_tag)
    v2 = load_hall_rates(args.v2_tag)
    md = report(v1, v2)
    print(md)
    out = ROOT / "data" / "eval" / "results" / (args.out or f"claude_asymmetry_{args.v2_tag}.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
