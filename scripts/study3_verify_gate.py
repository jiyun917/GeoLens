# -*- coding: utf-8 -*-
"""Study 3 §2.1 gate (mechanical). Files: run_<model>_study3verify_{dev,s2}_r1_*.json (full_system).
 dev: (a) new generation losses vs iteration-5 union = 0; (b) hall (v5 as scored) per model <= study-2
      verification-2 per-model count (1/1/1); (c) routing reported.
 s2 : (d) node-level routing at fault_sticks s4-s7 and horizon s4-s6 better than the study-2 bench
      (study-2: fault_sticks misroutes 19/19/19/18 of 30, horizon 30/30 x3 -> per-model per-step rates);
      (e) wrong advances = R2 advances whose step scored wrong AND whose picked node != expected: 0.
Also prints study-2-set step accuracy per model vs the study-2 run means (0.907/0.723/0.881).
Usage: .venv/Scripts/python.exe <this> [--tag study3verify]
"""
from __future__ import annotations
import argparse, glob, json, os, sys
from collections import defaultdict
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.chdir(r"C:\Users\user\Downloads\GeoLens-paper")
SCEN_WF = {"opendtect__survey_setup__01": "survey_setup", "opendtect__3d_visualization__01": "d3_visualization",
           "opendtect__attribute_computation__01": "seismic_attribute"}
exp = {}
for f in glob.glob("data/eval/scenarios/*.json"):
    sc = json.load(open(f, encoding="utf-8"))
    if sc.get("scenario_id"):
        for st in sc["steps"]:
            exp[(sc["scenario_id"], st["step_index"])] = st.get("expected_workflow_node")
model_of = lambda n: next(m for m in ("gemini", "claude", "gpt") if f"_{m}_" in n or n.startswith(f"run_{m}_") or n.startswith(f"dev_iter5_v3_{m}"))
ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="study3verify"); args = ap.parse_args()

# reference: iteration-5 union losses
ref = set()
for f in glob.glob("data/eval/results/dev_iter5_v3_*_r*.json"):
    run = json.load(open(f, encoding="utf-8")); m = model_of(os.path.basename(f))
    for sc in run["scenarios"]:
        for ps in sc["backends"]["full_system"]["per_step"]:
            if not ps["matched"]: ref.add((m, sc["scenario_id"].replace("opendtect__", ""), ps["step_index"]))
REF_HALL = {"gemini": 1, "claude": 1, "gpt": 1}
S2_MISROUTE = {("opendtect__fault_sticks__01", 4): 19 / 30, ("opendtect__fault_sticks__01", 5): 19 / 30, ("opendtect__fault_sticks__01", 6): 19 / 30, ("opendtect__fault_sticks__01", 7): 18 / 30,
               ("opendtect__horizon_autotrack__01", 4): 1.0, ("opendtect__horizon_autotrack__01", 5): 1.0, ("opendtect__horizon_autotrack__01", 6): 1.0}
S2_ACC = {"gemini": 0.907, "claude": 0.723, "gpt": 0.881}

# hall under v5 recomputed OFFLINE with the dev scenarios' manual sections (the stored value equals
# v4 for dev scenarios that lack manual_grounding_sections)
os.environ.setdefault("CHROMADB_PATH", "./data/chromadb_v4"); os.environ["GEOLENS_SCORER"] = "v5"
sys.path.insert(0, os.getcwd())
from api.services import evaluation as ev  # noqa: E402
SEC = {"opendtect__survey_setup__01": ["1.2.2a", "1.2 "], "opendtect__3d_visualization__01": ["1.3.1"], "opendtect__attribute_computation__01": ["1.5.1a"],
       "opendtect__fault_sticks__01": ["1.4.3b"], "opendtect__horizon_autotrack__01": ["1.4.2a"]}
SCEN = {sid: json.load(open(glob.glob(f"data/eval/scenarios/{sid}.json")[0], encoding="utf-8")) for sid in SEC}


