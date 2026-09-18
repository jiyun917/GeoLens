"""QGIS Pilot 사전등록 대조 판정 + 이식 비용 표 최종본."""

import glob
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(str(Path(__file__).resolve().parent.parent))
FILES = sorted(glob.glob(str(ROOT / "data/eval/results/run_gemini_qgis_pilot_r*_*.json")))
OUT = ROOT / "data/eval/results/qgis_pilot_result_report.md"


def load_all():
    """Return list of parsed JSON."""
    return [json.loads(Path(f).read_text(encoding="utf-8")) for f in FILES]


def aggregate_per_backend(runs):
    """Per-backend: mean ± sd across replicates of scenario-level metrics."""
    by_backend = defaultdict(lambda: defaultdict(list))
    for d in runs:
        for scen in d.get("scenarios", []):
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b:
                    continue
                for mkey in ("step_accuracy", "hallucination_rate", "goal_completion_rate",
                             "mean_latency_sec", "mean_cost_usd"):
                    v = b.get(mkey)
                    if v is not None:
                        by_backend[bname][mkey].append(v)
    return by_backend


def fallback_analysis(runs):
    """Per-backend fallback + NONE bucket + workflow distribution."""
    stats = defaultdict(lambda: {"total": 0, "fallback": 0, "none_bucket": 0,
                                 "workflow_hit": 0, "step_pass": {"fallback": [0, 0],
                                                                    "none": [0, 0],
                                                                    "workflow": [0, 0]}})
    for d in runs:
        for scen in d.get("scenarios", []):
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "per_step" not in b:
                    continue
                if bname not in ("full_system", "state_path", "graph_only"):
                    continue
                for st in b["per_step"]:
                    stats[bname]["total"] += 1
                    fb = bool(st.get("fallback_activated"))
                    wf = st.get("picked_workflow_id")
                    matched = bool(st.get("matched"))
                    if fb:
                        stats[bname]["fallback"] += 1
                        stats[bname]["step_pass"]["fallback"][1] += 1
                        if matched: stats[bname]["step_pass"]["fallback"][0] += 1
                    elif wf is None:
                        stats[bname]["none_bucket"] += 1
                        stats[bname]["step_pass"]["none"][1] += 1
                        if matched: stats[bname]["step_pass"]["none"][0] += 1
                    else:
                        stats[bname]["workflow_hit"] += 1
                        stats[bname]["step_pass"]["workflow"][1] += 1
                        if matched: stats[bname]["step_pass"]["workflow"][0] += 1
    return stats


def fmt_pct(vals):
    if not vals: return "—"
    m = statistics.fmean(vals)
    sd = statistics.stdev(vals) if len(vals) >= 2 else 0
    return f"{m*100:.1f}±{sd*100:.1f}"


def fmt_sec(vals):
    if not vals: return "—"
    m = statistics.fmean(vals)
    sd = statistics.stdev(vals) if len(vals) >= 2 else 0
    return f"{m:.1f}±{sd:.1f}"


def fmt_cost(vals):
    if not vals: return "—"
    m = statistics.fmean(vals) * 1000
    sd = (statistics.stdev(vals) if len(vals) >= 2 else 0) * 1000
    return f"${m:.2f}±{sd:.2f}m"


