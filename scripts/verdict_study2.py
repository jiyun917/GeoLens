# -*- coding: utf-8 -*-
"""Study 2 — mechanical application of the pre-registration §5 (same rules as v3 §6.3) and the
predictions Q1–Q6. Judgement set = the adopted test scenarios (tag study2). Comparison 1 =
full_system vs vanilla_budget, comparison 2 = full_system vs vanilla_vector. Replicate value =
the run's aggregate value for the backend (mean over scenarios). No interpretation.

Usage: .venv/Scripts/python.exe scripts/verdict_study2.py [--tag study2] [--scenarios data/eval/scenarios/.study2_test]
"""
from __future__ import annotations
import argparse, glob, json, os, re, statistics, sys
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


def runs(tag):
    out = defaultdict(list)
    for f in sorted(glob.glob(str(RES / f"run_*_{tag}_r*_*.json"))):
        m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", os.path.basename(f))
        if m and m.group(1) in MODELS:
            out[m.group(1)].append(json.load(open(f, encoding="utf-8")))
    return out


def rep_values(rs, backend, metric):
    return [r["aggregate"][backend][metric] for r in rs if (r.get("aggregate") or {}).get(backend) and r["aggregate"][backend].get(metric) is not None]


def mean(x):
    return statistics.mean(x) if x else float("nan")


def compare(data, A, B, metric="step_accuracy"):
    groups, rows = {}, []
    for mdl in MODELS:
        a, b = rep_values(data[mdl], A, metric), rep_values(data[mdl], B, metric)
        groups[mdl] = (a, b)
        d = mean(a) - mean(b)
        _, pm = perm_p(a, b)
        rows.append((mdl, mean(a), mean(b), d, pm))
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
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="study2"); ap.add_argument("--scenarios", default="data/eval/scenarios/.study2_test")
    args = ap.parse_args()
    q = runs(args.tag)
    exp = {}
    for f in glob.glob(str(ROOT / args.scenarios / "*.json")):
        sc = json.load(open(f, encoding="utf-8"))
        for st in sc["steps"]:
            exp[(sc["scenario_id"], st["step_index"])] = st.get("expected_workflow_node")
    L = [f"# Study 2 verdict — mechanical application of the pre-registration (tag {args.tag})\n",
         "runs: " + ", ".join(f"{m} n={len(q[m])}" for m in MODELS) + "\n", "## §5 judgement (replicate-level, strata = model)\n"]
    prim = []; grades = {}
    for name, comp in (("비교 1 (full_system vs vanilla_budget)", "vanilla_budget"), ("비교 2 (full_system vs vanilla_vector)", "vanilla_vector")):
        st = compare(q, "full_system", comp); hl = compare(q, "full_system", comp, "hallucination_rate")
        hall_ok_models = [r[0] for r in hl["rows"] if r[1] <= r[2]]; hall_ok = len(hall_ok_models) >= 2
        g = grade(st, hall_ok); grades[comp] = g; prim.append(st["p"])
        L += [f"### {name}\n", "| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |", "|---|---|---|---|---|---|---|---|"]
        for (m, a, b, d, pm), (_, ha, hb, _, _) in zip(st["rows"], hl["rows"]):
            L.append(f"| {m} | {a:.3f} | {b:.3f} | {d:+.3f} | {pm:.3f} | {ha:.3f} | {hb:.3f} | {'✓' if ha <= hb else '✗'} |")
        L += ["", f"- step: direction {st['wins']}/3 (ties {st['ties']}), stratified raw p = {st['p']:.4f}, Δ = {st['obs']:+.4f}, significant reverse: {st['rev_sig'] or 'none'} → {'성립' if (st['wins'] >= 2 and st['p'] < 0.05 and not st['rev_sig']) else '불성립'}",
              f"- hall: full ≤ comparator in {len(hall_ok_models)}/3 → {'성립' if hall_ok else '불성립'}", f"- **grade: {g}**\n"]
    hp = holm(prim)
    L.append(f"Holm (family 2): 비교 1 {prim[0]:.4f} → {hp[0]:.4f}; 비교 2 {prim[1]:.4f} → {hp[1]:.4f}. **Grades: 비교 1 = {grades['vanilla_budget']}, 비교 2 = {grades['vanilla_vector']}.**\n")
    L += ["## Descriptive (mean over replicates)\n", "| model | backend | step_acc | hall | goal_completion | cost_total $/step | latency s/step |", "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for b in BACKENDS:
            L.append(f"| {m} | {b} | {mean(rep_values(q[m], b, 'step_accuracy')):.3f} | {mean(rep_values(q[m], b, 'hallucination_rate')):.3f} | {mean(rep_values(q[m], b, 'goal_completion_rate')):.3f} | {mean(rep_values(q[m], b, 'mean_cost_total_usd')):.4f} | {mean(rep_values(q[m], b, 'mean_latency_sec')):.1f} |")
    L += ["", "## Predictions\n"]
    L.append("- Q1 no_rag mean step_acc per model: " + ", ".join(f"{m} {mean(rep_values(q[m], 'no_rag', 'step_accuracy')):.3f}" for m in MODELS))
    c = compare(q, "vanilla_budget", "no_rag"); n = sum(1 for r in c["rows"] if r[3] >= 0.03)
    L.append(f"- Q2 vanilla_budget − no_rag: " + ", ".join(f"{r[0]} {r[3]:+.3f}" for r in c["rows"]) + f" → ≥ +3pp in {n}/3 → {'적중' if n >= 2 else '반증'}")
    c = compare(q, "full_system", "vanilla_budget"); L.append(f"- Q3 비교 1 direction {c['wins']}/3 → {'적중' if c['wins'] >= 2 else '반증'}")
    c = compare(q, "full_system", "vanilla_vector"); L.append(f"- Q4 비교 2 direction (no prediction): " + ", ".join(f"{r[0]} {r[3]:+.3f}" for r in c["rows"]))
    c = compare(q, "full_system", "vanilla_budget", "hallucination_rate"); n = sum(1 for r in c["rows"] if r[3] <= 0)
    L.append(f"- Q5 hall full ≤ vanilla_budget in {n}/3 → {'적중' if n >= 2 else '반증'}")
    # Q6 routing (bench mode, full_system): workflow-level and node-level per scenario per model
    for m in MODELS:
        per_sc = defaultdict(lambda: [0, 0, 0])
        for r in q[m]:
            for sc in r["scenarios"]:
                sid = sc["scenario_id"]; wf = exp.get((sid, 0), "").rsplit("_0", 1)[0]
                for ps in sc["backends"]["full_system"]["per_step"]:
                    e = exp.get((sid, ps["step_index"]))
                    per_sc[sid][0] += 1; per_sc[sid][1] += (ps.get("picked_workflow_id") == wf); per_sc[sid][2] += (ps.get("picked_node_id") == e)
        L.append(f"- Q6 routing {m}: " + "; ".join(f"{sid.replace('opendtect__', '')} wf {v[1]}/{v[0]}, node {v[2]}/{v[0]}" for sid, v in per_sc.items()))
    md = "\n".join(L) + "\n"
    (RES / f"verdict_{args.tag}.md").write_text(md, encoding="utf-8"); print(md); print("saved:", RES / f"verdict_{args.tag}.md")


if __name__ == "__main__":
    main()
