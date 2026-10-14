# -*- coding: utf-8 -*-
"""Study 5x (exploratory ablation, outside the pre-registration): the intermediate condition linked_chunks
(full_system routing + the same manual text, no structure block) on the study-5 test set, compared with the
study-5 full_system and vanilla_budget cells. Replicate = mean over the three scenarios (equal weight), n = 10.
Descriptive statistics with the same stratified permutation test as study 5, reported as exploratory.
Usage: .venv/Scripts/python.exe scripts/verdict_study5x.py
"""
from __future__ import annotations
import glob, json, os, re, statistics, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_stratified import stratified_perm, perm_p  # noqa: E402
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "data" / "eval" / "results"
MODELS = ["gemini", "claude", "gpt"]
METRICS = ("step_accuracy", "hallucination_rate", "goal_completion_rate", "mean_cost_total_usd", "mean_latency_sec")


def load(tags, backends):
    """model -> rep -> backend -> metric -> [scenario values]; plus per-scenario accuracies and routing accuracy."""
    d = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    per_sc = defaultdict(lambda: defaultdict(list))        # (model, backend, sid) -> rep -> [acc]
    route = defaultdict(lambda: [0, 0])                     # (model, backend) -> [correct, total]
    ctx = defaultdict(list)                                 # (model, backend) -> context chars
    files = 0
    exp = {}
    for f in glob.glob(str(ROOT / "data/eval/scenarios/.study5_test_*/*.json")):
        sc = json.load(open(f, encoding="utf-8"))
        for st in sc["steps"]:
            exp[(sc["scenario_id"], st["step_index"])] = st.get("expected_workflow_node")
    for tag in tags:
        for f in sorted(glob.glob(str(RES / f"run_*_{tag}_r*_*.json"))):
            m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", os.path.basename(f))
            if not m or m.group(1) not in MODELS:
                continue
            files += 1
            run = json.load(open(f, encoding="utf-8")); model, rep = m.group(1), int(m.group(2))
            for sc in run["scenarios"]:
                for b, bd in sc["backends"].items():
                    if b not in backends:
                        continue
                    for k in METRICS:
                        if bd.get(k) is not None:
                            d[model][rep][b][k].append(bd[k])
                    per_sc[(model, b, sc["scenario_id"])][rep].append(bd["step_accuracy"])
                    for s in bd.get("per_step") or []:
                        ctx[(model, b)].append(s.get("context_chars") or len(s.get("context_block") or ""))
                        if s.get("route_method"):
                            route[(model, b)][1] += 1
                            route[(model, b)][0] += (s.get("picked_node_id") == exp.get((sc["scenario_id"], s["step_index"])))
    return d, per_sc, route, ctx, files


def rep_values(d, model, backend, metric):
    return [statistics.mean(v[backend][metric]) for r, v in sorted(d[model].items()) if v[backend][metric]]


def mean(x):
    return statistics.mean(x) if x else float("nan")


def compare(dA, dB, A, B, metric="step_accuracy"):
    groups, rows = {}, []
    for mdl in MODELS:
        a, b = rep_values(dA, mdl, A, metric), rep_values(dB, mdl, B, metric)
        n = min(len(a), len(b)); a, b = a[:n], b[:n]
        groups[mdl] = (a, b); dd = mean(a) - mean(b); _, pm = perm_p(a, b)
        rows.append((mdl, mean(a), mean(b), dd, pm, n))
    obs, p = stratified_perm(groups)
    return rows, obs, p


