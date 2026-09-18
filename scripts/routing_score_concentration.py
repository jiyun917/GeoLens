"""검증 #2 — 라우팅 실패 스텝에 step_match 하락이 집중되는지 진단.

목적: attribute_computation 시나리오의 full_system 스텝 중, workflow
라우팅이 올바르게 (`seismic_attribute`) 이루어진 스텝과 오라우팅된
(`d3_visualization`, `horizon_tracking`) 스텝의 step_match 통과율을
비교. 통과율 격차가 크면 → workflow signature 개선 (레버 1) 이 실제로
attribute 성능을 회복시킬 여지가 있음.

새 벤치 실행 없이 unified3 데이터만으로 완결.
"""

from __future__ import annotations

import glob
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "eval" / "results"

SCEN = "opendtect__attribute_computation__01"
BACKEND = "full_system"
TARGET_WF = "seismic_attribute"


def load_per_step() -> list[dict]:
    """전체 replicate × 4 model 의 attribute 시나리오 full_system per_step 반환."""
    rows: list[dict] = []
    for f in sorted(glob.glob(str(ROOT / "data/eval/results/run_*_unified3_r*_*.json"))):
        model = Path(f).name.split("run_")[1].split("_")[0]
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for s in d.get("scenarios", []) or []:
            if s.get("scenario_id") != SCEN:
                continue
            b = (s.get("backends") or {}).get(BACKEND)
            if not b or "per_step" not in b:
                continue
            for st in b["per_step"]:
                rows.append({
                    "model": model,
                    "file": Path(f).name,
                    "step_index": st.get("step_index"),
                    "matched": bool(st.get("matched")),
                    "hallucinated": bool(st.get("hallucinated")),
                    "picked_wf": st.get("picked_workflow_id"),
                    "picked_node": st.get("picked_node_id"),
                    "route_conf": st.get("route_confidence"),
                    "fallback": bool(st.get("fallback_activated")),
                })
    return rows


