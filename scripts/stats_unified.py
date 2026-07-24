"""Pairwise stats on the UNIFIED matrix only (5 replicates × 4 models ×
3 backends × 2 scenarios) using the current 3-gate goal_completion metric.

For each (model, metric), run pairwise comparisons between backends:
    no_rag vs vanilla_vector
    no_rag vs full_system
    vanilla_vector vs full_system

Report: Welch's t (n=5 per side), permutation-bootstrap p (n=10,000),
and the direction (which backend "wins" on that metric).

Highlights the "Gemini hybrid > vanilla" question by isolating that pair
per metric.

Usage:
    .venv/Scripts/python.exe scripts/stats_unified.py
"""

from __future__ import annotations

import glob
import json
import math
import random
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "data" / "eval" / "results"

MODELS = ["gemini", "claude", "gpt", "qwen"]
DEFAULT_BACKENDS = ["no_rag", "vanilla_vector", "graph_only",
                    "vision_only", "full_system", "state_path"]
METRICS = [
    ("step_accuracy",        "higher"),
    ("hallucination_rate",   "lower"),
    ("loop_rate",            "lower"),
    ("goal_completion_rate", "higher"),
    ("mean_latency_sec",     "lower"),
    ("mean_cost_usd",        "lower"),
]
# Accept any tag between model and r<N>, e.g. _unified_ or _unified2_ .
RE_UNIFIED = re.compile(
    r"^run_(?P<model>[a-z]+)_(?P<tag>[a-z0-9]+)_r(?P<rep>\d+)_\d+T\d+\.json$"
)
BOOTSTRAP_N = 10_000
SEED = 42


