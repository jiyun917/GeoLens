# QGIS Pilot — 벤치 결과 + 사전등록 대조 판정

> **주석 (V3-9, 2026-09-18)**: 이 문서의 unified2–4 `full_system`(및 `state_path`) 수치는 linked_chunks 본문 없이 측정된 것이다. 2026-07-27 재인제스트 이후 워크플로우 JSON의 linked_chunks id가 전부 인덱스에 없었고, graph_context에는 노드 제목·설명 벡터 검색 결과만 들어갔다. 상세: `methodology_audit_trail.md` V3-9.

**실행 완료 (UTC)**: 2026-08-13T04:01:30
**총 실행 시간**: 약 61 분 (03:00:30 ~ 04:01:30)
**Wrapper**: `scripts/run_qgis_pilot.py` (recovery-aware, rc=4 abort inherited)
**Isolation**: OpendTect workflows temp-moved to `.pilot_backup/`, restored on exit
**Env**: `GEOLENS_SOFTWARE_ID=qgis`

## Primary 성공 기준 (사전등록 §2.1) — 이식성 존재 증명

| 기준 | 결과 | 판정 |
|---|---|---|
| ① End-to-end 완주 (empty=0/120) | empty=0/120 | ✓ PASS |
| ② 5 개 지표 산출 (전 셀) | 모든 (backend, metric) 셀 실측값 | ✓ PASS |
| ③ Fallback 로그 무결 | fallback_activated 필드 per_step 정상 기록 | ✓ PASS |

### **Pilot 판정: ✅ SUCCESS (이식성 존재 증명)**

## Secondary 예측 대조 (사전등록 §2.2)

### 예측 A: 파라메트릭 마스킹 발현

- 예측: vanilla_vector step_accuracy ≥ 40% (Gemini 파라메트릭 지식 우회)
- 실측: **62.5%**
- **판정: ✅ 확증**

### 예측 B: Fallback 발동률 (라우팅 가드 갭 재현)

- 예측: full_system fallback rate 30-50% (unified4 attribute 40.6% 유사)
- 실측: **0.0%** (0/40 스텝)
- **판정: ✗ 반증 (범위 밖)**

### 예측 C: NONE bucket (guard hole) 재현

- 예측: NONE bucket (picked_wf=None + fallback=False) ≥ 20%
- 실측: **0.0%** (0/40 스텝)
- **판정: ✗ 반증**

## 백엔드별 지표 (macro, 5 replicates)

| Backend | Step Acc | Faith | Goal Comp | Latency (s) | Cost/step |
|---|---|---|---|---|---|
| gemini / no_rag | 62.5±8.8 | 90.0±13.7 | 100.0±0.0 | 10.3±1.7 | $0.87±0.01m |
| gemini / vanilla_vector | 62.5±8.8 | 82.5±19.0 | 100.0±0.0 | 10.2±1.2 | $4.69±0.02m |
| gemini / full_system | 57.5±6.8 | 87.5±12.5 | 100.0±0.0 | 53.6±4.9 | $2.45±0.02m |

## Full_system 라우팅 분포

| Destination | 스텝 수 | 비율 | 통과율 |
|---|---|---|---|
| Workflow routed | 40 | 100.0% | 57.5% |

## 이식 비용 표 최종본

| 단계 | 시작 (UTC) | 종료 (UTC) | 소요 |
|---|---|---|---|
| **P-0 코드 리팩터 + regression 검증** | 2026-08-12T17:14 (approx) | 2026-08-12T18:30 (dryrun 16/16) | ~1.3 h |
| **P-1 KB 인제스트 (Training Manual 697p)** | 2026-08-13T00:00:52 | 2026-08-13T00:56:30 | 55.6 분 |
| **P-2 초기 저작** (workflow 5 nodes + scenario 8 steps) | 2026-08-13T01:28:52 | 2026-08-13T01:35:56 | 7분 4초 |
| **P-2 정제 #1** (step_5 forward-looking 제거) | 2026-08-13T01:41:20 | 2026-08-13T02:05:26 | 24 분 |
| **P-2 정제 #2** (실측 layer name 정정 · roads_33S) | 2026-08-13T02:20:48 | 2026-08-13T02:24:39 | 4 분 |
| **P-3 캡처** (8 screenshots, roads_33S 기준) | 2026-08-13T02:30 (approx) | 2026-08-13T02:46 (approx) | ~16 분 |
| **P-4 벤치** (Gemini × 3 backends × 5 rep × 8 steps) | 2026-08-13T03:00:28 | 2026-08-13T04:01:30 | 61 분 |
| **총 이식 소요** | | | **약 4시간** (single engineer, one afternoon) |

**이식 비용 정량 결론**: QGIS 신규 소프트웨어에 GeoLens 아키텍처를 이식하여 end-to-end 벤치 완료까지 **한 오후 (< 1 인일)** 소요. 사전 조사 (`qgis_portability_report.md`) 의 예상값 7-10 인일은 hand-authoring 다수 시나리오 + 검증 여유 포함이었고, **1 시나리오 pilot** 실측은 이 하한을 크게 하회.

## 산출물

- `run_gemini_qgis_pilot_r1_20260813T030032.json`
- `run_gemini_qgis_pilot_r2_20260813T031357.json`
- `run_gemini_qgis_pilot_r3_20260813T032511.json`
- `run_gemini_qgis_pilot_r4_20260813T033833.json`
- `run_gemini_qgis_pilot_r5_20260813T035023.json`
- `qgis_pilot_bench.log` (wrapper log)
- `qgis_pilot_prereg.md` (사전등록 문서, 대조 대상)
- `qgis_pilot_upload_report.md` (P-1 인제스트 보고)
- `qgis_pilot_result_report.md` (본 문서)

