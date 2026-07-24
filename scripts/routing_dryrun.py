"""Routing dry-run — for each scenario step, call localize_to_graph()
using the scenario's ground-truth visual_state and report which workflow
node the router picked, its confidence, and whether the pick belongs to
the expected workflow.

This bypasses the Gemini vision call (recognize_visual_state) because the
scenario's visual_state_gt is the authored contract for what that call
should produce. It still hits Gemini Flash for the LLM rerank stage, so
GEMINI_API_KEY must be set.

Usage:
    .venv/Scripts/python.exe scripts/routing_dryrun.py

Reports per-scenario:
  - Step-by-step: picked node id, workflow_id, confidence, match/miss
  - Aggregate: exact-workflow-match rate (must be near 100%; else rerank
    or keyword-signature tuning is needed)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass


SCENARIO_TO_EXPECTED_WORKFLOW = {
    "opendtect__survey_setup__01": "survey_setup",
    "opendtect__3d_visualization__01": "d3_visualization",
}


def _load_scenario(scenario_id: str) -> dict | None:
    for sub in ("", "excluded/"):
        p = ROOT / "data" / "eval" / "scenarios" / sub / f"{scenario_id}.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


def run_dryrun(scenario_id: str) -> dict:
    from api.services.guide_pipeline import GuideRAGPipeline

    scen = _load_scenario(scenario_id)
    if not scen:
        return {"scenario_id": scenario_id, "error": "scenario file not found"}

    expected_wf = SCENARIO_TO_EXPECTED_WORKFLOW.get(scenario_id)
    goal = scen.get("goal", "")
    manual_id = scen.get("manual_id")

    pipeline = GuideRAGPipeline()

    steps_report = []
    visited_ids: list[str] = []
    exact_matches = 0
    total = 0

    for step in scen.get("steps", []):
        total += 1
        step_idx = step.get("step_index")
        vs = step.get("visual_state_gt", {}) or {}
        loc = pipeline.localize_to_graph(
            visual_state=vs,
            hint_workflow_id=None,
            screenshot_b64=None,   # no CLIP; rerank operates on kw_top only
            manual_ids=[manual_id] if manual_id else None,
            user_goal=goal,
            visited_node_ids=list(visited_ids),
        )
        node = loc.get("node")
        picked_id = node.get("id") if node else None
        picked_wf = node.get("workflow_id") if node else None
        conf = loc.get("confidence", 0.0)
        method = loc.get("match_method")

        matches_expected = (picked_wf == expected_wf)
        if matches_expected:
            exact_matches += 1

        if picked_id and picked_id not in visited_ids:
            visited_ids.append(picked_id)

        steps_report.append({
            "step_index": step_idx,
            "picked_node": picked_id,
            "picked_workflow": picked_wf,
            "confidence": conf,
            "method": method,
            "expected_workflow": expected_wf,
            "matches_expected": matches_expected,
        })

    match_rate = exact_matches / total if total else 0.0
    return {
        "scenario_id": scenario_id,
        "expected_workflow": expected_wf,
        "n_steps": total,
        "exact_workflow_matches": exact_matches,
        "match_rate": match_rate,
        "steps": steps_report,
    }


def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set; rerank stage will always return None")
        sys.exit(1)

    scenarios = list(SCENARIO_TO_EXPECTED_WORKFLOW.keys())
    print("=" * 70)
    print("ROUTING DRY-RUN — new workflow nodes coverage check")
    print("=" * 70)

    overall_correct = 0
    overall_total = 0
    for sid in scenarios:
        print(f"\n--- {sid} ---")
        rep = run_dryrun(sid)
        if "error" in rep:
            print(f"  ERROR: {rep['error']}")
            continue
        print(f"expected workflow: {rep['expected_workflow']}")
        for st in rep["steps"]:
            flag = "OK " if st["matches_expected"] else "MISS"
            conf = st["confidence"]
            print(
                f"  step {st['step_index']}: [{flag}] "
                f"node={st['picked_node']} "
                f"wf={st['picked_workflow']} "
                f"conf={conf:.2f} "
                f"method={st['method']}"
            )
        print(f"exact-workflow match: {rep['exact_workflow_matches']}/{rep['n_steps']}"
              f" ({rep['match_rate']*100:.0f}%)")
        overall_correct += rep["exact_workflow_matches"]
        overall_total += rep["n_steps"]

    print("\n" + "=" * 70)
    if overall_total:
        rate = overall_correct / overall_total
        print(f"OVERALL exact-workflow match: {overall_correct}/{overall_total}"
              f" ({rate*100:.1f}%)")
        if rate >= 0.95:
            print("STATUS: PASS — coverage effective")
        else:
            print("STATUS: FAIL — investigate rerank/signature tuning before proceeding")
    print("=" * 70)


if __name__ == "__main__":
    main()
