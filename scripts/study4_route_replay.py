# -*- coding: utf-8 -*-
"""Study 4 development: offline replay of routing rules on recorded sessions (no API calls).
Data: cached vision outputs (data/eval/study4/visual_states/), workflow graph (data/workflows/),
scenario GT nodes (expected_workflow_node), and the full_system routing telemetry of earlier runs
(the Flash rerank's pick per step and the session's previous pick). Generator responses are not read.
Modes: teacher-forced (rule applied to the recorded pick with the recorded previous pick) and chained
(previous pick = the rule's own previous output; the rerank pick stays the recorded one - approximation).
Usage: .venv/Scripts/python.exe scripts/study4_route_replay.py [--hops 3] [--min-tokens 1] [--files glob,...]
"""
from __future__ import annotations
import argparse, collections, glob, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("CHROMADB_PATH", "./data/chromadb_v4"); os.environ.setdefault("EMBED_MODEL", "BAAI/bge-m3")
SCEN_DIRS = ["data/eval/scenarios/.dev_opendtect", "data/eval/scenarios/.study2_test",
             "data/eval/scenarios/.study3_test_opendtect", "data/eval/scenarios/.study3_test_qgis"]
EXTRA = ["data/eval/scenarios/qgis__vector_buffer__01.json"]
RESULT_GLOBS = ["data/eval/results/run_*_study2_r*_*.json", "data/eval/results/run_*_study3_opendtect_r*_*.json",
                "data/eval/results/run_*_study3_qgis_r*_*.json", "data/eval/results/dev_iter4_v3_*_r0.json",
                "data/eval/results/run_*_v3_qgis_r*_*.json"]


def load_scenarios():
    out = {}
    for d in SCEN_DIRS:
        for f in glob.glob(str(ROOT / d / "*.json")):
            sc = json.load(open(f, encoding="utf-8")); out[sc["scenario_id"]] = sc
    for f in EXTRA:
        if (ROOT / f).exists():
            sc = json.load(open(ROOT / f, encoding="utf-8")); out.setdefault(sc["scenario_id"], sc)
    return out


def load_vs(sid, i):
    p = ROOT / "data/eval/study4/visual_states" / sid / f"step_{i}.json"
    if not p.exists():
        return None
    return json.load(open(p, encoding="utf-8")).get("visual_state") or None


def step_no(graph, nid):
    n = graph.get_node(nid) if nid else None
    try:
        return int(n.get("step_number")) if n else None
    except (TypeError, ValueError):
        return None


def rel(graph, pick, exp):
    if not exp: return "n/a"
    if pick == exp: return "ok"
    pn, en = graph.get_node(pick) if pick else None, graph.get_node(exp)
    if not pn: return "none"
    if not en or pn.get("workflow_id") != en.get("workflow_id"): return "other_wf"
    a, b = step_no(graph, pick), step_no(graph, exp)
    if a is None or b is None: return "other"
    return "behind" if a < b else "ahead"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hops", type=int, default=3); ap.add_argument("--min-tokens", type=int, default=1)
    ap.add_argument("--files", default=",".join(RESULT_GLOBS)); ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    from api.services.workflow_graph import get_workflow_graph
    from api.services.guide_pipeline import screen_delta_advance
    graph = get_workflow_graph(); scen = load_scenarios()
    files = []
    for g in args.files.split(","):
        files += sorted(glob.glob(str(ROOT / g)))
    stats = collections.defaultdict(collections.Counter); moves = collections.Counter(); examples = []
    for f in files:
        d = json.load(open(f, encoding="utf-8")); model = os.path.basename(f).split("_")[1]
        for sc in d["scenarios"]:
            sid = sc["scenario_id"]; S = scen.get(sid)
            if not S or "full_system" not in sc["backends"]:
                continue
            steps = sc["backends"]["full_system"]["per_step"]
            rec_last = None; chain_last = None
            for s in steps:
                i = s["step_index"]; exp = S["steps"][i].get("expected_workflow_node"); pick = s.get("picked_node_id")
                vs, pvs = load_vs(sid, i), (load_vs(sid, i - 1) if i > 0 else None)
                if vs is None:
                    stats[sid]["no_vs"] += 1; continue
                # teacher-forced
                tf, meta = screen_delta_advance(graph, pick, rec_last, vs, pvs, args.hops, args.min_tokens)
                # chained
                ch, meta_c = screen_delta_advance(graph, pick, chain_last, vs, pvs, args.hops, args.min_tokens)
                for label, out in (("base", pick), ("tf", tf), ("chain", ch)):
                    stats[sid][f"{label}_{rel(graph, out, exp)}"] += 1
                if meta:
                    moves[(rel(graph, pick, exp), rel(graph, tf, exp))] += 1
                    if args.verbose or rel(graph, tf, exp) in ("ahead", "other_wf") and len(examples) < 40:
                        examples.append(f"{model} {sid} s{i}: {rel(graph, pick, exp)}->{rel(graph, tf, exp)} pick={str(pick)[-28:]} exp={str(exp)[-28:]} to={meta['to'][-28:]} ev={meta['evidence']}")
                rec_last = pick or rec_last
                chain_last = ch or chain_last
    tot = collections.Counter()
    print(f"{'scenario':<34} {'n':>4} | base ok  behind ahead | tf ok  behind ahead | chain ok  behind ahead")
    for sid in sorted(stats):
        c = stats[sid]; n = sum(v for k, v in c.items() if k.startswith("base_"))
        tot.update(c)
        print(f"{sid[:34]:<34} {n:>4} | {c['base_ok']:>7} {c['base_behind']:>6} {c['base_ahead']:>5} | {c['tf_ok']:>5} {c['tf_behind']:>6} {c['tf_ahead']:>5} | {c['chain_ok']:>8} {c['chain_behind']:>6} {c['chain_ahead']:>5}")
    n = sum(v for k, v in tot.items() if k.startswith("base_"))
    print(f"{'TOTAL':<34} {n:>4} | {tot['base_ok']:>7} {tot['base_behind']:>6} {tot['base_ahead']:>5} | {tot['tf_ok']:>5} {tot['tf_behind']:>6} {tot['tf_ahead']:>5} | {tot['chain_ok']:>8} {tot['chain_behind']:>6} {tot['chain_ahead']:>5}")
    print("\nrule fired (teacher-forced): from -> to counts:", dict(moves))
    print("\nexamples of harmful moves (-> ahead / other_wf):"); [print("  ", e) for e in examples]


