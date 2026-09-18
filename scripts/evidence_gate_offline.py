"""Offline evaluation of the evidence-based routing gate (v3 iteration 2) on the
iteration-0 picks, BEFORE the gate goes into the bench (user directive).

For every full_system step of a dev-iteration result JSON (default: iteration 0,
14 routed picks = 11 correct + 3 wrong) it recomputes, on the dev screenshots only:
  vision v3 (verbatim window titles / dialog) → condition (i)
  the session's last confirmed node (from the run's own sequence) → condition (ii)
  bge-m3 embedding scores over the node pool → condition (iii) gap, swept over margins
and reports how many wrong picks the rule filters and how many correct picks it drops.

Runs from the worktree; data (screenshots, chromadb) come from --live-root.
    PATCHED WORKTREE> ../GeoLens-paper/.venv/Scripts/python.exe scripts/evidence_gate_offline.py \
        --run ../GeoLens-paper/data/eval/results/dev_iter0_v2mech_gemini_r0.json --live-root ../GeoLens-paper
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

SCEN_WF = {
    "opendtect__survey_setup__01": "survey_setup",
    "opendtect__3d_visualization__01": "d3_visualization",
    "opendtect__attribute_computation__01": "seismic_attribute",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--live-root", required=True, help="live repo root (screenshots, .env.local, chromadb_v4)")
    ap.add_argument("--out", default="data/eval/results/evidence_gate_offline_iter0.md")
    ap.add_argument("--vision-cache", default="data/eval/results/evidence_gate_offline_vision_v3.json")
    args = ap.parse_args()
    live = Path(args.live_root).resolve()
    from dotenv import load_dotenv
    load_dotenv(str(live / ".env.local"))
    os.environ.setdefault("CHROMADB_PATH", str(live / "data" / "chromadb_v4"))
    os.environ["VISION_PROMPT_VERSION"] = "v3"
    os.environ["AUX_THINKING_BUDGET"] = "0"

    from api.services.guide_pipeline import GuideRAGPipeline, _norm_text
    from api.services import node_matcher
    from api.services.workflow_graph import get_workflow_graph
    import base64

    graph = get_workflow_graph()
    pipe = GuideRAGPipeline()
    run = json.load(open(args.run, encoding="utf-8"))
    cache = json.load(open(args.vision_cache, encoding="utf-8")) if os.path.exists(args.vision_cache) else {}

    rows = []
    for scen in run["scenarios"]:
        sid = scen["scenario_id"]
        scen_json = json.load(open(live / "data" / "eval" / "scenarios" / f"{sid}.json", encoding="utf-8"))
        fs = scen["backends"].get("full_system", {})
        last_confirmed = None
        for ps in fs.get("per_step", []):
            si = ps["step_index"]
            step = scen_json["steps"][si]
            shot = live / step["screenshot_path"]
            key = f"{sid}/{si}"
            if key not in cache:
                b64 = base64.b64encode(open(shot, "rb").read()).decode()
                cache[key] = pipe.recognize_visual_state(b64)
                json.dump(cache, open(args.vision_cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            vs = cache[key]
            picked = ps.get("picked_node_id")
            exp_node = step.get("expected_workflow_node")
            exp_wf = SCEN_WF[sid]
            node = graph.get_node(picked) if picked else None
            correct = None
            if node:
                correct = (picked == exp_node) if exp_node else (node.get("workflow_id") == exp_wf)
            # (i)
            i_ok, matched = False, []
            if node:
                sig = node.get("visual_signature") or {}
                screen_n = _norm_text(" ".join([str(vs.get("current_dialog") or "")] + node_matcher._lst(vs, "window_titles")))
                parts = [p.strip() for p in re.split(r"/|\bor\b|\|", str(sig.get("expected_dialog") or "")) if len(_norm_text(p)) >= 4]
                matched = [p for p in parts if _norm_text(p) in screen_n]
                i_ok = bool(matched)
            # (ii)
            ii_ok = False
            if node and last_confirmed and graph.get_node(last_confirmed):
                ii_ok = picked == last_confirmed or picked in {n["id"] for n in graph.get_next_steps(last_confirmed)}
            # (iii) gaps: all-node pool and two-stage pool (top-2 workflows by goal + session wf)
            scored_all = sorted(node_matcher.score_nodes(vs, graph.get_all_nodes()), key=lambda p: -p[1])
            wf_scores = node_matcher.workflow_scores(scen_json["goal"], graph.list_workflows(), graph.get_all_nodes())
            sel = [w for w, _ in wf_scores[:2]]
            session_wf = graph.get_node(last_confirmed).get("workflow_id") if (last_confirmed and graph.get_node(last_confirmed)) else None
            if session_wf and session_wf not in sel:
                sel.append(session_wf)
            pool = [n for n in graph.get_all_nodes() if n.get("workflow_id") in sel]
            scored_pool = sorted(node_matcher.score_nodes(vs, pool), key=lambda p: -p[1])

            def gapinfo(scored):
                if not scored:
                    return None, 0.0
                top1 = scored[0][0]["id"]
                gap = scored[0][1] - (scored[1][1] if len(scored) > 1 else 0.0)
                return top1, gap
            t1_all, gap_all = gapinfo(scored_all)
            t1_pool, gap_pool = gapinfo(scored_pool)
            rows.append({"scenario": sid.replace("opendtect__", ""), "step": si, "picked": picked, "conf": ps.get("route_confidence"),
                         "fallback_in_run": ps.get("fallback_activated"), "correct": correct, "expected": exp_node or exp_wf,
                         "i": i_ok, "i_matched": matched[:1], "ii": ii_ok, "last_confirmed": last_confirmed,
                         "top1_all": t1_all, "gap_all": round(gap_all, 4), "top1_pool": t1_pool, "gap_pool": round(gap_pool, 4),
                         "wf_top": [(w, round(s, 3)) for w, s in wf_scores[:2]], "sel": sel,
                         "windows": node_matcher._lst(vs, "window_titles")[:3], "dialog": vs.get("current_dialog")})
            # the run's own session: confirmed = picked and passed the run's (confidence) gate
            if picked and not ps.get("fallback_activated"):
                last_confirmed = picked

    lines = ["# Evidence-gate offline evaluation — picks of " + os.path.basename(args.run), "",
             "Rule: confirm iff (i) expected_dialog ⊂ vision v3 window titles/dialog (normalised) OR (ii) pick == last confirmed node or its successor OR (iii) pick is embedding top-1 with gap ≥ margin; without a last confirmed node only (i)/(iii).",
             "Vision v3 recomputed offline on the dev screenshots (cache: " + args.vision_cache + "); (ii) uses the run's own confirmed sequence; (iii) reported for the all-node pool and for the two-stage pool (top-2 goal workflows + session workflow).", "",
             "| scenario | step | picked | conf | correct | (i) dialog | (ii) graph (last) | top-1 all / gap | top-1 pool / gap | windows (vision v3) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    picks = [r for r in rows if r["picked"] and r["correct"] is not None]
    for r in rows:
        lines.append(f"| {r['scenario']} | {r['step']} | {r['picked'] or '—'} | {r['conf']:.2f} | {'—' if r['correct'] is None else ('✓' if r['correct'] else '✗')} | "
                     f"{'✓ ' + str(r['i_matched']) if r['i'] else '✗'} | {'✓' if r['ii'] else '✗'} ({r['last_confirmed'] or '—'}) | "
                     f"{r['top1_all']} / {r['gap_all']:.3f} | {r['top1_pool']} / {r['gap_pool']:.3f} | {r['windows']} |")
    lines += ["", "## Margin sweep for (iii) — confirmed = (i) or (ii) or (iii); counts over the run's picks (routed AND gated ones)", "",
              "| pool | margin | wrong picks filtered | wrong picks confirmed | correct picks confirmed | correct picks dropped |", "|---|---|---|---|---|---|"]
    for pool_name, t1k, gk in (("all nodes", "top1_all", "gap_all"), ("two-stage", "top1_pool", "gap_pool")):
        for m in (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.08):
            wf = wc = cc = cd = 0
            for r in picks:
                iii = (r[t1k] == r["picked"]) and (r[gk] >= m)
                ok = r["i"] or r["ii"] or iii
                if r["correct"]:
                    cc += ok; cd += (not ok)
                else:
                    wc += ok; wf += (not ok)
            lines.append(f"| {pool_name} | {m:.2f} | {wf} | {wc} | {cc} | {cd} |")
    lines += ["", f"Picks evaluated: {len(picks)} (correct {sum(1 for r in picks if r['correct'])}, wrong {sum(1 for r in picks if not r['correct'])})."]
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("written:", args.out)


if __name__ == "__main__":
    main()
