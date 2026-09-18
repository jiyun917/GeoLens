"""Diagnosis of the attribute s0/s1 misroutes (user request, v3 iteration 3).

Reports, for attribute_computation steps 0 and 1:
  1. vision v3 output (with field_values) — recomputed offline, verbatim;
  2. embedding scores of seismic_attribute nodes 02/03/04 (and the rest of the
     pool) under the signature BEFORE and AFTER the iteration-3 rewrite;
  3. whether the near-tie prior condition held (same expected_dialog group,
     score gap ≤ ROUTER_TIE_MARGIN) and what it would have preferred;
  4. the three-candidate portion of the rerank input (the node lines) as the
     rerank sees them;
  5. scoring impact: for iteration 0/1 records, the step match of full_system
     on s0/s1 next to the routed node, and the other backends' matches.
No scenario file, signature or pattern is modified.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

SID = "opendtect__attribute_computation__01"
NODES = ["seismic_attribute_02_open_attribute_tool", "seismic_attribute_03_select_type", "seismic_attribute_04_configure"]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-rev", default="820e993~1", help="git revision holding the pre-iteration-3 signatures")
    ap.add_argument("--live-root", default="../GeoLens-paper")
    ap.add_argument("--out", default="data/eval/results/diag_attribute_s0s1_iter3.md")
    args = ap.parse_args()
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    os.environ.setdefault("CHROMADB_PATH", str(Path(args.live_root).resolve() / "data" / "chromadb_v4"))
    os.environ["VISION_PROMPT_VERSION"] = "v3"
    os.environ["AUX_THINKING_BUDGET"] = "0"
    from api.services import node_matcher
    from api.services import guide_pipeline as gp
    from api.services.workflow_graph import get_workflow_graph

    graph = get_workflow_graph()
    pipe = gp.GuideRAGPipeline()
    scen = json.load(open(f"data/eval/scenarios/{SID}.json", encoding="utf-8"))
    before = json.loads(subprocess.run(["git", "show", f"{args.before_rev}:data/workflows/seismic_attribute.json"],
                                       capture_output=True, text=True, encoding="utf-8").stdout)
    before_nodes = {n["id"]: n for n in before["nodes"]}
    after_nodes = {n["id"]: graph.get_node(n["id"]) for n in before["nodes"]}

    lines = ["# attribute s0/s1 diagnosis — iteration 3 code (" + subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() + ")", ""]
    all_nodes = graph.get_all_nodes()
    for si in (0, 1):
        step = scen["steps"][si]
        b64 = base64.b64encode(open(step["screenshot_path"], "rb").read()).decode()
        gp.reset_visual_state_cache()
        vs = pipe.recognize_visual_state(b64)
        lines += [f"## step {si} (expected {step.get('expected_workflow_node')})", "",
                  "### 1. vision v3 output (verbatim)", "```", json.dumps({k: vs.get(k) for k in ("current_dialog", "window_titles", "buttons", "labels", "field_values", "current_action")}, ensure_ascii=False, indent=1), "```", ""]
        # 2. scores under before/after signatures
        def scores_with(sig_nodes):
            tmp = []
            for n in all_nodes:
                m = dict(n)
                if m["id"] in sig_nodes:
                    m["visual_signature"] = sig_nodes[m["id"]]["visual_signature"]
                tmp.append(m)
            node_matcher._NODE_EMB.clear(); node_matcher._NODE_TEXT.clear()
            sc = sorted(node_matcher.score_nodes(vs, tmp), key=lambda p: -p[1])
            return sc
        sc_before = scores_with(before_nodes)
        sc_after = scores_with({k: v for k, v in after_nodes.items()})
        lines += ["### 2. embedding scores (cosine, vision text ↔ node text) — pool rank in parentheses", "",
                  "| node | before (2026-08-07 signature) | after (iteration 3) |", "|---|---|---|"]
        for nid in NODES:
            rb = next((i + 1, s) for i, (n, s) in enumerate(sc_before) if n["id"] == nid)
            ra = next((i + 1, s) for i, (n, s) in enumerate(sc_after) if n["id"] == nid)
            lines.append(f"| {nid.split('_', 2)[-1]} | {rb[1]:.4f} (#{rb[0]}) | {ra[1]:.4f} (#{ra[0]}) |")
        lines.append("")
        lines.append("top-5 after: " + ", ".join(f"{n['id'].split('_', 2)[-1]}={s:.4f}" for n, s in sc_after[:5]))
        lines.append("top-5 before: " + ", ".join(f"{n['id'].split('_', 2)[-1]}={s:.4f}" for n, s in sc_before[:5]))
        # 3. tie-prior condition
        top5 = [(n["id"], s) for n, s in sc_after[:5]]
        groups = {}
        for nid, s in top5:
            n = graph.get_node(nid)
            key = gp._norm_text(((n.get("visual_signature") or {}).get("expected_dialog") or "").split("/")[0])
            groups.setdefault(key, []).append((nid.split("_", 2)[-1], round(s, 4)))
        lines += ["", "### 3. near-tie prior condition (ROUTER_TIE_MARGIN = %.3f)" % gp.ROUTER_TIE_MARGIN, "",
                  "expected_dialog groups within the top-5 pool: " + json.dumps(groups, ensure_ascii=False)]
        gp._LAST_LOCALIZE_META.clear()
        pref = pipe._tie_prior(top5, None if si == 0 else "seismic_attribute_02_open_attribute_tool")
        lines.append(f"tie prior result (last confirmed = {'none' if si == 0 else '02'}): {pref}")
        in_pool = [nid.split('_', 2)[-1] for nid, _ in top5 if nid in NODES]
        lines.append(f"02/03/04 present in the top-5 pool: {in_pool}")
        # 4. rerank candidate lines for the three nodes
        lines += ["", "### 4. rerank input — candidate lines of 02/03/04 (as rendered, iteration-3 prompt)", "```"]
        for nid in NODES:
            n = graph.get_node(nid); sig = n.get("visual_signature") or {}
            lines.append(f'id="{nid}" step={n.get("step_number")}\n   title: {n.get("title")}\n   desc: {(n.get("description") or "")[:120]}\n   expected dialog: {sig.get("expected_dialog")}\n   expected elements: {", ".join(str(e).replace("_", " ") for e in (sig.get("expected_ui_elements") or [])[:8])}\n   keywords: {", ".join(sig.get("screenshot_keywords") or [])[:160]}')
        lines.append("```")
    # 5. scoring impact from iteration 0/1 records
    lines += ["", "## 5. scoring impact of the s0/s1 route (iteration 0 and 1 records)", "",
              "| run | step | full_system routed to | fs matched | vanilla_vector | vanilla_budget | no_rag |", "|---|---|---|---|---|---|---|"]
    live = Path(args.live_root)
    for tag in ("dev_iter0_v2mech_gemini_r0", "dev_iter1_v3_gemini_r0"):
        run = json.load(open(live / "data/eval/results" / f"{tag}.json", encoding="utf-8"))
        sc = next(s for s in run["scenarios"] if s["scenario_id"] == SID)
        for si in (0, 1):
            def m(b):
                ps = sc["backends"][b]["per_step"][si]
                return ps
            fs = m("full_system")
            lines.append(f"| {tag} | {si} | {fs.get('picked_node_id')} ({fs.get('route_confidence')}) | {'✓' if fs.get('matched') else '✗'} | "
                         f"{'✓' if m('vanilla_vector').get('matched') else '✗'} | {'✓' if m('vanilla_budget').get('matched') else '✗'} | {'✓' if m('no_rag').get('matched') else '✗'} |")
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("written:", args.out)


if __name__ == "__main__":
    main()
