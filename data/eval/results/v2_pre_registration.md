# V2 결과 해석 사전 등록

**작성 시점**: Phase 1 (Gemini) 실행 중, 어떤 v2 숫자도 보기 전.
**목적**: 결과 보기 전에 판정 기준을 못 박아, "숫자에 맞춰 해석이 휘는" 확증편향 차단.

## 사전 등록된 판정 프레임

n=5 replicates × 4 models × 6 backends × 2 scenarios. 통계 단위 = replicate.
개별 Welch t / permutation p는 n=5에서 관성적으로 유의차 안 남 (α=0.05
에서 β=충분히 큼). 그래서 **효과 방향의 일관성**을 판정에 병용.

### 핵심 지표 3개 (paper Table 1 후보)

| 지표 | 방향 | 왜 중요한가 |
|------|-----|-----------|
| step_accuracy | ↑ | 매 스텝의 지시 정확도 — 사용자 체감 유효성 |
| faithfulness (=1 − hall_rate) | ↑ | 근거 있는 답변 비율 — vision-grounded RAG 존재 이유 |
| goal_completion_rate (3-gate) | ↑ | 실제로 목표 도달했는가 (utterance habit 배제 후) |

**보조 지표 3개** (design trade-off / durability 발견):
- mean_latency_sec (↓): 6-25× 비용의 크기
- mean_cost_usd (↓): cost 역설이 v2에서도 유지되는가
- fallback_rate: 커버리지 개선 후 fallback이 얼마나 줄어드는가

### 세 시나리오 (사전 등록)

#### 스토리 A — 시스템 우위 ("hybrid가 이긴다")

**조건**:
- full_system이 vanilla_vector보다 step_accuracy 또는 goal_completion에서 **최소 3/4 모델에서 방향성 우위** (개별 p 무관)
- 그중 최소 1개 모델에서 permutation p < 0.10 (효과 크기가 우연을 넘음)
- faithfulness도 최소 3/4 모델에서 full_system > vanilla_vector
- cost 역설 유지 (API 유료 모델 3/3에서 full_system이 vanilla보다 저렴)

**논문 프레이밍**: "Hybrid manual-grounded RAG with hand-authored workflow
graphs achieves faithful step-by-step guidance at reduced generation cost,
trading interactive latency for accuracy and grounding."

**Table 1 강조**: 3-지표 표에서 full_system 열이 굵게 (4모델 중 3+ 우위).
Discussion 톱: 커버리지 갭 진단 → 수정 → 우위 재현 = 벤치 진단력 자체가
기여.

#### 스토리 B — 조건부 우위 ("트레이드오프, 모델 의존성")

**조건**:
- 위 A 조건 중 **일부만** 만족 (예: faithfulness는 3/4 우위인데 step_acc는 2/4)
- 또는 특정 모델에서만 hybrid > vanilla, 다른 모델에서 뒤집힘 (Claude
  hallucination 비대칭 같은 패턴이 v2에서도 유지)
- cost 역설은 유지

**논문 프레이밍**: "Hybrid RAG shows model-specific benefits — pronounced
faithfulness gains in Gemini/GPT/Qwen, absent or reversed in Claude —
paired with a robust cost-vs-latency trade-off. We characterize where the
architecture pays off and where it doesn't."

**Table 1 강조**: 모델별 승패 매트릭스 + cost 역설. Discussion 톱: "무관
컨텍스트에 대한 모델별 강건성"이 실제 논문 기여로 승격.

#### 스토리 C — 여전히 비등 ("천장 효과, 시나리오 확장 필요")

**조건**:
- 4모델 중 hybrid 우위가 2/4 이하 (지표 3개 통틀어)
- 즉 커버리지 수정 후에도 hybrid 이득 미미

**논문 프레이밍**: "On two-scenario OpendTect subset, RAG variants
(vanilla + hybrid) converge to a ceiling; we identify goal_completion
verification and cost-per-instruction as durable positive findings, and
outline scenario diversification as the next testbed."

**Action**: Table 1은 결과 그대로 정직히. cost 역설이 헤드라인으로 승격.
attribute_computation 시나리오 추가 (task #26 부활)가 논문 결론의
"future work"에서 "논문 완성 필수"로 이동.

### 방향 일관성 스코어링 규칙 (n=5 보완)

각 지표별로:
- `full_system > vanilla` (더 나은 방향)인 모델 수 카운트
- 4/4 = "일관 우위", 3/4 = "다수 우위", 2/4 = "혼재", ≤1/4 = "역효과"

지표 3개 × 방향 카운트로 매트릭스 작성. 이 매트릭스가 A/B/C 판정의 근거.

### 사전 등록된 "예상 밖" 경계선

이 결과가 나오면 **재조사** (해석 서두르지 말 것):
- Gemini에서 이전 낮은 fallback rate과 크게 다르게 대량 fallback 발동 (rerank 문제 재점화 신호)
- 어느 모델이든 no_rag가 full_system을 step_accuracy에서 유의하게 이김 (RAG가 오히려 방해)
- goal_completion이 모든 모델·백엔드 조합에서 0.500 근처로 완벽히 평평 (지표 재설계 자체가 힘 없는 신호)
- cost 역설이 뒤집힘 (workflow context가 generator 출력을 오히려 늘림)

### durable findings (v2 결과와 무관하게 살아남는 관찰)

프레이밍이 A/B/C 어디로 가든 이 두 개는 논문에 남는다:

1. **Goal completion의 3-gate 재설계 (methods 기여)**: sentinel-only 채점의
   결함 진단 → 재설계 → 재채점. utterance habit vs screen observation
   구분이 자체로 벤치 설계 교훈.
2. **Cost 역설 (v1에서 관측, v2에서 유지 여부 확인 대상)**: workflow
   context가 generator 출력을 짧게 만들어 hybrid가 API-priced 모델에서
   vanilla보다 저렴 — RAG 시스템 설계 일반 원칙.

Claude hallucination 비대칭 (+12.5pp)은 v2에서 유지되어야 discussion감.
v2에서 사라지면 v1의 커버리지 결함으로 재분류.

## 사전 등록의 서명

이 문서는 v2 결과를 보기 전에 작성됨. 이후 결과가 어떻게 나오든 이
문서의 기준을 적용해 A/B/C 판정. 판정 결과가 A/B/C 어디에 해당하는지는
v2 표를 이 기준에 대조해 결정.
