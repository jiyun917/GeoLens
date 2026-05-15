"""
Statistical analysis of benchmark results — required for any paper-grade
backend comparison.

For each metric (step_accuracy, hallucination_rate, dwell_loop_rate,
trap_pass_rate, recovery_rate, goal_completion_rate) we report:
  - per-backend mean + 95% bootstrap confidence interval
  - paired-bootstrap p-value matrix (every backend vs every other)
  - effect size (Cohen's d for normalized metrics)

A paired bootstrap is the right test here because the same set of
scenarios is run through all backends, so per-scenario scores are
paired observations. p-values are two-sided.

CLI:
    python -m api.services.bench_stats data/eval/results/v1.json
        [--metric step_accuracy]
        [--n-bootstrap 10000]
        [--alpha 0.05]

Output: prints a Markdown report + writes <result>_stats.md beside the
input.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Tuple

import math
import random


METRICS = (
    "step_accuracy",
    "hallucination_rate",
    "dwell_loop_rate",
    "trap_pass_rate",
    "recovery_rate",
    "goal_completion_rate",
)


def _paired_values(results: Dict, backend: str, metric: str) -> List[Optional[float]]:
    out = []
    for s in results.get("scenarios", []):
        b = (s.get("backends") or {}).get(backend) or {}
        v = b.get(metric)
        out.append(v if isinstance(v, (int, float)) else None)
    return out


def _drop_paired_none(vec_a: List[Optional[float]], vec_b: List[Optional[float]]) -> Tuple[List[float], List[float]]:
    a, b = [], []
    for x, y in zip(vec_a, vec_b):
        if x is None or y is None:
            continue
        a.append(float(x)); b.append(float(y))
    return a, b


def bootstrap_ci(values: List[float], n: int = 10000, alpha: float = 0.05,
                 rng: Optional[random.Random] = None) -> Tuple[float, float, float]:
    """Return (mean, lo, hi) where lo/hi are 1-alpha/2 percentile bounds."""
    rng = rng or random.Random(42)
    if not values:
        return (float("nan"), float("nan"), float("nan"))
    means = []
    k = len(values)
    for _ in range(n):
        sample = [values[rng.randrange(k)] for _ in range(k)]
        means.append(sum(sample) / k)
    means.sort()
    lo = means[int((alpha / 2) * n)]
    hi = means[int((1 - alpha / 2) * n) - 1]
    return (sum(values) / k, lo, hi)


def paired_bootstrap_p(a: List[float], b: List[float], n: int = 10000,
                        rng: Optional[random.Random] = None) -> float:
    """Two-sided p-value for H0: mean(a-b) = 0, via paired bootstrap.
    Resamples with replacement from the PAIRED differences vector."""
    rng = rng or random.Random(42)
    if not a or not b or len(a) != len(b):
        return float("nan")
    diffs = [x - y for x, y in zip(a, b)]
    k = len(diffs)
    observed_mean = sum(diffs) / k
    # Center under H0
    centered = [d - observed_mean for d in diffs]
    count_extreme = 0
    abs_obs = abs(observed_mean)
    for _ in range(n):
        sample = [centered[rng.randrange(k)] for _ in range(k)]
        m = sum(sample) / k
        if abs(m) >= abs_obs:
            count_extreme += 1
    return count_extreme / n


def cohens_d(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return float("nan")
    mean_a = sum(a) / len(a); mean_b = sum(b) / len(b)
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    var_a = sum((x - mean_a) ** 2 for x in a) / (len(a) - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (len(b) - 1)
    pooled = math.sqrt((var_a + var_b) / 2.0) if (var_a + var_b) > 0 else 0.0
    return (mean_a - mean_b) / pooled if pooled else 0.0


def analyze(results: Dict, n_bootstrap: int = 10000, alpha: float = 0.05,
            metrics: Tuple[str, ...] = METRICS) -> Dict:
    backends = []
    for s in results.get("scenarios", []):
        for b in (s.get("backends") or {}).keys():
            if b not in backends:
                backends.append(b)

    report: Dict = {
        "n_scenarios": len(results.get("scenarios", [])),
        "backends": backends,
        "alpha": alpha,
        "n_bootstrap": n_bootstrap,
        "per_metric": {},
    }

    for metric in metrics:
        # CIs
        cis: Dict[str, Dict] = {}
        for bk in backends:
            vec = [v for v in _paired_values(results, bk, metric) if v is not None]
            mean, lo, hi = bootstrap_ci(vec, n=n_bootstrap, alpha=alpha)
            cis[bk] = {"n": len(vec), "mean": mean, "ci_lo": lo, "ci_hi": hi}

        # Pairwise paired bootstrap p + Cohen's d
        pvals: Dict[str, Dict[str, float]] = {}
        deffs: Dict[str, Dict[str, float]] = {}
        for i, a in enumerate(backends):
            pvals[a] = {}
            deffs[a] = {}
            for b in backends:
                if a == b:
                    pvals[a][b] = float("nan")
                    deffs[a][b] = 0.0
                    continue
                va = _paired_values(results, a, metric)
                vb = _paired_values(results, b, metric)
                va2, vb2 = _drop_paired_none(va, vb)
                pvals[a][b] = paired_bootstrap_p(va2, vb2, n=n_bootstrap)
                deffs[a][b] = cohens_d(va2, vb2)

        report["per_metric"][metric] = {
            "ci": cis,
            "p_paired": pvals,
            "cohens_d": deffs,
        }
    return report


def render_markdown(stats: Dict) -> str:
    out: List[str] = ["# Benchmark Statistical Analysis", ""]
    out.append(f"- scenarios: {stats['n_scenarios']}")
    out.append(f"- bootstrap resamples: {stats['n_bootstrap']}")
    out.append(f"- significance level: α = {stats['alpha']}")
    out.append("")
    for metric, blk in stats["per_metric"].items():
        out.append(f"## {metric}")
        out.append("")
        out.append("**Per-backend mean (95% CI)**")
        out.append("")
        out.append("| backend | n | mean | 95% CI |")
        out.append("|---|---|---|---|")
        for bk, ci in blk["ci"].items():
            out.append(
                f"| {bk} | {ci['n']} | {ci['mean']:.3f} | "
                f"[{ci['ci_lo']:.3f}, {ci['ci_hi']:.3f}] |"
            )
        out.append("")
        out.append("**Paired-bootstrap p-value (vs each other)**")
        out.append("")
        backends = stats["backends"]
        out.append("| | " + " | ".join(backends) + " |")
        out.append("|" + "|".join(["---"] * (len(backends) + 1)) + "|")
        for a in backends:
            row = [a]
            for b in backends:
                p = blk["p_paired"].get(a, {}).get(b, float("nan"))
                if a == b:
                    row.append("—")
                elif math.isnan(p):
                    row.append("n/a")
                else:
                    star = "*" if p < stats["alpha"] else ""
                    row.append(f"{p:.3f}{star}")
            out.append("| " + " | ".join(row) + " |")
        out.append("")
    return "\n".join(out) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("results", help="results JSON from bench_runner")
    p.add_argument("--n-bootstrap", type=int, default=10000)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--metric", default=None, help="restrict to one metric")
    args = p.parse_args()

    with open(args.results, "r", encoding="utf-8") as f:
        results = json.load(f)

    metrics = (args.metric,) if args.metric else METRICS
    stats = analyze(results, n_bootstrap=args.n_bootstrap, alpha=args.alpha, metrics=metrics)
    md = render_markdown(stats)

    out_path = args.results.rsplit(".", 1)[0] + "_stats.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"Stats report written: {out_path}")


if __name__ == "__main__":
    main()
