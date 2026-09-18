"""v3 development-loop bench (OpendTect development set only).

One iteration = Gemini generator × {no_rag, vanilla_vector, vanilla_budget,
full_system} × the OpendTect scenarios × --reps replicates, followed by the
iteration report:

  primary evidence (user rule 2026-09-18 — step accuracy from 1–2 runs is
  within noise and is NOT the first criterion):
    (a) routing accuracy of full_system and the number of confident-wrong
        routes (confidence ≥ threshold, wrong node/workflow);
    (b) target-section retrieval hit per step (does the injected context
        contain the scenario's target manual section?) for full_system vs
        the vanilla baselines;
    (c) per-step loss classification where full_system lost to a vanilla
        baseline (misrouting / fallback_quality / context_or_generation),
        plus the steps every backend failed (response text + GT pattern).
  secondary: step accuracy vs vanilla_vector (untruncated) AND vanilla_budget
    (3,900 chars), total cost incl. aux, latency decomposed by stage; the
    latency goal is "minimise the extra latency over vanilla", not "faster".

The QGIS scenario is never loaded: the bench runs on a temporary scenario
directory that contains only OpendTect scenario files.

Usage (project root):
    .venv/Scripts/python.exe scripts/dev_iter.py --iter 1 [--profile v3|v2mech]
        [--reps 1] [--only survey_setup] [--note "reindex running"]
        [--backends ...] [--env KEY=VAL ...] [--analyze-only]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

SCEN_DIR = ROOT / "data" / "eval" / "scenarios"
DEV_DIR = SCEN_DIR / ".dev_opendtect"
RESULTS = ROOT / "data" / "eval" / "results"
DEV_SCENARIOS = [
    "opendtect__survey_setup__01.json",
    "opendtect__3d_visualization__01.json",
    "opendtect__attribute_computation__01.json",
]
# Scenario → workflow that a correct router must land in (step-level node GT
# is only present for attribute_computation; the other two carry no
# expected_workflow_node, so their routing is judged at workflow level).
SCEN_WF = {
    "opendtect__survey_setup__01": "survey_setup",
    "opendtect__3d_visualization__01": "d3_visualization",
    "opendtect__attribute_computation__01": "seismic_attribute",
}
# Target manual section(s) per scenario (from each scenario's manual_reference;
# same prefixes as scripts/retrieval_replay_v3.py). A context "hits" when any
# [Section: …] tag in it starts with one of these.
TARGET_SECTIONS = {
    "opendtect__survey_setup__01": ["1.2.2a"],
    "opendtect__3d_visualization__01": ["1.3.1a", "1.3.1 "],
    "opendtect__attribute_computation__01": ["1.5.1a"],
}
DEFAULT_BACKENDS = ["no_rag", "vanilla_vector", "vanilla_budget", "full_system"]
STAGES = ["vision", "vision_replayed", "embed", "clip", "rerank", "vector_search", "neighbor_fetch",
          "chunk_fetch", "kg_search", "generate", "localize", "goal_retrieval", "routed_retrieval"]
INCLUSIVE = {"localize", "goal_retrieval", "routed_retrieval"}

PROFILES: Dict[str, Dict[str, str]] = {
    "v2mech": {
        "ROUTER_MATCHER": "embedding",
        "ROUTER_POOL_K": "3",
        "ROUTER_GRAPH_PRIOR": "0",
        "VISION_PROMPT_VERSION": "v2",
        "RERANK_PROMPT_VERSION": "v2",
        "POST_COMPLETION_MODE": "override",
        "PARALLEL_RETRIEVAL": "0",
        "ROUTED_VECTOR_QUERY": "enriched",
        "GRAPH_VECTOR_AUX": "1",
        "RAG_KG_ENABLED": "1",
        "RAG_KG_POSITION": "last",
        "FALLBACK_CTX_CHARS": "1500",
        "VECTOR_CTX_CHARS": "1500",
        "GRAPH_CTX_CHARS": "800",
        "GRAPH_CTX_ITEMS": "3",
        "CONFIDENCE_THRESHOLD": "0.7",
        "GOAL_STATE_HINT": "0",
        "ROUTER_TWO_STAGE": "0",
        "ROUTER_EVIDENCE_GATE": "0",
        "GEN_PROMPT_VERSION": "v2",
    },
    "v3": {
        "ROUTER_MATCHER": "embedding",
        "ROUTER_POOL_K": "5",
        "ROUTER_GRAPH_PRIOR": "1",
        "VISION_PROMPT_VERSION": "v3",
        "RERANK_PROMPT_VERSION": "v4",
        "POST_COMPLETION_MODE": "soft",
        "PARALLEL_RETRIEVAL": "1",
        "ROUTED_VECTOR_QUERY": "goal",
        "GRAPH_VECTOR_AUX": "0",
        "RAG_KG_ENABLED": "0",
        "FALLBACK_CTX_CHARS": "3900",
        "VECTOR_CTX_CHARS": "1500",
        "GRAPH_CTX_CHARS": "800",
        "GRAPH_CTX_ITEMS": "3",
        "CONFIDENCE_THRESHOLD": "0.7",
        # iteration 2 (reduced scope, 2026-09-18): goal-state block ON; two-stage
        # routing ON HOLD; evidence gate only if the offline table meets the
        # user criterion (set ROUTER_EVIDENCE_GATE=1 via --env then); generator
        # naming rule not enabled.
        "GOAL_STATE_HINT": "1",
        "ROUTER_TWO_STAGE": "0",
        "ROUTER_EVIDENCE_GATE": "0",
        "GEN_PROMPT_VERSION": "v2",
    },
}
# Fixed for every profile (Task A / v3 evaluation settings).
COMMON_ENV = {
    "GEOLENS_SCORER": "v3",
    "EMBED_MODEL": "BAAI/bge-m3",
    "AUX_THINKING_BUDGET": "0",
    "GEMINI_THINKING_BUDGET": "1024",
    "GEN_TEMPERATURE": "0.2",
    "GEN_MAX_TOKENS": "1024",
    "VANILLA_BUDGET_CHARS": "3900",
    "BENCH_SAVE_CONTEXT": "1",
    "PYTHONIOENCODING": "utf-8",
}


def _scenario_files(only: Optional[str]) -> List[str]:
    files = DEV_SCENARIOS
    if only:
        files = [f for f in DEV_SCENARIOS if only in f]
        if not files:
            raise SystemExit(f"--only {only!r} matches no dev scenario")
    return files


def _prepare_dev_dir(files: List[str]) -> Path:
    if DEV_DIR.exists():
        shutil.rmtree(DEV_DIR)
    DEV_DIR.mkdir(parents=True)
    for name in files:
        shutil.copy2(SCEN_DIR / name, DEV_DIR / name)
    return DEV_DIR


def _bench_python() -> str:
    """Interpreter for the bench subprocess: BENCH_PYTHON env, else this repo's .venv,
    else the interpreter running this script (git worktrees have no .venv of their own)."""
    cand = os.environ.get("BENCH_PYTHON") or str(ROOT / ".venv" / "Scripts" / "python.exe")
    return cand if os.path.exists(cand) else sys.executable


def _run_bench(out_path: Path, backends: List[str], env: Dict[str, str], model: str) -> int:
    cmd = [_bench_python(), "-u", "-m", "api.services.bench_runner",
           "--model", model, "--backends", *backends,
           "--scenarios", str(DEV_DIR), "--out", str(out_path)]
    log_path = out_path.with_suffix(".log")
    print(f"[dev_iter] running: {' '.join(cmd)}\n[dev_iter] log: {log_path}", flush=True)
    with open(log_path, "w", encoding="utf-8") as lf:
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, stdout=lf, stderr=subprocess.STDOUT)
    return proc.returncode


# ───────────────────────────── analysis ─────────────────────────────

def _load_graph():
    from api.services.workflow_graph import WorkflowGraph
    return WorkflowGraph(str(ROOT / "data" / "workflows"))


def _wf_of(graph, node_id: Optional[str]) -> Optional[str]:
    if not node_id:
        return None
    n = graph.get_node(node_id)
    return n.get("workflow_id") if n else None


def _mean(xs: List[float]) -> float:
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else float("nan")


_SEC_RE = re.compile(r"Section: ([^\],\n]+)")


def _ctx_sections(block: Optional[str]) -> List[str]:
    return [m.strip() for m in _SEC_RE.findall(block or "")]


def _target_hit(block: Optional[str], sid: str) -> Optional[bool]:
    if block is None:
        return None
    secs = _ctx_sections(block)
    return any(s.startswith(t) for s in secs for t in TARGET_SECTIONS.get(sid, []))


def _y(v) -> str:
    return "—" if v is None else ("✓" if v else "✗")


def analyze(run_files: List[Path], out_md: Path, backends: List[str], threshold: float,
            note: str = "", scen_files: Optional[List[str]] = None) -> Dict:
    graph = _load_graph()
    scen_gt: Dict[str, Dict] = {}
    for name in (scen_files or DEV_SCENARIOS):
        d = json.load(open(SCEN_DIR / name, encoding="utf-8"))
        scen_gt[d["scenario_id"]] = d

    runs = [json.load(open(p, encoding="utf-8")) for p in run_files]
    n_rep = len(runs)

    acc: Dict[str, Dict[str, List[float]]] = {b: {} for b in backends}
    cost: Dict[str, List[float]] = {b: [] for b in backends}
    lat: Dict[str, List[float]] = {b: [] for b in backends}
    lat_wall: Dict[str, List[float]] = {b: [] for b in backends}
    hall: Dict[str, List[float]] = {b: [] for b in backends}
    ctx_chars: Dict[str, List[int]] = {b: [] for b in backends}
    aux_cost: Dict[str, List[float]] = {b: [] for b in backends}
    gen_cost: Dict[str, List[float]] = {b: [] for b in backends}
    stage_acc: Dict[str, Dict[str, List[float]]] = {b: {} for b in backends}
    steps: Dict[tuple, Dict[str, List[Dict]]] = {}
    for run in runs:
        for scen in run.get("scenarios", []):
            sid = scen["scenario_id"]
            if sid not in scen_gt:
                continue
            for b in backends:
                m = (scen.get("backends") or {}).get(b)
                if not m or "error" in m:
                    continue
                acc[b].setdefault(sid, []).append(float(m.get("step_accuracy") or 0.0))
                for ps in m.get("per_step", []):
                    key = (sid, ps["step_index"])
                    steps.setdefault(key, {}).setdefault(b, []).append(ps)
                    cost[b].append(float(ps.get("cost_total_usd") or 0.0))
                    gen_cost[b].append(float(ps.get("cost_usd") or 0.0))
                    aux_cost[b].append(float(ps.get("aux_cost_usd") or 0.0))
                    lat[b].append(float(ps.get("latency_sec") or 0.0))
                    lat_wall[b].append(float(ps.get("latency_wall_sec", ps.get("latency_sec")) or 0.0))
                    hall[b].append(1.0 if ps.get("hallucinated") else 0.0)
                    ctx_chars[b].append(int(ps.get("context_chars") or 0))
                    for st, v in (ps.get("stage_latency") or {}).items():
                        stage_acc[b].setdefault(st, []).append(float(v.get("sec", 0.0)))

    n_steps_total = {b: sum(len(v.get(b, [])) for v in steps.values()) for b in backends}
    lines: List[str] = []
    lines.append(f"# dev iteration report — {out_md.stem}")
    lines.append("")
    lines.append(f"Runs: {', '.join(p.name for p in run_files)} (n_rep={n_rep}); scorer v3; dev set = {', '.join(scen_gt)} ({sum(len(s['steps']) for s in scen_gt.values())} steps).")
    if note:
        lines.append(f"**Note: {note}**")
    lines.append("")
    lines.append("Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.")

    # ── summary table ──
    lines.append("")
    lines.append("## Backend summary (per-step means over scenarios × reps)")
    lines.append("")
    lines.append("| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    summary: Dict[str, Dict[str, float]] = {}
    hit_rate: Dict[str, float] = {}
    for b in backends:
        hits = [_target_hit(ps.get("context_block"), key[0]) for key in steps for ps in steps[key].get(b, [])]
        hits_known = [h for h in hits if h is not None]
        hit_rate[b] = (sum(1 for h in hits_known if h) / len(hits_known)) if hits_known else float("nan")
        scen_avg = _mean([_mean(v) for v in acc[b].values()])
        pooled = _mean([1.0 if ps.get("matched") else 0.0 for key in steps for ps in steps[key].get(b, [])])
        summary[b] = {
            "step_acc_scenario_avg": scen_avg, "step_acc_pooled": pooled,
            "hall_rate": _mean(hall[b]), "cost_total": _mean(cost[b]),
            "gen_cost": _mean(gen_cost[b]), "aux_cost": _mean(aux_cost[b]),
            "latency": _mean(lat[b]), "latency_wall": _mean(lat_wall[b]),
            "ctx_chars": _mean(ctx_chars[b]), "target_hit": hit_rate[b],
        }
        s = summary[b]
        lines.append(f"| {b} | {s['step_acc_scenario_avg']:.3f} | {s['step_acc_pooled']:.3f} | {s['hall_rate']:.3f} | "
                     f"{s['cost_total']:.5f} | {s['gen_cost']:.5f} | {s['aux_cost']:.5f} | {s['latency']:.2f} | {s['latency_wall']:.2f} | {s['ctx_chars']:.0f} | {s['target_hit']:.2f} |")
    lines.append("")
    lines.append("## Per-scenario step accuracy (mean over reps)")
    lines.append("")
    lines.append("| scenario | " + " | ".join(backends) + " |")
    lines.append("|---|" + "---|" * len(backends))
    for sid in scen_gt:
        lines.append(f"| {sid} | " + " | ".join(f"{_mean(acc[b].get(sid, [])):.3f}" for b in backends) + " |")

    # ── stage latency ──
    lines.append("")
    lines.append("## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)")
    if note:
        lines.append(f"Measured while: {note} — treat absolute values as possibly contaminated; the stage *shares* are still informative.")
    lines.append("")
    present = [st for st in STAGES if any(stage_acc[b].get(st) for b in backends)]
    if present:
        lines.append("| backend | wall | " + " | ".join((st + (" ⊃" if st in INCLUSIVE else "")) for st in present) + " | sum(exclusive) |")
        lines.append("|---|---|" + "---|" * (len(present) + 1))
        for b in backends:
            n = max(1, n_steps_total[b])
            vals = {st: (sum(stage_acc[b].get(st, [])) / n) for st in present}
            excl = sum(v for st, v in vals.items() if st not in INCLUSIVE)
            lines.append(f"| {b} | {summary[b]['latency_wall']:.2f} | " + " | ".join(f"{vals[st]:.2f}" for st in present) + f" | {excl:.2f} |")
    else:
        lines.append("- no stage_latency recorded in these runs (instrumentation added after they started).")
    if "vanilla_vector" in summary and "full_system" in summary:
        vb = summary.get("vanilla_budget", summary["vanilla_vector"])
        lines.append("")
        lines.append(f"- extra latency of full_system over vanilla_vector (charged): **{summary['full_system']['latency'] - summary['vanilla_vector']['latency']:+.2f} s/step**; "
                     f"over vanilla_budget: {summary['full_system']['latency'] - vb['latency']:+.2f} s/step.")

    # ── routing / loss analysis for full_system ──
    fs = "full_system"
    lines.append("")
    lines.append("## full_system routing per step (rep-wise; expected = GT node or scenario workflow)")
    lines.append("")
    lines.append("| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    conf_correct: List[float] = []
    conf_wrong: List[float] = []
    conf_correct_all: List[float] = []   # every pre-gate pick, gated or not
    conf_wrong_all: List[float] = []
    confident_wrong = 0
    routed_total = 0
    routed_ok = 0
    fallback_n = 0
    step_n = 0
    losses: Dict[str, int] = {}
    loss_detail: List[Dict] = []
    for key in sorted(steps):
        sid, si = key
        gt_step = scen_gt[sid]["steps"][si]
        exp_node = gt_step.get("expected_workflow_node")
        exp_wf = SCEN_WF[sid]
        for r, ps in enumerate(steps[key].get(fs, [])):
            step_n += 1
            picked = ps.get("picked_node_id")
            conf = float(ps.get("route_confidence") or 0.0)
            fb = bool(ps.get("fallback_activated"))
            picked_wf = _wf_of(graph, picked)
            route_ok = (picked == exp_node) if exp_node else ((picked_wf == exp_wf) if picked else False)
            if fb:
                fallback_n += 1
            if picked:
                (conf_correct_all if route_ok else conf_wrong_all).append(conf)
            if picked and not fb:
                routed_total += 1
                if route_ok:
                    routed_ok += 1
                    conf_correct.append(conf)
                else:
                    conf_wrong.append(conf)
                    if conf >= threshold:
                        confident_wrong += 1
            fs_ok = bool(ps.get("matched"))

            def _m(b):
                lst = steps[key].get(b, [])
                return bool(lst[r].get("matched")) if r < len(lst) else None

            def _h(b):
                lst = steps[key].get(b, [])
                return _target_hit(lst[r].get("context_block"), sid) if r < len(lst) else None
            vv_ok, vb_ok, nr_ok = _m("vanilla_vector"), _m("vanilla_budget"), _m("no_rag")
            loss = ""
            if not fs_ok and (vv_ok or vb_ok):
                loss = "fallback_quality" if fb else ("misrouting" if (picked and not route_ok) else "context_or_generation")
                losses[loss] = losses.get(loss, 0) + 1
                vv_lst = steps[key].get("vanilla_vector", [])
                loss_detail.append({"scenario": sid, "step": si, "rep": r, "class": loss,
                                    "picked": picked, "conf": conf, "expected": exp_node or exp_wf,
                                    "response": ps.get("response", ""),
                                    "context_block": ps.get("context_block") or "",
                                    "vv_response": vv_lst[r].get("response", "") if r < len(vv_lst) else ""})
            lines.append(f"| {sid.replace('opendtect__', '')} | {si} | {r} | {exp_node or exp_wf} | {picked or '—'} | {conf:.2f} | "
                         f"{ps.get('route_method', '')} | {'Y' if fb else ''} | {_y(route_ok) if picked and not fb else '—'} | "
                         f"{_y(_h(fs))}/{_y(_h('vanilla_vector'))}/{_y(_h('vanilla_budget'))} | "
                         f"{_y(fs_ok)} | {_y(vv_ok)} | {_y(vb_ok)} | {_y(nr_ok)} | {loss} |")

    lines.append("")
    lines.append("## (a) Routing summary (full_system)")
    lines.append("")
    lines.append(f"- steps × reps: {step_n}; routed (passed gate): {routed_total}; routed correct: {routed_ok}"
                 f" ({(routed_ok / routed_total) if routed_total else float('nan'):.2f}); fallback: {fallback_n} ({fallback_n / step_n if step_n else float('nan'):.2f})")
    lines.append(f"- confident-wrong routes (conf ≥ {threshold:.2f}, wrong node/workflow): **{confident_wrong}**")
    lines.append(f"- confidence of correct routed picks: {sorted(round(c, 2) for c in conf_correct)}")
    lines.append(f"- confidence of wrong routed picks: {sorted(round(c, 2) for c in conf_wrong)}")
    lines.append("")
    lines.append("### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)")
    lines.append("")
    lines.append(f"- correct picks (all): {sorted(round(c, 2) for c in conf_correct_all)}")
    lines.append(f"- wrong picks (all): {sorted(round(c, 2) for c in conf_wrong_all)}")
    lines.append("")
    lines.append("| t | correct kept | wrong kept | correct dropped (→ fallback) |")
    lines.append("|---|---|---|---|")
    best_t = None
    for t in (0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95):
        ck = sum(1 for c in conf_correct_all if c >= t)
        wk = sum(1 for c in conf_wrong_all if c >= t)
        lines.append(f"| {t:.2f} | {ck} | {wk} | {len(conf_correct_all) - ck} |")
        if wk == 0 and best_t is None:
            best_t = (t, ck, len(conf_correct_all) - ck)
    if best_t:
        lines.append("")
        lines.append(f"- smallest t with zero wrong picks kept: **{best_t[0]:.2f}** (keeps {best_t[1]} correct, drops {best_t[2]} correct to fallback).")
    else:
        lines.append("")
        lines.append("- no threshold ≤ 0.95 removes every wrong pick: the wrong picks are as confident as the correct ones → the fix must be upstream (candidate pool / rerank evidence), not the gate.")
    lines.append("")
    lines.append("## (b) Target-section retrieval hit (context contains the scenario's target section)")
    lines.append("")
    lines.append("| scenario | " + " | ".join(backends) + " |")
    lines.append("|---|" + "---|" * len(backends))
    for sid in scen_gt:
        row = []
        for b in backends:
            hs = [_target_hit(ps.get("context_block"), sid) for key in steps if key[0] == sid for ps in steps[key].get(b, [])]
            hs = [h for h in hs if h is not None]
            row.append(f"{sum(1 for h in hs if h)}/{len(hs)}" if hs else "—")
        lines.append(f"| {sid.replace('opendtect__', '')} | " + " | ".join(row) + " |")
    lines.append("")
    lines.append(f"## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): {losses if losses else 'none'}")

    # ── fallback steps ──
    fb_rows = []
    for key in sorted(steps):
        for r, ps in enumerate(steps[key].get(fs, [])):
            if not ps.get("fallback_activated"):
                continue

            def _mm(b):
                lst = steps[key].get(b, [])
                return bool(lst[r].get("matched")) if r < len(lst) else None
            vv_lst = steps[key].get("vanilla_vector", [])
            vv_chars = vv_lst[r].get("context_chars") if r < len(vv_lst) else None
            fb_rows.append((key[0], key[1], r, bool(ps.get("matched")), _mm("vanilla_vector"), _mm("vanilla_budget"),
                            int(ps.get("context_chars") or 0), vv_chars))
    lines.append("")
    lines.append("## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)")
    lines.append("")
    vv_all = [int(ps.get("context_chars") or 0) for key in steps for ps in steps[key].get("vanilla_vector", [])]
    if fb_rows:
        lines.append("| scenario | step | rep | fs | vanilla_vector | vanilla_budget | fs ctx chars | vv ctx chars |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for sid, si, r, a, b_, c, fc, vc in fb_rows:
            lines.append(f"| {sid.replace('opendtect__', '')} | {si} | {r} | {_y(a)} | {_y(b_)} | {_y(c)} | {fc} | {vc if vc is not None else '—'} |")
        n_fb = len(fb_rows)
        fs_ok_n = sum(1 for x in fb_rows if x[3])
        vv_ok_n = sum(1 for x in fb_rows if x[4])
        vb_ok_n = sum(1 for x in fb_rows if x[5])
        trunc_loss = sum(1 for x in fb_rows if (not x[3]) and x[4] and (not x[5]))
        lines.append("")
        lines.append(f"- fallback steps: {n_fb}; matched — fs {fs_ok_n}, vanilla_vector {vv_ok_n}, vanilla_budget {vb_ok_n}; "
                     f"steps where fs ✗ and vanilla_vector ✓ but vanilla_budget ✗ (truncation-attributable): **{trunc_loss}**")
        if vv_all:
            lines.append(f"- vanilla_vector untruncated context: mean {statistics.mean(vv_all):.0f} chars, max {max(vv_all)}, "
                         f"median {statistics.median(vv_all):.0f} (fallback/vanilla_budget budget = {os.environ.get('FALLBACK_CTX_CHARS', '3900')}).")
        if trunc_loss:
            lines.append(f"- BUDGET PROPOSAL: raise FALLBACK_CTX_CHARS and VANILLA_BUDGET_CHARS together (same-budget rule) "
                         f"toward the untruncated median ({statistics.median(vv_all):.0f} chars) and re-run; "
                         f"routed context keeps GRAPH_CTX_ITEMS×GRAPH_CTX_CHARS + VECTOR_CTX_CHARS = the same total.")
        else:
            lines.append("- no truncation-attributable loss on fallback steps; budget unchanged.")
    else:
        lines.append("- no fallback steps in this iteration.")
        if vv_all:
            lines.append(f"- vanilla_vector untruncated context: mean {statistics.mean(vv_all):.0f} chars, max {max(vv_all)}, median {statistics.median(vv_all):.0f}.")

    # ── steps every backend failed ──
    lines.append("")
    lines.append("## Steps every backend failed (same rep) — response text and GT pattern")
    all_fail = []
    for key in sorted(steps):
        sid, si = key
        n_r = max((len(steps[key].get(b, [])) for b in backends), default=0)
        for r in range(n_r):
            ok = [(bool(steps[key][b][r].get("matched")) if (b in steps[key] and r < len(steps[key][b])) else None) for b in backends]
            if ok and all(o is False for o in ok):
                all_fail.append((sid, si, r))
    if not all_fail:
        lines.append("")
        lines.append("- none.")
    for sid, si, r in all_fail:
        gt_step = scen_gt[sid]["steps"][si]
        lines.append("")
        lines.append(f"### {sid.replace('opendtect__', '')} step {si} rep {r}")
        lines.append("")
        lines.append(f"- GT pattern: `{gt_step.get('expected_action_text_pattern', '')}`")
        lines.append(f"- GT keywords: {gt_step.get('expected_action_keywords', [])}; allowed alternatives: {gt_step.get('allowed_alternatives', [])}")
        for b in backends:
            lst = steps[(sid, si)].get(b, [])
            if r < len(lst):
                ps = lst[r]
                th = _target_hit(ps.get("context_block"), sid)
                secs = sorted(set(s.split(" ")[0] for s in _ctx_sections(ps.get("context_block"))))
                lines.append(f"- **{b}** (target hit {_y(th)}; sections {', '.join(secs) or '—'}): `{(ps.get('response') or '')[:300].replace(chr(10), ' ')}`")

    # ── criteria check ──
    lines.append("")
    lines.append("## Criteria check")
    lines.append("")
    checks = []
    checks.append(("(a) confident-wrong routes == 0", confident_wrong == 0, str(confident_wrong)))
    checks.append(("(a) routing accuracy (routed steps)", routed_total > 0 and routed_ok == routed_total, f"{routed_ok}/{routed_total}"))
    for other in ("vanilla_vector", "vanilla_budget"):
        if other in summary and fs in summary:
            checks.append((f"(b) target-section hit fs ≥ {other}", summary[fs]["target_hit"] >= summary[other]["target_hit"],
                           f"{summary[fs]['target_hit']:.2f} vs {summary[other]['target_hit']:.2f}"))
    checks.append(("(c) no loss vs vanilla", not losses, str(losses) if losses else "0"))
    for name, ok, detail in checks:
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} ({detail})")
    lines.append("")
    lines.append("Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):")
    s_fs = summary.get(fs, {})
    for other in ("vanilla_vector", "vanilla_budget"):
        so = summary.get(other)
        if not so or not s_fs:
            continue
        lines.append(f"- step_acc fs vs {other}: {s_fs['step_acc_scenario_avg']:.3f} vs {so['step_acc_scenario_avg']:.3f}; "
                     f"cost_total {s_fs['cost_total']:.5f} vs {so['cost_total']:.5f}; latency {s_fs['latency']:.2f} vs {so['latency']:.2f} s "
                     f"(extra {s_fs['latency'] - so['latency']:+.2f} s)")
    primary_ok = all(ok for _, ok, _ in checks)
    lines.append("")
    lines.append(f"**Primary criteria {'MET' if primary_ok else 'NOT met'}.**")

    if loss_detail:
        lines.append("")
        lines.append("## Loss detail (full_system lost to a vanilla baseline)")
        for d in loss_detail:
            lines.append("")
            lines.append(f"### {d['scenario'].replace('opendtect__', '')} step {d['step']} rep {d['rep']} — {d['class']} (picked={d['picked']} conf={d['conf']:.2f} expected={d['expected']})")
            lines.append("")
            lines.append("full_system response:")
            lines.append("```")
            lines.append((d["response"] or "")[:600])
            lines.append("```")
            lines.append("vanilla_vector response:")
            lines.append("```")
            lines.append((d["vv_response"] or "")[:600])
            lines.append("```")
            lines.append(f"full_system context sections: {', '.join(_ctx_sections(d['context_block'])[:8]) or '—'}")
            lines.append("full_system context head:")
            lines.append("```")
            lines.append((d["context_block"] or "")[:1200])
            lines.append("```")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:60]))
    print(f"\n[dev_iter] analysis written: {out_md}")
    return {"summary": summary, "confident_wrong": confident_wrong, "losses": losses, "primary_ok": primary_ok,
            "routed_total": routed_total, "routed_ok": routed_ok, "fallback_n": fallback_n, "step_n": step_n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", type=int, required=True)
    ap.add_argument("--profile", default="v3", choices=sorted(PROFILES))
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--model", default="gemini")
    ap.add_argument("--backends", nargs="*", default=DEFAULT_BACKENDS)
    ap.add_argument("--env", nargs="*", default=[], help="KEY=VAL overrides applied after the profile")
    ap.add_argument("--chromadb", default=os.environ.get("CHROMADB_PATH_V4", "./data/chromadb_v4"))
    ap.add_argument("--only", default=None, help="substring filter on the dev scenario file names (e.g. survey_setup)")
    ap.add_argument("--note", default="", help="free-text note stored with the run (e.g. 'reindex running: latency possibly contaminated')")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--analyze-only", action="store_true")
    args = ap.parse_args()

    tag = args.tag or f"dev_iter{args.iter}_{args.profile}_{args.model}"
    env = dict(os.environ)
    try:
        from dotenv import dotenv_values
        for p in (".env.local", ".env"):
            if os.path.exists(p):
                env.update({k: v for k, v in dotenv_values(p).items() if v is not None})
    except ImportError:
        pass
    env.update(COMMON_ENV)
    env.update(PROFILES[args.profile])
    env["CHROMADB_PATH"] = args.chromadb
    for kv in args.env:
        k, _, v = kv.partition("=")
        env[k] = v
    knobs = {k: env.get(k) for k in sorted(set(PROFILES["v3"]) | set(COMMON_ENV) | {"CHROMADB_PATH"})}
    knobs["_note"] = args.note
    knobs["_only"] = args.only
    print(f"[dev_iter] tag={tag} knobs={json.dumps(knobs)}", flush=True)
    scen_files = _scenario_files(args.only)

    run_files: List[Path] = []
    knobs_path = RESULTS / f"{tag}_knobs.json"
    if not args.analyze_only:
        _prepare_dev_dir(scen_files)
        for rep in range(args.reps):
            out = RESULTS / f"{tag}_r{rep}.json"
            rc = _run_bench(out, args.backends, env, args.model)
            if rc != 0 or not out.exists():
                print(f"[dev_iter] bench rep {rep} failed rc={rc}; see {out.with_suffix('.log')}")
                sys.exit(rc or 1)
            run_files.append(out)
        knobs_path.write_text(json.dumps(knobs, indent=2), encoding="utf-8")
    else:
        run_files = sorted(RESULTS.glob(f"{tag}_r*.json"))
        if not run_files:
            print(f"[dev_iter] no run files for tag {tag}")
            sys.exit(1)
        if knobs_path.exists() and not args.note:
            try:
                args.note = json.loads(knobs_path.read_text(encoding="utf-8")).get("_note", "") or ""
            except Exception:
                pass
    threshold = float(env.get("CONFIDENCE_THRESHOLD", "0.7"))
    analyze(run_files, RESULTS / f"{tag}.md", args.backends, threshold, note=args.note, scen_files=scen_files)


if __name__ == "__main__":
    main()
