# -*- coding: utf-8 -*-
"""Study 4 K1 step 3 - generator-free routing dry-run on a scenario directory (pre-registered procedure).
For every scenario step: Flash vision (cached on disk by scripts/study4_cache_visual_states.py when available, else
called) -> localize_to_graph with the study-4 pins (candidate pool, Flash rerank, R1, R2''' with the GT edge
instruction of the previous step as the 'previous instruction', R3 with the previous screen) -> compare with the
scenario's expected_workflow_node. NO generator call is made and no instruction text is produced, so the test
set stays unseen by the generators; only routing accuracy and the mismatching steps are reported.
Session mode 'chained': the previous step's routed node is the session's last node (as in the bench);
'teacher': the previous step's GT node is the last node (isolates the per-step decision).
Usage: .venv/Scripts/python.exe scripts/study4_route_dryrun.py --scenarios data/eval/study4/scenarios_draft
           [--workflows data/workflows] [--vs data/eval/study4/visual_states] [--mode chained|teacher|both]
Requires: study-4 env pins in the environment (source scripts/study2_env.sh; source scripts/study4_env.sh),
GEOLENS_SOFTWARE_ID set per software (the script sets it from the scenario id prefix).
"""
from __future__ import annotations
import argparse, base64, glob, hashlib, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", required=True); ap.add_argument("--workflows", default=None)
    ap.add_argument("--vs", default="data/eval/study4/visual_states"); ap.add_argument("--mode", default="both")
    args = ap.parse_args()
    if args.workflows:
        os.environ["WORKFLOW_DATA_PATH"] = args.workflows
    from api.services import guide_pipeline as gp
    pipe = gp.get_guide_pipeline(); graph = pipe.graph
    modes = ["chained", "teacher"] if args.mode == "both" else [args.mode]
    total = {m: [0, 0] for m in modes}
    for f in sorted(glob.glob(str(ROOT / args.scenarios / "*.json"))):
        sc = json.load(open(f, encoding="utf-8")); sid = sc["scenario_id"]
        os.environ["GEOLENS_SOFTWARE_ID"] = "qgis" if sid.startswith("qgis") else "opendtect"
        gp._ACTIVE_SOFTWARE_ID = os.environ["GEOLENS_SOFTWARE_ID"]
        # vision outputs (cache on disk, else live)
        vs_list = []
        for st in sc["steps"]:
            cp = ROOT / args.vs / sid / f"step_{st['step_index']}.json"
            vs = None
            if cp.exists():
                c = json.load(open(cp, encoding="utf-8"))
                sp = ROOT / st["screenshot_path"]
                if sp.exists() and c.get("sha256") == hashlib.sha256(sp.read_bytes()).hexdigest():
                    vs = c.get("visual_state")
            if vs is None:
                sp = ROOT / st["screenshot_path"]
                if not sp.exists():
                    vs_list.append(None); continue
                b64 = "data:image/jpeg;base64," + base64.b64encode(sp.read_bytes()).decode("ascii")
                vs = pipe.recognize_visual_state(b64)
            vs_list.append(vs)
        print(f"\n## {sid} ({len(sc['steps'])} steps)")
        for mode in modes:
            last = None; prev_vs = None; hist = []; ok = 0; n = 0; rows = []
            for i, st in enumerate(sc["steps"]):
                vs = vs_list[i]; exp = st.get("expected_workflow_node")
                if vs is None:
                    rows.append(f"  s{i}: no screenshot"); continue
                for k in ("route_screen_advance", "route_advance", "route_sticky"):
                    gp._LAST_LOCALIZE_META[k] = None          # localize_to_graph does not reset these (process_guide_request does)
                loc = pipe.localize_to_graph(vs, None, screenshot_b64=None, manual_ids=[sc["manual_id"]], user_goal=sc.get("goal", ""),
                                             visited_node_ids=[], last_node_id=last, completed_steps=list(hist), clip_result=(None, 0.0, []),
                                             prev_visual_state=prev_vs)
                node = loc.get("node"); picked = node["id"] if node else None
                meta = gp.get_last_localize_meta()
                if exp:
                    n += 1; ok += 1 if picked == exp else 0
                mark = "ok" if picked == exp else ("n/a" if not exp else "MISS")
                rows.append(f"  s{i} {mark:4s} picked={str(picked).split('_')[-3:] if picked else None} exp={str(exp).split('_')[-3:] if exp else None} conf={loc.get('confidence'):.2f} R3={bool(meta.get('route_screen_advance'))} R2={bool(meta.get('route_advance'))} R1={bool(meta.get('route_sticky'))}")
                # session update
                if mode == "chained":
                    last = picked or last
                else:
                    last = exp or last
                # the GT edge instruction into the next step stands in for the generator's instruction (no generator)
                nxt_edge = ""
                if exp:
                    for s2 in graph.get_next_steps(exp):
                        nxt_edge = s2.get("edge_instruction") or ""
                        break
                if nxt_edge:
                    hist.append(nxt_edge)
                prev_vs = vs
            total[mode][0] += ok; total[mode][1] += n
            print(f"### mode={mode}: {ok}/{n} = {ok / max(n, 1):.2f}")
            print("\n".join(rows))
    for mode in modes:
        o, n = total[mode]
        print(f"\n== TOTAL {mode}: {o}/{n} = {o / max(n, 1):.3f}  (gate: >= 0.85)")


if __name__ == "__main__":
    main()
