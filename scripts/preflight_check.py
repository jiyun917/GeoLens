# -*- coding: utf-8 -*-
"""Pre-run integrity check (added after deviation V3-32, 2026-09-21). A confirmatory run must not
start unless this passes. It catches configuration/data omissions that no dev-set verification can
see, e.g. a workflow in the pool without linked_chunks (the study-2 defect).

Checks (all read-only):
  W1 every workflow JSON in data/workflows/ (the routing pool) has >= 1 linked_chunks on every node
  W2 every linked chunk id resolves in the configured CHROMADB_PATH collection of the manual it
     belongs to (OpendTect / QGIS by workflow), and the section-provenance field is present
  W3 every edge source/target exists; every node has a visual_signature with expected_dialog
  S1 every scenario in --scenarios: screenshot files exist, manual collection non-empty,
     expected_workflow_node (if set) exists in the pool, patterns compile, no placeholder GT
     ("_FILL_", "[TODO]"), visible_elements non-empty
  E1 pinned knobs (if --expect KEY=VAL given) match the environment
  G1 git tree clean for api/ scripts/ data/workflows/ data/eval/scenarios/
Exit code 0 = PASS, 1 = FAIL (with the list of failures).

Usage: .venv/Scripts/python.exe scripts/preflight_check.py --scenarios data/eval/scenarios/.study2_test \
           --expect CONTEXT_ASSEMBLY=v7 ROUTER_SESSION_STICKY=1 GEOLENS_SCORER=v4
"""
from __future__ import annotations
import argparse, fnmatch, glob, json, os, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT); sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
OPENDTECT = "645b7cdf2690408da843b9ce63c52d5b"; QGIS = "bf2804feea57434bb79b749134ed1df0"


def manual_for(wf_id: str, wf: dict) -> str:
    if wf.get("manual_id"):
        return wf["manual_id"]
    return QGIS if ("qgis" in wf_id or wf_id.startswith("auto_" + QGIS)) else OPENDTECT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default=None, help="scenario directory to check (default: skip S1)")
    ap.add_argument("--expect", nargs="*", default=[], help="KEY=VAL pins that must match os.environ")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--pool", default="data/workflows", help="routing pool directory (study 5: a staging pool while another run holds data/workflows)")
    ap.add_argument("--distractor", nargs="*", default=["auto_*"],
                    help="workflow-id globs that are frozen distractors (dangling links tolerated, reported as notes); default auto_* = the QGIS auto-generated workflow left untouched since v3 (V3-9)")
    args = ap.parse_args()
    fails, notes = [], []
    from api.services import vectorstore
    # ── workflows ──
    pool = {}
    for f in sorted(glob.glob(os.path.join(args.pool, "*.json"))):
        wf = json.load(open(f, encoding="utf-8")); wid = wf.get("workflow_id") or Path(f).stem
        pool[wid] = wf
        ids = {n["id"] for n in wf.get("nodes", [])}
        distractor = any(fnmatch.fnmatch(wid, g) for g in args.distractor)
        sink = notes if distractor else fails
        mid = manual_for(wid, wf)
        col = vectorstore.get_collection(mid)
        if not col or col.count() == 0:
            fails.append(f"W2 {wid}: manual collection {mid} empty/missing in {vectorstore.CHROMA_DIR}"); continue
        for n in wf.get("nodes", []):
            lc = n.get("linked_chunks") or []
            if not lc:
                sink.append(f"W1 {wid}/{n['id']}: no linked_chunks"); continue
            got = vectorstore.get_chunks_by_ids(mid, lc)
            ok = sum(1 for d in got.get("documents", []) if d)
            if ok < len(lc):
                sink.append(f"W2 {wid}/{n['id']}: {ok}/{len(lc)} linked chunk ids resolve" + (" (distractor, tolerated)" if distractor else ""))
            if not n.get("manual_sections") and not distractor:
                notes.append(f"W2 {wid}/{n['id']}: no manual_sections provenance")
            if not ((n.get("visual_signature") or {}).get("expected_dialog")):
                sink.append(f"W3 {wid}/{n['id']}: no expected_dialog" + (" (distractor, tolerated)" if distractor else ""))
        for e in wf.get("edges", []):
            s_, t_ = e.get("source") or e.get("from"), e.get("target") or e.get("to")
            if s_ not in ids or t_ not in ids:
                fails.append(f"W3 {wid}: edge {s_} -> {t_} references a missing node")
    notes.append(f"pool: {len(pool)} workflows: {', '.join(sorted(pool))}")
    all_nodes = {n["id"] for wf in pool.values() for n in wf.get("nodes", [])}
    # ── scenarios ──
    if args.scenarios:
        files = sorted(glob.glob(os.path.join(args.scenarios, "*.json")))
        if not files:
            fails.append(f"S1 no scenarios in {args.scenarios}")
        for f in files:
            sc = json.load(open(f, encoding="utf-8")); sid = sc.get("scenario_id", Path(f).stem)
            col = vectorstore.get_collection(sc.get("manual_id", ""))
            if not col or col.count() == 0:
                fails.append(f"S1 {sid}: manual collection {sc.get('manual_id')} empty/missing")
            raw = open(f, encoding="utf-8").read()
            for ph in ("_FILL_", "[TODO"):
                if ph in raw:
                    fails.append(f"S1 {sid}: placeholder {ph!r} present")
            for st in sc.get("steps", []):
                i = st.get("step_index")
                if not os.path.exists(st.get("screenshot_path", "")):
                    fails.append(f"S1 {sid} s{i}: screenshot missing {st.get('screenshot_path')}")
                e = st.get("expected_workflow_node")
                if e and e not in all_nodes:
                    fails.append(f"S1 {sid} s{i}: expected_workflow_node {e} not in pool")
                for pat in [st.get("expected_action_text_pattern")] + [a.get("pattern") for a in st.get("allowed_alternatives") or []]:
                    if pat:
                        try:
                            re.compile(pat)
                        except re.error as ex:
                            fails.append(f"S1 {sid} s{i}: bad regex {pat!r}: {ex}")
                if not ((st.get("visual_state_gt") or {}).get("visible_elements")):
                    fails.append(f"S1 {sid} s{i}: visible_elements empty")
            notes.append(f"scenario {sid}: {len(sc.get('steps', []))} steps")
    # ── env pins ──
    for kv in args.expect:
        k, _, v = kv.partition("=")
        if os.environ.get(k) != v:
            fails.append(f"E1 {k}={os.environ.get(k)!r}, expected {v!r}")
    # ── git ──
    dirty = subprocess.run(["git", "status", "--short", "--", "api", "scripts", "data/workflows", "data/eval/scenarios"], capture_output=True, text=True).stdout.strip()
    if dirty and not args.allow_dirty:
        fails.append("G1 uncommitted changes in api/scripts/workflows/scenarios:\n" + dirty)
    for n in notes:
        print("  note:", n)
    if fails:
        print("PREFLIGHT FAIL"); [print("  -", x) for x in fails]; sys.exit(1)
    print("PREFLIGHT PASS"); sys.exit(0)


if __name__ == "__main__":
    main()