def hall_v5(sid, ps):
    st = SCEN[sid]; gt = st["steps"][ps["step_index"]]
    labs = ev.hallucinated_elements(ps["response"], gt["visual_state_gt"]["visible_elements"], step_gt=gt, goal=st["goal"])
    g = ev._manual_grounding(st["manual_id"], SEC[sid])
    return [l for l in labs if not ev._manual_grounded(l, g)]


print("== dev set ==")
gen_new, hall, ok, tot, rows = set(), defaultdict(int), 0, 0, []
for f in sorted(glob.glob(f"data/eval/results/run_*_{args.tag}_dev_r1_*.json")):
    run = json.load(open(f, encoding="utf-8")); m = model_of(os.path.basename(f))
    for sc in run["scenarios"]:
        sid = sc["scenario_id"]; short = sid.replace("opendtect__", "")
        for ps in sc["backends"]["full_system"]["per_step"]:
            e = exp[(sid, ps["step_index"])]; good = (ps.get("picked_node_id") == e) if e else (ps.get("picked_workflow_id") == SCEN_WF[sid])
            tot += 1; ok += good; hv5 = hall_v5(sid, ps); hall[m] += bool(hv5)
            if hv5: rows.append(("HALL-v5", m, short, ps["step_index"], hv5))
            if not ps["matched"]:
                rows.append((m, short, ps["step_index"], "route✓" if good else "route✗", (ps.get("response") or "")[:90].replace("\n", " ")))
                if good and (m, short, ps["step_index"]) not in ref: gen_new.add((m, short, ps["step_index"]))
            if ps.get("route_advance"): rows.append(("ADV", m, short, ps["step_index"], ps["route_advance"], "match" if ps["matched"] else "MISS", "node✓" if good else "node✗"))
a = not gen_new; b = all(hall[m] <= REF_HALL[m] for m in REF_HALL)
print(f"(a) new generation losses: {sorted(gen_new) or 'none'} -> {'PASS' if a else 'FAIL'}")
print(f"(b) hall(v5) per model {dict(hall)} vs ref {REF_HALL} -> {'PASS' if b else 'FAIL'}")
print(f"(c) routing {ok}/{tot}"); [print("   ", r) for r in rows]

print("\n== study-2 set ==")
mis = defaultdict(lambda: [0, 0]); wrong_adv = []; acc = {}; advs = 0
for f in sorted(glob.glob(f"data/eval/results/run_*_{args.tag}_s2_r1_*.json")):
    run = json.load(open(f, encoding="utf-8")); m = model_of(os.path.basename(f)); acc[m] = run["aggregate"]["full_system"]["step_accuracy"]
    for sc in run["scenarios"]:
        sid = sc["scenario_id"]
        for ps in sc["backends"]["full_system"]["per_step"]:
            e = exp[(sid, ps["step_index"])]; good = ps.get("picked_node_id") == e
            if (sid, ps["step_index"]) in S2_MISROUTE:
                mis[(sid, ps["step_index"])][0] += (not good); mis[(sid, ps["step_index"])][1] += 1
            if ps.get("route_advance"):
                advs += 1
                if not ps["matched"] and not good: wrong_adv.append((m, sid[-20:], ps["step_index"], ps["route_advance"]))
better = all(v[0] / v[1] < S2_MISROUTE[k] for k, v in mis.items()) if mis else False
print("(d) node misroute rate at the lagging steps (now / study 2):")
for k, v in sorted(mis.items()): print(f"    {k[0][-20:]} s{k[1]}: {v[0]}/{v[1]} = {v[0]/v[1]:.2f} / {S2_MISROUTE[k]:.2f}")
print(f"    -> {'PASS' if better else 'FAIL'} (all lower)")
print(f"(e) wrong advances (advanced, node wrong, answer wrong): {wrong_adv or 'none'} of {advs} advances -> {'PASS' if not wrong_adv else 'FAIL'}")
print("step accuracy s2 set (1 run) vs study-2 mean:", {m: (round(acc.get(m, float('nan')), 3), S2_ACC[m]) for m in S2_ACC})
print("\nGATE:", "PASS" if (a and b and better and not wrong_adv) else "FAIL")
