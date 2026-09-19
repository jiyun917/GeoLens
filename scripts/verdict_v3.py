# -*- coding: utf-8 -*-
"""Mechanical application of the signed v3 pre-registration (§6.3) and the P1–P8 predictions.

Judgement set = QGIS test set (tag v3_qgis). Comparison 1 = full_system vs vanilla_budget,
comparison 2 = full_system vs vanilla_vector. Replicate value = the run's aggregate value for the
backend (mean over scenarios). Direction count: denominator 3, ties not counted. Step-accuracy
condition: wins >= 2/3 AND stratified permutation raw p < 0.05 AND no model with a significant
reverse difference (per-model permutation p < 0.05 with Δ < 0). Hall condition: full <= comparator
in >= 2/3 models. A = both; A' = step only; B = wins >= 2/3 but p >= 0.05 or model-dependent reversal;
C = wins <= 1/3. Holm over the two primary step-accuracy tests is reported; the verdict uses raw p.
Dev set (tag v3) is used only for the descriptive predictions that reference it (P1, P3, P4, P6).
No interpretation: prints numbers and the rule outcomes only.

Usage: .venv/Scripts/python.exe scripts/verdict_v3.py
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
QGIS_WF = "qgis_vector_buffer"
DEV_WF = {"opendtect__survey_setup__01": "survey_setup", "opendtect__3d_visualization__01": "d3_visualization",
          "opendtect__attribute_computation__01": "seismic_attribute"}


def runs(tag):
    out = defaultdict(list)  # model -> [run dict]
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
    """per-model Δ (mean_A − mean_B), wins/ties/reverse, stratified p, per-model p."""
    groups, rows = {}, []
    for mdl in MODELS:
        a, b = rep_values(data[mdl], A, metric), rep_values(data[mdl], B, metric)
        groups[mdl] = (a, b)
        d = mean(a) - mean(b)
        _, pm = perm_p(a, b)
        rows.append((mdl, mean(a), mean(b), d, pm))
    obs, p = stratified_perm(groups)
    wins = sum(1 for r in rows if r[3] > 0)
    ties = sum(1 for r in rows if r[3] == 0)
    rev_sig = [r[0] for r in rows if r[3] < 0 and r[4] < 0.05]
    return {"rows": rows, "obs": obs, "p": p, "wins": wins, "ties": ties, "rev_sig": rev_sig}


def grade(step, hall_ok):
    wins, p, rev = step["wins"], step["p"], step["rev_sig"]
    if wins <= 1:
        return "C"
    if p < 0.05 and not rev:
        return "A" if hall_ok else "A′"
    return "B"


def main():
    L = []
    q = runs("v3_qgis"); d = runs("v3")
    L.append("# v3 verdict — mechanical application of the signed pre-registration (§6.3, P1–P8)\n")
    L.append(f"QGIS test set runs: " + ", ".join(f"{m} n={len(q[m])}" for m in MODELS) + " | dev set runs: " + ", ".join(f"{m} n={len(d[m])}" for m in MODELS) + "\n")

    # ── §6.3 judgement on QGIS ──
    L.append("## §6.3 judgement (QGIS test set, replicate-level, strata = model)\n")
    prim_p, results = [], {}
    for name, comp in (("비교 1 (full_system vs vanilla_budget)", "vanilla_budget"), ("비교 2 (full_system vs vanilla_vector)", "vanilla_vector")):
        st = compare(q, "full_system", comp, "step_accuracy")
        hl = compare(q, "full_system", comp, "hallucination_rate")
        hall_ok_models = [r[0] for r in hl["rows"] if r[1] <= r[2]]
        hall_ok = len(hall_ok_models) >= 2
        g = grade(st, hall_ok)
        results[comp] = (st, hl, hall_ok, g)
        prim_p.append(st["p"])
        L.append(f"### {name}\n")
        L.append("| model | full step_acc | comparator step_acc | Δ | per-model perm p | full hall | comparator hall | hall full ≤ comp |")
        L.append("|---|---|---|---|---|---|---|---|")
        for (m, a, b, dd, pm), (_, ha, hb, _, _) in zip(st["rows"], hl["rows"]):
            L.append(f"| {m} | {a:.3f} | {b:.3f} | {dd:+.3f} | {pm:.3f} | {ha:.3f} | {hb:.3f} | {'✓' if ha <= hb else '✗'} |")
        L.append("")
        L.append(f"- step accuracy: direction count {st['wins']}/3 (ties {st['ties']}), stratified raw p = {st['p']:.4f}, observed Δ (mean over models) = {st['obs']:+.4f}, significant reverse in: {st['rev_sig'] or 'none'} → step condition {'성립' if (st['wins'] >= 2 and st['p'] < 0.05 and not st['rev_sig']) else '불성립'}")
        L.append(f"- hall: full ≤ comparator in {len(hall_ok_models)}/3 ({', '.join(hall_ok_models) or '—'}) → hall condition {'성립' if hall_ok else '불성립'}")
        L.append(f"- **grade: {g}**\n")
    hp = holm(prim_p)
    L.append(f"Holm over the two primary step-accuracy tests: 비교 1 p={prim_p[0]:.4f} → {hp[0]:.4f}; 비교 2 p={prim_p[1]:.4f} → {hp[1]:.4f} (verdict uses raw p).\n")
    g1, g2 = results["vanilla_budget"][3], results["vanilla_vector"][3]
    L.append(f"**Grades: 비교 1 = {g1}, 비교 2 = {g2}.**\n")

    # descriptive metrics on QGIS
    L.append("## Descriptive (QGIS, mean over replicates; not part of the verdict)\n")
    L.append("| model | backend | step_acc | hall | goal_completion | cost_total $/step | latency s/step |")
    L.append("|---|---|---|---|---|---|---|")
    for m in MODELS:
        for b in ("no_rag", "vanilla_vector", "vanilla_budget", "graph_only", "vision_only", "state_path", "full_system"):
            L.append(f"| {m} | {b} | {mean(rep_values(q[m], b, 'step_accuracy')):.3f} | {mean(rep_values(q[m], b, 'hallucination_rate')):.3f} | {mean(rep_values(q[m], b, 'goal_completion_rate')):.3f} | {mean(rep_values(q[m], b, 'mean_cost_total_usd')):.4f} | {mean(rep_values(q[m], b, 'mean_latency_sec')):.1f} |")
    L.append("")

    # ── predictions ──
    L.append("## Predictions P1–P8\n")
    # P1
    hits = {}
    for tagname, data in (("QGIS", q), ("dev", d)):
        c = compare(data, "vanilla_vector", "no_rag")
        n3 = sum(1 for r in c["rows"] if r[3] >= 0.03)
        hits[tagname] = (n3, c["rows"])
        L.append(f"- P1 ({tagname}): vanilla_vector − no_rag step_acc per model: " + ", ".join(f"{r[0]} {r[3]:+.3f}" for r in c["rows"]) + f" → ≥ +3pp in {n3}/3 → {'적중' if n3 >= 2 else '반증'}")
    # P2
    for tagname, data in (("QGIS", q), ("dev", d)):
        c = compare(data, "full_system", "vanilla_vector", "mean_cost_total_usd")
        L.append(f"- P2 ({tagname}): cost_total full − vanilla_vector $/step per model: " + ", ".join(f"{r[0]} {r[3]:+.4f}" for r in c["rows"]) + f" → full cheaper in {sum(1 for r in c['rows'] if r[3] < 0)}/3 (prediction: full may not be cheaper — descriptive)")
    # P3
    c = compare(d, "full_system", "vanilla_budget")
    n = sum(1 for r in c["rows"] if r[3] >= 0)
    L.append(f"- P3 (dev macro): full − vanilla_budget step_acc per model: " + ", ".join(f"{r[0]} {r[3]:+.3f}" for r in c["rows"]) + f" → ≥ 0 in {n}/3 → {'적중' if n >= 2 else '반증'}")
    # P4: attribute routing (dev, bench mode, workflow-level or node-level where expected node given)
    exp = {}
    for f in glob.glob(str(ROOT / "data/eval/scenarios/opendtect__*.json")):
        sc = json.load(open(f, encoding="utf-8"))
        for st in sc["steps"]:
            exp[(sc["scenario_id"], st["step_index"])] = st.get("expected_workflow_node")
    att = []; dev_route = []
    for m in MODELS:
        for r in d[m]:
            ok_att = 0; ok_all = 0
            for sc in r["scenarios"]:
                for ps in sc["backends"]["full_system"]["per_step"]:
                    e = exp[(sc["scenario_id"], ps["step_index"])]
                    good = (ps.get("picked_node_id") == e) if e else (ps.get("picked_workflow_id") == DEV_WF[sc["scenario_id"]])
                    ok_all += good
                    if sc["scenario_id"] == "opendtect__attribute_computation__01":
                        ok_att += good
            att.append(ok_att); dev_route.append(ok_all)
    L.append(f"- P4 (dev, bench mode): attribute routing correct per replicate: mean {mean(att):.2f}/8, min {min(att)}/8, replicates ≥ 5/8: {sum(1 for x in att if x >= 5)}/{len(att)} → {'적중' if mean(att) >= 5 else '반증'}; whole dev set routing {sum(dev_route)}/{16*len(dev_route)} (dry-run rule)")
    # P5
    L.append("- P5 (QGIS, full_system routing telemetry):")
    p5c_models = 0
    for m in MODELS:
        wf_ok = []; fbnone = []; node_ok = []
        for r in q[m]:
            sc = r["scenarios"][0]; steps = sc["backends"]["full_system"]["per_step"]
            wf_ok.append(sum(1 for ps in steps if ps.get("picked_workflow_id") == QGIS_WF))
            fbnone.append(sum(1 for ps in steps if ps.get("fallback_activated") or (ps.get("route_method") in (None, "none")) or not ps.get("picked_node_id")))
        L.append(f"  - {m}: (a) correct-workflow steps mean {mean(wf_ok):.2f}/8 (min {min(wf_ok)}) → {'≥ 5/8 ✓' if mean(wf_ok) >= 5 else '< 5/8 ✗'}; (b) fallback+none mean {mean(fbnone):.2f}/8 (max {max(fbnone)}) → {'≤ 3/8 ✓' if mean(fbnone) <= 3 else '> 3/8 ✗'}")
    c = compare(q, "full_system", "vanilla_budget")
    n5c = sum(1 for r in c["rows"] if r[3] >= 0)
    L.append(f"  - (c) full ≥ vanilla_budget step_acc in {n5c}/3 → {'적중' if n5c >= 2 else '반증'}; (d) = P1 (QGIS): {'적중' if hits['QGIS'][0] >= 2 else '반증'}")
    # P6: 3d_viz dev
    L.append("- P6 (dev, 3d_visualization): no_rag / vanilla_vector / full_system step_acc per model (mean over replicates):")
    for m in MODELS:
        vals = {}
        for b in ("no_rag", "vanilla_vector", "full_system"):
            xs = [sc["backends"][b]["step_accuracy"] for r in d[m] for sc in r["scenarios"] if sc["scenario_id"] == "opendtect__3d_visualization__01"]
            vals[b] = mean(xs)
        spread = max(vals.values()) - min(vals.values())
        L.append(f"  - {m}: " + " / ".join(f"{vals[b]:.3f}" for b in ("no_rag", "vanilla_vector", "full_system")) + f" (spread {spread*100:.1f}pp) → {'±5pp 내 ✓' if spread <= 0.05 else '±5pp 밖 ✗'}")
    # P7
    L.append("- P7 (QGIS, axes where full_system may be inferior): " + "; ".join(
        f"{m} hall full {mean(rep_values(q[m],'full_system','hallucination_rate')):.3f} vs vanilla_vector {mean(rep_values(q[m],'vanilla_vector','hallucination_rate')):.3f}, step_acc full {mean(rep_values(q[m],'full_system','step_accuracy')):.3f} vs vanilla_vector {mean(rep_values(q[m],'vanilla_vector','step_accuracy')):.3f}" for m in MODELS))
    # P8
    c = compare(q, "full_system", "vanilla_vector")
    L.append("- P8 (QGIS 비교 2 direction, no prediction): " + ", ".join(f"{r[0]} {r[3]:+.3f}" for r in c["rows"]) + f" → wins {c['wins']}/3, ties {c['ties']}")
    # §5.x (i): full_system losses at QGIS s1/s3/s4 per model (count only)
    L.append("- §5.x (i) check (count only): full_system losses at QGIS s1/s3/s4 per model over 10 replicates: " + ", ".join(
        f"{m} s1={sum(1 for r in q[m] for ps in r['scenarios'][0]['backends']['full_system']['per_step'] if ps['step_index']==1 and not ps['matched'])}"
        f"/s3={sum(1 for r in q[m] for ps in r['scenarios'][0]['backends']['full_system']['per_step'] if ps['step_index']==3 and not ps['matched'])}"
        f"/s4={sum(1 for r in q[m] for ps in r['scenarios'][0]['backends']['full_system']['per_step'] if ps['step_index']==4 and not ps['matched'])}" for m in MODELS))
    # QGIS routing stability (bench mode)
    L.append("- QGIS routing (bench mode, full_system): node-level correct per model: " + ", ".join(
        f"{m} {sum(1 for r in q[m] for ps in r['scenarios'][0]['backends']['full_system']['per_step'] if ps.get('picked_node_id') == json.load(open(ROOT/'data/eval/scenarios/qgis__vector_buffer__01.json', encoding='utf-8'))['steps'][ps['step_index']].get('expected_workflow_node'))}/{8*len(q[m])}" for m in MODELS))
    md = "\n".join(L) + "\n"
    (RES / "verdict_v3.md").write_text(md, encoding="utf-8")
    print(md); print("saved:", RES / "verdict_v3.md")


if __name__ == "__main__":
    main()