if __name__ == "__main__" and "--diag" not in sys.argv:
    main()


def diag(hops=3):
    """Residual lags after the rule (teacher-forced): per (scenario, step) where the majority outcome is still
    'behind', show the recorded last node, the GT node, the chain, and why the GT node had no evidence."""
    from api.services.workflow_graph import get_workflow_graph
    from api.services import guide_pipeline as gp
    graph = get_workflow_graph(); scen = load_scenarios()
    files = []
    for g in RESULT_GLOBS:
        files += sorted(glob.glob(str(ROOT / g)))
    residual = collections.defaultdict(collections.Counter); lasts = collections.defaultdict(collections.Counter)
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        for sc in d["scenarios"]:
            sid = sc["scenario_id"]; S = scen.get(sid)
            if not S or "full_system" not in sc["backends"]:
                continue
            rec_last = None
            for s in sc["backends"]["full_system"]["per_step"]:
                i = s["step_index"]; exp = S["steps"][i].get("expected_workflow_node"); pick = s.get("picked_node_id")
                vs, pvs = load_vs(sid, i), (load_vs(sid, i - 1) if i > 0 else None)
                if vs is not None:
                    tf, _ = gp.screen_delta_advance(graph, pick, rec_last, vs, pvs, hops, 1)
                    r = rel(graph, tf, exp); residual[(sid, i)][r] += 1
                    if r == "behind": lasts[(sid, i)][(rec_last or "-")[-30:] + " | pick " + (pick or "-")[-30:]] += 1
                rec_last = pick or rec_last
    for (sid, i), c in sorted(residual.items()):
        if c["behind"] < max(3, sum(c.values()) * 0.3):
            continue
        S = scen[sid]; exp = S["steps"][i].get("expected_workflow_node"); en = graph.get_node(exp) or {}
        vs, pvs = load_vs(sid, i), (load_vs(sid, i - 1) if i > 0 else None)
        now, before = gp._screen_text(vs), gp._screen_text(pvs)
        toks = gp._sig_tokens(en)
        print(f"\n## {sid} s{i}: outcomes {dict(c)} | GT {exp[-34:]} dialog={((en.get('visual_signature') or {}).get('expected_dialog') or '')[:40]!r}")
        for k, v in lasts[(sid, i)].most_common(3): print(f"   last/pick: {k} x{v}")
        print(f"   GT tokens now/before: " + ", ".join(f"{t}[{'N' if t in now else '-'}{'B' if before and t in before else '-'}]" for t in toks[:14]))
        print(f"   titles now: {gp._title_text(vs)[:90]!r}")


if __name__ == "__main__" and "--diag" in sys.argv:
    diag()
