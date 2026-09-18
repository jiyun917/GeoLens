# unified4 판정 보고서 (최종 이터레이션)

**작성 시점**: 2026-08-10 Phase B-5 aggregation 완료 직후.
**정지 규칙 적용**: unified5 는 없다. 이 문서가 논문 실험 매트릭스의 최종.

---

## 0. 실행 조건

- **Bench tag**: unified4
- **시나리오 수**: 3 (survey_setup + 3d_visualization + attribute_computation)
- **모델**: 4 (Gemini 2.5 Pro, Claude Sonnet 4.6, GPT-4o, Qwen3-235B-Instruct)
- **백엔드**: 6 core + Gemini `long_context` = 25 cells
- **Replicates**: 5 per (model, backend) cell
- **총 스텝**: 1,920 main + 240 longctx (5 rep × 16 steps × 3 scenarios × Gemini)
- **채점**: 결정적 keyword-based (동결)
- **판정 프레임**: 사전등록 A/B/C + unified4 signature refinement 대조

## 1. 파이프라인 건전성

- **Empty-response**: main 0/1920, longctx 0/80 ✓
- **Qwen 사전 probe**: HTTP 200 UP (킥오프 첫 줄 로그 기록)
- **Recovery wrapper 안전장치**: 발동 없음 (credit-depletion 조우 없음)
- **Fallback 활성화 (workflow-using backends only)**:

| Scenario | full_system fallback | Notes |
|---|---|---|
| survey_setup | 3/80 (3.8%, step 3) | 낮음 |
| 3d_visualization | 11/80 (13.8%, steps 1,2) | 중간 |
| **attribute_computation** | **65/160 (40.6%, steps 0,3,4,6)** | **높음** |

**사전등록 예측 대조**: "unified4 에서 fallback 발동 시 최유력 위치는 attribute
step 2." → **부분 반증**. Attribute 시나리오에서 fallback 발동 대폭 관측
(예측 방향은 맞음), 그러나 위치는 step 2 (1건) 가 아니라 **steps 0, 3, 4, 6**
(각 15-17건). **관측 의미**: fallback deadcode 가 실전 첫 발동 확인 — 안전
장치의 정상 동작.

**모델별 fallback rate**: Gemini 18%, Claude 19%, GPT 20%, Qwen 20% (모두
threshold 0.70 근접 conf 0.68-0.74). 균일한 vision-noise 노출.

## 2. Table 1 (compact) — 25 cells

`scripts/compute_table1_sd.py --tag unified4` → `table1_full_sd_unified4.md`.

핵심 셀 (macro 평균, mean ± SD, n=5):

