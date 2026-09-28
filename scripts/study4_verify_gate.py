# -*- coding: utf-8 -*-
"""Study 4 development verification summary + gate (mechanical). Files: run_<model>_<tag>_{opendtect,qgis}_r1_*.json
(all four backends, one replicate). Prints per model x backend step accuracy / hall / loop, per-scenario full_system
vs vanilla_vector, routing accuracy and R3 statistics, then the gate:
  (a) step: full_system >= vanilla_vector for every model (overall) and in >= 5/6 scenarios per model
  (b) hall: full_system <= vanilla_vector and <= vanilla_budget for every model
  (c) routing: picked node == expected node in >= 0.85 of full_system steps (all models pooled), wrong R3 advances = 0
      (R3 fired, picked != expected, step scored wrong)
  (d) no regression on the ceiling scenario (qgis__vector_buffer__01): full_system >= 0.95 per model
Usage: .venv/Scripts/python.exe scripts/study4_verify_gate.py [--tag study4ver]
"""
from __future__ import annotations
import argparse, glob, json, os, sys
from collections import defaultdict
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="study4ver"); args = ap.parse_args()
exp = {}
for d in ("data/eval/scenarios/.study4_dev_opendtect", "data/eval/scenarios/.study4_dev_qgis"):
    for f in glob.glob(f"{d}/*.json"):
        sc = json.load(open(f, encoding="utf-8"))
        for st in sc["steps"]:
            exp[(sc["scenario_id"], st["step_index"])] = st.get("expected_workflow_node")
MODELS = ("gemini", "claude", "gpt"); BACKENDS = ("no_rag", "vanilla_budget", "vanilla_vector", "full_system")
acc = defaultdict(list); hall = defaultdict(list); loop = defaultdict(list); scen_acc = defaultdict(list)
route = defaultdict(lambda: [0, 0]); r3 = defaultdict(lambda: {"fired": 0, "wrong": 0, "fixed": 0}); files = 0
for m in MODELS:
    for f in sorted(glob.glob(f"data/eval/results/run_{m}_{args.tag}_*_r1_*.json")):
        d = json.load(open(f, encoding="utf-8")); files += 1
        for sc in d["scenarios"]:
            sid = sc["scenario_id"]
            for be, r in sc["backends"].items():
                steps = r.get("per_step") or []
                acc[(m, be)] += [1 if s.get("matched") else 0 for s in steps]
                hall[(m, be)] += [1 if s.get("hallucinated") else 0 for s in steps]
                loop[(m, be)] += [1 if s.get("looped") else 0 for s in steps]
                scen_acc[(m, be, sid)] += [1 if s.get("matched") else 0 for s in steps]
                if be == "full_system":
                    for s in steps:
                        e = exp.get((sid, s["step_index"]))
                        if e:
                            route[sid][1] += 1; route[sid][0] += 1 if s.get("picked_node_id") == e else 0
                        adv = s.get("route_screen_advance")
                        if adv:
                            r3[m]["fired"] += 1
                            if e and s.get("picked_node_id") == e: r3[m]["fixed"] += 1
                            if e and s.get("picked_node_id") != e and not s.get("matched"): r3[m]["wrong"] += 1
mean = lambda xs: (sum(xs) / len(xs)) if xs else float("nan")
print(f"files: {files}\n\n| model | backend | n | step_acc | hall v6 | loop |\n|---|---|---|---|---|---|")
for m in MODELS:
    for be in BACKENDS:
        print(f"| {m} | {be} | {len(acc[(m, be)])} | {mean(acc[(m, be)]):.3f} | {mean(hall[(m, be)]):.3f} | {mean(loop[(m, be)]):.3f} |")
sids = sorted({k[2] for k in scen_acc})
print("\nper-scenario step accuracy: full_system / vanilla_vector (vanilla_budget)")
print("| model | " + " | ".join(s.replace("opendtect__", "").replace("qgis__", "q:")[:22] for s in sids) + " |")
cells_ok = defaultdict(int)
for m in MODELS:
    row = []
    for sid in sids:
        fs, vv, vb = mean(scen_acc[(m, "full_system", sid)]), mean(scen_acc[(m, "vanilla_vector", sid)]), mean(scen_acc[(m, "vanilla_budget", sid)])
        row.append(f"{fs:.2f} / {vv:.2f} ({vb:.2f})" + (" ✓" if fs >= vv else " ✗"))
        cells_ok[m] += 1 if fs >= vv else 0
    print(f"| {m} | " + " | ".join(row) + " |")
print("\nrouting (full_system, picked == expected):")
tot = [0, 0]
for sid in sorted(route):
    ok, n = route[sid]; tot[0] += ok; tot[1] += n
    print(f"  {sid}: {ok}/{n} = {ok / max(n, 1):.2f}")
print(f"  ALL: {tot[0]}/{tot[1]} = {tot[0] / max(tot[1], 1):.3f}")
print("R3 screen-delta advance:", {m: dict(v) for m, v in r3.items()})
print("\n=== GATE ===")
ga = all(mean(acc[(m, "full_system")]) >= mean(acc[(m, "vanilla_vector")]) for m in MODELS) and all(cells_ok[m] >= 5 for m in MODELS)
gb = all(mean(hall[(m, "full_system")]) <= min(mean(hall[(m, "vanilla_vector")]), mean(hall[(m, "vanilla_budget")])) for m in MODELS)
gc = (tot[0] / max(tot[1], 1)) >= 0.85 and all(v["wrong"] == 0 for v in r3.values())
gd = all(mean(scen_acc[(m, "full_system", "qgis__vector_buffer__01")]) >= 0.95 for m in MODELS) if any(k[2] == "qgis__vector_buffer__01" for k in scen_acc) else True
for name, ok in (("(a) step full >= vanilla_vector (per model + >=5/6 scenarios)", ga), ("(b) hall full <= both vanilla per model", gb),
                 ("(c) routing >= 0.85 and wrong R3 advances = 0", gc), ("(d) vector_buffer full >= 0.95", gd)):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
print("GATE:", "PASS" if all((ga, gb, gc, gd)) else "FAIL")
