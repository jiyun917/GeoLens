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

---

## unified3 attribute_computation 시나리오 예측 (2026-08-06 사전등록)

**작성 시점**: attribute_computation 시나리오 캡처 완료 직후, unified3
벤치 실행 전. 어떤 unified3 숫자도 보기 전.

**핵심 예측**: **attribute 시나리오는 vector 유사도가 무너지는 지형에서
그래프 라우팅이 검색을 구조하는가를 검증하는 실험** — 이 시나리오의
결과가 논문의 hybrid 우위 주장에 메커니즘 증거를 제공.

### 예측 진술 (unified3 결과 보기 전에 못박음)

> "attribute 시나리오에서 vanilla_vector의 retrieval hit가 이론
> 페이지(§1.5.1)로 쏠려 step acc·faithfulness가 저조할 것,
> full_system은 workflow 라우팅으로 절차 청크(p118~120)를 확보해
> 격차가 기존 2개 시나리오보다 벌어질 것."

### 예측의 근거

라이브 관측 (2026-08-06, 캡처 세션 중 GeoLens 대화형 사용):
- 인덱스에는 §1.5.1a 절차 청크(pages 118~128, 11개) 존재 확인
- 하지만 한글 쿼리로 vector 유사도 검색 시 §1.5.1 이론 페이지(p117,
  hydrocarbons/seismic response 등 도메인 term 풍부)로 쏠림
- 결과: 라이브 GeoLens 응답이 "녹색 A 아이콘 클릭" 등 매뉴얼에 없는
  UI 요소를 지시함 (retrieval 컨텍스트가 이론 페이지 → 모델이
  hallucinated action 생성)
- KG 트리플렛도 지질학 도메인 30+개가 노이즈로 섞임

### 예상 정량 결과

| 지표 | 예측 방향 | 크기 |
|---|---|---|
| vanilla_vector Step Acc (attribute) | 기존 2개 시나리오 대비 저하 | 예: 60% → 30% 이하 |
| vanilla_vector Faithfulness (attribute) | 기존 2개 시나리오 대비 저하 | 예: 75% → 40% 이하 |
| full_system Step Acc (attribute) | vanilla 대비 유의한 우위 | 예: full 55%+ vs vanilla 30% |
| full_system − vanilla Δ (attribute) | 기존 2개 시나리오 Δ보다 큼 | 시나리오 복잡도 축 vs. 격차 |

### 예측 확증 판정 기준 (사전 고정)

1. **격차 확대**: `(full − vanilla) attribute Δ > (full − vanilla) 기존 시나리오 평균 Δ`
   → 매크로 평균 기준으로 attribute 시나리오의 hybrid 우위가 기존
   시나리오보다 크면 예측 확증.
2. **retrieval attribution**: unified3 실행 중 vanilla_vector 의
   per-step retrieval 로그에서 attribute 시나리오의 top-1 페이지가
   §1.5.1 (p117) 또는 인접 non-procedural 페이지로 쏠리는지 확인.
   실제로 쏠리면 예측의 메커니즘 확증.
3. **full_system의 라우팅**: attribute 시나리오의 full_system
   per-step `picked_workflow_id` 가 `seismic_attribute` 워크플로우
   (p118~120 절차 청크와 연결) 로 안정적으로 라우팅되는지 확인.

### 예측 반증 시 대응

만약 예측 반증 (attribute 시나리오에서 vanilla 도 잘 하거나, full 도
못 함) 시:
- vanilla 잘함 → 한글 쿼리로도 §1.5.1a 절차가 잘 검색됨 → 예측의
  라이브 관측이 GeoLens 대화형 세션 특수성이었음. 정직하게 보고.
- full 못함 → workflow 라우팅이 attribute 시나리오에서도 절차 청크를
  못 찾음 → hybrid 우위 주장 자체 재검토 필요. limitations 강화.

