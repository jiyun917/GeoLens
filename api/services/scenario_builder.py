"""
Scenario template generator.

Given an auto-generated workflow JSON (data/workflows/auto_*.json) this
emits a scenario JSON skeleton with the per-step shell pre-filled from the
workflow node:
  - step_index, expected_workflow_node, expected_action_keywords (from
    action_verb + title), allowed_alternatives blank
  - screenshot_path defaulted to a guessed manual-image path (when the
    matching p{page:03d}_i*.png exists) so a human only needs to RECAPTURE
    if they want a real user-side screenshot
  - visual_state_gt as a TODO stub with hints

The intent: ~80% of the boilerplate is auto-filled; a human labels only
the screenshots + the per-step UI state ground truth + any trap flags.

CLI:
    python -m api.services.scenario_builder \\
        --workflow-id auto_<manual>__<section> \\
        --out data/eval/scenarios/<slug>.json \\
        [--goal "user-facing goal text"] \\
        [--language ko|en]
"""

import argparse
import glob
import json
import os
import re
import sys
from typing import Dict, List, Optional

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Use raw paths so we don't depend on a running app
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
WORKFLOW_DIR = os.path.join(PROJECT_ROOT, "data", "workflows")
IMAGE_DIR    = os.path.join(PROJECT_ROOT, "data", "manual_images")
SCEN_DIR     = os.path.join(PROJECT_ROOT, "data", "eval", "scenarios")
SHOT_DIR     = os.path.join(PROJECT_ROOT, "data", "eval", "screenshots")


def _slug(s: str) -> str:
    return re.sub(r"[^\w\-]+", "_", (s or "").lower()).strip("_")[:40] or "scenario"


def _guess_screenshot(manual_id: str, page: Optional[int]) -> Optional[str]:
    """If a manual image exists for this page, return its repo-relative path
    so the user can decide whether to keep it as the 'screenshot' or replace
    with a real user-side capture."""
    if not page:
        return None
    candidates = sorted(glob.glob(
        os.path.join(IMAGE_DIR, manual_id, f"p{page:03d}_i*.png")
    ) + sorted(glob.glob(
        os.path.join(IMAGE_DIR, manual_id, f"p{page:03d}_i*.jpeg")
    )))
    if not candidates:
        return None
    return os.path.relpath(candidates[0], PROJECT_ROOT).replace("\\", "/")


def _action_keywords(node: Dict) -> List[str]:
    """Pull a few salient tokens from title + action_verb."""
    title = node.get("title", "")
    verb = node.get("action_verb", "")
    out: List[str] = []
    if verb:
        out.append(verb)
    # Take Capitalized tokens from title (likely UI names)
    for m in re.findall(r"\b[A-Z][\w\-]{1,}\b", title):
        if m.lower() not in out and len(out) < 5:
            out.append(m)
    return out[:6]


def build_scenario(workflow_id: str, goal: Optional[str] = None,
                   language: str = "ko") -> Dict:
    wf_path = os.path.join(WORKFLOW_DIR, f"{workflow_id}.json")
    if not os.path.exists(wf_path):
        raise FileNotFoundError(f"Workflow JSON not found: {wf_path}")
    with open(wf_path, "r", encoding="utf-8") as f:
        wf = json.load(f)

    nodes = sorted(wf.get("nodes", []), key=lambda n: n.get("step_number", 0))
    manual_id = wf.get("source_manual_id") or wf.get("workflow_id", "").split("__", 1)[0].replace("auto_", "")
    name = wf.get("name", workflow_id)

    if not goal:
        goal = f"[TODO 작성: {name} 워크플로우의 사용자 목표 (구체적 path/이름 포함)]"

    steps = []
    for i, n in enumerate(nodes):
        page = n.get("page")
        screenshot = _guess_screenshot(manual_id, page)
        steps.append({
            "step_index": i,
            "screenshot_path": screenshot or f"data/eval/screenshots/[TODO_screenshot_{i}].png",
            "visual_state_gt": {
                "current_dialog": f"[TODO: dialog 이름 — 예: '{n.get('title','')[:40]}']",
                "active_menu": None,
                "visible_elements": ["[TODO: 화면에 보이는 주요 UI 요소들]"],
                "data_state": "[TODO: 데이터 상태]"
            },
            "expected_action_text_pattern": None,
            "expected_action_keywords": _action_keywords(n),
            "expected_workflow_node": n.get("id"),
            "allowed_alternatives": [],
            "is_error_recovery_test": False,
            "_node_hint": {
                "title": n.get("title", ""),
                "description": n.get("description", ""),
                "step_type": n.get("step_type", ""),
                "page": page,
            }
        })

    return {
        "scenario_id": f"{manual_id[:8]}__{_slug(name)}__01",
        "manual_id": manual_id,
        "manual_name": "[TODO: 매뉴얼 제목]",
        "category": "[TODO: import / visualization / attribute / etc.]",
        "difficulty": "medium",
        "language": language,
        "goal": goal,
        "steps": steps,
        "completion": {
            "final_screenshot_path": f"data/eval/screenshots/[TODO_done_{_slug(name)}].png",
            "expected_done_sentinel": True,
        },
        "_meta": {
            "source_workflow_id": workflow_id,
            "auto_generated_template": True,
            "labeling_checklist": [
                "1) 각 step의 screenshot_path를 실제 사용자 화면 캡처로 교체 (또는 매뉴얼 이미지 그대로 사용)",
                "2) visual_state_gt를 채워서 화면 ground-truth 명시",
                "3) trap이 있는 step에 'trap': {...} + 'is_error_recovery_test': true 추가",
                "4) 첫 번째 step의 current_dialog는 어플리케이션 메인 화면이 보통",
                "5) goal 텍스트에 사용자가 입력할 구체적 path/이름 포함",
                "6) _meta + _node_hint 필드는 라벨링 후 삭제 가능",
            ]
        }
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workflow-id", required=True, help="auto workflow id (without .json)")
    p.add_argument("--out", required=True, help="output scenario path")
    p.add_argument("--goal", default=None)
    p.add_argument("--language", default="ko", choices=["ko", "en"])
    args = p.parse_args()

    scen = build_scenario(args.workflow_id, args.goal, args.language)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(scen, f, ensure_ascii=False, indent=2)
    print(f"Wrote scenario template: {args.out}")
    print(f"  steps: {len(scen['steps'])}")
    print(f"  screenshots auto-filled: "
          f"{sum(1 for s in scen['steps'] if not s['screenshot_path'].startswith('data/eval/screenshots/[TODO'))}")


if __name__ == "__main__":
    main()
