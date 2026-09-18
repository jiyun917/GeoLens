"""QGIS Pilot — routing dry-run for qgis__vector_buffer__01.

Uses hint_workflow_id="qgis_vector_buffer" for bench-level isolation
(Q2 option A per audit trail — deployment-reality reflection, not hint).

Reports both workflow-level match (8/8 target) and node-level
distribution — especially _03_configure_buffer split across scenario
steps 3/4/5 (same node, distinct sub-states).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


SCENARIO_ID = "qgis__vector_buffer__01"
TARGET_WORKFLOW = "qgis_vector_buffer"
MANUAL_ID = "bf2804feea57434bb79b749134ed1df0"


def main():
    from api.services.guide_pipeline import GuideRAGPipeline

    scen_path = ROOT / "data" / "eval" / "scenarios" / f"{SCENARIO_ID}.json"
    scen = json.loads(scen_path.read_text(encoding="utf-8"))
    goal = scen.get("goal", "")
    steps = scen.get("steps", [])

    print(f"=== QGIS Pilot dry-run — {SCENARIO_ID} ===")
    print(f"hint_workflow_id: {TARGET_WORKFLOW}  (Q2 option A isolation)")
    print(f"manual_id: {MANUAL_ID}")
    print(f"steps: {len(steps)}")
    print()

    pipeline = GuideRAGPipeline()
    visited: list[str] = []
    workflow_hits = 0
    node_report = []
    per_node_counts = Counter()

    for step in steps:
        si = step.get("step_index")
        vs = step.get("visual_state_gt", {}) or {}
        expected_node = step.get("expected_workflow_node")

        loc = pipeline.localize_to_graph(
            visual_state=vs,
            hint_workflow_id=TARGET_WORKFLOW,   # ← Q2 option A
            screenshot_b64=None,
            manual_ids=[MANUAL_ID],
            user_goal=goal,
            visited_node_ids=list(visited),
        )
        node = loc.get("node")
        picked_node = node.get("id") if node else None
        picked_wf = node.get("workflow_id") if node else None
        conf = loc.get("confidence", 0.0)
        method = loc.get("match_method", "")

        wf_match = (picked_wf == TARGET_WORKFLOW)
        node_match = (picked_node == expected_node) if expected_node else None
        if wf_match:
            workflow_hits += 1
        if picked_node and picked_node not in visited:
            visited.append(picked_node)
        per_node_counts[picked_node or "NONE"] += 1

        node_report.append({
            "step": si,
            "expected_node": expected_node,
            "picked_node": picked_node,
            "picked_wf": picked_wf,
            "conf": conf,
            "method": method,
            "wf_match": wf_match,
            "node_match": node_match,
        })

    # ─── Workflow-level report ─────────────────────────────
    print("─── Workflow-level match (target: 8/8) ───")
    print(f"{workflow_hits}/{len(steps)} steps routed to '{TARGET_WORKFLOW}'")
    print()

    # ─── Node-level report ─────────────────────────────────
    print("─── Node-level localization (per-step) ───")
    print(f"{'step':>4}  {'expected_node':<45}  {'picked_node':<45}  {'conf':>5}  {'match':>5}")
    node_hits = 0
    for r in node_report:
        exp = r["expected_node"] or "(scenario level)"
        pk = r["picked_node"] or "NONE"
        conf = f"{r['conf']:.2f}"
        nm = "✓" if r["node_match"] else ("✗" if r["node_match"] is False else "—")
        if r["node_match"]:
            node_hits += 1
        print(f"  {r['step']:>3}  {exp:<45}  {pk:<45}  {conf:>5}  {nm:>5}")
    print()
    print(f"Node-level exact match: {node_hits}/{len(steps)}")
    print()

    # ─── _03 node discrimination check (user request) ──────
    print("─── _03_configure_buffer localization discrimination (steps 3,4,5 request) ───")
    for r in node_report:
        if r["step"] in (3, 4, 5):
            exp = r["expected_node"] or "?"
            pk = r["picked_node"] or "NONE"
            note = ""
            if pk == "qgis_vector_buffer_03_configure_buffer":
                note = "  (routed to _03 as expected)"
            elif pk and pk != exp:
                note = f"  (misroute vs expected {exp})"
            print(f"  step_{r['step']}: picked={pk} conf={r['conf']:.2f}{note}")
    print()

    # ─── Node distribution summary ─────────────────────────
    print("─── Node pick distribution (all 8 steps) ───")
    for node_id, count in per_node_counts.most_common():
        print(f"  {count} steps → {node_id}")
    print()

    # ─── Pass/fail verdict ─────────────────────────────────
    if workflow_hits == len(steps):
        print(f"STATUS: PASS — workflow-level 8/8 = target met")
        if node_hits == len(steps):
            print(f"        node-level 8/8 = precise localization")
        else:
            print(f"        node-level {node_hits}/{len(steps)} — some sub-state generalization (expected within a shared node like _03)")
    else:
        print(f"STATUS: FAIL — workflow-level {workflow_hits}/{len(steps)} < 8, investigate")


if __name__ == "__main__":
    main()