### 혼입 변수 명시 (교수님 보고 대비 사전등록)

교수님 보고 프레임은 "복잡한 워크플로우에서 격차 확대"이나, 관측된
실패의 실제 축은 스텝 수가 아니라 **한글 쿼리 ↔ 영문 매뉴얼의
교차언어 유사도가 이론/절차 페이지를 구분 못 하는** 것. Discussion 서술:

- **일차 관찰**: attribute 시나리오는 (a) 스텝 수 8개로 기존 4개보다
  많고, (b) 매뉴얼 §1.5의 이론+절차 혼재로 vector 검색 취약성 노출.
- **정확한 서술**: "복잡한 챕터일수록 이론·절차가 혼재해 vector 검색이
  취약해진다. hybrid는 workflow 그래프 라우팅으로 절차 청크를 명시적
  선택함으로써 이 취약성을 우회한다."
- **언어 혼입 처리 (Limitations)**: "쿼리 한글, 매뉴얼 영문의 교차언어
  조건은 한국 실사용 환경 반영. 단일언어 조건과의 분리는 향후 과제."

### 리트리버 튜닝 금지 (사전등록)

발견된 vanilla vector 취약성 (한글 쿼리 → 이론 페이지 쏠림) 을 실험 전
수정 금지. 이유:
- 지금 고치면 이 발견이 사라짐 (vanilla 무너지는 것을 측정하는 게
  실험 가치)
- 튜닝 (이중언어 임베딩, BM25 하이브리드) 은 unified3 결과 확인 후
  future work 또는 후속 실험 트랙

### 쿼리 언어 일관성

`bench_backends.py:backend_vanilla_vector` 는 `scenario.goal` 을 query
로 사용. 3개 시나리오 모두 goal 필드가 한글로 작성됨 → **시나리오 간
쿼리 언어 조건 동일** → 시나리오 간 비교 성립. (2026-08-06 확인)

---

## unified4 signature refinement 예측 (2026-08-07 사전등록)

**작성 시점**: unified3 판정 확정 + routing_score_concentration 결과 확인 후,
seismic_attribute workflow signature 재작성 **직전**. 어떤 unified4
숫자도 보기 전.

### 사전등록의 근거가 된 unified3 진단

`routing_score_concentration_unified3.md` 에서 발견:
- `seismic_attribute_04_configure` 노드가 스텝 0-3 을 confidence 0.91 로
  전부 흡수 (76 hit), 하지만 이 노드로 라우팅된 스텝의 통과율은 48.7%
  vs 오라우팅 스텝의 73.1% — **성공 라우팅이 오히려 더 못함** 역설
- 스텝 1 (Attribute Set 3D 창 오픈) 이 `_04_configure` 로 잡혔지만
  통과율 **5%** — 결정적 실패점
- `_06_display` 는 0 hit (스텝 5-7 이 모두 d3_visualization 으로 흡수)
- 즉 시그니처가 **넓어서** 자기 담당 범위를 넘어 흡수하는 것이 문제
  (원래 예상한 "signature 부족으로 다른 workflow 로 새는" 것의 정반대)

### unified4 signature 수리 방향 (사전 확정)

1. **`_04_configure` 축소**: "Attribute Set 3D 창의 파라미터 편집 (Time
   gate, Compute gradient, Attribute Name) + Add as new + Save on Close
   체크 + Save Attribute Set 다이얼로그 저장" 만 담당. Attribute Set 3D
   창 자체를 여는 스텝은 담당 X.
2. **신규 노드 `_02_open_attribute_tool` (or 축소된 `_02`)**: "toolbar
   Attribute 3D icon 클릭, Attribute Set 3D 창 오픈, Attribute Type
   dropdown 조작" 담당. 스텝 0, 1 을 위한 별도 노드.
3. **`_06_display` signature 강화**: "inline number 우클릭, Add >
   Attribute submenu, Select dialog (Attributes radio, on-the-fly),
   Energy layer 렌더링, Color Bar" 명시. 스텝 5, 6, 7 을 흡수.
