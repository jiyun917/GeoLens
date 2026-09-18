# 검증 #2 — 라우팅 실패 vs step_match 하락 집중

**대상**: `opendtect__attribute_computation__01` × `full_system` × 4 모델 × 5 replicates.
**총 스텝**: 160 (8 스텝 × 4 × 5 = 160).

## 1. 라우팅 성공 vs 실패 스텝 accuracy 격차

| 조건 | 스텝 수 | step_match 통과율 | hallucination 발생률 |
|---|---|---|---|
| ✅ `seismic_attribute` 라우팅 성공 | 76 | **48.7%** | 44.7% |
| ❌ 다른 workflow 오라우팅 | 67 | **73.1%** | 14.9% |
| **격차 (성공 − 실패)** | — | **-24.5pp** | +29.8pp |

## 2. 스텝별 라우팅 분포 + step_match 통과율

| step_index | 라우팅 분포 (wf: count) | 이 스텝 통과율 | `seismic_attribute` 통과율 | 오라우팅 통과율 |
|---|---|---|---|---|
| 0 | seismic_attribute: 20 | 80% | 80% (n=20) | — |
| 1 | seismic_attribute: 20 | 5% | 5% (n=20) | — |
| 2 | seismic_attribute: 9, none: 8, d3_visualization: 3 | 30% | 33% (n=9) | 33% (n=3) |
| 3 | seismic_attribute: 20 | 60% | 60% (n=20) | — |
| 4 | horizon_tracking: 13, seismic_attribute: 7 | 75% | 71% (n=7) | 77% (n=13) |
| 5 | d3_visualization: 20 | 55% | — | 55% (n=20) |
| 6 | d3_visualization: 20 | 80% | — | 80% (n=20) |
| 7 | d3_visualization: 11, none: 9 | 95% | — | 100% (n=11) |

## 3. 라우팅 노드별 통과율

| picked_node_id | 스텝 수 | 통과율 | 평균 confidence |
|---|---|---|---|
| `seismic_attribute_04_configure` | 76 | 49% | 0.91 |
| `d3_visualization_01_main_window_ready` | 48 | 69% | 0.68 |
| `none` | 17 | 59% | 0.00 |
| `horizon_tracking_08_save` | 13 | 77% | 0.61 |
| `d3_visualization_05_all_slices_displayed` | 6 | 100% | 0.60 |

## 4. 레버 1 성립 판정

**레버 1 미성립**. 격차 -24.5pp — 라우팅 정오와 통과율이 거의 무관. 문제는 라우팅이 아니라 (a) 8-스텝 합성 자체의 난이도, (b) 파라메트릭 지식으로 vanilla 도 우회 가능한 스텝 정답 구조. → 레버 2 (파라메트릭 마스킹 조건 시나리오) 로 이동 권장.

## 5. Signature 수리 우선순위 (오라우팅 top 노드)

| 오라우팅 노드 | 오라우팅 스텝 수 | 이 노드로 간 스텝 통과율 |
|---|---|---|
| `d3_visualization_01_main_window_ready` | 48 | 69% |
| `horizon_tracking_08_save` | 13 | 77% |
| `d3_visualization_05_all_slices_displayed` | 6 | 100% |

→ 위 노드로 흡수되는 스텝들에 대해 `seismic_attribute` 워크플로우 의 대응 노드 signature 를 강화하는 것이 다음 액션.

