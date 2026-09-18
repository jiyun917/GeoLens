"""Offline check of narrowed goal-state trigger rules (user directive 2026-09-18, item 2).

Anchors come from an iteration-4 routing dry-run JSON (per rep: the pick and the
session's last confirmed node, replayed from the run's own sequence). The vision
output is recomputed per screenshot (cached). For every step where the CURRENT rule
(terminal node anchored + screen ≈ terminal node within GOAL_STATE_MARGIN) fires or
would fire, three general variants are evaluated — none uses step numbers or node ids:

  A  terminal anchor AND vision reports no open dialog (front-most window is the main
     window: current_dialog == first window title and no second window title)
  B  A AND at least one of the terminal node's completion keywords/elements that no
     predecessor node carries appears literally (normalised substring) in the vision text
  C  terminal anchor AND the literal completion evidence of B (dialog state ignored)

Reports, per step and rep, which variants fire; the acceptance criterion is: fires at
survey s3 and attribute s7, not at attribute s5/s6; 3d_viz s3 reported alongside.

Run from the WORKTREE (iteration-4 code) after the benches:
  python scripts/goal_state_rule_offline.py --run data/eval/results/routing_dryrun_v3_iter4b_x5.json
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--live-root", default="../GeoLens-paper")
    ap.add_argument("--vision-cache", default="data/eval/results/goal_state_rule_vision_v3fv.json")
    ap.add_argument("--out", default="data/eval/results/goal_state_rule_offline_iter4.md")
    args = ap.parse_args()
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    os.environ.setdefault("CHROMADB_PATH", str(Path(args.live_root).resolve() / "data" / "chromadb_v4"))
    os.environ["VISION_PROMPT_VERSION"] = "v3"
    os.environ["AUX_THINKING_BUDGET"] = "0"
    from api.services import guide_pipeline as gp
    from api.services import node_matcher
    from api.services.workflow_graph import get_workflow_graph

    graph = get_workflow_graph()
    pipe = gp.GuideRAGPipeline()
    run = json.load(open(args.run, encoding="utf-8"))
    cache = json.load(open(args.vision_cache, encoding="utf-8")) if os.path.exists(args.vision_cache) else {}

    def vision_for(sid, si):
        key = f"{sid}/{si}"
        if key not in cache:
            scen = json.load(open(f"data/eval/scenarios/{sid}.json", encoding="utf-8"))
            b64 = base64.b64encode(open(scen["steps"][si]["screenshot_path"], "rb").read()).decode()
            gp.reset_visual_state_cache()
            cache[key] = pipe.recognize_visual_state(b64)
            json.dump(cache, open(args.vision_cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return cache[key]

    def no_open_dialog(vs):
        wins = node_matcher._lst(vs, "window_titles")
        cur = str(vs.get("current_dialog") or "")
        # main-window state: a single window title, and the front-most dialog is that window
        return len(wins) <= 1 and (not wins or gp._norm_text(cur) == gp._norm_text(wins[0]))

    def completion_evidence(node, vs):
        wf = node.get("workflow_id")
        preds = [n for n in graph.get_workflow_nodes(wf) if n.get("step_number", 0) < node.get("step_number", 0)]
        def kws(n):
            sig = n.get("visual_signature") or {}
            return [str(k) for k in (sig.get("screenshot_keywords") or [])] + [str(e).replace("_", " ") for e in (sig.get("expected_ui_elements") or [])]
        pred_norm = {gp._norm_text(k) for p in preds for k in kws(p)}
        own = [k for k in kws(node) if gp._norm_text(k) and gp._norm_text(k) not in pred_norm]
        text_n = gp._norm_text(node_matcher.visual_state_text(vs))
        hits = [k for k in own if len(gp._norm_text(k)) >= 6 and gp._norm_text(k) in text_n]
        return hits

    lines = ["# Narrowed goal-state trigger — offline check on " + os.path.basename(args.run), "",
             "Current rule = terminal anchor (last confirmed node, or the pick if it is that node's successor) AND screen ≈ terminal node (top-1 or within GOAL_STATE_MARGIN). "
             "Variants: A = + no open dialog (single window title, front-most == main window); B = A + literal completion evidence (a terminal-node keyword/element absent from all predecessors, ≥6 chars normalised, found in the vision text); C = terminal anchor + literal evidence only.", "",
             "| rep | scenario | step | anchor(s) | current rule fired (node) | no-open-dialog | evidence hits | A | B | C |", "|---|---|---|---|---|---|---|---|---|---|"]
    summary = {}
    for rep_rows in run["reps"]:
        last = None
        for r in rep_rows:
            sid, si, picked = r["scenario"], r["step"], r["picked"]
            anchors = []
            if last and graph.get_node(last):
                anchors.append(last)
                if picked and picked != last and picked in {n["id"] for n in graph.get_next_steps(last)}:
                    anchors.append(picked)
            term_anchor = None
            for a in anchors:
                wf = graph.get_node(a).get("workflow_id")
                if a in {t["id"] for t in pipe._terminal_nodes(wf)}:
                    term_anchor = a
                    break
            fired = r.get("goal_state_node")
            if term_anchor or fired:
                vs = vision_for(sid, si)
                node = graph.get_node(fired or term_anchor)
                nod = no_open_dialog(vs)
                hits = completion_evidence(node, vs) if node else []
                A = bool(term_anchor) and nod
                C = bool(term_anchor) and bool(hits)
                B = A and bool(hits)
                key = (sid.replace("opendtect__", ""), si)
                summary.setdefault(key, []).append((bool(fired), A, B, C))
                lines.append(f"| {r['rep']} | {key[0]} | {si} | {', '.join(anchors) or '—'} | {'✓ ' + fired if fired else '✗'} | {'✓' if nod else '✗'} | {hits[:3]} | {'✓' if A else '✗'} | {'✓' if B else '✗'} | {'✓' if C else '✗'} |")
            if picked and not r.get("fallback"):
                last = picked
    lines += ["", "## Per-step firing counts over reps (current / A / B / C)", "", "| scenario | step | current | A | B | C |", "|---|---|---|---|---|---|"]
    for key in sorted(summary):
        v = summary[key]
        lines.append(f"| {key[0]} | {key[1]} | {sum(x[0] for x in v)}/{len(v)} | {sum(x[1] for x in v)}/{len(v)} | {sum(x[2] for x in v)}/{len(v)} | {sum(x[3] for x in v)}/{len(v)} |")
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("written:", args.out)


if __name__ == "__main__":
    main()
