# -*- coding: utf-8 -*-
"""Study 2 §2.1 gate, amended before signing (V3-30): the assembly/router changes are judged on
 (a) GENERATION losses: full_system steps that were routed correctly but scored wrong, not in the
     iteration-5 union loss set (dev_iter5_v3_*_r*.json, 4 benches) -> must be 0
 (b) hallucination count per model not above the iteration-5 per-model MAX
 (c) routing in bench mode: reported (correct/total, misroutes listed), plus the number of
     session-sticky overrides; a misroute is not a gate failure by itself but any misroute that
     the sticky rule could have prevented (same-dialog cross-workflow) counts as a failure of R1.
Prints the numbers and PASS/FAIL. Files: run_<model>_study2verify2_r1_*.json (v7, sticky, sb1).
"""
from __future__ import annotations
import glob, json, os, sys
from collections import defaultdict
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN_WF = {"opendtect__survey_setup__01": "survey_setup", "opendtect__3d_visualization__01": "d3_visualization",
           "opendtect__attribute_computation__01": "seismic_attribute"}
exp = {}
for f in glob.glob("data/eval/scenarios/opendtect__*.json"):
    sc = json.load(open(f, encoding="utf-8"))
    for st in sc["steps"]:
        exp[(sc["scenario_id"], st["step_index"])] = st.get("expected_workflow_node")


def model_of(name):
    return next(m for m in ("gemini", "claude", "gpt") if f"_{m}_" in name or name.startswith(f"run_{m}_") or name.startswith(f"dev_iter5_v3_{m}"))


def analyse(files):
    gen_losses, route_losses, hall, ok, tot, rows, sticky = set(), set(), defaultdict(int), 0, 0, [], 0
    for f in files:
        run = json.load(open(f, encoding="utf-8")); model = model_of(os.path.basename(f))
        for sc in run["scenarios"]:
            sid = sc["scenario_id"]; short = sid.replace("opendtect__", "")
            for ps in sc["backends"]["full_system"]["per_step"]:
                e = exp[(sid, ps["step_index"])]
                good = (ps.get("picked_node_id") == e) if e else (ps.get("picked_workflow_id") == SCEN_WF[sid])
                tot += 1; ok += good
                if ps.get("route_sticky"):
                    sticky += 1
                if not good:
                    rows.append(("MISROUTE", model, short, ps["step_index"], ps.get("picked_node_id"), ps["matched"]))
                if not ps["matched"]:
                    (gen_losses if good else route_losses).add((model, short, ps["step_index"]))
                    rows.append(("LOSS", model, short, ps["step_index"], "route✓" if good else "route✗", (ps.get("response") or "")[:100].replace("\n", " ")))
                hall[model] += bool(ps.get("hallucinated"))
    return gen_losses, route_losses, hall, ok, tot, rows, sticky


ref_union = set(); ref_hall_max = defaultdict(int)
for f in sorted(glob.glob("data/eval/results/dev_iter5_v3_*_r*.json")):
    run = json.load(open(f, encoding="utf-8")); model = model_of(os.path.basename(f)); h = 0
    for sc in run["scenarios"]:
        for ps in sc["backends"]["full_system"]["per_step"]:
            if not ps["matched"]:
                ref_union.add((model, sc["scenario_id"].replace("opendtect__", ""), ps["step_index"]))
            h += bool(ps.get("hallucinated"))
    ref_hall_max[model] = max(ref_hall_max[model], h)
print("iteration-5 union loss set:", sorted(ref_union), "| hall max per model:", dict(ref_hall_max))
files = sorted(glob.glob("data/eval/results/run_*_study2verify2_r1_*.json"))
print(f"\nverify2 files: {len(files)}")
gen, rl, hall, ok, tot, rows, sticky = analyse(files)
new_gen = sorted(gen - ref_union)
a = not new_gen
b = all(hall[m] <= ref_hall_max[m] for m in ("gemini", "claude", "gpt"))
print(f"(a) new GENERATION losses vs iteration-5 union: {new_gen or 'none'} -> {'PASS' if a else 'FAIL'}; generation losses in set: {sorted(gen & ref_union) or 'none'}; resolved vs union: {sorted(ref_union - gen - rl) or 'none'}")
print(f"(b) hall per model {dict(hall)} vs iteration-5 max {dict(ref_hall_max)} -> {'PASS' if b else 'FAIL'}")
print(f"(c) routing {ok}/{tot}; sticky overrides {sticky}; route-caused losses {sorted(rl) or 'none'}")
for r in rows:
    print("   ", r)
print("\nGATE:", "PASS" if (a and b and len(files) == 3) else "FAIL")
