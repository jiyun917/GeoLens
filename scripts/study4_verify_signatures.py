# -*- coding: utf-8 -*-
"""Study 4 - KB signature verification against the captured screens (pre-registered procedure, run AFTER capture
and BEFORE any model run; uses the Flash vision output of the screenshots ONLY - no generator, no GT labels).
For every scenario step with an expected_workflow_node, compares the node's visual signature with what the
vision read on that screen:
  dialog  : expected_dialog (first alternative before '/') contained in the window titles?
  keywords: each screenshot_keyword literally on screen (normalised substring / truncated-label prefix)?
Prints a per-node table and a list of proposed STRING corrections (dialog title / keyword spelling / dataset
names). Node and edge structure are never changed by this tool; corrections are applied by the owner in the
workflow JSON and logged. Then the deterministic routing replay (scripts/study4_route_replay.py, teacher-forced
on the GT chain with NO rerank) can be re-run to check routing evidence coverage.
Usage: .venv/Scripts/python.exe scripts/study4_verify_signatures.py --scenarios data/eval/study4/scenarios_draft
       [--vs data/eval/study4/visual_states] [--workflows data/workflows]
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("CHROMADB_PATH", "./data/chromadb_v4"); os.environ.setdefault("EMBED_MODEL", "BAAI/bge-m3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", required=True); ap.add_argument("--vs", default="data/eval/study4/visual_states")
    ap.add_argument("--workflows", default="data/workflows")
    args = ap.parse_args()
    from api.services import guide_pipeline as gp
    from api.services.node_matcher import _lst
    nodes = {}
    for f in glob.glob(str(ROOT / args.workflows / "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        for n in d.get("nodes", []):
            nodes[n["id"]] = n
    total = {"dialog_ok": 0, "dialog_bad": 0, "kw_ok": 0, "kw_bad": 0}
    proposals = []
    for f in sorted(glob.glob(str(ROOT / args.scenarios / "*.json"))):
        sc = json.load(open(f, encoding="utf-8")); sid = sc["scenario_id"]
        print(f"\n## {sid}")
        for st in sc["steps"]:
            nid = st.get("expected_workflow_node"); n = nodes.get(nid)
            p = ROOT / args.vs / sid / f"step_{st['step_index']}.json"
            if not n or not p.exists():
                print(f"  s{st['step_index']}: {'node missing' if not n else 'no vision output'} ({nid})"); continue
            vs = json.load(open(p, encoding="utf-8")).get("visual_state") or {}
            titles = gp._title_text(vs); screen = gp._screen_text(vs); trunc = gp._truncated_labels(vs)
            sig = n.get("visual_signature") or {}
            dlg_raw = (sig.get("expected_dialog") or "").split("/")[0].strip(); dlg = gp._norm_text(dlg_raw)
            dlg_ok = bool(dlg) and (dlg in titles or len(dlg) < 6)
            actual_title = (vs.get("current_dialog") or "") + " | " + ", ".join(_lst(vs, "window_titles")[:2])
            kws = [str(k) for k in (sig.get("screenshot_keywords") or [])]
            missing = []
            for k in kws:
                t = gp._norm_text(k)
                if not t:
                    continue
                if t in screen or any(t.startswith(x) for x in trunc):
                    total["kw_ok"] += 1
                else:
                    total["kw_bad"] += 1; missing.append(k)
            total["dialog_ok" if dlg_ok else "dialog_bad"] += 1
            flag = "" if (dlg_ok and not missing) else "  <-- check"
            print(f"  s{st['step_index']} {nid.split('_')[-3:]}: dialog {'ok ' if dlg_ok else 'BAD'} [{dlg_raw[:38]!r} vs {actual_title[:60]!r}] | keywords {len(kws) - len(missing)}/{len(kws)} on screen{flag}")
            if missing:
                print(f"       not on screen: {missing}")
            if not dlg_ok and dlg_raw:
                proposals.append((nid, "expected_dialog", dlg_raw, (vs.get("current_dialog") or "").strip()))
            for k in missing:
                # nearest on-screen string (shared 6-char prefix) as a spelling/dataset-name proposal
                cand = [s for key in ("labels", "buttons", "field_values", "visible_elements", "window_titles") for s in _lst(vs, key)]
                near = [s for s in cand if gp._norm_text(k)[:6] and gp._norm_text(k)[:6] in gp._norm_text(s)]
                if near:
                    proposals.append((nid, "keyword", k, near[0][:60]))
    print("\n== totals:", total)
    print("\n== proposed STRING corrections (owner decides; structure untouched):")
    for nid, kind, old, new in proposals:
        print(f"  {nid}: {kind} {old!r} -> {new!r}")


if __name__ == "__main__":
    main()