4. **`d3_visualization_01_main_window_ready` signature 는 그대로 유지** —
   현재 스텝 5-7 을 흡수하지만 통과율이 55/80/95% 로 우수. 이 라우팅을
   막지 않고, `_06_display` 가 이보다 더 관련성 높게 signature 매칭되도록
   조정만 함.

### 예측 진술 (unified4 결과 보기 전에 못박음)

> "시그니처 축소 + 노드 2개 신설 (또는 재정의) 로 attribute 시나리오
> 스텝 0~3 의 라우팅이 담당 노드로 정렬되고, attribute step_acc 가
> 회복되어 full − vanilla 격차가 **양(+) 으로 반전**될 것이다. 반전의
> 크기는 열려 있고, 방향만 예측한다."

**중요**: `routing_score_concentration_unified3.md § 4` 의 "회복 상한
+10.7pp" 는 스텝 1/2/3 이 모두 correct-routing 통과율로 이동한 가정
하의 **상한값 (upper bound) 이지 예측값이 아니다**. 예측은 방향 (양전환)
만이고, 실제 크기가 상한 미달이더라도 방향이 맞으면 확증.

### 예측 확증 판정 기준 (사전 고정)

**1차 판정 (attribute 시나리오, macro 평균 4 모델)**:
- **확증**: `(full_system − vanilla_vector) attribute Step Acc Δ > 0` (양전환)
- **강확증**: 위 + 4/4 모델 방향 일관성 (전 모델 확증)
- **부분 확증**: 위 + 2-3/4 모델 방향 일관성
- **반증**: `Δ ≤ 0` 유지 (음전환 or 0 근처)

**2차 판정 (라우팅 자체)**:
- attribute 시나리오 `full_system` 스텝 중 `seismic_attribute` 워크플로우
  라우팅률: 현재 47.5% → **≥ 70%** 이면 signature 수리 성공
- `_04_configure` 로 흡수되는 스텝: 현재 76 → **≤ 30** (스텝 2-4 전용)
- `_06_display` hit: 현재 0 → **≥ 30**

### 예측 반증 시 대응 (사전 확정)

만약 unified4 에서 격차 여전히 음이거나 0 근처면:
- 라우팅률이 목표 (≥70%) 를 만족했음에도 반전 실패 → **레버 1 무효 확정**.
  Downstream 합성 한계 or 파라메트릭 지식 상쇄 효과가 근본 원인.
- 라우팅률 자체가 목표 미달 → signature 재작성이 부정확했다는 뜻.
  이 경우도 이번 논문에서는 unified4 결과 그대로 보고, **unified5 는 없음**.
- 두 경우 모두: 논문은 B 판정 + 파라메트릭 마스킹 발견 + signature
  refinement 시도 및 실패 기록을 정직하게 서술.

### 재실행 스코프 (사전 확정)

**Graph 노드 수정은 지식 베이스 변경 = 시스템 버전 변경**. 따라서
unified4 는 **전 매트릭스 재실행**:
- 4 모델 × 6 core backends × 5 replicates × 3 시나리오 = 1,920 스텝
- Gemini × long_context × 5 replicates × 3 시나리오 = 240 스텝
- 실행 전 dry-run 게이트: **기존 16/16 유지 + 신규 attribute 8/8 통과**
  둘 다 만족해야 킥오프.
- 실행 순서: qwen (NAS 상태 의존성) → gpt → gemini → claude → longctx
- Recovery wrapper 는 unified3 검증된 `run_unified3_recovery.sh` 재사용
  (credit-depletion aware probe + inter-replicate sleep).

### 비열화 조건 (기존 시나리오 보호)

