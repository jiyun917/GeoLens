# -*- coding: utf-8 -*-
"""Study 5 verdict — merges the two pass tags (study5_opendtect, study5_qgis) replicate-wise
(replicate r of a model = mean over the three test scenarios of the aggregate backend value,
weighting each scenario equally as pre-registered), then applies §5 (same as study 2) and Q1–Q7.
Usage: .venv/Scripts/python.exe scripts/verdict_study5.py
"""
from __future__ import annotations
import glob, json, os, re, statistics, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_stratified import stratified_perm, perm_p, holm  # noqa: E402
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "data" / "eval" / "results"
MODELS = ["gemini", "claude", "gpt"]
BACKENDS = ["no_rag", "vanilla_budget", "vanilla_vector", "full_system"]
TAGS = ["study5_opendtect", "study5_qgis"]


def load():
    """model -> rep -> backend -> metric -> [scenario values]"""
    d = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    for tag in TAGS:
        for f in sorted(glob.glob(str(RES / f"run_*_{tag}_r*_*.json"))):
            m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", os.path.basename(f))
            if not m or m.group(1) not in MODELS:
                continue
            run = json.load(open(f, encoding="utf-8"))
            for sc in run["scenarios"]:
                for b, bd in sc["backends"].items():
                    for k in ("step_accuracy", "hallucination_rate", "goal_completion_rate", "mean_cost_total_usd", "mean_latency_sec"):
                        if bd.get(k) is not None:
                            d[m.group(1)][int(m.group(2))][b][k].append(bd[k])
    return d


def rep_values(d, model, backend, metric):
    return [statistics.mean(v[backend][metric]) for r, v in sorted(d[model].items()) if v[backend][metric]]


def mean(x):
    return statistics.mean(x) if x else float("nan")


def compare(d, A, B, metric="step_accuracy"):
    groups, rows = {}, []
    for mdl in MODELS:
        a, b = rep_values(d, mdl, A, metric), rep_values(d, mdl, B, metric)
        groups[mdl] = (a, b); dd = mean(a) - mean(b); _, pm = perm_p(a, b)
        rows.append((mdl, mean(a), mean(b), dd, pm))
    obs, p = stratified_perm(groups)
    return {"rows": rows, "obs": obs, "p": p, "wins": sum(1 for r in rows if r[3] > 0), "ties": sum(1 for r in rows if r[3] == 0),
            "rev_sig": [r[0] for r in rows if r[3] < 0 and r[4] < 0.05]}


def grade(step, hall_ok):
    if step["wins"] <= 1:
        return "C"
    if step["p"] < 0.05 and not step["rev_sig"]:
        return "A" if hall_ok else "A′"
    return "B"


