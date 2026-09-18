"""Routing dry-run on the OpendTect development set (no generator call).

Runs the guide pipeline exactly as the bench's full_system backend does —
vision → localization → gates → context — with the same session semantics
(visited nodes, last confirmed node) but WITHOUT calling the generator, so
completed_steps is empty (the rerank sees no prior instructions). Reports, per
step, the candidate pool (with sources), the rerank raw answer, the pick, gate
reason, goal-state hint and the (optional) rerank prompt, and a summary of
correct routes. Used for (a) the iteration-1 attribute s0/s1 reconstruction
(--only attribute --steps 0 1 --knobs iter1 --dump-prompt) and (b) the
iteration-2 stability check (--reps 3).

QGIS is never loaded as a scenario (only the OpendTect scenario files).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

DEV = ["opendtect__survey_setup__01", "opendtect__3d_visualization__01", "opendtect__attribute_computation__01"]
SCEN_WF = {"opendtect__survey_setup__01": "survey_setup", "opendtect__3d_visualization__01": "d3_visualization",
           "opendtect__attribute_computation__01": "seismic_attribute"}
KNOBS = {
    "iter1": {"ROUTER_TWO_STAGE": "0", "ROUTER_EVIDENCE_GATE": "0", "GOAL_STATE_HINT": "0", "GEN_PROMPT_VERSION": "v2"},
    "iter2": {},   # module defaults of the iteration-2 code
}
COMMON = {"CHROMADB_PATH": "./data/chromadb_v4", "EMBED_MODEL": "BAAI/bge-m3", "RAG_KG_ENABLED": "0", "AUX_THINKING_BUDGET": "0",
          "ROUTER_MATCHER": "embedding", "ROUTER_POOL_K": "5", "ROUTER_GRAPH_PRIOR": "1", "VISION_PROMPT_VERSION": "v3",
          "RERANK_PROMPT_VERSION": "v3", "POST_COMPLETION_MODE": "soft", "CONFIDENCE_THRESHOLD": "0.7", "PARALLEL_RETRIEVAL": "1",
          "ROUTED_VECTOR_QUERY": "goal", "GRAPH_VECTOR_AUX": "0", "FALLBACK_CTX_CHARS": "3900"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--knobs", default="iter2", choices=sorted(KNOBS))
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--only", default=None, help="substring of a dev scenario id")
    ap.add_argument("--steps", nargs="*", type=int, default=None)
    ap.add_argument("--dump-prompt", action="store_true")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--env", nargs="*", default=[])
    args = ap.parse_args()
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    for k, v in {**COMMON, **KNOBS[args.knobs]}.items():
        os.environ[k] = v
    for kv in args.env:
        k, _, v = kv.partition("=")
        os.environ[k] = v
    tag = args.tag or f"routing_dryrun_v3_{args.knobs}"

    from api.services.rag_router import get_rag_router
    from api.services.guide_pipeline import get_last_localize_meta, reset_last_localize_meta, reset_visual_state_cache, CONFIDENCE_THRESHOLD
    from api.services.workflow_graph import get_workflow_graph
    from api.services.bench_runner import code_version
    graph = get_workflow_graph()
    router = get_rag_router()
    sids = [s for s in DEV if (not args.only or args.only in s)]
    out = {"tag": tag, "knobs": {k: os.environ.get(k) for k in sorted(set(COMMON) | set(KNOBS["iter1"]))},
           "code_version": code_version(), "reps": []}
    lines = [f"# routing dry-run v3 — {tag}", "", f"code: {out['code_version'].get('commit')} dirty={out['code_version'].get('dirty')}; knobs: {json.dumps(out['knobs'])}", ""]
    for rep in range(args.reps):
        reset_visual_state_cache()   # every rep pays its own vision call
        rep_rows = []
        for sid in sids:
            scen = json.load(open(f"data/eval/scenarios/{sid}.json", encoding="utf-8"))
            visited, last_confirmed = [], None
            for step in scen["steps"]:
                si = step["step_index"]
                if args.steps is not None and si not in args.steps:
                    continue
                b64 = base64.b64encode(open(step["screenshot_path"], "rb").read()).decode()
                reset_last_localize_meta()
                t0 = time.time()
                res = router.route(user_message=scen["goal"], screenshot_b64=b64,
                                   session_state={"mode": "guide", "visited_node_ids": list(visited),
                                                  "last_confirmed_node_id": last_confirmed, "completed_steps": []},
                                   manual_ids=[scen["manual_id"]])
                dt = time.time() - t0
                meta = get_last_localize_meta()
                picked = meta.get("picked_node_id")
                exp_node = step.get("expected_workflow_node")
                node = graph.get_node(picked) if picked else None
                ok = (picked == exp_node) if exp_node else (bool(node) and node.get("workflow_id") == SCEN_WF[sid])
                if picked:
                    visited.append(picked)
                if picked and not meta.get("fallback_activated"):
                    last_confirmed = picked
                row = {"scenario": sid, "step": si, "rep": rep, "expected": exp_node or SCEN_WF[sid], "picked": picked,
                       "conf": meta.get("confidence"), "method": meta.get("match_method"), "fallback": meta.get("fallback_activated"),
                       "gate_reason": meta.get("gate_reason"), "route_ok": ok, "candidates": meta.get("candidates"),
                       "emb_top": meta.get("emb_top"), "evidence": meta.get("evidence"), "goal_state_node": meta.get("goal_state_node"),
                       "rerank_raw": meta.get("rerank_raw"), "sec": round(dt, 2),
                       "context_head": (res.get("context_block") or "")[:400]}
                if args.dump_prompt:
                    row["rerank_prompt"] = meta.get("rerank_prompt")
                rep_rows.append(row)
                print(f"[{rep}] {sid.replace('opendtect__', '')} s{si}: picked={picked} conf={row['conf']} gate={row['gate_reason'] or '-'} "
                      f"goal_state={row['goal_state_node']} ok={ok} ({dt:.1f}s)", flush=True)
        out["reps"].append(rep_rows)
        n_ok = sum(1 for r in rep_rows if r["route_ok"])
        n_fb = sum(1 for r in rep_rows if r["fallback"])
        lines.append(f"## rep {rep}: correct {n_ok}/{len(rep_rows)}; fallback {n_fb}; goal-state hints {sum(1 for r in rep_rows if r['goal_state_node'])}")
        lines.append("")
        lines.append("| scenario | step | expected | picked | conf | gate | goal_state | ok | candidates (source:score) | rerank raw |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in rep_rows:
            cands = "; ".join(f"{c['id'].split('_', 2)[-1]}[{','.join(c['sources'])}]" for c in (r["candidates"] or []))
            lines.append(f"| {r['scenario'].replace('opendtect__', '')} | {r['step']} | {r['expected']} | {r['picked'] or '—'} | {r['conf'] or 0:.2f} | "
                         f"{r['gate_reason'] or ''} | {r['goal_state_node'] or ''} | {'✓' if r['route_ok'] else '✗'} | {cands} | `{(r['rerank_raw'] or '')[:60]}` |")
        lines.append("")
        if args.dump_prompt:
            for r in rep_rows:
                lines.append(f"### rerank input — {r['scenario'].replace('opendtect__', '')} step {r['step']} (rep {r['rep']})")
                lines.append("")
                lines.append("```")
                lines.append((r.get("rerank_prompt") or "(no rerank call)")[:6000])
                lines.append("```")
                lines.append(f"rerank answer: `{r['rerank_raw']}` → picked {r['picked']} (expected {r['expected']}); evidence: {r['evidence']}")
                lines.append("")
    Path(f"data/eval/results/{tag}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(f"data/eval/results/{tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(l for l in lines if l.startswith("## rep")))
    print(f"written: data/eval/results/{tag}.md / .json")


if __name__ == "__main__":
    main()