시그니처 축소가 기존 2 시나리오 (survey_setup, 3d_visualization) 의
라우팅에 부작용을 일으킬 수 있음. **명시적 비열화 확인**:
- 기존 2 시나리오의 `full_system`, `graph_only`, `state_path` step_acc
  가 unified3 값 대비 **−5pp 이내** 이면 허용 (n=5 variance 범위)
- 그 이상 하락 시 → **결함 발견으로 기록** (attribute 를 살리려다 기존
  시나리오 죽인 signature 트레이드오프). 이 경우 논문에는 "attribute-
  specific 시그니처는 기존 워크플로우 라우팅에 부작용을 준다" 관측을
  결함으로 명시. 억지로 되돌리지 않음.

### 정지 규칙 (Stop Rule) — unified4 는 마지막 이터레이션

**이 논문에서 unified5 는 없다.** unified4 결과가 어느 쪽이든:
- 격차 반전 성공 (A 급) → 성공 스토리로 논문 마감
- 실패 (B 판정 유지) → 파라메트릭 마스킹 + signature 시도 결함 기록으로
  마감

**정지 규칙을 사전 등록하는 이유**:
1. "이길 때까지 반복" 프레임 차단 — 이번 수정 사이클이 결함 주도
   (defect-driven) 였음을 보이는 최선의 증거는 "미리 선언된 정지 규칙"
2. v1→v2 (커버리지 결함), v3→v4 (시그니처 결함) 의 전후 비교를 Claude
   비대칭 사례처럼 정직한 자기 검증 서사로 논문화 가능
3. 리뷰어가 로그를 파고들어도 방어 가능한 구조

### 채점 · 시나리오 · 사전등록 동결 재확인

unified4 사이클에서 **손대지 않는 것 (동결)**:
- 채점기: `step_match` 키워드, `_COMPLETION_CLAIM_PATTERNS`, hallucination
  scorer 로직 및 파라미터 — 전량 그대로
- 시나리오 JSON: 3 시나리오의 스텝·트랩·visible_elements·expected_action
  패턴 그대로 (attribute JSON 의 `expected_workflow_node` 도 그대로 —
  signature 만 바꾸고 정답 노드 지정은 이미 옳음)
- 사전등록 문서: 이 unified4 예측 포함, 확증/반증 기준 사후 변경 금지

**손대는 것 (허용)**:
- `data/workflows/seismic_attribute.json` 의 노드 signature 및 노드 수 —
  signature_audit 블록으로 provenance 명시
- 필요 시 `signature_audit` 블록 추가

### Fallback 발동 예상 지점 (사전 기록)

Dry-run 에서 attribute 시나리오의 8 스텝 모두 seismic_attribute 워크플로우
로 라우팅되었으나, **step 2 confidence = 0.75** 로 유일한 marginal.
Fallback threshold 0.70 바로 위. 실제 벤치의 vision 추출은 hand-authored
visual_state_gt 보다 노이지하므로, unified4 에서 **step 2 가 fallback
threshold 아래로 떨어질 가능성 상존**.

**예상 관측**:
- attribute step 2 에서 fallback 발동 (workflow 라우팅 실패 → vector-only
  RAG 컨텍스트로 대체 채점) 가능
- 다른 스텝: dry-run conf ≥ 0.90 이므로 fallback 여지 낮음

**해석 원칙 (사전 확정)**:
- Fallback 발동은 결함이 아니라 안전장치의 정상 동작. 부록에 "fallback
  deadcode" 로 언급했던 로직이 실전에서 처음 발동하는 관측이므로 오히려
  긍정적.
- 발동 시 그 스텝은 vector-only 컨텍스트 (vanilla_vector 백엔드와 동일한
  RAG 결과) 로 채점됨을 판정 보고서에 명시.
- Fallback 발동률 자체가 시스템 안정성 지표.

### 서명

이 문서는 unified4 실행 전에 작성됨. 이후 결과가 어떻게 나오든 이
문서의 기준을 적용해 판정.
