# -*- coding: utf-8 -*-
"""Study 2 §2.1 dev-set verification gate (mechanical).
For each RERANK_SESSION_BLOCK value (0 / 1) with CONTEXT_ASSEMBLY=v6 and scorer v4, over the three
full_system-only dev benches run_<model>_study2verify_sb<sb>_r1_*.json:
  (i)   bench-mode routing correct 64/64 (dry-run rule: expected node if given, else workflow)
  (ii)  no NEW full_system loss vs the iteration-5 loss set (model, scenario, step)
  (iii) hallucination count not above iteration 5 for the same model
Iteration-5 reference = dev_iter5_v3_<model>_r*.json (v4 assembly, v3 scorer as recorded; the
scorer change does not affect the dev set — rescore_scorer_v4_sensitivity.md shows Δ = 0).
Prints PASS/FAIL per criterion and per sb value, plus the loss lists. No API calls.
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


def analyse(files):
    losses, hall, route_ok, route_tot, rows = set(), defaultdict(int), 0, 0, []
    for f in files:
        run = json.load(open(f, encoding="utf-8")); name = os.path.basename(f)
        model = next(m for m in ("gemini", "claude", "gpt") if name.startswith(f"run_{m}_") or f"_{m}_" in name)
        for sc in run["scenarios"]:
            sid = sc["scenario_id"]
            for ps in sc["backends"]["full_system"]["per_step"]:
                e = exp[(sid, ps["step_index"])]
                ok = (ps.get("picked_node_id") == e) if e else (ps.get("picked_workflow_id") == SCEN_WF[sid])
                route_tot += 1; route_ok += ok
                if not ps["matched"]:
                    losses.add((model, sid.replace("opendtect__", ""), ps["step_index"]))
                    rows.append((model, sid.replace("opendtect__", ""), ps["step_index"], "route✗" if not ok else "route✓", (ps.get("response") or "")[:100].replace("\n", " ")))
                hall[model] += bool(ps.get("hallucinated"))
    return losses, hall, route_ok, route_tot, rows


ref_losses, ref_hall, _, _, ref_rows = analyse(sorted(glob.glob("data/eval/results/dev_iter5_v3_*_r0.json")))  # r0 of each model (1 run per model, like the verification)
print("iteration-5 reference (r0 per model): losses", sorted(ref_losses), "| hall per model", dict(ref_hall))
verdict = {}
for sb in ("0", "1"):
    files = sorted(glob.glob(f"data/eval/results/run_*_study2verify_sb{sb}_r1_*.json"))
    if len(files) < 3:
        print(f"\n== sb={sb}: only {len(files)}/3 files present — not evaluated"); continue
    losses, hall, ok, tot, rows = analyse(files)
    new = sorted(losses - ref_losses)
    c1 = ok == tot; c2 = not new; c3 = all(hall[m] <= ref_hall[m] for m in ("gemini", "claude", "gpt"))
    verdict[sb] = c1 and c2 and c3
    print(f"\n== sb={sb} (CONTEXT_ASSEMBLY=v6, scorer v4) ==")
    print(f"(i) routing {ok}/{tot} -> {'PASS' if c1 else 'FAIL'}")
    print(f"(ii) new losses vs iteration 5: {new or 'none'} -> {'PASS' if c2 else 'FAIL'}; resolved: {sorted(ref_losses - losses) or 'none'}")
    print(f"(iii) hall per model {dict(hall)} vs ref {dict(ref_hall)} -> {'PASS' if c3 else 'FAIL'}")
    print("losses:"); [print("  ", r) for r in rows]
print("\nVERDICT:", {sb: ("PASS" if v else "FAIL") for sb, v in verdict.items()})