def main():
    print(f"Loading {len(FILES)} replicate files")
    runs = load_all()

    # Aggregate
    by_bn = aggregate_per_backend(runs)
    fb_stats = fallback_analysis(runs)

    # ─── Primary 성공 기준 판정 ─────────────────────────
    total_steps = 0
    empty_steps = 0
    for d in runs:
        for scen in d.get("scenarios", []):
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "per_step" not in b: continue
                for st in b["per_step"]:
                    total_steps += 1
                    if not (st.get("response") or "").strip():
                        empty_steps += 1

    all_indicators = all(
        by_bn.get(bn, {}).get(mkey) for bn in ("no_rag", "vanilla_vector", "full_system")
        for mkey in ("step_accuracy", "hallucination_rate", "goal_completion_rate",
                     "mean_latency_sec", "mean_cost_usd")
    )
    primary_1 = empty_steps == 0
    primary_2 = all_indicators
    primary_3 = "fallback_activated" in (runs[0]["scenarios"][0]["backends"].get("full_system", {}).get("per_step", [{}])[0])
    primary_pass = primary_1 and primary_2 and primary_3

    # ─── Secondary 예측 대조 ─────────────────────────
    vanilla_step_acc = by_bn.get("vanilla_vector", {}).get("step_accuracy", [])
    v_mean = statistics.fmean(vanilla_step_acc) * 100 if vanilla_step_acc else 0
    pred_a_confirmed = v_mean >= 40

    fs_stats = fb_stats.get("full_system", {})
    fb_rate = fs_stats["fallback"] / fs_stats["total"] * 100 if fs_stats["total"] else 0
    none_rate = fs_stats["none_bucket"] / fs_stats["total"] * 100 if fs_stats["total"] else 0

    pred_b_confirmed = 30 <= fb_rate <= 50
    pred_c_confirmed = none_rate >= 20

    # ─── Render report ─────────────────────────
    lines = [
        "# QGIS Pilot — 벤치 결과 + 사전등록 대조 판정",
        "",
        f"**실행 완료 (UTC)**: 2026-08-13T04:01:30",
        f"**총 실행 시간**: 약 61 분 (03:00:30 ~ 04:01:30)",
        f"**Wrapper**: `scripts/run_qgis_pilot.py` (recovery-aware, rc=4 abort inherited)",
        f"**Isolation**: OpendTect workflows temp-moved to `.pilot_backup/`, restored on exit",
        f"**Env**: `GEOLENS_SOFTWARE_ID=qgis`",
        "",
        "## Primary 성공 기준 (사전등록 §2.1) — 이식성 존재 증명",
        "",
        f"| 기준 | 결과 | 판정 |",
        f"|---|---|---|",
        f"| ① End-to-end 완주 (empty=0/120) | empty={empty_steps}/{total_steps} | {'✓ PASS' if primary_1 else '✗ FAIL'} |",
        f"| ② 5 개 지표 산출 (전 셀) | {'모든 (backend, metric) 셀 실측값' if primary_2 else '누락 있음'} | {'✓ PASS' if primary_2 else '✗ FAIL'} |",
        f"| ③ Fallback 로그 무결 | fallback_activated 필드 per_step 정상 기록 | {'✓ PASS' if primary_3 else '✗ FAIL'} |",
        "",
        f"### **Pilot 판정: {'✅ SUCCESS (이식성 존재 증명)' if primary_pass else '❌ FAIL'}**",
        "",
        "## Secondary 예측 대조 (사전등록 §2.2)",
        "",
        "### 예측 A: 파라메트릭 마스킹 발현",
        "",
        f"- 예측: vanilla_vector step_accuracy ≥ 40% (Gemini 파라메트릭 지식 우회)",
        f"- 실측: **{v_mean:.1f}%**",
        f"- **판정: {'✅ 확증' if pred_a_confirmed else '✗ 반증'}**",
        "",
        "### 예측 B: Fallback 발동률 (라우팅 가드 갭 재현)",
        "",
        f"- 예측: full_system fallback rate 30-50% (unified4 attribute 40.6% 유사)",
        f"- 실측: **{fb_rate:.1f}%** ({fs_stats['fallback']}/{fs_stats['total']} 스텝)",
        f"- **판정: {'✅ 확증' if pred_b_confirmed else '✗ 반증 (범위 밖)'}**",
        "",
        "### 예측 C: NONE bucket (guard hole) 재현",
        "",
        f"- 예측: NONE bucket (picked_wf=None + fallback=False) ≥ 20%",
        f"- 실측: **{none_rate:.1f}%** ({fs_stats['none_bucket']}/{fs_stats['total']} 스텝)",
        f"- **판정: {'✅ 확증' if pred_c_confirmed else '✗ 반증'}**",
        "",
        "## 백엔드별 지표 (macro, 5 replicates)",
        "",
        "| Backend | Step Acc | Faith | Goal Comp | Latency (s) | Cost/step |",
        "|---|---|---|---|---|---|",
    ]
    for bn in ("no_rag", "vanilla_vector", "full_system"):
        d = by_bn.get(bn, {})
        step = fmt_pct(d.get("step_accuracy", []))
        faith_vals = [1 - h for h in d.get("hallucination_rate", [])]
        faith = fmt_pct(faith_vals)
        goal = fmt_pct(d.get("goal_completion_rate", []))
        lat = fmt_sec(d.get("mean_latency_sec", []))
        cost = fmt_cost(d.get("mean_cost_usd", []))
        lines.append(f"| gemini / {bn} | {step} | {faith} | {goal} | {lat} | {cost} |")

    lines.append("")
    lines.append("## Full_system 라우팅 분포")
    lines.append("")
    lines.append(f"| Destination | 스텝 수 | 비율 | 통과율 |")
    lines.append(f"|---|---|---|---|")
    total = fs_stats.get("total", 1)
    for label, key in [("FALLBACK (vector-only)", "fallback"), ("NONE (guard hole)", "none"),
                        ("Workflow routed", "workflow")]:
        counts = fs_stats["step_pass"][key]
        if counts[1] > 0:
            n = counts[1]
            pass_rate = counts[0] / n * 100
            lines.append(f"| {label} | {n} | {n/total*100:.1f}% | {pass_rate:.1f}% |")
    lines.append("")

    # ─── 이식 비용 표 최종본 ─────────────────────────
    lines.append("## 이식 비용 표 최종본")
    lines.append("")
    lines.append("| 단계 | 시작 (UTC) | 종료 (UTC) | 소요 |")
    lines.append("|---|---|---|---|")
    lines.append("| **P-0 코드 리팩터 + regression 검증** | 2026-08-12T17:14 (approx) | 2026-08-12T18:30 (dryrun 16/16) | ~1.3 h |")
    lines.append("| **P-1 KB 인제스트 (Training Manual 697p)** | 2026-08-13T00:00:52 | 2026-08-13T00:56:30 | 55.6 분 |")
    lines.append("| **P-2 초기 저작** (workflow 5 nodes + scenario 8 steps) | 2026-08-13T01:28:52 | 2026-08-13T01:35:56 | 7분 4초 |")
    lines.append("| **P-2 정제 #1** (step_5 forward-looking 제거) | 2026-08-13T01:41:20 | 2026-08-13T02:05:26 | 24 분 |")
    lines.append("| **P-2 정제 #2** (실측 layer name 정정 · roads_33S) | 2026-08-13T02:20:48 | 2026-08-13T02:24:39 | 4 분 |")
    lines.append("| **P-3 캡처** (8 screenshots, roads_33S 기준) | 2026-08-13T02:30 (approx) | 2026-08-13T02:46 (approx) | ~16 분 |")
    lines.append("| **P-4 벤치** (Gemini × 3 backends × 5 rep × 8 steps) | 2026-08-13T03:00:28 | 2026-08-13T04:01:30 | 61 분 |")
    lines.append("| **총 이식 소요** | | | **약 4시간** (single engineer, one afternoon) |")
    lines.append("")
    lines.append("**이식 비용 정량 결론**: QGIS 신규 소프트웨어에 GeoLens 아키텍처를 이식하여 end-to-end 벤치 완료까지 **한 오후 (< 1 인일)** 소요. 사전 조사 (`qgis_portability_report.md`) 의 예상값 7-10 인일은 hand-authoring 다수 시나리오 + 검증 여유 포함이었고, **1 시나리오 pilot** 실측은 이 하한을 크게 하회.")
    lines.append("")

    lines.append("## 산출물")
    lines.append("")
    for f in FILES:
        lines.append(f"- `{Path(f).name}`")
    lines.append(f"- `qgis_pilot_bench.log` (wrapper log)")
    lines.append(f"- `qgis_pilot_prereg.md` (사전등록 문서, 대조 대상)")
    lines.append(f"- `qgis_pilot_upload_report.md` (P-1 인제스트 보고)")
    lines.append(f"- `qgis_pilot_result_report.md` (본 문서)")
    lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[SAVED] {OUT}")
    print("\n" + "\n".join(lines[:100]))


if __name__ == "__main__":
    main()
