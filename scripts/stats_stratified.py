"""Primary test for v3 (pre-registered): stratified permutation test with the
generator model as stratum.

For a backend pair (A, B) and a metric, the replicate-level values (one per
replicate = mean over scenarios) are grouped by model. Within each model the
A/B labels are permuted among that model's 2n replicates; the test
statistic is the mean over models of (mean_A − mean_B). Two-sided p from
10,000 label permutations (seed 42). Per-model raw permutation p and the
Holm-corrected values over the declared family are printed alongside.

Usage:
    .venv/Scripts/python.exe scripts/stats_stratified.py --tag v3
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MODELS = [m.strip() for m in os.environ.get("BENCH_MODELS", "gemini,claude,gpt").split(",") if m.strip()]
PAIRS = [("full_system", "vanilla_budget"), ("full_system", "vanilla_vector"), ("full_system", "no_rag"),
         ("state_path", "vanilla_budget"), ("graph_only", "vanilla_budget")]
METRICS = [("step_accuracy", "higher"), ("hallucination_rate", "lower"), ("goal_completion_rate", "higher"),
           ("mean_cost_total_usd", "lower"), ("mean_latency_sec", "lower")]
N_PERM = 10_000
SEED = 42


def load(tag: str):
    """{model: {backend: [replicate value per metric dict]}}"""
    data = defaultdict(lambda: defaultdict(list))
    for f in sorted(glob.glob(str(ROOT / f"data/eval/results/run_*_{tag}_r*_*.json"))):
        m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", os.path.basename(f))
        if not m or m.group(1) not in MODELS:
            continue
        d = json.load(open(f, encoding="utf-8"))
        agg = d.get("aggregate") or {}
        for b, a in agg.items():
            if a:
                data[m.group(1)][b].append(a)
    return data


def stratified_perm(groups, n_perm=N_PERM, seed=SEED):
    """groups: {model: (list_A, list_B)}. Returns (observed, p_two_sided)."""
    rng = random.Random(seed)
    def stat(gs):
        return st.fmean(st.fmean(a) - st.fmean(b) for a, b in gs.values() if a and b)
    obs = stat(groups)
    count = 0
    for _ in range(n_perm):
        perm = {}
        for mdl, (a, b) in groups.items():
            pool = list(a) + list(b)
            rng.shuffle(pool)
            perm[mdl] = (pool[:len(a)], pool[len(a):])
        if abs(stat(perm)) >= abs(obs) - 1e-12:
            count += 1
    return obs, (count + 1) / (n_perm + 1)


def perm_p(a, b, n_perm=N_PERM, seed=SEED):
    rng = random.Random(seed)
    obs = st.fmean(a) - st.fmean(b); pool = list(a) + list(b); count = 0
    for _ in range(n_perm):
        rng.shuffle(pool)
        if abs(st.fmean(pool[:len(a)]) - st.fmean(pool[len(a):])) >= abs(obs) - 1e-12:
            count += 1
    return obs, (count + 1) / (n_perm + 1)


def holm(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i]); m = len(pvals); out = [0.0] * m; running = 0.0
    for rank, i in enumerate(idx):
        val = min(1.0, (m - rank) * pvals[i]); running = max(running, val); out[i] = running
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--out", default=None)
    args = ap.parse_args()
    data = load(args.tag)
    lines = [f"# Stratified permutation tests — {args.tag} (strata = model: {', '.join(MODELS)}; {N_PERM} permutations, seed {SEED}, two-sided)", "",
             "| pair | metric | direction | observed Δ (mean over models) | stratified p | per-model Δ (raw p) | direction count |", "|---|---|---|---|---|---|---|"]
    fam_p = []; fam_rows = []
    for A, B in PAIRS:
        for metric, better in METRICS:
            groups = {}
            for mdl in MODELS:
                a = [x.get(metric) for x in data[mdl].get(A, []) if x.get(metric) is not None]
                b = [x.get(metric) for x in data[mdl].get(B, []) if x.get(metric) is not None]
                if a and b:
                    groups[mdl] = (a, b)
            if len(groups) < 2:
                continue
            obs, p = stratified_perm(groups)
            per = []; wins = 0
            for mdl, (a, b) in groups.items():
                d, pm = perm_p(a, b); per.append(f"{mdl} {d:+.3f} ({pm:.3f})")
                good = (d > 0) if better == "higher" else (d < 0)
                wins += good
            lines.append(f"| {A} vs {B} | {metric} | {better} | {obs:+.4f} | {p:.4f} | {'; '.join(per)} | {wins}/{len(groups)} |")
            fam_p.append(p); fam_rows.append((A, B, metric))
    if fam_p:
        h = holm(fam_p)
        lines += ["", f"## Holm correction over the {len(fam_p)}-test family (stratified p)", "", "| pair | metric | p | Holm p |", "|---|---|---|---|"]
        for (A, B, metric), p, hp in zip(fam_rows, fam_p, h):
            lines.append(f"| {A} vs {B} | {metric} | {p:.4f} | {hp:.4f} |")
    md = "\n".join(lines) + "\n"
    out = args.out or str(ROOT / f"data/eval/results/stats_stratified_{args.tag}.md")
    Path(out).write_text(md, encoding="utf-8"); print(md); print("saved:", out)


if __name__ == "__main__":
    main()