def main():
    dx, scx, routex, ctxx, fx = load(["study5x_opendtect", "study5x_qgis"], {"linked_chunks"})
    d5, sc5, route5, ctx5, f5 = load(["study5_opendtect", "study5_qgis"], {"full_system", "vanilla_budget", "vanilla_vector", "no_rag"})
    L = ["# Study 5x — exploratory ablation (outside the pre-registration): linked_chunks on the study-5 test set\n",
         f"files: study5x {fx} (expected 60), study5 {f5}. linked_chunks = full_system routing + same manual text, no structure block.\n",
         "reps per model: " + ", ".join(f"{m} {len(dx[m])}" for m in MODELS) + "\n"]

    L.append("## Step accuracy (replicate mean, 3 scenarios equal weight)\n")
    L.append("| model | no_rag | vanilla_budget | linked_chunks | full_system | full − linked | linked − vanilla_budget |")
    L.append("|---|---|---|---|---|---|---|")
    for m in MODELS:
        nr, vb, fs = mean(rep_values(d5, m, "no_rag", "step_accuracy")), mean(rep_values(d5, m, "vanilla_budget", "step_accuracy")), mean(rep_values(d5, m, "full_system", "step_accuracy"))
        lc = mean(rep_values(dx, m, "linked_chunks", "step_accuracy"))
        L.append(f"| {m} | {nr:.3f} | {vb:.3f} | {lc:.3f} | {fs:.3f} | {fs - lc:+.3f} | {lc - vb:+.3f} |")

    for A, dA, B, dB, title in [("full_system", d5, "linked_chunks", dx, "full_system vs linked_chunks (structure block effect)"),
                                ("linked_chunks", dx, "vanilla_budget", d5, "linked_chunks vs vanilla_budget (graph-selected text effect)")]:
        rows, obs, p = compare(dA, dB, A, B)
        L.append(f"\n### {title}\n")
        L.append("| model | " + A + " | " + B + " | Δ | per-model p | n |")
        L.append("|---|---|---|---|---|---|")
        for r in rows:
            L.append(f"| {r[0]} | {r[1]:.3f} | {r[2]:.3f} | {r[3]:+.3f} | {r[4]:.4f} | {r[5]} |")
        wins = sum(1 for r in rows if r[3] > 0); ties = sum(1 for r in rows if r[3] == 0)
        L.append(f"- direction {wins}/3 (ties {ties}), stratified Δ = {obs:+.4f}, raw p = {p:.4f} (exploratory, not pre-registered)")

    L.append("\n## Hallucination rate v6, goal completion, cost, latency (replicate mean)\n")
    L.append("| model | backend | hall v6 | goal completion | cost $/step | latency s/step | context chars (mean) |")
    L.append("|---|---|---|---|---|---|---|")
    for m in MODELS:
        for b, dd, cc in (("vanilla_budget", d5, ctx5), ("linked_chunks", dx, ctxx), ("full_system", d5, ctx5)):
            L.append(f"| {m} | {b} | {mean(rep_values(dd, m, b, 'hallucination_rate')):.3f} | {mean(rep_values(dd, m, b, 'goal_completion_rate')):.3f} | "
                     f"{mean(rep_values(dd, m, b, 'mean_cost_total_usd')):.4f} | {mean(rep_values(dd, m, b, 'mean_latency_sec')):.1f} | {mean(cc[(m, b)]):,.0f} |")

    L.append("\n## Per-scenario step accuracy (mean over replicates)\n")
    sids = sorted({k[2] for k in list(scx) + list(sc5)})
    L.append("| model | backend | " + " | ".join(s.replace("opendtect__", "").replace("qgis__", "q:") for s in sids) + " |")
    L.append("|---|---|" + "---|" * len(sids))
    for m in MODELS:
        for b, sc in (("vanilla_budget", sc5), ("linked_chunks", scx), ("full_system", sc5)):
            row = [f"{mean([statistics.mean(x) for x in sc[(m, b, s)].values()]):.3f}" if sc[(m, b, s)] else "-" for s in sids]
            L.append(f"| {m} | {b} | " + " | ".join(row) + " |")

    L.append("\n## Routing parity (node-level accuracy of the routed steps; same mechanism in both backends)\n")
    L.append("| model | linked_chunks | full_system |")
    L.append("|---|---|---|")
    for m in MODELS:
        a, b = routex[(m, "linked_chunks")], route5[(m, "full_system")]
        L.append(f"| {m} | {a[0]}/{a[1]} = {a[0] / max(1, a[1]):.3f} | {b[0]}/{b[1]} = {b[0] / max(1, b[1]):.3f} |")

    md = "\n".join(L) + "\n"
    out = RES / "verdict_study5x.md"
    out.write_text(md, encoding="utf-8")
    print(md); print("saved:", out)


if __name__ == "__main__":
    main()