def load(tag_filter: str | None = None,
         backends: list[str] | None = None) -> Dict[Tuple[str, int], Dict[str, Dict[str, float]]]:
    """(model, replicate) -> backend -> {metric: value}. Filters to a
    specific tag (e.g. 'unified2') if provided; else accepts any tag."""
    _backends = backends or DEFAULT_BACKENDS
    per_replicate: Dict[Tuple[str, int], Dict[str, Dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    pattern = f"run_*_{tag_filter}_r*_*.json" if tag_filter else "run_*_r*_*.json"
    for p in sorted(RESULTS_DIR.glob(pattern)):
        m = RE_UNIFIED.match(p.name)
        if not m:
            continue
        model = m.group("model")
        tag = m.group("tag")
        rep = int(m.group("rep"))
        if model not in MODELS:
            continue
        if tag_filter and tag != tag_filter:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Compute per-backend replicate aggregate = mean across scenarios
        agg: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        for scen in d.get("scenarios", []) or []:
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b or bname not in _backends:
                    continue
                for mkey, _ in METRICS:
                    v = b.get(mkey)
                    if v is not None:
                        agg[bname][mkey].append(float(v))
                # Also carry fallback_rate + mean_route_confidence if present
                for extra in ("fallback_rate", "mean_route_confidence"):
                    v = b.get(extra)
                    if v is not None:
                        agg[bname][extra].append(float(v))
        for bname in _backends:
            for mkey in [k for k, _ in METRICS] + ["fallback_rate", "mean_route_confidence"]:
                vs = agg[bname].get(mkey, [])
                if vs:
                    per_replicate[(model, rep)][bname][mkey] = sum(vs) / len(vs)
    return per_replicate


def welch_t(a: List[float], b: List[float]) -> Tuple[float, float, float]:
    if len(a) < 2 or len(b) < 2:
        return (float("nan"), float("nan"), float("nan"))
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    na, nb = len(a), len(b)
    if va == 0 and vb == 0:
        return (0.0, float("inf"), 1.0 if ma == mb else 0.0)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return (0.0, float("inf"), 1.0)
    t = (ma - mb) / se
    df_num = (va / na + vb / nb) ** 2
    df_den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    df = df_num / df_den if df_den else float("inf")
    # Approximate p via normal for df>=30 or Cornish-Fisher-ish adjustment
    absT = abs(t)
    if df >= 30:
        z = absT
    else:
        z = absT * (1 - 1 / (4 * df)) / math.sqrt(1 + absT * absT / (2 * df))
    p = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
    return (t, df, p)


def perm_p(a: List[float], b: List[float], n: int = BOOTSTRAP_N) -> float:
    if not a or not b:
        return float("nan")
    rng = random.Random(SEED)
    observed = abs(statistics.fmean(a) - statistics.fmean(b))
    combined = list(a) + list(b)
    na = len(a)
    hits = 0
    for _ in range(n):
        rng.shuffle(combined)
        d = abs(statistics.fmean(combined[:na]) - statistics.fmean(combined[na:]))
        if d >= observed:
            hits += 1
    return hits / n


def per_metric_vals(
    per_replicate: dict, model: str, backend: str, metric: str
) -> List[float]:
    out = []
    for (mdl, rep), by_b in per_replicate.items():
        if mdl != model:
            continue
        cell = by_b.get(backend, {})
        if metric in cell:
            out.append(cell[metric])
    return out


def report_pairwise(per_replicate: dict) -> str:
    lines = []
    lines.append("# Pairwise backend tests — Unified matrix (n=5 per side)\n")
    lines.append("Welch's unequal-variance t + 10,000-resample permutation p.\n")
    for metric, direction in METRICS:
        lines.append(f"\n## {metric} ({'higher better' if direction=='higher' else 'lower better'})\n")
        header = "| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |"
        sep    = "|---|---|---|---|---|---|---|---|---|---|"
        lines.append(header); lines.append(sep)
        for model in MODELS:
            pairs = [("no_rag","vanilla_vector"),
                     ("no_rag","full_system"),
                     ("vanilla_vector","full_system")]
            for A, B in pairs:
                a = per_metric_vals(per_replicate, model, A, metric)
                b = per_metric_vals(per_replicate, model, B, metric)
                if not a or not b:
                    continue
                mA, mB = statistics.fmean(a), statistics.fmean(b)
                d = mA - mB
                t, df, p_w = welch_t(a, b)
                p_p = perm_p(a, b)
                if direction == "higher":
                    winner = A if mA > mB else (B if mB > mA else "tie")
                else:
                    winner = A if mA < mB else (B if mB < mA else "tie")
                sig_marker = " ✓" if (p_p < 0.05 or (not math.isnan(p_w) and p_w < 0.05)) else ""
                lines.append(
                    f"| {model} | {A} vs {B} | {mA:.3f} | {mB:.3f} | {d:+.3f} "
                    f"| {t:.2f} | {df:.1f} | {p_w:.3f} | {p_p:.3f} | {winner}{sig_marker} |"
                )
    return "\n".join(lines) + "\n"


def report_gemini_hybrid_focus(per_replicate: dict) -> str:
    """Isolate the 'Gemini hybrid > vanilla' question."""
    lines = []
    lines.append("\n# GEMINI — hybrid (full_system) vs vanilla_vector focus\n")
    lines.append("Does Gemini show a significant full_system > vanilla_vector "
                 "trend that other models don't?\n")
    lines.append("| metric | Gemini full_system | Gemini vanilla | Δ | perm p | direction |")
    lines.append("|---|---|---|---|---|---|")
    for metric, direction in METRICS:
        a = per_metric_vals(per_replicate, "gemini", "full_system", metric)
        b = per_metric_vals(per_replicate, "gemini", "vanilla_vector", metric)
        if not a or not b:
            continue
        mA, mB = statistics.fmean(a), statistics.fmean(b)
        d = mA - mB
        p_p = perm_p(a, b)
        # For higher-better metrics: hybrid wins if mA > mB.
        # For lower-better metrics: hybrid wins if mA < mB.
        if direction == "higher":
            hyb_wins = mA > mB
        else:
            hyb_wins = mA < mB
        arrow = "full_system ↑ (helps)" if hyb_wins else "vanilla ↑ (hybrid hurts)"
        sig = " ✓ sig" if p_p < 0.05 else ""
        lines.append(f"| {metric} | {mA:.3f} | {mB:.3f} | {d:+.3f} | {p_p:.3f}{sig} | {arrow} |")

    lines.append("\n## Same pair, other models — is Gemini's pattern unique?\n")
    lines.append("| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |")
    lines.append("|---|---|---|---|---|---|---|")
    for metric, direction in METRICS:
        for model in MODELS:
            a = per_metric_vals(per_replicate, model, "full_system", metric)
            b = per_metric_vals(per_replicate, model, "vanilla_vector", metric)
            if not a or not b:
                continue
            mA, mB = statistics.fmean(a), statistics.fmean(b)
            d = mA - mB
            p_p = perm_p(a, b)
            if direction == "higher":
                hyb_wins = mA > mB
            else:
                hyb_wins = mA < mB
            sig = " ✓" if p_p < 0.05 else ""
            lines.append(f"| {metric} | {model} | {mA:.3f} | {mB:.3f} | {d:+.3f} | {p_p:.3f}{sig} | {'yes' if hyb_wins else 'no'} |")
    return "\n".join(lines) + "\n"


def report_pipeline_health(data: dict) -> str:
    """Fallback activation rate + mean route confidence per (model, backend).
    Only meaningful for backends that route via guide_pipeline (full_system,
    state_path); other backends report empty."""
    lines = []
    lines.append("\n# Pipeline health — routing confidence + fallback rate\n")
    lines.append("Fallback activates when rerank confidence < 0.7. Zero on "
                 "backends that don't call the router (no_rag, vanilla_vector, "
                 "graph_only, vision_only if it doesn't hit the reranker).\n")
    lines.append("| model | backend | mean_route_conf | fallback_rate (of routed steps) |")
    lines.append("|---|---|---|---|")
    for model in MODELS:
        for backend in DEFAULT_BACKENDS:
            confs = []
            fbrs = []
            for (mdl, rep), by_b in data.items():
                if mdl != model:
                    continue
                cell = by_b.get(backend, {})
                if "mean_route_confidence" in cell:
                    confs.append(cell["mean_route_confidence"])
                if "fallback_rate" in cell:
                    fbrs.append(cell["fallback_rate"])
            if confs or fbrs:
                mc = (sum(confs) / len(confs)) if confs else float("nan")
                mfb = (sum(fbrs) / len(fbrs)) if fbrs else float("nan")
                lines.append(
                    f"| {model} | {backend} | "
                    f"{'—' if math.isnan(mc) else f'{mc:.2f}'} | "
                    f"{'—' if math.isnan(mfb) else f'{mfb*100:.0f}%'} |"
                )
    return "\n".join(lines) + "\n"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=None,
                    help="Filter to specific tag (e.g. unified2). Default: all.")
    ap.add_argument("--out", default=None,
                    help="Output markdown filename inside data/eval/results/.")
    args = ap.parse_args()

    data = load(tag_filter=args.tag)
    if not data:
        print(f"No files matching tag={args.tag!r}")
        return
    reps = defaultdict(set)
    for (mdl, rep), _ in data.items():
        reps[mdl].add(rep)
    print(f"Tag: {args.tag or 'ALL'}. Replicates per model:")
    for m in MODELS:
        print(f"  {m}: {sorted(reps[m])}")
    print()

    md = (report_pipeline_health(data)
          + report_pairwise(data)
          + report_gemini_hybrid_focus(data))
    out_name = args.out or (
        f"stats_{args.tag}.md" if args.tag else "stats_unified.md"
    )
    out = RESULTS_DIR / out_name
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
