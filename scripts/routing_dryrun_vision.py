"""Vision-based routing dry-run (v3 gate).

Unlike routing_dryrun.py (which feeds the hand-authored visual_state_gt to
the localizer), this runs the REAL pipeline path per scenario step:
screenshot → recognize_visual_state (Gemini Flash) → localize_to_graph
(keyword top-3 + CLIP top-3 → Flash rerank) with every workflow JSON
loaded, and reports whether the picked node belongs to the scenario's
target workflow. Run once with thinking off (AUX_THINKING_BUDGET=0, the v3
setting) and once with the model default (-1) to check that disabling
thinking does not degrade routing.

Usage:
    AUX_THINKING_BUDGET=0  .venv/Scripts/python.exe scripts/routing_dryrun_vision.py --label think0
    AUX_THINKING_BUDGET=-1 .venv/Scripts/python.exe scripts/routing_dryrun_vision.py --label thinkdyn
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
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

EXPECTED_WF = {
    "opendtect__survey_setup__01": "survey_setup",
    "opendtect__3d_visualization__01": "d3_visualization",
    "opendtect__attribute_computation__01": "seismic_attribute",
    "qgis__vector_buffer__01": "qgis_vector_buffer",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="think0")
    ap.add_argument("--scenarios", nargs="*", default=None)
    args = ap.parse_args()
    from api.services.bench_backends import _load_screenshot_b64
    from api.services.guide_pipeline import get_guide_pipeline, get_aux_usage, reset_aux_usage, CONFIDENCE_THRESHOLD
    pipeline = get_guide_pipeline()
    rows = []
    for f in sorted(glob.glob(str(ROOT / "data/eval/scenarios/*.json"))):
        scen = json.load(open(f, encoding="utf-8"))
        sid = scen.get("scenario_id")
        if not sid or sid == "EXAMPLE_PLACEHOLDER" or (args.scenarios and sid not in args.scenarios):
            continue
        os.environ["GEOLENS_SOFTWARE_ID"] = "qgis" if sid.startswith("qgis") else "opendtect"
        visited = []
        for i, step in enumerate(scen["steps"]):
            b64 = _load_screenshot_b64(scen, i)
            reset_aux_usage()
            t0 = time.time()
            vs = pipeline.recognize_visual_state(b64)
            loc = pipeline.localize_to_graph(vs, None, screenshot_b64=b64, manual_ids=[scen["manual_id"]],
                                             user_goal=scen.get("goal", ""), visited_node_ids=list(visited))
            dt = time.time() - t0
            node = loc.get("node") or {}
            if node.get("id"):
                visited.append(node["id"])
            aux = get_aux_usage()
            rows.append({
                "scenario": sid, "step": i, "expected_wf": EXPECTED_WF.get(sid),
                "picked_wf": node.get("workflow_id"), "picked_node": node.get("id"),
                "conf": round(float(loc.get("confidence") or 0), 2), "method": loc.get("match_method"),
                "kept": bool(node.get("id")) and float(loc.get("confidence") or 0) >= CONFIDENCE_THRESHOLD,
                "aux_calls": aux["calls"], "aux_in": aux["input_tokens"], "aux_out": aux["output_tokens"],
                "aux_think": aux["thoughts_tokens"], "aux_cost_usd": aux["cost_usd"], "latency": round(dt, 1),
                "visual_state": vs,
            })
            print(f"{sid[10:32]:22s} s{i} picked={node.get('workflow_id')}/{node.get('id')} conf={rows[-1]['conf']} "
                  f"method={loc.get('match_method')} kept={rows[-1]['kept']} aux={aux['calls']}calls "
                  f"think={aux['thoughts_tokens']} ${1000*aux['cost_usd']:.2f}m {dt:.1f}s", flush=True)
    # summary
    by = {}
    for r in rows:
        s = by.setdefault(r["scenario"], {"n": 0, "correct": 0, "kept": 0, "none": 0, "cost": 0.0, "think": 0, "lat": 0.0})
        s["n"] += 1; s["correct"] += r["picked_wf"] == r["expected_wf"]; s["kept"] += r["kept"]
        s["none"] += r["method"] == "none"; s["cost"] += r["aux_cost_usd"]; s["think"] += r["aux_think"]; s["lat"] += r["latency"]
    lines = [f"# Vision-based routing dry-run — {args.label} (AUX_THINKING_BUDGET={os.environ.get('AUX_THINKING_BUDGET', 'unset')})", "",
             "| scenario | steps | correct workflow | kept (conf≥0.7) | rerank none | aux cost/step | thinking tok/step | latency/step |",
             "|---|---|---|---|---|---|---|---|"]
    for sid, s in by.items():
        lines.append(f"| {sid} | {s['n']} | {s['correct']}/{s['n']} | {s['kept']}/{s['n']} | {s['none']} | ${1000*s['cost']/s['n']:.2f}m | {s['think']/s['n']:.0f} | {s['lat']/s['n']:.1f}s |")
    lines += ["", "| scenario | step | expected | picked wf / node | conf | method | kept |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['scenario']} | {r['step']} | {r['expected_wf']} | {r['picked_wf']} / {r['picked_node']} | {r['conf']} | {r['method']} | {r['kept']} |")
    out = ROOT / f"data/eval/results/routing_dryrun_vision_{args.label}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / f"data/eval/results/routing_dryrun_vision_{args.label}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines[:8]))
    print("saved:", out)


if __name__ == "__main__":
    main()