def render(rows: list[dict]) -> str:
    total = len(rows)
    correct_wf = [r for r in rows if r["picked_wf"] == TARGET_WF]
    wrong_wf = [r for r in rows if r["picked_wf"] and r["picked_wf"] != TARGET_WF]

    def rate(rs, key):
        return statistics.fmean([1.0 if r[key] else 0.0 for r in rs]) * 100 if rs else 0.0

    correct_acc = rate(correct_wf, "matched")
    wrong_acc = rate(wrong_wf, "matched")
    correct_hall = rate(correct_wf, "hallucinated")
    wrong_hall = rate(wrong_wf, "hallucinated")

    lines = [
        "# 검증 #2 — 라우팅 실패 vs step_match 하락 집중",
        "",
        f"**대상**: `{SCEN}` × `{BACKEND}` × 4 모델 × 5 replicates.",
        f"**총 스텝**: {total} (8 스텝 × 4 × 5 = 160).",
        "",
        "## 1. 라우팅 성공 vs 실패 스텝 accuracy 격차",
        "",
        f"| 조건 | 스텝 수 | step_match 통과율 | hallucination 발생률 |",
        f"|---|---|---|---|",
        f"| ✅ `seismic_attribute` 라우팅 성공 | {len(correct_wf)} | **{correct_acc:.1f}%** | {correct_hall:.1f}% |",
        f"| ❌ 다른 workflow 오라우팅 | {len(wrong_wf)} | **{wrong_acc:.1f}%** | {wrong_hall:.1f}% |",
        f"| **격차 (성공 − 실패)** | — | **{correct_acc - wrong_acc:+.1f}pp** | {correct_hall - wrong_hall:+.1f}pp |",
        "",
    ]

    # 스텝 인덱스별 라우팅 분포 + 정확도
    lines.append("## 2. 스텝별 라우팅 분포 + step_match 통과율")
    lines.append("")
    lines.append("| step_index | 라우팅 분포 (wf: count) | 이 스텝 통과율 | `seismic_attribute` 통과율 | 오라우팅 통과율 |")
    lines.append("|---|---|---|---|---|")
    by_step = defaultdict(list)
    for r in rows:
        by_step[r["step_index"]].append(r)
    for si in sorted(by_step.keys()):
        step_rows = by_step[si]
        wf_count = defaultdict(int)
        for r in step_rows:
            wf_count[r["picked_wf"] or "none"] += 1
        wf_str = ", ".join(f"{k}: {v}" for k, v in sorted(wf_count.items(), key=lambda x: -x[1]))
        overall = rate(step_rows, "matched")
        correct = [r for r in step_rows if r["picked_wf"] == TARGET_WF]
        wrong = [r for r in step_rows if r["picked_wf"] and r["picked_wf"] != TARGET_WF]
        c_acc = f"{rate(correct, 'matched'):.0f}% (n={len(correct)})" if correct else "—"
        w_acc = f"{rate(wrong, 'matched'):.0f}% (n={len(wrong)})" if wrong else "—"
        lines.append(f"| {si} | {wf_str} | {overall:.0f}% | {c_acc} | {w_acc} |")
    lines.append("")

    # 노드별 통과율 (상위 라우팅 노드)
    lines.append("## 3. 라우팅 노드별 통과율")
    lines.append("")
    lines.append("| picked_node_id | 스텝 수 | 통과율 | 평균 confidence |")
    lines.append("|---|---|---|---|")
    by_node = defaultdict(list)
    for r in rows:
        by_node[r["picked_node"] or "none"].append(r)
    for node, node_rows in sorted(by_node.items(), key=lambda x: -len(x[1])):
        acc = rate(node_rows, "matched")
        conf = statistics.fmean([r["route_conf"] or 0 for r in node_rows])
        lines.append(f"| `{node}` | {len(node_rows)} | {acc:.0f}% | {conf:.2f} |")
    lines.append("")

    # 판정
    delta = correct_acc - wrong_acc
    lines.append("## 4. 레버 1 성립 판정")
    lines.append("")
    if delta >= 20:
        judgment = (
            f"**레버 1 성립 (강)**. 라우팅 성공 스텝의 통과율이 오라우팅보다 "
            f"{delta:.1f}pp 높음. Workflow signature 수리로 오라우팅 스텝 "
            f"({len(wrong_wf)}개, {len(wrong_wf)/total*100:.0f}%) 이 성공으로 "
            f"이동하면 attribute 시나리오 step_acc 는 최대 "
            f"~{(correct_acc*total - correct_acc*len(correct_wf) - wrong_acc*len(wrong_wf))/total + correct_acc*len(wrong_wf)/total:.0f}% "
            f"까지 회복 가능 (상한 추정: 모든 스텝이 correct 통과율로 이동한 가정)."
        )
    elif delta >= 10:
        judgment = (
            f"**레버 1 성립 (중)**. 격차 {delta:.1f}pp. signature 수리로 "
            f"일부 회복 가능하나 극적 개선은 어려움. 오라우팅 스텝 자체가 "
            f"어려운 스텝일 가능성도 병존."
        )
    elif delta >= 5:
        judgment = (
            f"**레버 1 부분 성립**. 격차 {delta:.1f}pp — 신호는 있으나 약함. "
            f"signature 수리만으로 attribute 격차 반전 어려움. 레버 2 병행 필요."
        )
    else:
        judgment = (
            f"**레버 1 미성립**. 격차 {delta:.1f}pp — 라우팅 정오와 통과율이 "
            f"거의 무관. 문제는 라우팅이 아니라 (a) 8-스텝 합성 자체의 난이도, "
            f"(b) 파라메트릭 지식으로 vanilla 도 우회 가능한 스텝 정답 구조. "
            f"→ 레버 2 (파라메트릭 마스킹 조건 시나리오) 로 이동 권장."
        )
    lines.append(judgment)
    lines.append("")

    # 오라우팅 노드 top 3 — 수리 target 후보
    lines.append("## 5. Signature 수리 우선순위 (오라우팅 top 노드)")
    lines.append("")
    wrong_by_node = defaultdict(list)
    for r in wrong_wf:
        wrong_by_node[r["picked_node"] or "none"].append(r)
    lines.append("| 오라우팅 노드 | 오라우팅 스텝 수 | 이 노드로 간 스텝 통과율 |")
    lines.append("|---|---|---|")
    for node, nrs in sorted(wrong_by_node.items(), key=lambda x: -len(x[1]))[:5]:
        acc = rate(nrs, "matched")
        lines.append(f"| `{node}` | {len(nrs)} | {acc:.0f}% |")
    lines.append("")
    lines.append("→ 위 노드로 흡수되는 스텝들에 대해 `seismic_attribute` 워크플로우 "
                 "의 대응 노드 signature 를 강화하는 것이 다음 액션.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    rows = load_per_step()
    print(f"loaded {len(rows)} per_step records", file=sys.stderr)
    md = render(rows)
    out = RESULTS / "routing_score_concentration_unified3.md"
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"\nsaved: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