def main():
    d = load()
    L = ["# Study 5 verdict — mechanical application of the pre-registration (tags study5_opendtect + study5_qgis merged per replicate)\n",
         "runs: " + ", ".join(f"{m} n={len(d[m])}" for m in MODELS) + "\n", "## §5 judgement (replicate-level, strata = model; hall = v6 as scored)\n"]
    prim, grades = [], {}
    for name, comp in (("비교 1 (full_system vs vanilla_budget)", "vanilla_budget"), ("비교 2 (full_system vs vanilla_vector)", "vanilla_vector")):
        st = compare(d, "full_system", comp); hl = compare(d, "full_system", comp, "hallucination_rate")
        hok = [r[0] for r in hl["rows"] if r[1] <= r[2]]; hall_ok = len(hok) >= 2; g = grade(st, hall_ok); grades[comp] = g; prim.append(st["p"])
        L += [f"### {name}\n", "| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |", "|---|---|---|---|---|---|---|---|"]
        for (m, a, b, dd, pm), (_, ha, hb, _, _) in zip(st["rows"], hl["rows"]):
            L.append(f"| {m} | {a:.3f} | {b:.3f} | {dd:+.3f} | {pm:.3f} | {ha:.3f} | {hb:.3f} | {'✓' if ha <= hb else '✗'} |")
        L += ["", f"- step: direction {st['wins']}/3 (ties {st['ties']}), stratified raw p = {st['p']:.4f}, Δ = {st['obs']:+.4f}, significant reverse: {st['rev_sig'] or 'none'} → {'성립' if (st['wins'] >= 2 and st['p'] < 0.05 and not st['rev_sig']) else '불성립'}",
              f"- hall: full ≤ comparator in {len(hok)}/3 → {'성립' if hall_ok else '불성립'}", f"- **grade: {g}**\n"]
    hp = holm(prim)
    L.append(f"Holm (family 2): 비교 1 {prim[0]:.4f} → {hp[0]:.4f}; 비교 2 {prim[1]:.4f} → {hp[1]:.4f}. **Grades: 비교 1 = {grades['vanilla_budget']}, 비교 2 = {grades['vanilla_vector']}.**\n")
    L += ["## Descriptive (mean over replicates, 3 scenarios equally weighted)\n", "| model | backend | step_acc | hall v6 | goal_completion | cost_total $/step | latency s/step |", "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for b in BACKENDS:
            L.append(f"| {m} | {b} | {mean(rep_values(d, m, b, 'step_accuracy')):.3f} | {mean(rep_values(d, m, b, 'hallucination_rate')):.3f} | {mean(rep_values(d, m, b, 'goal_completion_rate')):.3f} | {mean(rep_values(d, m, b, 'mean_cost_total_usd')):.4f} | {mean(rep_values(d, m, b, 'mean_latency_sec')):.1f} |")
    L += ["", "## Per-scenario step accuracy (mean over replicates)\n", "| model | backend | " + " | ".join(TAGS) + " |", "|---|---|---|---|"]
    per = defaultdict(lambda: defaultdict(list))
    for tag in TAGS:
        for f in sorted(glob.glob(str(RES / f"run_*_{tag}_r*_*.json"))):
            m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", os.path.basename(f))
            if not m: continue
            run = json.load(open(f, encoding="utf-8"))
            for sc in run["scenarios"]:
                for b in BACKENDS:
                    per[(m.group(1), b, sc["scenario_id"])]["a"].append(sc["backends"][b]["step_accuracy"])
    sids = sorted({k[2] for k in per})
    L[-2] = "| model | backend | " + " | ".join(s.replace("opendtect__", "").replace("qgis__", "q:") for s in sids) + " |"; L[-1] = "|---|---|" + "---|" * len(sids)
    for m in MODELS:
        for b in BACKENDS:
            L.append(f"| {m} | {b} | " + " | ".join(f"{mean(per[(m, b, s)]['a']):.3f}" for s in sids) + " |")
    L += ["", "## Predictions\n"]
    L.append("- Q1/Q7 no_rag mean step_acc per model: " + ", ".join(f"{m} {mean(rep_values(d, m, 'no_rag', 'step_accuracy')):.3f}" for m in MODELS))
    c = compare(d, "vanilla_budget", "no_rag"); n = sum(1 for r in c["rows"] if r[3] >= 0.03)
    L.append(f"- Q2 vanilla_budget − no_rag: " + ", ".join(f"{r[0]} {r[3]:+.3f}" for r in c["rows"]) + f" → ≥ +3pp in {n}/3 → {'적중' if n >= 2 else '반증'}")
    c = compare(d, "full_system", "vanilla_budget"); L.append(f"- Q3 비교 1 direction {c['wins']}/3, p {c['p']:.4f} → {'적중' if (c['wins'] == 3 and c['p'] < 0.05) else '반증'}")
    c = compare(d, "full_system", "vanilla_vector"); L.append(f"- Q4 비교 2 direction {c['wins']}/3, reverse {c['rev_sig'] or 'none'} → {'적중' if (c['wins'] >= 2 and not c['rev_sig']) else '반증'}")
    c1 = compare(d, "full_system", "vanilla_budget", "hallucination_rate"); c2 = compare(d, "full_system", "vanilla_vector", "hallucination_rate")
    n1 = sum(1 for r in c1["rows"] if r[3] <= 0); n2 = sum(1 for r in c2["rows"] if r[3] <= 0)
    L.append(f"- Q5 hall(v6) full ≤ vanilla_budget {n1}/3, ≤ vanilla_vector {n2}/3 → {'적중' if (n1 >= 2 and n2 >= 2) else '반증'}")
    # Q6 routing telemetry
    exp = {}
    for f in glob.glob(str(ROOT / "data/eval/scenarios/.study5_test_*/*.json")):
        sc = json.load(open(f, encoding="utf-8"))
        for st in sc["steps"]: exp[(sc["scenario_id"], st["step_index"])] = st.get("expected_workflow_node")
    for m in MODELS:
        agg = defaultdict(lambda: [0, 0, 0, 0, 0])
        for tag in TAGS:
            for f in glob.glob(str(RES / f"run_{m}_{tag}_r*_*.json")):
                run = json.load(open(f, encoding="utf-8"))
                for sc in run["scenarios"]:
                    sid = sc["scenario_id"]; wf = (exp.get((sid, 0)) or "").rsplit("_0", 1)[0]
                    for ps in sc["backends"]["full_system"]["per_step"]:
                        v = agg[sid]; v[0] += 1; v[1] += ps.get("picked_workflow_id") == wf; v[2] += ps.get("picked_node_id") == exp.get((sid, ps["step_index"])); v[3] += bool(ps.get("route_advance")); v[4] += bool(ps.get("route_sticky"))
        L.append(f"- Q6 routing {m}: " + "; ".join(f"{sid.replace('opendtect__', '').replace('qgis__', 'q:')} wf {v[1]}/{v[0]}, node {v[2]}/{v[0]}, R2 {v[3]}, R1 {v[4]}" for sid, v in agg.items()))
    md = "\n".join(L) + "\n"
    (RES / "verdict_study5.md").write_text(md, encoding="utf-8"); print(md); print("saved:", RES / "verdict_study5.md")


if __name__ == "__main__":
    main()