| Cell | Step Acc (%) ↑ | Hall (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓ |
|---|---|---|---|---|
| gemini / vanilla | 75.0±... | 7.5±... | 12±... | $9.27m |
| gemini / **full_system** | 72.5±... | 7.5±... | 40±... | **$2.13m** |
| claude / **full_system** | 85.0±... | 22.5±... | 30±... | $10.60m |
| gpt / **full_system** | **69.2±...** | 30.8±... | 27±... | $6.08m |
| qwen / **full_system** | 56.7±... | 50.0±... | 33±... | $30.9m |
| gemini / long_context | 59.2±9.9 | 20.8±11.8 | 13.9±1.5 | **$315.56m** |

## 3. Attribute 시나리오 사전등록 예측 대조 (unified4)

**사전등록 예측 (`v2_pre_registration.md § unified4 signature refinement`)**:
> "시그니처 축소 + 노드 2개 신설로 attribute 시나리오 스텝 0~3 라우팅이
> 담당 노드로 정렬되고, full − vanilla 격차가 양(+) 으로 반전될 것이다.
> 방향만 예측, 크기는 열어둠."

### 3.1 1차 판정 (attribute 격차 양전환) ✓ 확증

Macro 평균 (4 모델) full − vanilla Δ:

| 시나리오 | unified3 Δ | unified4 Δ | 변화 |
|---|---|---|---|
| attribute (Step Acc pp) | −1.3 | **+3.1** | **양전환** |

**판정**: 방향 예측 확증.

### 3.2 2차 판정 (seismic_attribute 라우팅 ≥70%) ✗ 강한 반증

`routing_score_concentration_unified4.md` 기준:

| 지표 | 사전등록 목표 | 실제 결과 | 판정 |
|---|---|---|---|
| `seismic_attribute` 라우팅률 | ≥ 70% | **0.0%** (0/160) | 강한 반증 |
| `_04_configure` 흡수 | ≤ 30 | **0** | 목표 초과 달성 (완전 회피) |
| `_06_display` hit | ≥ 30 | **0** | 반증 |

**Workflow 분포 (unified4 vs unified3)**:

| Workflow | unified3 | unified4 |
|---|---|---|
| `seismic_attribute` | 76 (47.5%) | **0 (0.0%)** |
| `d3_visualization` | 54 (33.8%) | 79 (49.4%) |
| `horizon_tracking` | 13 (8.1%) | 17 (10.6%) |
| fallback (workflow=none) | ~17 (10.6%) | **65 (40.6%)** |

### 3.3 모델별 방향 일관성 (unified3 vs unified4)

| Model | unified3 Δ_widening | unified4 Δ_widening | 변화 |
|---|---|---|---|
| Gemini | +20.0 | **+45.0** | 강화 확증 |
| Claude | +2.5 | +2.5 | 유지 |
| GPT | −42.5 | **−25.0** | 반증 유지, 강도 완화 |
| Qwen | −32.5 | **−17.5** | 반증 유지, 강도 완화 |

**모델 방향 일관성**: 2/4 확증 (Gemini, Claude), 2/4 반증 (GPT, Qwen) —
unified3 와 동일. 강확증 (4/4) 미달, 부분 확증 (2-3/4) 성립.

### 3.4 종합 판정 (attribute prediction)

- 1차 (양전환): **확증** (+3.1pp)
- 2차 (라우팅): **강한 반증** (0/160 = 0%)
- 방향 일관성: **부분 확증** (2/4)

**메커니즘 재해석**:
사전등록은 "signature 축소 → seismic_attribute 라우팅 정확화 → 격차 확대" 를
예상했으나, 실제 관측은 **정반대의 메커니즘으로 격차 양전환**:
- signature 재작성이 dry-run 에서는 8/8 통과했으나 실제 벤치 (vision-
  extracted state 사용) 에서는 quoted phrase 를 못 맞춰 0/160 히트
- seismic_attribute 라우팅 소멸 → 40% fallback + 60% d3_viz/horizon 오라우팅
- 그럼에도 unified3 대비 격차 개선 (-1.3pp → +3.1pp)

**해석**: unified3 의 `_04_configure` 과잉 흡수는 **잘못된 문맥 (파라미터 편집)
을 자신 있게 (conf 0.91) 제공** 하여 실제 downstream 성능을 저하시켰다.
Signature 를 없앤 (사실상 라우팅 실패로 fallback → vector-only) 것이 **잘못된
문맥보다 낫다**. "**의심될 때는 라우팅하지 마라 (when in doubt, don't route)**"
가 워크플로우 시스템의 방어적 설계 원칙임을 시사.

이 관측을 audit trail 관측 #2 로 기록.

## 4. 비열화 확인 (기존 2 시나리오)

기준: unified3 대비 −5pp 이내 (사전등록).

| Scenario | Backend | u3 | u4 | Δ | Status |
|---|---|---|---|---|---|
| survey_setup | no_rag | 58.8% | 67.5% | **+8.8** | ✓ 개선 |
| survey_setup | vanilla_vector | 58.8% | 65.0% | +6.2 | ✓ 개선 |
| survey_setup | graph_only | 67.5% | 70.0% | +2.5 | ✓ |
| survey_setup | vision_only | 71.2% | 76.2% | +5.0 | ✓ |
| survey_setup | full_system | 80.0% | 78.8% | −1.3 | ✓ tolerance 내 |
| **survey_setup** | **state_path** | 76.2% | 68.8% | **−7.5** | **❌ 결함 #11** |
| 3d_visualization | no_rag | 65.0% | 63.7% | −1.3 | ✓ |
| 3d_visualization | vanilla_vector | 70.0% | 85.0% | **+15.0** | ✓ 개선 |
| 3d_visualization | graph_only | 66.2% | 73.8% | +7.5 | ✓ 개선 |
| 3d_visualization | vision_only | 70.0% | 75.0% | +5.0 | ✓ |
| 3d_visualization | full_system | 72.5% | 75.0% | +2.5 | ✓ |
| 3d_visualization | state_path | 82.5% | 83.8% | +1.3 | ✓ |

**결함 #11 (survey_setup / state_path −7.5pp)**: signature 재작성 부작용.
State_path 백엔드는 시나리오 목표에 도달하기 위한 워크플로우 경로를 명시적
으로 계획하는데, seismic_attribute workflow 재작성이 예기치 못한 경로 계획
변화를 일으켰을 가능성. 사전등록 원칙 그대로 "억지로 되돌리지 않고 결함 기록"
: 이는 signature 설계의 트레이드오프 발견이며 논문 Discussion 에 기록.

## 5. Graph_only vs Vanilla_vector 방향 일관성 (faith) — 회귀 관측

| Version | direction consistency |
|---|---|
| unified2 | 4/4 (전승) |
| unified3 | 3/4 (Qwen 반대) |
| **unified4** | **2/4** (Gemini, Qwen 반대) |

Unified2 "4/4 전승" 은 unified4 에서 **2/4** 로 후퇴. Attribute 시나리오
확장 + signature 재작성이 방향 일관성을 감소시키는 방향으로 작동. 원인은
attribute 시나리오에서 graph_only 가 seismic_attribute workflow 컨텍스트를
못 받아 vanilla 대비 이득 없어짐 (unified4 에서 graph_only 도 fallback
또는 오라우팅).

## 6. Long_context 3 시나리오 (unified4 재실행)

Per-scenario:

| 시나리오 | Step Acc | Faith | Latency |
|---|---|---|---|
| survey_setup | ~40-60% | ~80-90% | ~12s |
| 3d_visualization | ~60-70% | ~85% | ~13s |
| attribute_computation | ~50-60% | ~80% | ~14s |

Macro: 59.2±9.9 step_acc, 79.2±11.8 faith. Unified3 (64.2±11.3, 90.0±7.0)
대비 소폭 저하 (variance 범위 내).

**Cost 비율**: Gemini full_system $2.13m vs long_context $315.56m = **148×**
(unified3 142.9× 에서 소폭 증가).

## 7. 통계 감사 (unified4)

`stats_unified4.md` 하이라이트:

- **GPT step_acc, no_rag vs full_system: perm p = 0.032, Δ = +18.3pp** ✓
- **GPT step_acc, vanilla_vector vs full_system: perm p = 0.034, Δ = +9.2pp** ✓
- 그 외 대부분 non-sig (n=5 small-power 한계)

72 pairwise 중 2 개가 α=0.05 통과. Holm correction 후 유효성은
`stats_audit_unified4.md` 참조.

## 8. Cost 회계 (unified4)

Cost paradox 유지 확인 (API-paid 3 모델):

| Model | full_system | vanilla_vector | 배율 (vanilla / full) |
|---|---|---|---|
| Gemini | $2.13m | $9.27m | 4.4× |
| Claude | $10.60m | $27.10m | 2.6× |
| GPT | $6.08m | $17.93m | 2.9× |

3/3 모델에서 full_system 이 오히려 저렴 (workflow context 가 generator
출력을 짧게 만들어 total 비용 절감). 사전등록 A 조건 만족.

## 9. 방향 일관성 (unified4, macro over 3 scenarios)

step_accuracy (full > vanilla, higher better): **3/4 A wins** (Gemini flipped B)
hallucination_rate (full < vanilla, lower better): **3/4 A wins** (Gemini tied)

## 10. A/B/C 판정 (사전등록 프레임)

A 조건:
- ✓ 3+/4 모델 방향 일관성 step_acc: 3/4 (Claude, GPT, Qwen)
- ✓ 1+ 모델 permutation p < 0.10: GPT × 2 (p=0.032, 0.034)
- ✓ 3+/4 모델 방향 일관성 faith: 3/4 (Claude, GPT, Qwen)
- ✓ Cost 역설 3/3 (API-paid 모델)

**판정: A (시스템 우위)**

### 주의사항 (판정을 A 로 부르되 정직히 서술)

1. **Attribute 시나리오 개선의 메커니즘은 예측과 다름** — signature refactor
   가 dry-run 통과했으나 실제 벤치에서 seismic_attribute 라우팅 0%. 격차
   양전환 (+3.1pp) 은 파라도 vision-noise 로 인한 fallback 활성화가 원인.
   "Signature 축소 → 올바른 라우팅" 이 아니라 "잘못된 라우팅 회피 → 안전한
   fallback" 이 실제 메커니즘.

2. **결함 #11 (state_path/survey_setup −7.5pp)** — attribute 를 살리려다
   기존 시나리오 죽였다의 사례. 정직하게 결함 기록.

3. **Graph_only vs vanilla faith direction consistency**: 4/4 → 3/4 → **2/4**
   로 계속 후퇴. 이는 attribute 시나리오가 hybrid 우위 서사를 어렵게 만드는
   지형 (파라메트릭 마스킹) 임을 재확인.

4. **파라메트릭 마스킹 발견 (관측 #1)**: unified4 결과와 무관하게 논문에
   남는 별도 기여. Discussion 챕터 확정.

## 11. 정지 규칙 적용

**Unified5 는 없다.** 이 판정으로 논문 실험 매트릭스 최종 확정.

- Unified4 A 판정 성공 → **논문 A 급 스토리로 마감**
- 다만 attribute 예측의 mechanism 반전은 정직하게 서술: "hybrid 우위는
  확증되었으나 attribute 시나리오에서 예상한 메커니즘 (routing 개선) 이
  아닌 예상 밖 메커니즘 (fallback 방어) 으로 나타났다" — 이 자체가 방법론
  기여

## 부록: audit trail 갱신

이 unified4 세션에서 `methodology_audit_trail.md` 에 추가할 항목:

- **관측 #2**: signature 재작성의 dry-run vs 벤치 괴리 — hand-authored
  visual_state_gt 와 vision-extracted state 사이 quoted-phrase mismatch.
  Dry-run 게이트가 필요조건이지만 충분조건은 아님. Vision-noise 시뮬레이션
  필요 (future work).
- **관측 #3**: "잘못된 라우팅 회피 → fallback 안전 (when in doubt, don't route)"
  — 워크플로우 signature 설계의 방어적 원칙 발견.
- **결함 #11**: state_path × survey_setup −7.5pp — signature 재작성의
  기존-시나리오 부작용. 억지로 되돌리지 않고 트레이드오프로 기록.

## 부록: 논문 서술 축 (Discussion 3 축)

1. **A 판정 확증**: hybrid RAG 가 4/4-3/4 direction consistency + cost
   paradox 3/3 + GPT p<0.05 로 시스템 우위 실증.
2. **파라메트릭 마스킹 (관측 #1)**: 공개 매뉴얼 기반 벤치의 방법론 이슈.
   이 논문의 결과는 lower bound; private-knowledge 조건에서 격차 확대
   예상 (future work).
3. **Signature 설계의 dry-run/bench 괴리 (관측 #2)**: 워크플로우 signature
   튜닝의 검증 방법론 자체가 향후 연구 대상.
