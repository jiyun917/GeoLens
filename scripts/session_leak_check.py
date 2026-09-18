"""Session-state leakage check (user item 1, 2026-09-18) — no API calls.

Replays the bench harness for one scenario with three stubs:
  vision  -> cached vision outputs (one per screenshot)
  rerank  -> the pick/confidence recorded in a bench JSON for (scenario, step)
  generator -> the response recorded in the same bench JSON for (backend, step)
and records, per backend and step, the context block handed to the generator and
the rerank prompt (routing input). Orders compared:
  (a) each backend alone (fresh process state)
  (b) bench order  no_rag -> vanilla_vector -> vanilla_budget -> full_system
  (c) full_system -> vanilla_vector
Differences in context blocks / rerank prompts between (a) and (b)/(c) mean session
state or telemetry crosses backends. Run from the worktree.
"""
from __future__ import annotations

import argparse
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
    ap.add_argument("--bench", default="data/eval/results/dev_iter4_v3_gemini_r0.json")
    ap.add_argument("--vision-cache", default="data/eval/results/evidence_gate_offline_vision_v3.json")
    ap.add_argument("--live-root", default="../GeoLens-paper")
    ap.add_argument("--out", default="data/eval/results/session_leak_check_iter4.md")
    args = ap.parse_args()
    os.environ.setdefault("CHROMADB_PATH", str(Path(args.live_root).resolve() / "data" / "chromadb_v4"))
    os.environ.setdefault("MANUAL_IMAGE_DIR", str(Path(args.live_root).resolve() / "data" / "manual_images"))
    for k, v in {"RAG_KG_ENABLED": "0", "ROUTER_MATCHER": "embedding", "VISION_PROMPT_VERSION": "v3", "RERANK_PROMPT_VERSION": "v4",
                 "PARALLEL_RETRIEVAL": "1", "FALLBACK_CTX_CHARS": "3900", "VANILLA_BUDGET_CHARS": "3900", "GEOLENS_SCORER": "v3",
                 "AUX_THINKING_BUDGET": "0", "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "stub")}.items():
        os.environ[k] = v
    import base64
    from api.services import guide_pipeline as gp
    from api.services import bench_backends as bb

    bench = json.load(open(args.bench, encoding="utf-8"))
    cache = json.load(open(args.vision_cache, encoding="utf-8"))
    scen_by_id = {s["scenario_id"]: s for s in bench["scenarios"]}
    sids = list(scen_by_id)
    scen_json = {sid: json.load(open(f"data/eval/scenarios/{sid}.json", encoding="utf-8")) for sid in sids}
    # screenshot bytes -> cache key
    shot_key = {}
    for sid in sids:
        for st in scen_json[sid]["steps"]:
            b64 = base64.b64encode(open(st["screenshot_path"], "rb").read()).decode()
            shot_key[b64] = f"{sid}/{st['step_index']}"

    # ── stubs ──
    pipe = gp.get_guide_pipeline()
    state = {"cur": None}   # (sid, step, backend) of the step being replayed

    def stub_vision(self, screenshot_b64):
        key = shot_key.get(screenshot_b64)
        gp.record_aux_usage("vision_cached", "gemini-2.5-flash", None)
        return dict(cache[key]) if key in cache else {}
    gp.GuideRAGPipeline.recognize_visual_state = stub_vision

    def stub_rerank_once(self, prompt):
        sid, si, b = state["cur"]
        ps = scen_by_id[sid]["backends"]["full_system"]["per_step"][si]
        pid = ps.get("picked_node_id")
        return (pid, float(ps.get("route_confidence") or 0.0)) if pid else (None, 0.0)
    gp.GuideRAGPipeline._rerank_once = stub_rerank_once

    def stub_generator(messages):
        sid, si, b = state["cur"]
        bb._reset_usage()
        return scen_by_id[sid]["backends"][b]["per_step"][si]["response"]
    bb._call_generator = stub_generator

    def run_backend(sid, b):
        """Replay one backend over the scenario's steps as the evaluator does; return per-step (context, rerank_prompt)."""
        fn = bb.BACKEND_REGISTRY[b]
        rows = []
        prior = []
        for st in scen_json[sid]["steps"]:
            si = st["step_index"]
            state["cur"] = (sid, si, b)
            gp.reset_last_localize_meta()
            gp.reset_aux_usage()
            resp = fn(si, scen_json[sid], prior)
            meta = gp.get_last_localize_meta()
            rows.append({"step": si, "context": bb.get_last_context_block(), "rerank_prompt": meta.get("rerank_prompt") if b == "full_system" else None,
                         "picked": meta.get("picked_node_id") if b == "full_system" else None, "goal_state": meta.get("goal_state_node") if b == "full_system" else None})
            prior.append(resp)
        return rows

    def fresh():
        bb._SESSION_VISITED.clear(); bb._SESSION_CONFIRMED.clear(); gp.reset_visual_state_cache(); gp.reset_last_localize_meta()

    lines = ["# Session-state leakage check — replay with stubs (no API), bench " + os.path.basename(args.bench), "",
             "| scenario | backend | order | steps with identical context vs alone | steps with identical rerank prompt vs alone | first differing step |", "|---|---|---|---|---|---|"]
    detail = []
    for sid in sids:
        alone = {}
        for b in ("no_rag", "vanilla_vector", "vanilla_budget", "full_system"):
            fresh(); alone[b] = run_backend(sid, b)
        orders = {"bench order (no_rag→vv→vb→fs)": ["no_rag", "vanilla_vector", "vanilla_budget", "full_system"],
                  "fs→vv": ["full_system", "vanilla_vector"], "vv→fs": ["vanilla_vector", "full_system"]}
        for oname, seq in orders.items():
            fresh()
            for b in seq:
                got = run_backend(sid, b)
                n = len(got)
                same_ctx = sum(1 for a, g in zip(alone[b], got) if a["context"] == g["context"])
                same_rr = sum(1 for a, g in zip(alone[b], got) if a["rerank_prompt"] == g["rerank_prompt"])
                first = next((g["step"] for a, g in zip(alone[b], got) if a["context"] != g["context"] or a["rerank_prompt"] != g["rerank_prompt"]), None)
                lines.append(f"| {sid.replace('opendtect__', '')} | {b} | {oname} | {same_ctx}/{n} | {same_rr}/{n} | {first if first is not None else '—'} |")
                for a, g in zip(alone[b], got):
                    if a["context"] != g["context"] or a["rerank_prompt"] != g["rerank_prompt"]:
                        detail.append((sid, b, oname, g["step"], a["context"][:300], g["context"][:300]))
    if detail:
        lines += ["", "## Differences (alone vs in-order), context head", ""]
        for sid, b, o, st, a, g in detail[:20]:
            lines += [f"### {sid} {b} [{o}] step {st}", "alone:", "```", a, "```", "in order:", "```", g, "```"]
    else:
        lines += ["", "No difference: context blocks and rerank prompts are identical whether a backend runs alone or after other backends."]
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:40]))
    print("written:", args.out)


if __name__ == "__main__":
    main()
