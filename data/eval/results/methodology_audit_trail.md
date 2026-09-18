# Methodology audit trail — GeoLens paper benchmark

이 문서는 벤치마크가 "믿을 만한 표"에 이르기까지의 결함 발견과 수정
이력을 시간순으로 기록한다. Methods / Limitations 섹션 원자재이자,
"이 논문의 숨은 기여는 벤치마크를 감사 가능하게 만든 것 자체"라는
서술의 근거.

---

## 결함 #1 — Windows cp949 stdout 인코딩 버그 (3회 재발)

### 증상
`gemini` 백엔드 벤치 실행 중 랜덤한 step에서 응답이 `""` (빈 문자열)로
기록됨. 로그에는 명시적 예외 없음. `[BENCH] EMPTY response at step N`
라는 하위 경보만.

### 잘못된 진단 1 (2026-07-06)
"Gemini API가 가끔 empty response를 반환한다" — 실제 원인은 다른 곳.
해결책: Gemini 호출에 retry 로직 추가. **증상 소멸했지만 원인 미규명.**

### 잘못된 진단 2 (2026-07-08)
동일 증상이 재발. "Gemini 2.5 Pro의 thinking token exhaustion" 가설.
max_output_tokens 조정 시도. **역시 증상 소멸했지만 원인 미규명.**

### 실제 근본 원인 (2026-07-14 확정)
`bench_runner.py`와 `bench_backends.py`의 print 문 중 하나에 em-dash
(U+2014) 문자 포함. Windows cp949 기본 stdout 인코딩에서 이 문자 인쇄
시 `UnicodeEncodeError` 발생 → 상위 try/except가 삼킴 → `response=""`
저장 → 벤치 결과에는 "empty response"로 남음.

증거:
- `_call_gemini_variant`에 `print(...)`가 em-dash 포함
- Windows에서 재현: `python -c "print('—')"` → cp949 crash
- retry가 아무 예외 없이 "성공"하는 이유: 예외는 print에서 났고 API
  응답은 성공적으로 파싱됐지만 이후 로그 라인이 크래시했기 때문.

### 수정
- `bench_runner.py` 최상단에 `sys.stdout.reconfigure(encoding="utf-8")`
- `bench_backends.py`도 동일
- `run_all_models.py`도 동일 (wrapper 자체도 em-dash 프린트로 죽었었음)

### 배운 점 → 논문 methods
> 벤치마크 파이프라인의 인코딩 처리는 재현성의 필수 조건이다.
> print 문 하나의 U+2014가 특정 OS에서 응답을 "empty"로 오분류하고,
> 그 오분류가 정확도 지표에 그대로 계수되는 경로가 존재했다.
> 향후 벤치 코드에는 프로세스 시작 시점 UTF-8 강제를 표준으로 삼는다.

---

## 결함 #2 — goal_completion sentinel-only 채점 결함

### 증상
Claude·Gemini의 unified matrix (v1) goal_completion이 모두 1.000 ± 0.000.
이상하게 완벽한 만점.

### 진단 (2026-07-15, 사용자 지시로 검증 1 수행)
Claude no_rag / 3d_visualization / 5 replicates의 최종 step 응답 원문
추출:
- r1: `완료` (bare)
- r2: "In-line, Cross-line, Z-slice 모두 로드… 완료"
- r3: "Cross-line 우클릭하세요" (sentinel 없음)
- r4: 같은 패턴 → 3개 모두 로드 주장 + 완료
- r5: 같은 패턴

**실제 화면 (step_3.jpg + scenario visual_state_gt)**: In-line + Cross-line
만 표시. Z-slice는 아직 없음. 즉 r2/r4/r5는 화면에 없는 요소를 "로드됨"
이라 단언 → 자기 대화 이력 기반 환각.

**지표 결함**: `has_done_sentinel()` 하나로만 채점되어 환각 완료 응답도
1.0을 받음. 지표가 화면 관찰이 아니라 발화 습관을 측정.

### 수정
`api/services/evaluation.py`에 3-gate 채점 도입:
1. sentinel 존재
2. 응답이 언급한 UI 요소가 최종 visual_state로 확인됨 (`completion_visually_grounded`)
3. 최종 visual_state가 goal-reached를 명시함 (`_visual_state_indicates_goal_reached`)

셋 다 만족해야 goal_ok = 1.

### 재채점 결과 (2026-07-15)
`scripts/rescore_results.py`로 archived 결과 전체 재채점.

주요 flip:
- claude_unified: 1.000 → 0.500 (3개 백엔드 전부)
- gemini_unified: 1.000 → 0.500 (3개 백엔드 전부)
- gpt_unified full_system: 0.400 → 0.000
- qwen_unified vanilla_vector: 0.400 → 0.000

즉 이전 만점은 utterance habit 부산물. 3d_visualization은 이 시나리오의
step_3.jpg가 실제 goal-reached 상태를 담고 있지 않아 어떤 sentinel도
그 지표에서 통과 못 함.

### 배운 점 → 논문 methods
> Task completion을 sentinel token만으로 채점하면, LLM이 conversation
> history에서 완료 문구를 습관적으로 emit하는 경향이 만점으로 계수된다.
> 우리는 3-gate 검증층 (sentinel + grounded + visual_state confirms)을
> 도입해 발화 습관을 배제하고 화면 관찰에 기반한 완료만을 인정한다.
> archived 로그를 이 규칙으로 재채점해 old/new 비교표를 제공한다.

---

## 결함 #3 — Workflow 커버리지 공백 (Table 1의 무효화)

### 증상
Unified matrix v1에서 full_system이 vanilla_vector를 어떤 지표에서도
유의하게 이기지 못함. 언뜻 "hybrid 아키텍처가 vanilla 대비 이득 없다"는
결론.

### 진단 (2026-07-15, 사용자 지시로 검증 2 수행)
Full_system routing 로그 분석:
- `data/workflows/` 에는 3개 workflow만 존재:
  seismic_attribute, horizon_tracking, fault_interpretation
- 벤치의 두 시나리오 (survey_setup, 3d_visualization)에 해당하는 workflow
  노드가 **하나도 없음**
- rerank가 유사도로 아무 무관 workflow 노드를 강제 매칭 → 무관 청크가
  컨텍스트에 주입 → 잘못된 지시

**결론**: v1 결과는 "고장난 시스템의 성적표". "hybrid가 이득 없다"는
해석은 아키텍처 한계가 아니라 지식베이스 공백을 아키텍처 결함으로
오귀속한 것.

### 수정
`data/workflows/`에 2개 workflow 추가 (5 nodes each):
- `survey_setup.json` (매뉴얼 1.2.2a)
- `d3_visualization.json` (매뉴얼 1.3.1a)

`scripts/routing_dryrun.py`로 커버리지 검증: 8/8 (100%) 정확 workflow
매칭 확인.

### 배운 점 → 논문 methods
> Hybrid RAG 아키텍처의 성능은 workflow 그래프의 커버리지에 결정적으로
> 의존한다. 커버리지 공백은 "hybrid의 실패"가 아니라 "지식베이스 결함"
> 이며, 아키텍처 자체를 evaluate하려면 커버리지 관문 (routing 정확
> 매칭률)을 먼저 통과시켜야 한다. v1 매트릭스는 이 관문을 통과하지
> 못한 상태의 성적표였으며, v2는 관문 통과 후 재실행된 최종 표다.

---

## 결함 #4 — Confidence 게이트 부재

### 증상
v1 routing에서 workflow 노드는 매칭되어도 confidence < 0.7인 저신뢰
매칭이 그대로 컨텍스트로 진입. 저신뢰 노드의 linked_chunks는 무관한
경우가 많아 컨텍스트를 오염시킴.

### 수정
`guide_pipeline.py`에 `CONFIDENCE_THRESHOLD = 0.7` 도입. rerank
confidence < 0.7 시 `current_node = None`으로 강등, `hybrid_retrieve`가
자동으로 vector-only fallback.

각 스텝의 `route_confidence`, `picked_node_id`, `fallback_activated`가
per_step에 기록되고, aggregate에 `fallback_rate` + `mean_route_confidence`
집계.

### 논문에서의 위치
Design 서술: "confidence-gated fallback — hybrid는 확신 없을 때 우아하게
vector-only로 후퇴한다" — v2 로그의 fallback rate 통계가 이 서술의
정량 근거.

---

## 결함 #5 — Visual_state 캐싱 없음 (O(N²) 재분석)

### 증상
Full_system이 step N에서 visited_node_ids 재구성을 위해 앞선 N개 스텝의
스크린샷 각각에 대해 Gemini vision을 재호출. step 3에서는 같은 스크린샷을
4번 재분석. 이 반복이 74s 이상의 latency의 큰 부분.

### 수정
`recognize_visual_state`에 SHA-256 image-content 해시 기반 in-process
캐시 도입. 동일 스크린샷 재분석 시 캐시 히트.

### 논문에서의 위치
Latency trade-off 표: "cached vs uncached full_system"를 v2 로그에서
후처리 가능 (mean_latency_sec는 캐시 적용 후 값).

---

## 재실행 이력

| 회차 | 태그 | 조건 | 결과 |
|------|------|------|------|
| v0 (2026-06~07) | (untagged) | 4 model × 5 backend × 3 rep, 8-9 scenarios | 인코딩 버그로 다수 empty; 파기 |
| v1 (2026-07-15) | `unified` | 4 model × 3 backend × 5 rep × 2 scenarios | goal 지표 결함 + workflow 커버리지 공백으로 무효 |
| **v2 (2026-07-16~20)** | `unified2` | 4 model × 6 backend × 5 rep × 2 scenarios | 두 관문 (라우팅 100%, 재채점 확인) 통과 후 실행. qwen r2 재실행 후 논문 Table 1 확정 |

## v2 실행 중 이벤트 — qwen r2 폐기 및 재실행 (2026-07-20)

**발생 시각**: 2026-07-16 실행 중 (원래 파일 timestamp T084817).
**감지 시각**: 2026-07-20, GPT/Qwen mini-checkpoint 실행 중.

**증상**: `[GuidePipeline] Visual state recognition failed: 503 UNAVAILABLE`
2건 (동일 스텝에서 retry 3회 후 실패 → 즉시 재시도 3회 후 재실패).

**영향 범위 조사**:
- 발생 백엔드: qwen r2 / opendtect__survey_setup__01 / **graph_only**
- 영향 스텝: 4개 스텝 중 1개 (probably step 3, latency 32s + `<think>` tag leak)
- 응답 생성 여부: 예 (Empty=0/240 유지). matched=True로 스코어링됨.
- 다른 39 스텝 무영향.

**결정 근거**:
- 사용자 사전 원칙: "부분 데이터를 표에 섞지 말 것"
- 503은 429/RESOURCE_EXHAUSTED와는 카테고리 다르지만 (환경적 transient),
  판정 기준은 규칙 문구가 아니라 **논문 주장 오염 여부**.
- graph_only는 v2 미리보기에서 Gemini에서 hallucination 최저(2.5)로
  ablation 관전 포인트 → 그 백엔드의 열화된 스텝이 스코어에 반영되면
  ablation 표의 그 셀이 각주 달린 숫자가 됨.
- `<think>` tag leak = 정상 응답 경로가 아니었다는 방증. matched=True는
  오히려 문제 (열화된 스텝이 이미 점수에 반영됨).
- 30분 재실행으로 각주 없는 표 확보 가능 → 규율 대로.

**조치**:
1. `run_qwen_unified2_r2_20260716T084817.json` → `data/eval/results/discarded/`
   로 이동 (완전 삭제 아님, 감사 트레일 보존)
2. `run_qwen_unified2_r2_20260716T084817.md` 동일 이동
3. qwen 단독 5-backend × 2-scenario 재실행 (신규 timestamp로 새 r2 파일)
4. 재실행 완료 후 mini-checkpoint clean 확인 → 5-script 판정 프로토콜 착수

**교훈 → methods**: v2 매트릭스는 "무손실 240×24 실행 = 5760 스텝 전부 clean" 이라는 조건을 만족하기 위해 aux 실패 발생 시 replicate 단위로 재실행함. 이 원칙 덕분에 논문의 어떤 셀도 aux 열화 각주가 붙지 않음.

## v3 실행 중 이벤트 — long_context r5 폐기 및 재실행 (2026-07-23)

**증상**: long_context 백엔드가 매뉴얼 전문(226,660 tokens/step)을 주입하며
Gemini 프로젝트의 monthly spending cap을 소진. r5의 마지막 스텝(survey_setup
step 3)이 empty 응답으로 저장됨. 로그에 `429 RESOURCE_EXHAUSTED` 다수.

**결정 근거**: 사용자 사전 원칙에 명시적으로 등재된 "429/quota exhaustion
→ replicate 폐기" 규칙에 정확히 해당. 카테고리 판단 여지 없음.

**조치**: 
1. `run_gemini_longctx_r5_20260723T035334.json` → `data/eval/results/discarded/`
2. 사용자가 Gemini AI Studio에서 spending cap 상향
3. 재실행 후 `run_gemini_longctx_r5_20260723T041637.json` (전 스텝 clean)

## 폐기 replicate 감사 트레일

두 이벤트 모두 `data/eval/results/discarded/` 하위에 원본 파일이 보존되어
있으며, 폐기 사유와 재실행 결과가 `discarded/README.md`에 문서화되어 있다.
Reviewer는 다음을 통해 폐기 격리 여부를 검증 가능:

```bash
# Final result files (aggregation target)
ls data/eval/results/run_*_r*_*.json | wc -l   # 25 (4 unified2 × 5 + longctx × 5)

# Discarded originals (audit only, not aggregated)
ls data/eval/results/discarded/*.json | wc -l  # 2
```

Aggregation 스크립트의 glob 패턴이 top-level만 매칭하므로 discarded 파일이
자동으로 표에 섞이지 않음.

---

## 결함 #7 — unified3 longctx 연속 실행 → Gemini spend-based rate limit 연쇄 실패 (2026-08-07)

### 증상
unified3 Phase B-4 (Gemini long_context × 5 replicates) 를 wrapper 가
간격 없이 순차 실행 → 총 76 × 429 (RESOURCE_EXHAUSTED) 발생 →
replicate 별 empty response 비율:

| Replicate | 시각 | Empty | 비율 |
|---|---|---|---|
| r1 | 17:07 | 2/16 | 12.5% |
| r2 | 17:12 | 12/16 | 75% |
| r3 | 17:16 | 4/16 | 25% |
| r4 | 17:21 | 16/16 | **100%** |
| r5 | 17:24 | 16/16 | **100%** |
| **총합** | | 50/80 | **62.5%** |

### 근본 원인
두 종류의 429 가 겹침:
1. **Per-minute token quota** (`generate_content_paid_tier_input_token_count`,
   limit: 2,000,000 tokens/min): long_context 스텝당 ~226K token 이므로
   9개 정도 스텝이면 이 quota 소진. retry 로직이 10-15초 대기 후 재시도
   하면 회복.
2. **Spend-based rate limit** ("You exceeded your spend-based rate limit"):
   최근 소비 속도 대비 billing tier 상한 초과. 이건 명시적 retry_delay
   없이 광범위 throttle → retry 성공 확률 시간 갈수록 낮아짐.

간격 없는 순차 실행 → r1 (retries 성공) → r2 (일부 실패) → r3 (경계) →
r4/r5 (spend-based limit 완전 발동, 모든 retry 실패).

### 왜 unified2 때는 안 걸렸나
unified2 longctx 는 2 시나리오 (survey_setup + 3d_visualization) × 4
스텝 = 8 스텝/rep 로 스텝당 비용은 같아도 rep 당 API 콜 부하가 절반.
unified3 는 3 시나리오 (attribute_computation 추가) × 평균 5.3 스텝 =
16 스텝/rep 로 spend rate 가 두 배 이상 → 순차 실행 시 tier 초과.

### 폐기 결정 근거 (unified2 qwen r2 선례 일관성)
unified2 qwen r2 는 **단 1 step 의 aux 503** 열화만으로도 replicate 전체
폐기. 이 기준 적용 시:
- r1 (12.5% empty), r3 (25% empty) 도 폐기 대상 (>0% 열화 = 폐기)
- **5개 replicate 전량 폐기 필요**

더 중요한 규범적 이유: **long_context 는 논문에서 열세를 보여야 할
비교군** (hybrid 대비 106.6× 비싸고 정확도 낮음). Empty 는 0점 처리
되므로 열화된 데이터를 사용하면 long_context 점수가 실제보다 낮게
나옴 → "자해된 상대를 이긴 기록" → 리뷰어가 empty count 발견 시
핵심 반박 실험 (long_context 비교) 전체 의심 대상. **베이스라인에게도
공정한 기회를 준 깨끗한 5 반복** 이 유일한 방어.

### 재발 방지 (recovery wrapper 에 반영)
`scripts/run_unified3_recovery.sh` 신규 작성:

1. **Per-replicate quota probe**: 매 replicate 시작 전 tiny Gemini 요청으로
   quota 여유 확인. 429 반환 시 최대 5분 대기 후 재확인. probe 통과 후
   실제 replicate 시작. r4/r5 100% 실패의 근본 대응.
2. **Inter-replicate sleep 60s**: replicate 간 60초 sleep 으로
   per-minute quota (2M tokens/min) 회복 시간 확보.
3. **Recovery 로그 별도 파일**: `data/eval/results/unified3_recovery.log`
   에 quota probe 결과 + replicate 별 exit code + 최종 empty-response
   audit 자동 실행.

### 폐기 파일 위치
- `data/eval/results/discarded/unified3_longctx/` — 5개 corrupt longctx 파일 보존 (감사)
- `data/eval/results/discarded/unified3_qwen_r1_transient/` — Qwen r1 (아래 결함 #8)

---

## 결함 #8 — Qwen unified3 r1 transient <think>-only response (2026-08-07)

### 증상
Qwen r1 파일 480 스텝 중 1 스텝에서 empty response.
- 시나리오: `opendtect__survey_setup__01`
- 백엔드: `full_system`
- Step: 1
- Latency: 27.174s
- output_tokens: **1024** (max-tokens 정확 도달)
- cost_usd: 0 (self-hosted)

### 근본 원인
Qwen3-235B-Instruct 가 `<think>...</think>` 추론 블록만 max_tokens=1024
까지 채우고 실제 answer text 를 생성하지 못한 채 종료. `bench_backends.py:
_strip_thinking()` 이 think 블록을 제거하고 나면 남은 응답이 empty.
Qwen instruct 모델의 알려진 transient 실패 패턴 (unified2 qwen r2 폐기
사례와 동일).

### 폐기 결정 근거
- unified2 선례: qwen r2 는 aux 503 1 step 만으로도 전체 replicate 폐기
- 0.2% empty (1/480) 도 위 원칙 적용 시 폐기 대상
- "환경적 실패는 일괄 폐기·재실행" 원칙 (Methods 서술) 예외 없이 성립

### 재실행 계획
`run_unified3_recovery.sh` Phase R-1 에서 Qwen r1 만 재실행 (NAS vLLM
서버 살아있음 확인, 30분 소요 예상).

### 재실행 결과 (2026-08-07)
- Qwen r1 재실행: **성공** (480 스텝 0 empty). NAS vLLM 서버 (<INTERNAL_HOST>
  post-reboot 4-GPU 회복 상태) 로 정상 응답. Main matrix 최종:
  **1920/1920 valid, 0 empty across 4 models**.

---

## 결함 #9 — Gemini prepayment credits depletion 중 recovery 실행 실패 (2026-08-07)

### 증상
Recovery run Phase R-2 longctx 반복 실행 중, r1-r3 은 완전 클린 (각 16 스텝
0 empty) 로 성공. **r4 실행 중 429 급증** (14/16 empty, 87.5% 손실).
Recovery 즉시 중단.

### 근본 원인
429 메시지 유형이 이전 rate-limit-류와 다름:
```
"Your prepayment credits are depleted. Please go to AI Studio at
 https://ai.studio/projects to manage your project and billing."
```
= rate limit 이 아니라 **Gemini API 계정 prepayment 잔액 완전 소진**. Retry
로 회복 불가. Sleep 이나 대기로도 해결 안 됨. 크레딧 재충전 없이는 무한
실패.

### 원인 시나리오 (누적 비용 계산)
- unified2 초기 실행 (이전 세션): ~$15-20
- unified3 초기 실행 (Phase B-3 3모델 + longctx 초기 실패): ~$30
  - 3 모델 (gemini/claude/gpt) × 5 rep 정상
  - Longctx r1-r5 초기 실행: 76 × 429 retry + 부분 성공 = ~$27 소진
- unified3 recovery (Phase R-1 Qwen + Phase R-2 longctx r1-r3 성공): ~$18
- **누계 ~$63-68** (사용자 초기 $70 잔액에 근접)
- Recovery r4 시점에 잔액 완전 소진 → credit depletion 429

### Wrapper probe 의 한계
`gemini_quota_probe` 는 tiny 요청 (5 output tokens) 이라 credit 여유 여부
검출 못 함:
- Rate-limit throttle 은 감지 가능 (probe 자체가 429 받으므로)
- Credit depletion 은 tiny 요청도 실패시키므로 감지되어야 하나, r4 pre-probe
  당시 credit 은 아슬아슬 남아있었고 (probe 성공), 실제 replicate 실행 중
  누적 스텝 비용이 잔액을 넘겨 실행 중반부부터 credit depletion 발동.
- Pre-run probe 는 "실행 시점의 순간 잔액 확인" 이지 "이번 replicate 를
  끝낼 수 있는 잔액 확인" 이 아님.

### 방지 조치 (다음 recovery 재실행 전)
1. **Credit-depletion 감지 로직 추가**: 429 메시지에 "prepayment credits are
   depleted" 문자열 포함 시 retry 하지 말고 **즉시 abort** 로 wrapper 개선.
   Rate-limit 429 와 credit-depletion 429 는 다른 대응 필요.
2. **사전 잔액 추정**: 각 replicate 예상 비용 (~$4.5) 대비 현재 잔액 확인.
   잔액 부족 예상 시 실행 전 abort + 사용자 알림.
3. **사용자 크레딧 충전 요청**: r4/r5 재실행 최소 예산 $10-15 필요.

### 폐기 파일
`data/eval/results/discarded/unified3_longctx_r4_credit_depleted/` — r4
14/16 empty 파일 보존.

### 부산 결함 — TaskStop 후 zombie process 로 인한 r5 오염 (2026-08-07)
Original recovery 스크립트를 TaskStop 으로 중단할 때 Windows Bash 의
TaskStop 이 자식 프로세스까지 cascade kill 하지 못해서 bench_runner 가
zombie 로 계속 실행됨. 그 zombie 가 사용자 결제 (credit 재충전) 직후
retry 로 응답을 받으면서 `r5_011701` 파일을 만들어냄. Empty 는 0 이나
"clean 실행 아님" 판정으로 폐기:
`data/eval/results/discarded/unified3_longctx_zombie_r5/`. 
Clean rerun 은 새 wrapper (`run_longctx_r4_r5.sh`) 로 별도 실행 중
(`r5_012551`).

**교훈**: Windows/Git Bash 환경에서 TaskStop 은 프로세스 트리 cascade
아님. 향후 크리티컬 킬 필요 시 `taskkill //F //T //PID <parent>` 로
프로세스 트리 강제 종료 필요.

### 현재 unified3 상태 (crediting 대기 중)
- Main matrix: **1920/1920 valid, 0 empty** ✅
- Long_context (recovery): **3/5 valid** (r1, r2, r3 — 각 16/16 valid)
- Long_context r4, r5: **크레딧 충전 후 재실행 대기**

---

## 시나리오 refinement #1 — 3d_visualization step_3 재정의 (2026-08-06)

### 배경
unified2 의 `opendtect__3d_visualization__01` step_3 은 "In-line + Cross-line
displayed; Z-slice next" (penultimate 상태) 로 정의됨. 이 정의 하에서
어떤 백엔드도 goal_completion 3-gate 를 구조적으로 통과 불가 (visual_state
가 goal-reached 를 나타내지 않음 → sentinel 응답 거부). 논문 unified2 표에서
3d_viz 의 goal_completion 상한이 사실상 50% 로 고정된 이유.

### unified3 재캡처 결정 (사용자 승인 2026-08-06, opt B)
수동 재캡처 세션에서 step_3 를 **all-three-slices-displayed goal state** 로
잡음 (penultimate 아님). 이는 캡처 실체 변경이며, 이에 맞춰 시나리오 JSON
도 정정:

- `visual_state_gt.data_state`: "In-line + Cross-line displayed; Z-slice
  next" → "Goal achieved — In-line + Cross-line + Z-slice all three
  displayed" (goal marker 포함)
- `expected_action_text_pattern`: "Z-slice|Add.*Data" → "^\s*(완료|Done)\.?\s*$"
- `expected_action_keywords`: ["Z-slice", "Add"] → ["완료"]
- `trap.type`: `category_vs_child_item` → `goal_completion_sentinel`
- `allowed_alternatives` 에 grounding validator 용 요소 mention 키워드
  ("In-line", "Cross-line", "Z-slice", "3D Scene", "Elements") 추가

### 이 refinement 가 채점 완화가 아닌 이유
- 3-gate 완료 체크 로직 자체는 변경 없음 (sentinel + grounded + visual
  indicates goal)
- 전 백엔드에 **대칭적으로** 열림 — hybrid만 이득 보는 게 아니라 no_rag
  포함 모두 통과 가능해짐
- 채점 rubric 완화가 아니라 시나리오 정의를 캡처 실체에 맞춘 정확화

### Cross-version 비교 금지 명문화
**unified2 와 unified3 의 goal_completion_rate 는 직접 비교 금지.** 시나리오
정의 refinement 로 인해 unified3 에서 3d_viz goal 이 개선되어 보이는 것은
시스템 개선 효과와 시나리오 정의 변경 효과가 섞이는 것. 논문 Table 6
같은 교차버전 비교표에 goal_completion 열 절대 포함 금지. Table 1 은 unified3
숫자만 사용.

### 논문 서술 갱신 대상 (Results / 통합최종본)
"3d_viz 는 goal_completion 구조적으로 통과 불가, 상한 50%" 문장 계열이
아래 위치에 존재. unified3 결과 확정 후 전부 갱신 필요:

- `data/eval/results/final_unified2_table.md` — footnote
- `data/eval/results/pypdf_migration_audit.md` — Goal Comp 서술
- `data/eval/results/direction_unified2.md` — goal_completion_rate 노트
- `scripts/build_final_table.py` — hardcoded Goal Comp footnote
- `scripts/compute_table1_sd.py` — Appendix A footnote
- `data/eval/results/statistical_analysis.md` — On goal completion 문단
- `data/eval/results/qwen_cost_estimation.md` — 참고
- `GeoLens_최종결과_통합최종본.docx` (레포 밖) — P24, P55 등 goal-related
  문장
- Results 원고 초안 (별건) — 해당 서술 전부 갱신

**갱신 원칙**: "unified3 재캡처로 3d_viz step_3 가 goal-reached 상태로
재정의됨. 이제 이 시나리오도 goal_completion 이 구조적으로 측정 가능함.
unified2 대비 goal_comp 개선은 시나리오 refinement 효과이며 시스템 개선
효과와 구분해야 함 (cross-version 비교 금지)." 취지 반영.

---

## 결함 #6 — validate_screenshots.py 필드 혼용 설계 결함 (2026-08-06)

### 증상
`opendtect__attribute_computation__01` 시나리오 (매뉴얼 §1.5.1a, 8스텝)
의 수동 재캡처 후 `scripts/validate_screenshots.py` 실행 시 8스텝 중
3스텝이 FAIL 판정:
- step_0 (Attribute Set 3D 창 방금 열림): expected `["Energy", "Attribute Type"]` 미매칭
- step_5 (In-line 250 base seismic 표시): expected `["Add", "Attribute"]` 미매칭
- step_7 (Energy 렌더링 완료 = 목표 상태): expected `["완료"]` 미매칭

### 근본 원인
`validate_screenshots.py` 는 각 스텝의 `expected_action_keywords`
(**모델이 다음에 할 응답 검증용**)를 스크린샷에서 추출한
`visual_state` 텍스트 (**현재 화면 내용 기술**)에 대조함. 두 필드는
개념적으로 이질:
- `expected_action_keywords` = "다음 스텝의 정답 응답에 포함돼야 할 단어"
- `visual_state` = "현재 화면에 시각적으로 존재하는 UI 요소"

**FAIL 3건의 패턴이 진단을 지지**: step_0 / step_5 는 "다음 행동이
아직 화면에 나타나지 않은 pre-action 스텝", step_7 은 sentinel("완료")
을 응답으로 기대하나 sentinel은 화면 내용이 아니라 응답 텍스트임. 즉
**"다음 행동이 화면에 아직 없는 스텝"에서만 FAIL이 발생**했음. 실제
bench 실행 시 `step_match()` 는 모델 응답을 keywords와 정확히 대조하므로
채점에는 지장 없음 — validate 스크립트만의 사전 sanity check 편향.

### 수정 방향 (unified3 이후 반영, 지금은 스키마 동결)
시나리오 스키마에 별도 필드 `expected_visual_keywords` 신설:
- `expected_action_keywords` (기존): 모델 응답 검증
- `expected_visual_keywords` (신규): visual_state 추출 결과 검증

`validate_screenshots.py` 는 `expected_visual_keywords` 만 대조하도록
분리. 두 필드의 목적이 명확해지고 pre-action 스텝의 false FAIL 소멸.

### 왜 지금 안 고치는가
1. **동결 원칙**: `expected_action_keywords` 는 bench_runner 의
   `step_match()` 와 공유되는 채점 필드. 이걸 튜닝해서 validate 만
   통과시키면 실질적으로 채점 완화가 되어 unified2/3 비교 무효.
2. **스키마 변경은 별건**: `expected_visual_keywords` 신설은 스키마
   확장으로 vs. unified3는 스키마 고정에서 실행. 다음 iteration으로.

### 벤치 실행에 미치는 영향
없음. `validate_screenshots.py` 는 사전 sanity check 도구이며 bench
채점 파이프라인과 독립. 3건 FAIL은 audit-only 기록으로 처리하며
unified3 bench는 정상 진행.

---

## Limitations 섹션 원자재

이 audit trail에서 뽑을 limitations:
1. **시나리오 수가 3개 (survey_setup + 3d_visualization + attribute_computation)**
   로 확장됨 (unified3 기준, unified2 는 2개). 여전히 external validity
   제한.
2. **3d_visualization 의 최종 스크린샷이 실제 goal-reached 상태를 담고
   있지 않음** (unified2 관측) → 이 시나리오에서는 어떤 시스템도
   goal_completion 3-gate 통과 불가. unified3 재캡처 시 이 이슈 재검토.
3. **Fallback rate이 초기 관측에서 상당** — hybrid의 실제 우위는
   "fallback이 발동하지 않는 스텝"에서만 온다. v2 로그로 이 비율 정량화.
4. **모델별 무관 컨텍스트 강건성 차이 (Claude 비대칭)**의 원인은 이
   벤치로 규명 불가 — 후속 연구.
5. **`validate_screenshots.py` 필드 혼용 결함** (결함 #6): 사전
   sanity check 정확도의 한계. 채점 파이프라인은 무관하며 unified3
   이후 스키마 확장으로 해결 예정.
6. **파라메트릭 마스킹 (parametric masking)** — 관측 #1 (unified3
   attribute 시나리오, 2026-08-07): 발견 원문은 아래 § 관측 #1 참조.

---

## 관측 #1 — 파라메트릭 마스킹 (parametric masking, 2026-08-07)

**정의**: RAG 시스템의 벤치 상대 (vanilla_vector, no_rag) 가 검색에서
관련 청크를 확보하지 못했음에도 **모델의 사전학습 파라메트릭 지식**
으로 부분 정답을 생성해 성능 하한이 인위적으로 올라가는 현상. 결과적
으로 검색 정확도의 실제 개선분이 downstream task metric 상에서 압축
되어 나타난다.

**발견 경로 (unified3)**:

증거 1 (검색 완전 실패에도 성능 유지):
- `retrieval_attribution_unified3.md § opendtect__attribute_computation__01`
  에서 vanilla_vector 는 §1.5.1a (p118-128, 목표 절차 페이지) 를 **0/15
  hit**. 상위 15 청크가 §2.3.1g (fault filter), §1.5.2a (spectral),
  §2.3.1f (diffusion), §2.3.2b (curvature), §2.5.1a (coloured inversion)
  같은 **완전히 다른 attribute 계열 절차** 로 편향.
- 그럼에도 vanilla_vector 의 attribute 시나리오 step_acc = 61.3% (macro),
  full_system 의 60.0% 와 사실상 동등.
- 즉 vanilla 는 매뉴얼의 정확한 절차를 못 봤음에도 "다른 attribute 절차"
  를 근거로 (또는 파라메트릭 지식으로) 정답 근처의 답 생성.

증거 2 (오라우팅 스텝에서 오히려 잘 통과):
- `routing_score_concentration_unified3.md § 2` 에서 full_system 의 스텝
  5-7 이 `d3_visualization_01_main_window_ready` 로 오라우팅됐음에도
  통과율 **55/80/95%**. 정작 "정답 워크플로우" 인 `seismic_attribute`
  로 라우팅된 스텝 1 은 5% 통과.
- 즉 문맥이 부정확해도 모델이 파라메트릭 지식으로 채워 넣음.

**해석 (open-book vs closed-book 비유)**:
- 시험 상황: RAG 시스템은 오픈북, 상대 (no_rag, vanilla with wrong hits)
  는 클로즈드북에 가까움.
- 문제: 상대가 시험 문제집을 **통암기하고 왔음** (파라메트릭 사전지식이
  OpendTect 를 이미 알고 있음).
- 결과: 오픈북의 이점이 압축되어 정확히 측정되지 않음. 개선분이 있어도
  metric 상 격차로 드러나지 않음.

**논문 함의**:
1. RAG 시스템 벤치의 **일반적 방법론 이슈**: 공개 소프트웨어 (OpendTect,
   QGIS 등) 매뉴얼 기반 벤치는 파라메트릭 마스킹으로 hybrid 우위 측정이
   구조적으로 낮게 나옴.
2. **엄정한 hybrid 우위 측정 조건**: 모델의 학습 cutoff 이후 릴리즈된
   신기능 문서, 또는 사내 비공개 문서 기반 시나리오. Zero-shot 과
   vanilla 가 기댈 파라메트릭 지식이 없어 격차가 구조적으로 벌어짐.
3. **본 연구의 유효 조건 서술**: unified3/4 의 결과는 파라메트릭 마스킹
   환경에서의 "conservative lower bound" 로 해석. 실제 사용 환경 (사내
   워크플로우, 신기능) 에서는 격차가 확대될 것으로 예상 (검증은 future
   work).

**논문 Discussion 초안 문장 후보** (2026-08-07 확정):

> "Our attribute-computation scenario reveals a methodological artifact
> we term **parametric masking**: the vanilla baseline retrieves zero
> of the target §1.5.1a procedural chunks yet achieves step-accuracy
> statistically indistinguishable from the hybrid full_system. The
> mechanism is that the underlying language models — trained on
> publicly indexed content that includes OpendTect documentation and
> tutorials — can generate near-correct next-step instructions from
> parametric knowledge alone, bypassing the retrieval pathway entirely.
> This compresses the measurable hybrid advantage on public-manual
> benchmarks. The corollary is that our reported gains understate the
> gains one would observe in the intended deployment condition —
> internal workflow documents or post-training-cutoff features — where
> parametric knowledge does not substitute for retrieval. A controlled
> evaluation on such private-knowledge material is left as future work."

**독립성**: 이 관측은 unified3 결과 자체로 완결. unified4 성공/실패와
무관하게 논문에 남는 finding.

**Audit hash**: 이 관측의 원 데이터는 `retrieval_attribution_unified3.md`,
`routing_score_concentration_unified3.md`, `per_scenario_unified3.md`,
`complexity_gap_unified3.md` 네 산출물에서 교차 확인 가능.

---

## 결함 #10 — signature 과잉 흡수 (over-absorption, 2026-08-07)

**발견 경로**: `routing_score_concentration_unified3.md` 에서
`seismic_attribute_04_configure` 가 confidence 0.91 로 160 스텝 중 76
을 흡수. 그러나 이 노드로 라우팅된 스텝의 통과율은 48.7% vs 오라우팅
스텝의 73.1% — **성공 라우팅이 더 못한다** 는 역설.

**원인**: `_04_configure` 의 signature (screenshot_keywords 12개 + UI
elements 7개) 가 너무 넓어 스텝 0 (Attribute Set 3D 창 진입), 스텝 1
(Attribute Type 선택), 스텝 2 (파라미터 입력), 스텝 3 (Save on Close 체크)
을 모두 자기 것으로 잡음. 스텝 1 에서 통과율 **5%** — 노드가 담당해야
할 문맥 (파라미터 편집) 과 스텝의 실제 요구 (다이얼로그 오픈) 가 어긋남.

**함의**: workflow 저작 시점의 시그니처는 "커버리지 부족" 뿐 아니라
"과잉 흡수" 도 결함이 될 수 있다. 특히 confidence 값이 높은 경우
(0.9+) 는 오히려 진단 신호로 활용 가능 — 정확도가 낮은데 confidence
가 높다면 signature 재검토 필요.

**수리 계획**: unified4 사이클에서 `seismic_attribute.json` 재작성 (별건
사전등록: `v2_pre_registration.md § unified4 signature refinement`).

**동결 위반 아님 확인**: 채점기·시나리오·사전등록 예측 문구 모두 그대로.
workflow signature 만 수정. Signature 자체는 사전등록 대상이 아님
(사전등록은 시스템 우위 판정 프레임에 관한 것).

---

## 관측 #2 — Dry-run 게이트 vs 벤치 실제의 vision-noise 괴리 (2026-08-10)

**발견 경로**: unified4 실행 결과 seismic_attribute workflow 라우팅률이
dry-run 8/8 통과에도 불구하고 벤치 실제에서 **0/160 (0.0%)**. Signature
재작성이 dry-run 은 통과했으나 실제 벤치는 완전 회피.

**메커니즘**:
- **Dry-run** 은 시나리오 JSON 의 hand-authored `visual_state_gt` 를 그대로
  vs_text 에 flatten. 이 텍스트는 저자가 목표 노드 signature 를 알고 작성
  하므로 quoted phrases (`'Select Layer 2'`, `on-the-fly energy overlay`,
  `bright-spot highlights` 등) 가 그대로 포함됨.
- **벤치 실제** 는 Gemini Vision 이 스크린샷에서 추출한 visual_state 를
  사용. 이 텍스트는 자연스러운 요약체 (예: "Attribute Set 3D dialog with
  Energy attribute type selected, parameters visible") 로 quoted phrase 는
  거의 없음.
- Signature 축소 (unified3 `_04_configure` 12 keywords → unified4 특정
  값 `Time gate populated: -28 to +28` 등) 는 dry-run 매칭에는 정확하나
  vision 요약체와는 mismatch.

**결과**: unified4 attribute full_system 스텝 중 **65/160 (40.6%) 이 fallback**,
나머지는 d3_visualization (79) + horizon_tracking (17) 로 오라우팅. Target
seismic_attribute workflow 는 **완전 소멸**.

**함의**:
- Dry-run 게이트는 **필요조건이지만 충분조건이 아니다**. Signature 튜닝
  검증에는 vision-noise 시뮬레이션 필수.
- 방법론 개선 방향: (a) 스크린샷에서 실제 vision 추출을 dry-run 에 사용,
  (b) 요약체 텍스트에 대한 robustness 테스트 세트 구축.
- Future work: signature 자동 튜닝 파이프라인 (vision-extracted state 로
  검증하는 A/B 프레임)

**독립성**: 이 관측은 unified4 결과 자체로 완결. 논문 methodology 절 또는
future work 로 삽입 가능.

---

## 관측 #3 — "의심될 때는 라우팅하지 마라" (when-in-doubt-don't-route, 2026-08-10)

**발견 경로**: unified3 → unified4 에서 attribute full_system step_acc 가
**60.0% → 58.8% (거의 동일)** 이나 vanilla 대비 격차는 **−1.3pp → +3.1pp
(양전환)**. 원인은 vanilla 시나리오 성능 하락 (61.3% → 55.6%) 이 아니라
전체 관점에서:
- unified3: `_04_configure` 가 스텝 0-3 을 confidence 0.91 로 흡수 →
  잘못된 문맥 (파라미터 편집 지침) → 스텝 1 통과율 5%
- unified4: seismic_attribute 라우팅 자체 소멸 → 40% fallback (vector-only
  RAG) + 60% d3_viz 오라우팅. Fallback 는 vanilla_vector 백엔드와 동일한
  검색 결과를 받지만 "잘못 자신 있는 문맥" 은 없음.

**해석**: **잘못된 라우팅으로 잘못된 문맥을 신뢰하게 만드는 것이 라우팅
실패보다 나쁘다**. 워크플로우 signature 설계에서 confidence 가 높은데
정확도가 낮은 패턴은 최악의 실패 모드.

**설계 원칙 (관측에서 유도)**:
- Signature 는 "잘 맞을 때만 자신 있게" 설계 — false positive 회피가
  false negative 회피보다 중요.
- Fallback threshold (0.70) 를 지금보다 더 보수적 (예: 0.80) 으로 설정
  하는 것을 검토 가치. Fallback 은 예상보다 유용한 안전장치.
- Confidence 0.90+ 인데 downstream 통과율 낮은 노드는 signature 재검토
  1순위 신호.

**논문 함의**: RAG + workflow routing 시스템의 방어적 설계 원칙. Discussion
서브챕터로 승격 가능.

---

## 결함 #11 — signature 재작성의 기존 시나리오 부작용 (2026-08-10)

**발견**: unified4 에서 `survey_setup × state_path` step_acc 가 unified3
대비 **−7.5pp** (76.2% → 68.8%). 사전등록 비열화 tolerance (−5pp) 초과.

**진단 후보**:
- state_path 백엔드는 시나리오 목표까지의 워크플로우 노드 경로를 명시적
  으로 계획함. Seismic_attribute workflow 의 edge 재작성 (특히 `_04_configure`
  → `_05_compute` (conditional batch_path) 와 → `_06_display` (conditional
  on_the_fly_path) 로 분기 추가) 이 어떤 방식으로 state_path 의 경로 계획
  로직에 영향을 미쳤을 가능성.
- Survey_setup 시나리오와 seismic_attribute workflow 는 무관해 보이나
  workflow_graph 전역 스코어링 (get_top_k_nodes) 에서 순위 재조정이 일어
  났을 수 있음.

**대응 (사전등록 원칙)**: **억지로 되돌리지 않음**. 이는 signature 설계의
트레이드오프 발견이므로 그대로 결함으로 기록. 논문 Discussion 에 "복잡한
매트릭스에서 워크플로우 재설계는 국지적 트레이드오프를 유발한다" 로 서술.

**정지 규칙 준수**: unified5 로 이 결함을 수정하려 시도하지 않음.

---

## QGIS Pilot 감사 기록 (tag: qgis_pilot, 착수 2026-08-12)

### Pilot 스코프 및 격리 원칙

Pilot 은 **이식의 존재 증명** 이 목적 — "4개 touch-point 수정 + 정규 업로드
기능만으로 파이프라인이 새 소프트웨어에서 end-to-end 작동하고 벤치 지표가
산출된다". 성능 우위 입증이 아님. Unified4 매트릭스 동결 유지, pilot 은
별도 태그 (`qgis_pilot`) · 별도 산출물로 완전 분리.

### P-0 리팩터 완료 (4 touch-point)

| # | 파일 | 변경 | 스위칭 메커니즘 |
|---|---|---|---|
| 1 | `api/services/guide_pipeline.py:81` | `VISUAL_STATE_PROMPT` → `_build_visual_state_prompt(software_id)` + `SOFTWARE_PROFILES` dict | env `GEOLENS_SOFTWARE_ID` (default `opendtect`) |
| 2 | `api/services/evaluation.py:578` | `_COMPLETION_CLAIM_PATTERNS` → `_COMPLETION_CLAIM_PATTERNS_BY_SOFTWARE` dict + `_get_completion_claim_patterns()` | 위와 동일 env |
| 3 | `lib/prompts/action.ts:134-163` | 3D-scene block 을 `softwareSpecificSection` 변수로 추출, QGIS 용 Layers Panel + Processing Toolbox 블록 추가 | `NEXT_PUBLIC_SOFTWARE_ID` (frontend) |
| 4 | `components/multimodal-input.tsx:81` | `NEXT_PUBLIC_SOFTWARE_ID` 조건부 suggested actions | 위와 동일 env |

**Backward compat**: 모든 대체 지점에서 `default = "opendtect"` — env 미설정
시 unified4 실행 조건과 완전 동일. `VISUAL_STATE_PROMPT`, `_COMPLETION_
CLAIM_PATTERNS` 모듈-level 이름 유지 (외부 import 호환).

### P-0 회귀 검증 결과

- 2026-08-12: routing dry-run 실행 → 16/16 통과 (survey 4/4, 3d_viz 4/4,
  attribute 8/8). Attribute step 2 confidence 0.75 → 0.80 소폭 상승, 나머지
  0.90+ 유지. **OpendTect 회귀 없음 확인.**
- Unified4 결과 파일 (`data/eval/results/run_*_unified4_r*.json`) 무변경
  확인 — 리팩터가 결과 파일에 접근하지 않음.
- 최초 dry-run 은 Gemini API credit depletion 으로 실패 (unified3 관측 #9
  재발). Credit 재충전 후 재실행에서 16/16 확인.

### Q2 결정: 워크플로우 격리 방식 (사용자 결정: 옵션 A)

**결정**: **옵션 A** — QGIS 벤치 러너에서 `hint_workflow_id` prefix 로 QGIS
workflows 만 검색 대상 명시.

**채택 근거 (deployment reality 반영)**:
배포 상황에서 GeoLens 는 사용자가 어떤 소프트웨어를 쓰는지 이미 알고 있다
(`software_id` 필드의 존재 이유). 벤치에서 QGIS workflow 만 검색 대상으로
한정하는 것은 **그 배포 현실을 반영** 하는 것이지, 시스템에 부당한 힌트를
주는 것이 아니다. Pilot 러너의 hint_workflow_id 지정은 production 환경에서
프론트엔드가 자연히 알고 있는 소프트웨어 컨텍스트를 벤치에 재현하는 것.

**한계 (pilot 보고서에 명시)**:
Pilot 의 워크플로우 격리는 **벤치 설정 수준** 에서 시행되며, **시스템 수준
네임스페이싱 (production-grade workflow namespacing) 은 future work**.
Loader 자체는 여전히 `data/workflows/` 전역 로드하며, software_id 기반 필터
는 각 호출부의 책임.

**옵션 B 기각 사유 (touch-point 4 유지)**:
`data/workflows/` 를 `opendtect/`, `qgis/` 서브디렉토리로 분리하는 것이
아키텍처적으로 가장 깔끔하나, `WorkflowGraph._load_workflow` 코어 수정을
요구 → P-0 회귀 검증 사이클 재실행 필요 + **논문의 "4 touch-point" 이식
비용 주장을 5 개로 바꿈**. Pilot 의 핵심 데이터가 이식 비용 정량이므로
중간에 touch-point 를 늘리면 그 표의 의미가 흔들림. 디렉토리 분리는
future work (production-grade workflow namespacing) 로 별도 기록.

**옵션 C 기각 사유 (unified3→4 학습 역행)**:
"오라우팅 나면 그때 대응" 은 unified3→4 에서 이틀 걸려 배운 패턴의 역행.
d3_visualization 이 attribute 스텝을 흡수했던 것이 **같은 소프트웨어 안** 
에서도 일어났는데, OpendTect workflow 와 QGIS workflow 가 한 풀에서 경쟁
하게 두면 그 실패 모드를 **소프트웨어 단위로 재현**. 측정 후 발견 안 함.

### 사전 확인 (Q1, Q2) 결과 요약 재기재

- **Q1**: 정규 업로드는 vector 인덱싱 + auto workflow graph + knowledge graph
  (LightRAG) + CLIP 이미지 인덱스 **4종 자동 구축** (`embedder.py:160-183`).
  이식 비용 표에 수작업 항목 **없음**.
- **Q2**: Manual/Vector 는 UUID 기반 컬렉션 (`manual_{uuid}`) 로 자연 격리
  되나, Workflow 그래프는 `data/workflows/*.json` **전역 로드**. Cross-
  software 오라우팅 위험 존재. 이에 대응해 옵션 A (hint_workflow_id 벤치
  수준 격리) 채택.

### P-1 소스 판단: 전체 매뉴얼 PDF 채택 (narrowed URL 기각)

**최초 제안**: `https://docs.qgis.org/3.44/en/docs/training_manual/vector_analysis/`
(module-narrowed URL, Vector Analysis 모듈만 depth-2 crawl).

**결정: PDF (보유본, 전체 QGIS Training Manual 3.44)**.

**Narrowed URL 기각 사유** (사용자 지시, 감사 기록 원문):

1. **software_id 격리 논리 비적용**: software_id 로 QGIS workflow 만 검색
   대상 한정하는 것은 "배포 현실 반영" (사용자가 어떤 SW 를 쓰는지는 시스템
   이 아는 게 당연) 으로 정당화 가능. 그러나 **모듈 수준 사전 축소는 그
   논리가 성립하지 않음** — 실제 사용자는 매뉴얼 전체를 업로드하지, 자기가
   질문할 모듈만 골라 올리지 않음. 모듈 수준 사전 필터링 = "정답이 있는
   장소를 미리 알려주는 힌트" = software_id 격리와 성격이 다름.

2. **Vanilla_vector 비교 해석 가능성 훼손 (실질 피해)**: pilot 벤치에
   vanilla_vector 백엔드 비교가 들어가는데, KB 에 관련 모듈만 있으면
   **검색 난이도가 붕괴**. OpendTect 벤치에서는 454쪽 전체 매뉴얼 건초
   더미에서 vanilla 가 §1.5.1a 를 0/15 hit 하는 관찰이 나왔음. QGIS
   에서 건초더미를 미리 치워주면 fallback 발동률 예측 (~40%) 이든 파라
   메트릭 마스킹 관찰이든 **OpendTect 결과와 나란히 해석 불가**. 리뷰어
   가 "KB 를 해당 모듈로 사전 축소" 를 발견하면 pilot 관측 전체에 별표
   가 붙음.

3. **OpendTect 조건과의 대응 유지**: 전체 매뉴얼 인제스트 = OpendTect
   unified4 와 동일 조건 (raw haystack). Cross-software 관측 (마스킹,
   fallback 발동) 을 비교하려면 조건 통제 필요.

**PDF 채택 사유**:
- 결정적·오프라인·텍스트 기반 검증 완료 (사용자 사전 확인)
- OpendTect PDF 의 스캔 이미지 문제 없음 → HTML 우선 이유 소멸
- Full URL crawl 은 100+ 페이지 depth-2 로 네트워크 리스크
- Full manual 인제스트 시간 자체가 이식 비용 표의 정직한 실측값

**한계 기재 (pilot 보고서에 명시)**:
- **CLIP 이미지 인덱스 감소** — PDF 에서 embedded images 는 추출되나 HTML
  대비 커버리지 다를 수 있음. 시각 검색 (vision_only 백엔드) 성능에 영향
  가능. 한계로 기록하고 진행.

**Fallback 규칙**: PDF 업로드 자체가 실패하는 경우에 한해 full URL crawl 로
전환. **10분 초과 시 중단** 규칙 유지. **Narrowed URL 은 사용 금지.**

**업로드 실행 경로 (regular-path 원칙)**: 업로드는 UI 의 Submit 버튼이
호출하는 것과 **동일한 HTTP 엔드포인트** (`POST /api/manual/upload`) 로 수행.
내부 함수 직접 호출 (embedder.process_pdf 등) 금지 — 정규 업로드 경로
사용 주장이 이식성 논거의 조건이므로 유지. 자동화 스크립트는 스톱워치·수동
확인을 대체할 뿐, 시스템 경로 자체는 UI 와 동일.

### KB 범위 결정: Training Manual 단독 (Desktop User Guide 제외)

**최초 계획**: QGIS Training Manual + Desktop User Guide 두 PDF 를 순차 업로드
(사용자가 두 파일 경로 제공).

**변경 결정 (2026-08-12, 사용자 지시)**: **Training Manual 단독**. Desktop
User Guide 업로드 취소.

**근거**:
1. **OpendTect 벤치 KB 와의 조건 대응 유지** — unified4 의 KB 는
   OpendTect Training Manual 단독 (454p). QGIS 도 Training Manual 단독
   (697p) 으로 통일해야 cross-software 관측 (파라메트릭 마스킹, fallback
   발동, retrieval attribution) 이 나란히 해석 가능.
2. **시나리오 정의 소스와 KB 정합** — pilot 시나리오는 Training Manual 의
   레슨에서 추출. 시나리오와 KB 가 동일 문서에서 나와 절차 용어 매칭이
   자연스럽고 hint 논란 소지 최소화.
3. **이식 비용 계측 범위 명확화** — pilot 의 "이식 비용" 이 어느 문서
   범위인지 명확 (Training Manual 인제스트 시간 = 실측값). User Guide
   포함 시 계측 범위가 흐려짐.

**User Guide 처리**: "실사용 시 추가 업로드 가능한 문서" 로 pilot 보고서에
언급만 (실측 계측 없이 방법론 설명 목적).

**실행 시점**: PDF 2 (User Guide) 는 업로드 큐 진입 전에 script 강제 종료로
차단. Manual list 조회로 User Guide manual_id 생성 안 됨 확인 (컬렉션 오염
없음, 삭제 작업 불필요). Training Manual (`1b63832805da406bab1e06567cac7c69`)
인제스트는 FastAPI BackgroundTask 로 독립 실행 중이므로 script 종료와 무관
하게 완료까지 계속 진행.

### P-1 최종 결과 (Training Manual 인제스트 완료)

**첫 시도 (`1b63832805da...`)**: 45분 monitor timeout 초과, chromadb mtime
불변으로 확인 후 진단. 실제로는 hang 아니고 매우 느린 embedding 진행 중이
었으나 monitor budget 부족으로 놓침. DELETE 후 재시도.

**두 번째 시도 (`bf2804feea57434bb79b749134ed1df0`)**:
- 업로드 시각 (t0, Manual.created_at): `2026-08-13T00:00:52 UTC`
- ChromaDB 최종 write (t1_embed): `2026-08-13T00:56:23 UTC`
- Auto workflow 파일 최종 write (t1_wf): `2026-08-13T00:56:30 UTC`
- **총 소요 시간: 55.6 분 (약 56분)**
- chunk_count: 733
- workflow_count (auto): 1

**Ingest throughput 계측**: 697 페이지 / 55.6 분 = **12.5 페이지/분** (Gemini
Flash classifier + OpenAI-equivalent local embed + auto workflow build 포함).
비교: OpendTect Training Manual 454p, chunk_count 486 (unified2 setup).

**Auto workflow 관찰 특기**: AutoGraphBuilder 가 QGIS 매뉴얼에서 **1 개
workflow** 만 추출 (`auto_bf2804feea57..._follow_along_implementing_a_systematic_s`,
3 nodes). OpendTect (454p) 은 2 개 auto workflow. QGIS Training Manual 의
"Follow Along" 절차형 튜토리얼 스타일 중 특정 섹션만 인식된 것으로 보임.
Pilot 시나리오 정의 시 이 auto workflow 활용 또는 hand-author 추가 필요
(OpendTect 의 seismic_attribute 와 동일 방식).

**진단 스크립트 결과** (b6lc393wm, 격리 실행): parse 22.6s + chunk 0.3s +
classifier 13.6s/batch of 5 = 733 chunks × ~2.7s/chunk = 33분 (classify only).
남은 22분은 embed + store + auto workflow build + KG build.

**교훈** (methodology 노트): 대용량 문서 인제스트 시 monitor budget 은 **문서
크기 × 3-4 배 여유** 로 설정. QGIS 매뉴얼 697p → 56분 실측 → 최소 90-120분
budget 필요 (내가 30분 monitor budget 으로는 놓친 이유).

**Uvicorn stdout 캐치 이슈**: Windows 환경에서 `--reload` 자식 프로세스의
stdout 이 부모에 파이프되지 않는 문제 확인. Pilot 스코프 밖 (별건 개선
사항). 진단은 Manual API + 파일 mtime 으로 우회.

**산출물**: `data/eval/results/qgis_pilot_upload_report.md` (이식 비용 표
첫 실측값 + Auto workflow 목록 + QA 10-청크 샘플)

### P-2 방향 결정: β (Vector Analysis Buffer, hand-author)

**결정 (2026-08-13, 사용자 지시)**: **β — Vector Analysis Buffer 레슨을
hand-author, attribute_computation__01 상세도 의무화**.

**근거**:
1. **사전 등록된 시나리오 기준 대비 α 미달**: α (Auto workflow — Systematic
   Sampling, 3 nodes) 는 pilot 지시서의 "6~8스텝, 다이얼로그·파라미터
   포함, 상세도 의무화" 조건에 미달. 시나리오 표준 (attribute_computation__01
   템플릿) 을 pilot 에도 그대로 적용하는 것이 방법론 대응.
2. **OpendTect 방법론 대응**: OpendTect 벤치의 seismic_attribute workflow
   가 hand-authored + 시나리오 hand-authored (attribute_computation__01)
   구성이었음. QGIS 도 동일 조건 (hand-authored workflow + hand-authored
   시나리오) 으로 이식 비용 정량 측정.
3. **hand-authoring 소요 시간이 이식 비용 표의 목적 데이터**: pilot 의
   핵심 산출물은 "이식 비용 정량 (단계별 소요 시간)". Hand-authoring
   실측값이 그 표의 필수 행. Auto workflow 만 사용하면 이 실측값 자체가
   존재하지 않음.

**α 는 관찰로 유지**: Systematic Sampling auto workflow (1 개 추출) 은
"Auto extraction 의 현재 한계" 관찰로 pilot 보고서에 기재. Workflow 그래프
에는 유지 (삭제 안 함) — hint_workflow_id 로 pilot 벤치 시 QGIS workflows
만 검색 대상 지정할 때 이 auto wf 도 포함.

**진행 순서**:
1. Vector Analysis Buffer 레슨 스텝 목록 추출 (매뉴얼 chunks 검색 + 원문 대조)
2. 시나리오 JSON + workflow hand-authoring (attribute_computation__01 상세도)
3. 매뉴얼↔시나리오 스텝 대조표 제시 → **체크포인트 9 (사용자 응답 대기)**
4. Dry-run + hint_workflow_id 격리 확인

**Authoring 소요 시간 계측 시작**: `2026-08-13T01:28:52 UTC` (사용자
β 결정 접수 직후, chunk 검색 시작 전).

**초기 저작 (initial authoring) 완료**: `2026-08-13T01:35:56 UTC`.
- 소요: **7분 4초**
- 산출물: `data/workflows/qgis_vector_buffer.json` (5 nodes, 4 edges) +
  `data/eval/scenarios/qgis__vector_buffer__01.json` (8 steps, attribute_
  computation__01 상세도)
- 이식 비용 표 행 라벨: **"P-2 초기 저작"**
- 정제 (refinement) 발생 시 별도 행으로 기재 (dry-run 지적 반영·사용자
  피드백 반영 등 재편집)

**체크포인트 9 승인 후 goal 텍스트 dissolved 명시 확인** (2026-08-13):
Goal 텍스트에 "dissolved" 관련 6 회 언급 확인 — Dissolve results 활성/체크,
roads_buffer_50m_dissolved (레이어명 3회), dissolved 버퍼 렌더. 추가 편집
불필요. 사전 조건 충족.

### Dry-run 판정 기준 정정 (2026-08-13, 사용자 지시)

**사전 지시된 관문 재확인**: workflow 8/8 만이 아니라 **node 레벨 8/8 이
관문**. 초기 dry-run 리포트에서 workflow 8/8 만 확인 후 "PASS" 판정한
것은 판정 기준 완화. 정정.

**Step_5 dry-run 입력 정정 (충실도 개선)**:
- 문제: step_5 의 `current_action` 이 "about to click the '…' button next
  to Output to open **'Save to GeoPackage…' dialog**" 로 서술되어 있음.
  "Save to GeoPackage" 는 화면 밖 서사 (다음 단계 예고) 이고, 실전 라우터
  입력은 vision 추출로 오직 **화면에 표시된 것** 만 포함.
- 이 forward-looking 문구가 `_04_save_output` signature (`Save to GeoPackage`,
  `about to click Save`) 와 강 매칭되어 LLM rerank 가 다음 노드로 픽.
- **정정**: step_5 의 `visual_state_gt.current_action` 을 "cursor near the
  '…' button next to Output field" 로 재기술. `data_state` 도 "Ready to
  configure save location" 문구 제거. 화면 상 실제 표시 요소만.
- **근거**: dry-run 충실도 정정 (실전 vision 추출 반영), 관문 완화 아님.
  Attribute_computation__01 step_5 (routing_note 참조) 도 화면 상태만
  기술하고 forward action 은 최소화한 것과 동일 방침.

**이식 비용 표 정제 (refinement) 행 시작**: dry-run 결과 반영 편집 시작.
- 정제 소요 시간 계측 시작: `2026-08-13T01:41:20 UTC` (step_5 정정 편집 착수)
- 정제 완료: `2026-08-13T02:05:26 UTC` (dry-run 재실행 8/8 확인)
- **소요: 약 24 분** (편집 자체는 수 분, dry-run 재실행 + 결과 확인 포함)
- 이식 비용 표 행 라벨: **"P-2 정제 (step_5 forward-looking 문구 제거)"**
- 정제 결과: workflow 8/8 유지 + **node 8/8 신규 달성**. `_04` 시그니처
  축소 검토 불필요 (관문 통과).

### 정제 #2: 실측 데이터 불일치 정정 (2026-08-13, 사용자 실측 보고)

**불일치**: 매뉴얼 §6.2 본문 표기 (`roads_34S`, `buildings_34S`, UTM zone 34S,
EPSG:32734) vs 배포 QGIS Training Data 3.44 실제 (`roads_33S` 만, UTM zone
33S, EPSG:32733). Buildings 계열 부재.

**적용 원칙**: OpendTect `Seismic_data` 정정 선례 준수 — **실측 배포 데이터
기준 채택**. Ground truth 는 매뉴얼 텍스트가 아니라 사용자가 실제로 조작할
데이터.

**일괄 정정 사항**:
- `roads_34S` → `roads_33S` (scenario 23 곳, workflow 7 곳)
- `buildings_34S` → 시나리오·workflow 에서 완전 제거 (배포 데이터 부재)
- UTM zone 34S → 33S, EPSG:32734 → EPSG:32733 (프로세스 표기)
- 출력 레이어명 `roads_buffer_50m_dissolved` 는 유지 (매뉴얼 지정 사용자
  명명, 배포 데이터 의존 없음)
- `manual_reference` 에 불일치 노트 + buildings 제외 근거 추가

**Dry-run 재실행 필수 판단**: 레이어명 `roads_33S`, `buildings_34S` 가
workflow `_01` 및 `_03` signature `screenshot_keywords` 에 포함되어 있어
signature 매칭 대상 변경 → **재실행 실시**.

**Dry-run #2 결과**: workflow 8/8 · **node 8/8 유지** (모든 conf 0.90+).
`_03` 구분 step_3 (0.95), step_4 (0.90), step_5 (0.95) 정확. 관문 통과.

**Refinement #2 계측**:
- Start: `2026-08-13T02:20:48 UTC` (실측 불일치 보고 접수)
- End: `2026-08-13T02:24:39 UTC` (dry-run #2 통과 확인)
- 소요: **약 4 분**
- 이식 비용 표 행 라벨: **"P-2 정제 #2 (실측 layer name 정정 · roads_33S · buildings 제외)"**

**CRS 값 (EPSG:32733) 사용자 확인 대기**: 사용자가 "33S면 EPSG:32733 예상"
이라 하셨음. 실측 CRS 다르면 후속 정제 필요 (그 경우 정제 #3 행 신설).

**CRS 실측 확정 (2026-08-13, 사용자 실측 보고)**: **EPSG:32733 = WGS 84 / UTM
zone 33S (meters)** — 예상값 정확히 일치. **정제 불요**. `initial_state.description`
및 `must_be_true[2]` 의 EPSG:32733 표기는 실측 확정값이며 후속 편집 대상
아님. 시나리오 `initial_state` 전체를 **FINALIZED** 처리.

### P-3 캡처 진행 시작 (2026-08-13)

- **관문 통과 확정**: node 8/8 + 데이터 정합성 (실측 layer name + CRS 실측
  확정) 완료.
- **캡처 대상**: 8 스크린샷 (`data/eval/screenshots/qgis__vector_buffer__01/step_{0..7}.jpg`)
- **캡처 체크리스트**: 사용자 측 제공 완료 (직전 메시지 참조, layer 명칭은
  `roads_33S` 로 읽음)
- **진행 상태**: **IN PROGRESS** (사용자 QGIS 실행 → 8 스크린샷 저장 중)
- 캡처 완료 후 회신 대기 → `validate_screenshots.py` 실행 → P-4 벤치 진입

### P-3 캡처 완료 + validate 결과 (2026-08-13)

- **캡처 완료**: 8/8 파일 (`step_0.jpg`~`step_7.jpg`, 총 ~1.7MB)
- **validate_screenshots.py 결과**: 7/8 OK + 1 FAIL (step_7 false negative)
- **Step_7 false negative 진단**: 결함 #6 (validate_screenshots 필드 혼용) 재현.
  Validator 의 `_match_check` 가 `allowed_alternatives` 의 regex 패턴을 리터럴
  substring 으로 취급 + `expected_action_keywords: ["완료"]` 는 한글이나 vision
  extraction 은 영어 반환 → 매칭 실패.
- **실제 vision 확인** (수동): step_7 은 goal state 정확 인식 —
  `roads_buffer_50m_dissolved` 3회 명시 + `EPSG:32733` + `Layers panel` +
  `Map canvas displaying road network`. 캡처 자체는 완벽 통과.
- **판정**: 실측 vision 기준 **validate 통과**. Validator 결함은 audit-only
  기록이며 벤치 채점 파이프라인 무관 (unified3/4 도 같은 조건에서 정상 진행).
- **CRS 실측 재확인**: vision extraction 에서 `EPSG:32733` 명시 → 시나리오
  JSON initial_state 의 `EPSG:32733` 확정값 벤치 시점에도 정합 확인.

### P-4 벤치 실행 및 판정 결과 (2026-08-13, 프로젝트 마지막 벤치)

**실행**: 2026-08-13T03:00:30 ~ 04:01:30 UTC (**61 분**), Wrapper
`scripts/run_qgis_pilot.py` (recovery-aware, rc=4 credit-depletion 감지
포함), Isolation: OpendTect workflows 5 개 `.pilot_backup/` 임시 이동 + QGIS
시나리오만 있는 `.qgis_pilot_only/` 서브디렉토리.

**Primary 성공 기준 (사전등록 §2.1) 판정: ✅ SUCCESS (이식성 존재 증명 완료)**:
- ① End-to-end 완주 empty=0/120 ✓
- ② 5 개 지표 산출 전 셀 ✓
- ③ Fallback 로그 무결 ✓

**Secondary 예측 대조**:
- ✅ **예측 A (파라메트릭 마스킹) 확증**: vanilla_vector step_accuracy
  **62.5%** (예측 ≥40% 만족). 파라메트릭 마스킹의 **세 번째 데이터 포인트**
  — OpendTect attribute 시나리오 (0/15 검색 hit 에도 61.3% 유지) 와 유사
  패턴 재현.
- ✗ **예측 B (Fallback 30-50%) 반증**: 실측 **0.0%** (0/40). Hand-authored
  QGIS workflow signature 가 unified4 attribute (40.6%) 대비 훨씬 vision-
  extracted state 와 정합. 반증이지만 **긍정적 발견**.
- ✗ **예측 C (NONE bucket ≥20%) 반증**: 실측 **0.0%** (0/40). Guard hole
  재현 안 됨. Full_system 40 스텝 전량 `qgis_vector_buffer` workflow 로
  정확 라우팅 (통과율 57.5%).

**논문 함의**:
1. **Unified4 attribute fallback 40.6% + NONE 40% 는 signature 부적합
   특이 사례**. Signature 품질이 낮을 때 (unified4 attribute) 만 guard hole
   대량 발현. QGIS pilot 처럼 hand-authored signature 가 vision 과 잘
   매칭되면 fallback/NONE 은 0%. → "signature 품질이 시스템 안정성에 결정적"
   이라는 새 관찰.
2. **파라메트릭 마스킹은 재현 가능한 방법론적 이슈**: OpendTect + QGIS
   두 소프트웨어에서 동일 패턴 (vanilla 검색 실패에도 40%+ 유지). 논문
   `discussion_draft_parametric_masking.md` 의 lower-bound 서술 근거 강화.
3. **이식 비용 실측**: 4 시간 (single engineer, one afternoon). 사전 조사
   (7-10 인일) 는 다중 시나리오 + 여유 포함 예상. 1 시나리오 pilot 은 이
   하한을 크게 하회.

**성능 관찰 (판정 아님)**:
- vanilla_vector 와 no_rag 가 step_acc 동률 (62.5%) — 파라메트릭 마스킹
  극단 사례. Vector 검색 컨텍스트가 파라메트릭 지식 대비 이득 없음.
- Full_system 57.5% (약간 낮음) — 파라메트릭 강한 지형에서 workflow 문맥이
  오히려 방해 가능성 (attribute 시나리오와 유사).
- Cost 역설 유지: full $2.45m vs vanilla $4.69m (1.9× 저렴)
- Goal Completion 3 backends 모두 100% (3-gate 통과, 시나리오 goal state
  캡처 정확)

**정지 규칙 적용**: qgis_pilot2 없음. Primary 성공, 예측 B/C 반증도 그대로
기록. 논문 Discussion 에 "signature 품질과 guard hole 발현의 상관" 관찰
승격.

**산출물**:
- `data/eval/results/run_gemini_qgis_pilot_r{1..5}_*.json` (5 파일)
- `data/eval/results/qgis_pilot_bench.log`
- `data/eval/results/qgis_pilot_result_report.md` (최종 판정 보고 + 이식 비용 표)
- `data/eval/results/qgis_pilot_prereg.md` (사전등록, 대조 대상)
- `data/eval/results/qgis_pilot_upload_report.md` (P-1 인제스트)

---

## 저장소 정리 이력 (2026-08-13, 사용자 지시)

**Pre-refinement 캡처 백업 삭제**: 아래 3 폴더 (총 12 파일) 삭제, 재캡처
버전만 유지:
- `data/eval/screenshots/opendtect__survey_setup__01.unified2_bak/` (4 파일)
- `data/eval/screenshots/opendtect__3d_visualization__01.unified2_bak/` (4 파일)
- `data/eval/screenshots/_stale/opendtect__3d_visualization__01_pre_20260707/` (4 파일)

**정리 후 활성 시나리오 캡처 (4 폴더)**:
- `opendtect__survey_setup__01/` (4)
- `opendtect__3d_visualization__01/` (4)
- `opendtect__attribute_computation__01/` (8)
- `qgis__vector_buffer__01/` (8)

**감사 영향**: unified2 시점 캡처 원본은 소실. 대신 methodology_audit_trail
§ 시나리오 refinement #1 (2026-08-06) 에 refinement 사유 · 정의 변경 텍스트가
남아있음 (파일 크기 비교 근거는 소실). Refinement 이력의 서술적 근거는 유지되나
캡처 원본 대조는 불가.

---

## v3 재실행 준비 — 변경 기록 (2026-09-17 ~ 2026-09-18, append-only)

**전제**: unified4 매트릭스는 검토 결과 양쪽(시스템·baseline) 결함이 확인되어 v3로 재실행하기로 함. 모든 수정은 사전등록 서명 전에 확정하고 전 백엔드에 동일 적용한다. 브랜치 `v3-rerun`. 사전등록 초안: `v3_pre_registration_DRAFT.md`.

### V3-0. 2026-09-17 코드 변경 (사전등록 초안 §2에 대응)
- 채점기 v3 (`api/services/evaluation.py`): (S1) 시나리오 패턴의 `\b( … )\b`를 ASCII 경계로 재작성 — Python `\b`가 한글 조사를 단어 문자로 취급해 'name에', 'Cross-line에서'가 불일치하던 결함. (S2) 환각 판정을 따옴표 무관하게 — 대문자 시작 라틴 라벨 구를 모두 추출, 근거 어휘 = visible_elements + current_dialog + active_menu + data_state + current_action + screen_state, 목표 문장의 값 제외. (S3) `_strip_thinking`이 미폐쇄 `<think>` 블록을 제거. `GEOLENS_SCORER=v2`로 구 채점기 재현(저장값과 2,120/2,120 일치 확인).
- 비용 회계: 생성기 thinking 토큰(출력 단가)과 vision·rerank 보조 호출(캐시 적중 포함)을 기록, `cost_total_usd` 신설 (`guide_pipeline.record_aux_usage`, `bench_backends._record_usage`).
- 하네스: visited_node_ids를 세션 상태로 유지(재-localize O(N²) 제거), state_path 텔레메트리 기록, rerank 'none' 경로를 fallback으로 라벨.
- 컨텍스트 조립: KG triplet 블록을 뒤로(`RAG_KG_POSITION=last`); graph_only에 linked_chunks 본문 주입; `vanilla_budget` 백엔드(3,900자 예산) 추가.
- 생성 설정 통일: temperature 0.2, 답변 1,024 토큰, Gemini thinking 예산 1,024 (`GEN_*`, `GEMINI_THINKING_BUDGET`). 보조 Flash 호출 thinking off(`AUX_THINKING_BUDGET=0`, dry-run으로 채택 근거 확보: 정답 12/24 vs 13/24, 비용 5.3배 절감).
- 임베더: all-MiniLM-L6-v2(256 토큰 절단, 영어 중심) → BAAI/bge-m3, 같은 청크 id로 재임베딩한 `data/chromadb_v3` (OpendTect 521, QGIS 733). google-genai 1.3.0 → 1.75.0.
- QGIS 실행 비격리(`run_qgis_pilot.py --isolate` 기본 off).
- 재채점 자료: `rescore_v3_{unified4,longctx,qgis_pilot}.md`, 리플레이 `retrieval_replay_{minilm,bgem3}.md`, dry-run `routing_dryrun_vision_{think0,thinkdyn}.md`, 스모크 `run_gemini_v3smoke_r1_20260917T093224.json`.

### V3-1. 작업 0 — Qwen 제외 (2026-09-18)
- 사유: Qwen3-VL 서빙 불가(NAS 미접속), 텍스트 전용 Qwen은 스크린샷을 받지 못해 입력 조건이 다름(unified4에서 이미 그랬음: no_rag 입력 토큰 514 vs 550/1,394/2,056).
- 변경: 집계 스크립트 9종의 `MODELS`를 `BENCH_MODELS` 환경변수(기본 gemini,claude,gpt)로, `run_all_models.py` 기본 모델 3종, `run_v3.sh`에서 Qwen 프로브·환경 제거. unified2/3/4 재집계는 `BENCH_MODELS=gemini,claude,gpt,qwen`으로 가능. `_call_qwen` 코드는 남기되 v3 파이프라인에서 호출하지 않음.

### V3-2. 작업 2 — 사전등록 항목 점검 (2026-09-18)
- 확인: vanilla_budget ✓, 생성 설정 통일 ✓, QGIS 비격리(41노드 풀) ✓, rerank none → fallback ✓, KG 블록 후순위 ✓, graph_only 청크 본문 ✓.
- 추가 구현: `run_qgis_pilot.py --models gemini,claude,gpt` (3모델 전부), QGIS도 dev 세트와 같은 7 백엔드 실행(`--backends` 제한 제거).

### V3-3. 작업 3 — 3d_visualization 목표 절 0/13 원인 (2026-09-18)
- 인덱스의 `1.3.1a Display An Inline` 청크는 1개(p.46, 572자)이며 제목·라이선스·메모리 안내만 있고 절차 문장이 없다. pdfplumber 기준 p.46 텍스트 384자 + 이미지 1, p.47 53자 + 이미지 2. OCR 규칙은 `MIN_TEXT_LENGTH = 50` 미만 페이지만 OCR하므로 두 페이지 모두 OCR 대상에서 제외되어 그림 속 절차(우클릭 → Add Default Data 등)가 인덱스에 없다.
- 결론: 목표 청크 정의 오류가 아니라 인덱스 내용 결손(OCR 임계값). 목표 문장의 어휘('Add Data', 'Select Cube')는 1.3.2a(p.52), 1.2.2a(p.27) 등 다른 절에만 존재. 조치는 사용자 결정 사항(OCR 임계 상향 재인제스트는 KB 변경이라 사전등록에 명시 필요).

### V3-4. 작업 4 — rescore 요약 (2026-09-18)
- `rescore_v3_summary.md`: 3모델 18셀의 v3 환각률 분포 {0: 1, 0–5: 3, 5–10: 3, 10–20: 8, >20: 3} — 0 근처가 아니므로 판정 지표에서 제외할 근거는 없음(단, GT visible_elements 보정 전 값). 채점기만 바꿨을 때 full vs vanilla step accuracy 방향: Gemini vanilla → full, Claude full → 동률, GPT 불변(full); 3모델 카운트 2/3 → 2/3.

### V3-5. 작업 1 — 라우팅 진단과 메커니즘 수정, 동결 (2026-09-18)
- 진단(개발 세트 16스텝, 저장된 vision 출력으로 오프라인 재계산, `routing_diag_dev_v2.md`): 실패 9 = 후보 단계 탈락 8(attribute 전부) + rerank 거절 1(3d_viz s3). seismic_attribute 노드의 v2 부분문자열 점수 0.18–0.20 vs 타 워크플로우 0.47–0.67. CLIP 후보는 모든 OpendTect 화면에서 d3_visualization·auto_bf2804(QGIS) 노드에 0.82–0.91.
- 결정: 개별 signature 수정 금지 원칙에 따라 후보 단계의 매칭 함수만 교체 — 부분문자열 비율 → bge-m3 코사인(vision 출력 ↔ 노드 제목·설명·expected_dialog·UI 요소·키워드). `api/services/node_matcher.py`, `WorkflowGraph.get_top_k_nodes/get_current_node`가 `ROUTER_MATCHER=embedding`(기본)일 때 위임, `substring`으로 v2 재현. vision 프롬프트 변경(a)은 화면 문자열이 이미 보고되므로 채택하지 않음.
- 오프라인 확인(같은 vision 출력): 기대 워크플로우가 top-3 풀에 8/16 → 14/16.
- dry-run(vision+rerank, thinking off, 개발 세트만): 정답 워크플로우 7/16 → 12/16 (survey 4/4→4/4, 3d_viz 3/4→**2/4**, attribute 0/8→6/8), 유지 10→13, none 5→3, 보조비용 $1.35m→$1.30m/스텝, 지연 10.7→10.6 s. 불리한 변화: 3d_viz s2가 d3_visualization(0.8)→none. attribute s5는 d3_visualization으로 오라우팅, s7은 none.
- QGIS 테스트 세트는 실행하지 않음(동결 전 금지 준수).
- **메커니즘 동결 커밋**: `bacfde7f79b2dff13361a159767339d9a4e36061` (branch v3-rerun, 2026-09-18 09:46 KST). 이 커밋 이후 라우팅 메커니즘(후보 단계·CLIP·rerank·confidence 게이트)은 QGIS 결과와 무관하게 변경하지 않는다. 커밋에는 unified3/4·QGIS 파일럿의 미커밋 산출물, 2026-08-07 seismic_attribute signature 재작성, v3 코드·문서가 함께 들어감(로그 unified3/4_bench.log는 제외).

### V3-6. 작업 6 — 사전등록 초안 v2 (2026-09-18)
- `v3_pre_registration_DRAFT.md` 전면 개정: |M|=3, 층화 순열검정(`scripts/stats_stratified.py`) 1차, A 조건(방향 3/3 또는 2/3+층화 p<0.05), Qwen 제외 사유, 재개 사유 D1–D12, 세트 구분·이력, 금지 사항·동결 해시, QGIS 실행 전 예측(P5), hall 처리 규칙(S6 후 중앙값 <5%면 기술 지표), judge κ 보조 지표, S6 절차, n=10, v4 없음, 열세 시 보고, unified4 비용 직접 비교 불가, 한계.

### V3-7. 작업 5 — GT visible_elements 전수 열거 (2026-09-18, 반영 전)
- 절차: 24장(OpendTect 16 + QGIS 8) 전부에 같은 프롬프트로 gemini-2.5-pro, temperature 0, JSON 출력. 화면의 창 제목·메뉴·버튼·탭·필드 라벨·리스트/트리 항목·체크박스/라디오·기타 텍스트를 원문 그대로 열거. 모델 응답 로그는 참조하지 않음. 스크립트 `scripts/gt_enumerate_visible_elements.py`, 원자료 `gt_visible_elements_enum_v3.json`, 검수용 diff `gt_visible_elements_review_v3.md`.
- 결과: 현 GT 137항목 vs vision 열거 1,378항목. 후보 추가(A) 1,129, vision이 읽지 못한 현 GT 항목(B) 25. B의 다수는 텍스트 없는 아이콘 버튼(survey s0의 Add/Edit)이나 GT의 서술형 표기('Survey Data Root tab')로, 사람이 판단할 항목.
- 반영하지 않음. 사용자 검수 후 반영하며, 반영 시 unified4 로그를 구·신 GT로 재채점해 백엔드별 변화량을 사전등록 §3에 추가한다. QGIS 라우팅 dry-run이 아니며 QGIS 파일은 GT 필드만 대상.

---

## v3 개발 루프 (2026-09-18 ~) — 목표: full_system이 vanilla_vector·vanilla_budget보다 step accuracy·총비용·지연에서 앞서도록 개선. 개발 세트 = OpendTect 3 시나리오, 테스트 세트 = QGIS(동결 전 미실행). 채점기·GT·판정 기준은 개발 결과를 이유로 바꾸지 않는다.

### V3-8. 작업 A — 선행 정리 (2026-09-18)
- Qwen: 3모델 고정(BENCH_MODELS 기본값). held-out 초안(`scenarios/excluded/heldout_drafts/`) 삭제 — 테스트 세트는 QGIS 하나.
- KB 재인제스트: `pdf_parser.py`에 이미지 면적 기준 일반 OCR 규칙 추가 — 본문이 있는 페이지의 임베디드 이미지 중 면적 ≥ 3%(`OCR_FIGURE_AREA_MIN`)를 각각 잘라 Gemini Flash OCR 후 `[Figure OCR p.N #k]` 블록으로 본문에 덧붙임(`OCR_FIGURES=0`이면 v2). 근거: OpendTect §1.3.1a(p.46)의 절차가 그림에만 있음 — 프로브 OCR로 "1. Right-click on Inline in the tree and select Add and Select Data. 2. … 4 Dip steered median filter. 3. Click OK" 복원 확인. 대상: OpendTect 텍스트 페이지 중 이미지 ≥10% 104p(+기존 <50자 279p), QGIS 541p. 양쪽 매뉴얼을 같은 규칙으로 `scripts/reindex_v4.py`(파싱→청킹→bge-m3→`data/chromadb_v4`; 분류기·자동 워크플로우·KG·CLIP 재생성은 하지 않음)로 재인제스트 시작. linked_chunks는 완료 후 (section, page, 텍스트 중복도)로 재매핑 예정.
- GT: `scripts/gt_apply_visible_elements.py`로 24장 전부에 vision 열거 A 항목 반영(902개 추가; 스텝별 GT 크기 10~60). 3자 미만 항목은 정확 일치만 인정(`evaluation._hallucinated_elements_impl`). B 25건과 표본 3장(survey s0, attribute s3, QGIS s3)은 `gt_review_B_and_samples.md`로 사용자 검수용 정리. 패턴(survey s0 '+', QGIS s3)은 변경하지 않음.
- 새 GT로 unified4 재채점(`rescore_v3_unified4_gtv3.md`): v3 hall 3모델 18셀 5.8~13.3%(중앙값 8.3%) → 사전등록 규칙(중앙값 <5%면 기술 지표)에 따라 hall은 판정 지표로 유지. full vs vanilla_vector: step_acc Gemini full/Claude 동률/GPT full, hall 3/3 full 우세. (v2 채점기 재현이 저장값과 110/1,920 불일치하는 것은 GT 변경 때문이며 예상된 결과.)

### V3-9. 작업 B 준비 — 메커니즘 구현과 linked_chunks 결손 발견 (2026-09-18)
- **발견**: `data/workflows/*.json`의 linked_chunks id 98개(OpendTect 5개 파일 92 + QGIS auto 6)가 unified2–4에 쓰인 `data/chromadb`에도, `data/chromadb_v3`에도 하나도 존재하지 않는다. 원인: 2026-04-16 `chunk_mapper`로 생성된 id가 2026-07-27 pdfplumber+pypdf 재인제스트(청크 uuid 전부 재생성)로 무효화됨. 따라서 unified2–4의 full_system graph_context에는 linked_chunks 본문이 한 번도 들어가지 않았고, 노드 제목·설명으로 한 벡터 검색(graph_vector) 결과만 들어갔다(v3에서 추가한 graph_only의 linked_chunks 주입도 v3 인덱스에서는 빈 값이었음). 대응: 옛 청크 본문이 없어 id 재매핑이 불가능하므로, 원래 메커니즘(`chunk_mapper.map_node_to_chunks`: 쿼리 = 워크플로우명+제목+설명+screenshot_keywords, 임베딩 top-3)을 v4 인덱스·bge-m3로 재실행해 OpendTect 5개 워크플로우만 재링크한다(`scripts/relink_chunks_v4.py`, 노드별 provenance와 옛 id 기록). QGIS auto 워크플로우(auto_bf2804…)는 손대지 않음 — v2와 같은 dangling 상태이며 런타임은 graph_vector로 대체된다.
- **구현**(전부 env 스위치, v2 동작 재현 가능; 채점기·GT·판정 기준은 변경 없음):
  - 후보 풀: `ROUTER_MATCHER=embedding|substring|hybrid`; 임베딩 top-`ROUTER_POOL_K`(기본 5) ∪ CLIP top-3 ∪ 그래프 prior(직전에 게이트를 통과한 노드의 후속 노드 + 그 노드, `ROUTER_GRAPH_PRIOR=1`). 부분문자열 경로도 v3 vision 필드(window_titles/menu_items/buttons/labels)를 포함(`node_matcher.flatten_visual_state`).
  - vision 프롬프트 v3(`VISION_PROMPT_VERSION=v3`): 화면 문자열을 원문 그대로 window_titles·menu_items·buttons·labels로 보고(기존 5개 키 유지).
  - rerank 프롬프트 v3(`RERANK_PROMPT_VERSION=v3`): 세션에서 이미 준 지시(최근 6개)와 그래프 prior(expected-next)를 입력에 포함, 화면 문자열 대조 규칙, confidence 구간 정의(≥0.9 문자 증거 / 0.7–0.85 같은 워크플로우·화면 일치 / ≤0.65 불확실). v2의 'bias toward picking' 규칙은 `v2`로 재현.
  - confidence 게이트: `CONFIDENCE_THRESHOLD` env(기본 0.7). 개발 세트에서 정답/오답 pick의 confidence 분포로 보정 예정.
  - 검색·컨텍스트: 목표 질의 벡터 검색(vanilla와 동일한 검색)을 vision 호출과 병렬 스레드로 실행(`PARALLEL_RETRIEVAL=1`). fallback(rerank none·게이트 미달) 컨텍스트 = 그 결과를 `FALLBACK_CTX_CHARS`=3,900(= vanilla_budget) 예산으로 매뉴얼 본문만. 라우팅 시 = linked_chunks 본문 `GRAPH_CTX_ITEMS`×`GRAPH_CTX_CHARS`(3×800) 우선 + 같은 목표 질의 결과 `VECTOR_CTX_CHARS`(1,500) (합계 3,900). 라우팅 시 벡터 질의는 v2의 '[wf > title] goal' 대신 목표 질의 결과 재사용(`ROUTED_VECTOR_QUERY=goal`, v2는 `enriched`); linked_chunks가 있으면 노드별 제목 검색 생략(`GRAPH_VECTOR_AUX=0`). 지질 KG 블록은 전 백엔드에서 제외(`RAG_KG_ENABLED=0`).
  - 세션 상태: bench의 full_system·state_path가 `completed_steps`(이전 스텝 응답)와 `last_confirmed_node_id`(게이트 통과한 마지막 노드)를 파이프라인에 전달.
  - 계측(불리한 방향): vision 캐시 적중 시 원 호출의 벽시계 지연을 재계상(`replayed_latency_sec`; 평가기 `latency_sec` = 측정 벽시계 + 재계상, `latency_wall_sec` 별도 저장). 같은 프로세스에서 여러 백엔드가 같은 스크린샷을 분석해 캐시에 맞으면 full_system 지연이 과소평가되던 것을 막는다. rerank 지연도 보조 호출 기록에 포함. 스텝별 컨텍스트 길이(`context_chars`)와 본문(`BENCH_SAVE_CONTEXT=1`) 기록.
  - 개발 루프 도구 `scripts/dev_iter.py`: OpendTect 3 시나리오만 담은 임시 디렉터리로 bench 실행(QGIS 시나리오 미적재; 워크플로우 7개는 전부 적재), 프로파일 `v2mech`(동결 커밋 bacfde7f 시점 메커니즘을 knob으로 재현: pool 3, prior 없음, v2 프롬프트, 순차 검색, enriched 질의, KG 블록 포함, fallback 1,500자)와 `v3`, 스텝별 라우팅 표·손실 분류(misrouting / fallback_quality / context_or_generation)·정답/오답 confidence 분포·정지 조건 판정.
- QGIS 시나리오·signature 미접촉, 미실행(dry-run 포함).

### V3-10. 사용자 결정·확인 사항 반영 (2026-09-18, 개발 루프 중)
- **QGIS linked_chunks 연결 결정**: QGIS 워크플로우(`qgis_vector_buffer.json`, 노드 5개, linked_chunks 없음)에도 OpendTect와 같은 절 출처 규칙을 적용한다 — `manual_sections = ["6.2.6"]`(QGIS Training Manual 3.44 §6.2.6, 워크플로우 파일 자체의 manual_reference), `chunk_mapper.map_node_to_chunks`로 해당 절 청크를 임베딩 거리순 top-3. signature·노드 제목·설명·시나리오 파일은 건드리지 않는다. QGIS 재인제스트 완료 후, 동결 커밋 전에, QGIS 시나리오를 실행하지 않은 상태에서 수행한다(`scripts/relink_chunks_v4.py --manual qgis`; 소요 시간을 보고서에 기록해 이식 비용 표에 넣는다). 사전등록 초안에는 "QGIS 결과를 보기 전에 수행한 배포 설정"으로 적는다.
- **그래프 prior·완료 지시문의 출처 확인**(코드 근거): full_system의 `last_confirmed_node_id`는 `bench_backends._session_last_confirmed()`가 돌려주는 값으로, 앞 스텝에서 파이프라인이 스스로 고른 노드가 confidence 게이트를 통과했을 때 `_session_note_confirmed()`로 기록된 세션 상태다(스텝 0에서 초기화). `completed_steps`는 평가기가 넘겨주는 `prior_responses`, 즉 같은 백엔드가 앞 스텝에서 생성한 응답 원문이다. `visited_node_ids`도 앞 스텝의 파이프라인 pick(게이트 전)이다. `bench_backends.py`·`guide_pipeline.py` 어디에서도 시나리오의 `expected_workflow_node`·`visual_state_gt` 등 GT 필드를 읽지 않는다(grep 확인). 생성기 프롬프트의 완료 스텝(`_build_messages`의 `completed = prior_responses`)은 모든 백엔드에 동일하게 주어지는 기존 방식 그대로다. 변경 없음.
- **보고 방식**: 각 iteration 보고에서 full_system을 vanilla_vector(무절단)와 vanilla_budget(3,900자) 양쪽과 비교하고, fallback 스텝만 따로 떼어 fs / vanilla_vector / vanilla_budget 정답 여부와 컨텍스트 길이를 표로 낸다. fs ✗·vanilla_vector ✓·vanilla_budget ✗인 스텝(절단 귀속 손실)이 있으면 FALLBACK_CTX_CHARS와 VANILLA_BUDGET_CHARS를 함께 올리는 예산안을 제시한다(`dev_iter.py` 분석 확장).
- **V3-9 주석 위치 정리**: unified2–4 full_system 수치를 인용하는 문서를 스캔해 `data/eval/results/v3_linked_chunks_annotation_sites.md`에 정리(마크다운 153개 파일의 절/표 제목, Downloads의 논문 원고 2종·종합결과보고서 1종의 단락/표). 붙일 문구: "unified2–4 full_system은 linked_chunks 본문 없이 측정됨(2026-07-27 재인제스트 이후 id 전부 무효, graph_context = 노드 제목·설명 벡터 검색만; V3-9)".
- **기록해 둘 실수**: `scripts/retrieval_replay_v3.py`가 시나리오 디렉터리 전체를 돌기 때문에, v4 리플레이(`retrieval_replay_bgem3_v4.md`) 실행 시 QGIS 시나리오의 목표 문장으로 벡터 검색 1회가 호출됐다. 그 시점에 QGIS v4 컬렉션이 없어 결과는 0청크였고 vision·라우팅·생성은 없었다. 스크립트는 이제 `--include-qgis` 없이는 QGIS를 건너뛴다.

### V3-11. QGIS linked_chunks 연결 완료, 지연 계측 분해, 판단 기준 변경 (2026-09-18)
- **QGIS 연결(사용자 결정 V3-10)**: QGIS v4 재인제스트 완료(745청크, 1,507 s, 그림 OCR 668건) 직후, QGIS 시나리오를 실행하지 않은 상태에서 `scripts/relink_chunks_v4.py --manual qgis` 실행. QGIS 파서는 절 번호가 아니라 절 제목(난이도 별 포함)을 section 라벨로 저장하므로 §6.2.6은 라벨 "★☆☆ Follow Along: Analyzing the Problem: Distances From Schools and Roads"(pp. 212–218, 7청크, 유일)로 지정했다. 첫 실행은 접두사 "6.2.6"으로 해 절 청크가 0개 매칭되어 전역 top-3으로 떨어졌고(노드 01·04가 다른 절), 라벨 접두사로 고쳐 재실행했다 — 최종: 노드 5개 전부 §6.2.6 청크 3개씩(pp. 213–218). 이식 비용: 스크립트 벽시계 15.8 s(모델 로드 포함, 노드 5개), 사람 작업(라벨 형식 확인 + 매핑 한 줄) 약 5분. 바뀐 필드는 `linked_chunks`·`manual_sections`·`linked_chunks_provenance`뿐임을 git HEAD와 비교해 확인(signature·제목·설명·edges·시나리오 파일 불변). 사전등록 초안에 "QGIS 결과를 보기 전에 수행한 배포 설정"으로 기재.
- **지연 분해 계측**(`api/services/stage_timer.py`): 스텝마다 vision / vision_replayed(캐시 재계상) / embed(질의·노드 임베딩) / clip / rerank / vector_search / neighbor_fetch / chunk_fetch / kg_search / generate 와 포함 단계 localize·goal_retrieval·routed_retrieval 초를 기록해 `per_step.stage_latency`에 저장. `dev_iter.py` 보고서에 단계별 표와 "vanilla 대비 추가 지연"을 넣음. iteration 0(v2mech)은 계측 전 코드로 실행돼 단계 값이 없고, 실행 중 QGIS 재인제스트(그림 OCR·bge-m3 임베딩)가 돌아 지연 절대값은 "오염 가능"으로 표시한다. iteration 1(v3)은 재인제스트 종료 후 단독 실행.
- **판단 기준 변경(사용자 지시)**: 1~2회 실행의 step accuracy 차이는 잡음이므로 1차 근거에서 제외. 1차 = (a) full_system 라우팅 정답률과 confidence ≥ 0.7 오라우팅 건수, (b) 스텝별 목표 절 검색 적중(컨텍스트의 [Section] 태그가 시나리오 목표 절로 시작하는지; fs vs vanilla 양쪽), (c) 스텝별 손실 분류 + 네 백엔드 전부 실패한 스텝의 응답 원문·GT 패턴 보고. 2차 = step acc(vanilla_vector·vanilla_budget 양쪽), 총비용, 단계별 지연. 지연 목표는 "vanilla보다 빠름"이 아니라 "vanilla 대비 추가 지연 최소화". 채점 패턴은 바꾸지 않는다.
- **V3-9 주석 배치(사용자 지시)**: 과거 결과 파일 153개는 수정하지 않음. `data/eval/results/README.md`(신규) 1회, `final_unified4_table.md`·`table1_full_sd_unified4.md`·`qgis_pilot_result_report.md` 머리에 한 줄씩. 종합결과보고서는 Word에서 열려 있어 원본 저장이 거부되어(`PermissionError`) 백업 `GeoLens_종합결과보고서_final.backup_20260918.docx`를 만든 뒤 주석본 `GeoLens_종합결과보고서_final.annotated_V3-9_20260918.docx`로 저장(§1.2 백엔드 정의 단락 뒤 굵은 한 단락). ACAGS 원고는 건드리지 않음.

### V3-12. iteration 0·1 결과, 기준 지연, step-3 패턴 이력, iteration 2 범위 축소 (2026-09-18)
- **작업 방식(사용자 지시)**: 벤치 실행 중에는 라이브 작업 트리의 파일을 수정하지 않는다. iteration 패치는 별도 git worktree(`../GeoLens-paper-wt-iter2`, branch `v3-iter2`)에서 만들고 벤치 종료 후 적용한다. 모든 결과 JSON에 코드 커밋 해시와 미커밋 diff 해시를 기록한다(`bench_runner.code_version()`; iteration 0·1·기준 지연 JSON은 사후에 커밋 `c15259f`로 표기하고 차이를 메모). **기록해 둘 실수**: iteration 1 실행 중 iteration-2 패치의 "드라이런"이 ROOT 치환 실패로 라이브 파일 4개에 실제 적용됐다가 약 1분 뒤 패치 전 복사본으로 바이트 동일하게 복원됨(실행 중이던 벤치 프로세스는 모듈을 이미 적재해 영향 없음; 복원 후 컴파일·식별자 검사로 확인). 이후 위 작업 방식을 채택.
- **iteration 0 (v2mech knob, v4 KB, 재인제스트와 동시 실행 → 지연 오염 가능)**: 라우팅 14/16 통과 중 정답 11, confidence ≥ 0.7 오라우팅 3(attribute s0·s1 → 04_configure 0.9, s5 → d3_visualization 0.7), fallback 2. 목표 절 적중 full 15/16 vs vanilla 12/16(3d_viz: full 3/4, vanilla 0/4). 손실 2(attribute s7 fallback_quality, survey s0 context_or_generation). 네 백엔드 전부 실패: 3d_viz s3(완료 sentinel 대신 지시 출력 — 목표 상태 인식 실패, KB·패턴 아님), attribute s1(같은 다이얼로그 내 다른 하위 동작 — 생성). 임계값 보정표: 오라우팅 confidence(0.7, 0.9, 0.9)가 정답과 같은 범위라 0.95 미만 어떤 임계값도 오라우팅을 걸러내지 못함 → 게이트가 아니라 상류(후보·rerank 근거)에서 고쳐야 함. step acc fs 0.750 / vv 0.750 / vb 0.792(참고).
- **iteration 1 (v3 메커니즘 V3-9, 재인제스트 종료 후)**: 라우팅 16/16 정답, 오라우팅 0, fallback 0. 목표 절 적중 full 16/16 vs vanilla 12/16. 손실 1(3d_viz s3: fs "Add Default Data" ✗, vanilla_vector "Z-slice를 우클릭" ✓ — 요소 언급 허용 대안 패턴에 의한 일치; 둘 다 sentinel이 아님). 전 백엔드 실패 스텝 없음. confidence 정답 분포 0.7×2, 0.9×10, 0.95×4. step acc fs 0.917 / vv 0.792 / vb 0.792(참고); 총비용/스텝 $0.0111 / $0.0159 / $0.0080. attribute s0·s1의 0.9 오라우팅은 iteration 1에서 사라짐(s0 → 02 0.95, s1 → 03 0.90); 후보 풀·rerank 입력 재구성은 V3-13.
- **기준 지연(재인제스트 종료 후 단독 실행, survey_setup, Gemini, iteration-1 코드, `latency_baseline_survey_iter1.md`)**: full_system 24.1 s/스텝 = generate 9.0 + vision 4.5 + clip 4.0 + embed 3.2 + rerank 1.3 + 검색 0.4(+ 스레드 대기); vanilla_vector 9.6(generate 7.4 + embed 1.9), vanilla_budget 7.8. vanilla 대비 추가 지연 +14.6 s(iteration 1 전체에서는 +10.4 s). 단계별 절감 후보: CLIP(4.0 s, 로컬)을 vision 호출과 병렬화 — iteration 2에 적용; 나머지(vision·rerank 호출, 노드/질의 임베딩)는 사용자 지시로 보류. 최종 실행의 지연 보고 방식 제안: 모델·백엔드는 순차 실행(동시 실행 금지), 재인제스트 등 다른 작업 없음, 지연 표는 별도 "clean run"(survey_setup × full/vanilla × 3회, 단일 프로세스)에서 단계 분해로 보고하고 본 행렬의 지연은 참고 값으로 표기.
- **3d_viz step 3 허용 대안 패턴 이력(사용자 요청)**: 요소 언급 패턴 `(?i)(In[- ]?line|Cross[- ]?line|Z[- ]?slice|3D Scene|Elements)`("Ground-truth element mention for the grounding validator")은 2026-08-06 unified3 step_3 재정의(목표 달성 상태로 재캡처, sentinel 패턴 도입)와 **같은 변경**으로 추가됨(본 문서 "시나리오 refinement #1", 항목 "allowed_alternatives 에 grounding validator 용 요소 mention 키워드 추가"). git에서는 8월 변경이 미커밋 상태였다가 동결 커밋 `bacfde7`(2026-09-18)에 처음 들어감(직전 커밋 37b170f 2026-07-24의 step_3은 "Z-slice|Add.*Data" 패턴, 대안 1개). 즉 재정의 이전이 아니라 재정의의 일부. 제거 시 영향(`pattern_impact_3dviz_s3.md`, 패턴 미변경): iteration 0 변화 없음; iteration 1 vanilla_vector s3 ✓→✗(1셀); unified4: Claude state_path 1, Gemini state_path 1, GPT state_path 2·vision_only 1, Qwen 13셀 ✓→✗ — 3모델의 full_system·vanilla_vector·no_rag·graph_only는 변화 없음.
- **iteration 2 범위(사용자 결정)**: 넣는 것 = 종료 상태 블록(직전 확정/현재 pick이 워크플로우 말단 노드이고 화면이 그 노드에 가장 가까우면 "[Goal State Check]" 블록; 워크플로우 구조·세션·vision만 사용) + CLIP‖vision 병렬화. 증거 기반 gate((i) expected_dialog ⊂ 창 제목, (ii) 직전 확정 노드/후속, (iii) 임베딩 1–2위 격차)는 오프라인 표에서 iteration 1 정답 16건을 하나도 떨어뜨리지 않고 iteration 0 오라우팅 3건을 모두 거를 때만 켠다(규칙 수정 금지). 2단계 라우팅 보류. 생성기 명명 규칙 미적용. 패턴은 사용자 결정 전까지 불변.

### V3-13. 사용자 결정: 3d_viz step 3 허용 대안 패턴 유지; 증거 gate 미채택; iteration 2 벤치 보류 → iteration 3 (2026-09-18)
- **step 3 패턴**: 조사 결과(V3-12: 요소 언급 대안은 2026-08-06 step_3 재정의와 같은 변경에서 grounding validator용으로 의도적으로 추가됨; 제거 시 3모델 full_system·vanilla_vector 변화 없음, state_path·vision_only 일부와 Qwen 다수 변화) 위에서 사용자 결정 **"유지"**. 패턴·GT 변경 없음.
- **증거 기반 gate 미채택**: 오프라인 표(`evidence_gate_offline_iter0.md`, `_iter1.md`) — iteration 0 오라우팅 3건 중 (i)로 확정되는 attribute s0(노드 02·03·04가 모두 expected_dialog "Attribute Set 3D"를 공유), (i)+(ii)로 확정되는 s1은 어떤 margin에서도 걸러지지 않고 s5만 (iii) margin ≥ 0.02에서 걸러짐(최대 1/3). iteration 1 정답 16건은 전체 노드 풀에서 3d_viz s0 1건이 항상 탈락(화면 문자 증거 없음·prior 없음·임베딩 1위가 survey 노드), 2단계 풀에서만 margin ≤ 0.03에서 16/16 유지. 사용자 기준(정답 16건 무손실 AND 오라우팅 3건 전부 필터) 불충족 → 규칙 수정 없이 미채택, 코드는 `ROUTER_EVIDENCE_GATE=0`으로 비활성.
- **attribute s0·s1 재구성(`recon_iter1_attribute_s0s1.md`, iteration-1 knob, 생성기 없음)**: 벤치에서 02(0.95)·03(0.90)을 고른 같은 코드가 오프라인에서는 04(0.95)·04(0.90)을 고름. s0 후보 풀 = 01(emb 0.75)·02(0.74)·04(0.73) + 타 워크플로우 3(d3_04, survey_01, QGIS auto_03[clip 0.90], d3_01[clip 0.88]); 02와 04의 임베딩 차 0.01. 원인: vision v3 출력에 Attribute Set 3D 창이 열리자마자 기본값(type "Similarity", Time gate −28/28, Input Data Seismic_data)이 채워져 있는 것이 보고되는데, 노드 02 signature는 "empty attribute set, parameter panel disabled"를 기대하고 노드 04는 "Time gate populated −28..+28"를 기대해 화면이 04 쪽으로도 읽힘 — signature와 실제 화면의 불일치(2026-08-07 signature 재작성의 가정 오류). s1은 Attribute Name 입력 여부만이 03/04를 가르는데 signature에 명시가 없음.
- **iteration 2 벤치 보류(사용자 결정)**: 대기 중이던 벤치 4건(Gemini 2·Claude 1·GPT 1)은 dry-run 3회가 모두 16/16이 아니면 실행하지 않고 iteration 3으로 간다(대기 체인 중단). dry-run 3회 결과는 V3-14에 기록.
- **iteration 3 계획(사용자 지시, worktree 작업)**: (a) seismic_attribute 노드 02·03·04 signature를 실제 OpendTect 동작(열리자마자 기본값 채워짐)에 맞춰 관찰 가능한 필드 상태로 구별되게 수정(다른 워크플로우·QGIS 불변, 전후 원문 기록); (b) vision 프롬프트에 드롭다운 선택값·입력란 내용·체크 상태를 원문 그대로 보고하는 항목 추가(소프트웨어 공통); (c) 같은 expected_dialog를 공유하는 후보의 임베딩 점수 차가 근소할 때 그래프 순서 prior(직전 확정 노드의 후속, 없으면 워크플로우 앞 노드 우선); (d) dry-run 5회, 전부 16/16이 아니면 rerank 3회 병렬 다수결 추가 후 다시 5회. 5회 모두 16/16이면 개발 벤치(Gemini 2·Claude 1·GPT 1) 후 정지, 사용자 동결 결정.

### V3-14. iteration 3 결과·진단, 가설 확인, iteration 4(라우팅 마지막 수정) (2026-09-18)
- **iteration 3 dry-run ×5 (커밋 820e993; signature 02·03·04 관찰 상태 재작성 + vision field_values + 근소차 prior + 종료 상태 앵커)**: 정답 14, 14, 14, 14, 13 /16. 오라우팅: attribute s0 = 04, 03, 03, 04, 03(5/5 오답, 02는 한 번도 아님), attribute s1 = 04 ×5(5/5 오답), rep 4 survey s3 → d3_visualization_01(메인 창 화면의 워크플로우 간 혼동, 1/5). 같은 스텝의 선택이 회차마다 갈리지 않고 일관되게 오답이므로 사용자 규칙에 따라 다수결은 쓰지 않음. 종료 상태 블록 발동: rep당 5건 — survey s3(05, 정상), 3d_viz s3(04, 정상), attribute s5·s6·s7(06) 중 s7만 정상이고 s5·s6은 조기 발동(06_display가 스텝 5–7을 담당하는 다단계 노드라 첫 화면부터 말단 조건 충족) → rep당 오발동 2건, 5회 합계 10/24.
- **진단(`diag_attribute_s0s1_iter3.md`, iteration-3 코드)**: (1) vision v3의 field_values 원문 — s0: "Attribute set: <not saved>", "Input Data: Seismic_data", "Time gate (ms): -28 / 28", "Extension: Cross", "Attribute Name: (empty)", "Save on Close: checked"(attribute type 값은 field_values에 없고 labels에도 없음); s1: "Energy: Energy", "Compute gradient: No", "Output: Energy", "Attribute Name: (empty)", "Save on Close: checked". (2) 임베딩 점수(변경 전 → 후): s0 02 0.742(#2) → 0.805(#1), 03 0.673(#8) → 0.713(#4), 04 0.752(#1) → 0.739(#2); s1 02 0.722(#3) → 0.787(#1), 03 0.692(#5) → 0.744(#3), 04 0.770(#1) → 0.757(#2). 즉 signature 재작성 후 후보 단계는 02를 1위로 올렸고 02·03·04 모두 top-5 풀에 있었다. (3) 근소차 prior 미발동 이유: 세 노드가 같은 expected_dialog 묶음("Attribute Set 3D")이지만 1–2위 격차(s0 0.066, s1 0.030)가 margin 0.02를 넘어 "근소차" 조건에 걸리지 않음. (4) rerank 입력의 세 후보 부분은 위 파일 §4에 원문 수록. (5) 채점 영향: iteration 0(s0→04) fs s0 ✓·s1 ✗, iteration 1(s0→02, s1→03) fs s0 ✓·s1 ✓(s1은 fs만 정답, vanilla 3종 ✗) — n=1이지만 s1 라우팅이 fs의 s1 채점과 함께 움직였다.
- **사용자 가설(기준 불일치) 확인**: 워크플로우 5개의 관례 — seismic_attribute는 노드 설명이 "매뉴얼 step N 결과"로 시작하는 **동작 후 상태**; survey_setup·d3_visualization·QGIS는 "창 열림/표시됨" 상태와 진행 중 상태(컨텍스트 메뉴 열림, 입력 중)가 섞임; fault/horizon은 도구·다이얼로그 이름. 벤치의 라우팅 정답(attribute의 `expected_workflow_node`)은 "화면이 보여 주는 완료 상태의 노드"(s0 = 02 창 방금 열림, s1 = 03 유형 선택됨) 기준. 반면 rerank 프롬프트(v3)는 "사용자가 지금 하고 있거나 다음에 하려는 단계"를 고르게 하고, 문자 증거 규칙이 기본 화면에도 보이는 라벨("Save on Close", "Attribute Name")을 04의 증거로 세게 만들었다. iteration 1·2에서 02가 가끔 선택된 것은 옛 02 signature의 "about to choose an Attribute Type"이라는 동작 전 문구가 프롬프트 프레이밍과 우연히 맞았기 때문이고, iteration 3에서 상태 문구로 바꾸자 03/04 편향이 일관되게 됐다 — 가설과 부합. 임베딩은 이미 02를 1위로 두므로 편향은 rerank 기준에서 발생.
- **iteration 4(커밋 d064577, 라우팅 마지막 수정)**: (a) 같은 expected_dialog 묶음에는 점수 차와 무관하게 그래프 순서 prior(묶음에 확정 노드 없으면 가장 앞 노드, 있으면 후속 노드; `ROUTER_GROUP_PRIOR=1`), 우선 노드를 후보 목록 맨 앞에 두고 rerank에는 묶음 구성원의 구별 상태(다른 구성원에 없는 키워드·요소)를 대조 형태로 제시(`_group_contrast_block`, 모든 워크플로우 공통). (b) 03·04 signature를 비기본 상태 요구로 재작성(03: "attribute type changed to Energy (NOT the default Similarity)", "Attribute Name still (empty)"; 04: "Attribute Name (Energy [-28,+28]) — field FILLED, not empty", "attribute list contains 'Energy [-28,+28]' — NOT empty", "Save on Close (checked)", "Save Attribute as dialog open"; 기본 화면 토큰 "Attribute set (<not saved>)", "OK", "Attribute Set 3D" 제거) — 전후 원문은 노드의 `signature_audit.previous_signature`와 `iter4_signature_change.txt`. (c) rerank 프롬프트 v4(`RERANK_PROMPT_VERSION=v4`, v3·v2 재현 가능): 과제 문장 "Pick the candidate whose described screen state matches the CURRENT screen — the step the user has reached (not the action they will do next)"; DECISION RULE(state match): 후보는 "그 단계가 현재 위치일 때의 화면 상태"를 기술하므로 현재 화면과 일치하는 상태를 고르고 다음 동작은 엣지에서 공급; 같은 다이얼로그 후보는 field VALUES(선택된 항목·채움/비움·체크·목록 비어 있음)로 구별하며 라벨이 보이는 것만으로는 증거가 아님; NOTE(v4): 후속 노드는 그 후속 노드의 상태(값이 설정됨)가 화면에 보일 때만 선택, 지시가 끝났어도 화면이 그대로면 현재 단계 유지. v3의 "CURRENTLY doing or trying to do next" 문장과 "expected dialog or elements literally appear on screen is a strong match", "prefer the NEXT step" 규칙은 v4에서 제거. (d) dev_iter가 worktree에서 벤치 인터프리터를 찾도록 수정(`BENCH_PYTHON`).
- iteration 4 dry-run ×5 결과와 개발 벤치(Gemini 2·Claude 1·GPT 1), 종료 상태 블록 발동·오발동은 V3-15에 기록. iteration 4 이후 라우팅은 더 고치지 않는다(사용자 원칙); 남는 불안정은 사전등록 초안 한계 절에 수치로 적는다.

### V3-15. iteration 4 결과: dry-run ×5, 개발 벤치 4건, 종료 상태 블록 발동, 세션 누출 검증 (2026-09-18)
- **묶음 prior 범위 버그와 정정**: iteration 4 첫 dry-run ×5(커밋 d064577)는 16, 16, 15, 15, 15 /16 — 세 번의 오라우팅이 모두 survey s3 → d3_visualization_01. 원인은 내 구현 오류: expected_dialog 묶음을 워크플로우 구분 없이 만들어 survey_05와 d3_01(둘 다 "OpendTect Main Window")이 한 묶음이 되고 "가장 앞 노드" 규칙이 다른 워크플로우의 노드를 고름. 벤치를 2분 만에 중단하고 묶음을 같은 워크플로우 안으로 한정(커밋 21f0dec; 단위 검사: 교차 워크플로우 쌍은 묶이지 않음). 정정 후 dry-run ×5: **16/16 ×5**, attribute s0 → 02, s1 → 03, survey s3 → 05 전 회차 동일. 오라우팅·fallback 0.
- **종료 상태 블록 발동(정정 dry-run, rep당 4건)**: survey s3(05, 정상), attribute s7(06, 정상), attribute s5·s6(06, 조기 — 06_display가 스텝 5–7을 담당) → rep당 오발동 2/4, 5회 합계 10/20. 3d_viz s3에서는 발동하지 않음: v4 상태 일치 기준이 3d_viz s2·s3 화면을 d3_01(main_window_ready)로 보내(워크플로우 단위로는 정답, 노드 GT 없음) 말단 앵커가 생기지 않기 때문. 개발 벤치 4건의 조기 발동 8건(attribute s5·s6 × 4)에서 full_system 응답은 전부 다음 동작("250 우클릭", "OK 버튼")이었고 **조기 '완료' 응답 0건** → 사용자 규칙 3에 따라 블록 유지, 좁힌 발동 조건은 적용하지 않음(오프라인 검사 스크립트 `scripts/goal_state_rule_offline.py`만 보관). 오발동 건수는 사전등록 초안 한계 절에 기재.
- **개발 벤치(커밋 21f0dec, 단독 실행, 옛 GT로 채점 후 신 GT 재채점 — step acc 동일)**: 시나리오 평균 step accuracy full / vanilla_vector / vanilla_budget / no_rag — Gemini(2회) 0.792 / 0.771 / 0.771 / 0.708, Claude 0.875 / 0.875 / 0.875 / 0.875, GPT 0.833 / 0.833 / 0.667 / 0.750. 방향: Gemini full > 두 vanilla, Claude 동률, GPT vanilla_vector와 동률·vanilla_budget 우위. n이 1~2라 잡음 범위(판단 기준 아님). 라우팅: 4건 64스텝 전부 정답, fallback 0. 목표 절 적중 full 16/16 vs vanilla 12/16(3d_viz 0/4).
- **손실 분류(full_system ✗, 4건 합계 12)**: 라우팅 0, 컨텍스트 0, 생성 9, 표기 3. 표기 3 = survey s0 "녹색 더하기/플러스 아이콘", "새로운 설문 아이콘"(패턴 Survey|Create|New|Add, 규칙 3 보류). 생성 9 중 5건이 attribute s1(Gemini ×2, Claude)과 Claude의 s2·s3: 라우팅은 정답(03/04)인데 응답이 "Input Data를 4 Dip steered median filter로 변경" — [Current Step] 설명이 "Input Data = 4 Dip steered median filter 선택 완료"라고 단정하지만 화면은 Seismic_data여서 생성기가 그 불일치를 '고치려' 함. 나머지: 3d_viz s3 sentinel(Gemini r1), GPT 3d s2, attribute s5(Gemini ×2, "250 우클릭" — GT는 Add > Attribute 단계).
- **정답 라우팅 스텝의 기대 동작 위치**: attribute s1의 기대 동작(Time gate·Attribute Name 입력)은 현재 노드(03)의 동작이 아니라 **엣지 03→04의 지시**, 즉 다음 노드의 동작이며 [Possible Next Steps]에 그대로 들어 있었다. s2·s3(04 라우팅)의 기대 동작(Add as new, Close)은 현재 노드 04의 통합 설명 안의 동작. v4 rerank 기준(완료 상태가 화면과 일치하는 노드)과 컨텍스트 블록은 어긋나지 않으나, [Current Step]의 서술형 설명이 화면과 다른 값을 단정하면 생성기가 그것을 우선한다. **컨텍스트 조립 수정안(공통, 적용은 사용자 결정)**: [Current Step]을 "이미 도달한 상태"로 명시하고 서술형 설명 대신 signature의 기대 상태(expected dialog·elements·keywords)를 붙이며, "[Next Action]"에 엣지 지시를 두고 "현재 단계에서 이미 설정된 값을 다시 고치지 말 것"을 프롬프트에 명시. 여러 동작을 담는 노드(04, 06)는 설명의 동작 목록 중 화면 상태(field_values)로 아직 안 된 첫 동작을 고르라고 안내.
- **세션 상태 누출 검증(`session_leak_check_iter4.md`, API 호출 없음)**: 캐시 vision·기록된 rerank pick·기록된 응답을 스텁으로 넣어 3 시나리오 × 4 백엔드를 (a) 단독, (b) 벤치 순서, (c) fs→vv, vv→fs로 재생 — 모든 스텝에서 생성기 컨텍스트 블록과 rerank 프롬프트가 단독 실행과 바이트 동일(48/48). 세션 상태(visited·직전 확정·종료 상태 힌트)는 (scenario, backend) 키로 분리되어 백엔드 간 공유 없음. 단, 텔레메트리 dict의 추가 키(goal_state_node·candidates 등)가 `reset_last_localize_meta()`에서 지워지지 않아 non-routing 백엔드의 per_step 기록에 직전 full_system 값이 남는 결함 발견(채점·동작 무관) → 동결 커밋에 텔레메트리 수정 포함.
- **iteration 4 이후 라우팅 수정 없음**(사용자 원칙). 남은 불안정(3d_viz 노드 단위, 다단계 노드의 조기 발동)은 사전등록 초안 한계 절에 수치로 기재.

### V3-16. GT 검수 — 스크린샷만 본 별도 세션, 고정 규칙 (2026-09-18)
- 절차: 하위 에이전트(새 세션)에 `data/eval/gt_review_session/`(스크린샷 24장, `gt_visible_elements_review_v3.md`, 시나리오 4개, 매뉴얼 해당 절 발췌, RULES.md)만 주고 실행 로그·모델 응답·채점 결과 접근 금지, 파이프라인 실행 금지. 판단 규칙은 사용자 지시 원문(규칙 1~5)으로 고정, 규칙 밖은 "보류".
- 결과: 표본 3장(survey s0, attribute s3, QGIS s3) 104항목 중 오독 1건(0.96%; 표기 차이 합산 4.81%) < 5% → 반영. 변경 19(규칙 1: 삭제 2·라벨 원문 11·아이콘 표기 1(`Add button` → `New Survey (+)`); 규칙 4: QGIS s3 5건 — Input layer가 이미 `roads_33S [EPSG:32733]`로 채워져 있어 data_state·current_action·visible_elements 정정, 패턴에 `Distance|50|Dissolve`, 키워드에 `Distance`, `50` 추가), 유지 5, 보류 11(H1–H11: 부재 서술 항목, Edit 아이콘 표기, 중복 6건, A 항목 오독 정정 여부, QGIS s3·s4 상태 동일화 등). survey s0 Add 버튼(규칙 3)은 **보류**: 매뉴얼 §1.2.2a p.21이 "Click on the New Survey icon"이라 부르므로 규칙 조건(Add 또는 "+") 불성립 → 패턴·허용 대안 불변.
- 검증·적용: 제안 파일 4개의 diff가 허용 GT 필드에만 걸림을 확인(스텝 필드 11건) 후 커밋 44fa1ab. 재채점(`rescore_gt_compare_v3.md`, `rescore_gt_compare_iter4.md`; unified4 20파일 + dev iteration 0·1·4 + 기준 지연, 전 백엔드): step accuracy 변화 0; 환각률 대부분 −6.2 pp(attribute s4 `Name (my first attribute set)` 라벨 원문화로 97건 ✓→✗), survey s0 33건 ✗→✓(`New Survey (+)` 표기로 "Add (+) 버튼" 응답이 화면 외 문자열로 잡힘 — 사용자 결정 사항).
- 외부 검토용 파일: `gt_review_session/GT_change_list.md`, `GT_hold_list.md`, `sample_check.md`, `SUMMARY.md`, `proposed/*.json`; 보류 스크린샷 7장, survey s0·QGIS s3 스크린샷 경로는 보고서에 기재.

### V3-17. 마지막 개발 변경: 컨텍스트 조립 v4, GT 결정 2건, QGIS s3 패턴 되돌림 (2026-09-18)
- **컨텍스트 조립 v4(사용자 결정, worktree 커밋 fcfa184, `CONTEXT_ASSEMBLY=v4`; `v3`로 이전 블록 재현)**: full_system의 라우팅된 노드를 "[Current State (reached)]"로 렌더링하고 노드 signature의 상태(expected dialog·elements·keywords)만 적는다 — 매뉴얼 예시 값이 들어간 노드 설명은 이 블록에 넣지 않는다. "[Next Action] (from the workflow edge)"에 후속 노드로 가는 엣지 지시를 두고(말단 노드면 완료 sentinel 안내), 공통 문구 "매뉴얼의 예시 값(파일명·파라미터)은 사용자의 데이터와 다를 수 있다. 화면에 이미 설정된 값을 고치도록 안내하지 않는다."를 붙인다. 모든 워크플로우 공통(QGIS는 코드로만 적용, 실행 없음).
  - 변경 전(attribute 노드 03, 후속 04): `[Current Step] seismic_attribute > Step 3: 속성 유형 + 입력 데이터 선택 (파라미터 편집 직전) / Description: 매뉴얼 §1.5.1a step 2 결과: Attribute Type = Energy 선택 완료, Input Data = 4 Dip steered median filter 선택 완료. … / [Possible Next Steps] - Next (sequential): Step 4 … — Time gate 를 -28..+28 로 입력하고 Attribute Name 'Energy [-28,+28]' 를 입력하세요`
  - 변경 후: `[Current State (reached)] seismic_attribute > Step 3: 속성 유형 + 입력 데이터 선택 (파라미터 편집 직전) / The screen at this step shows — dialog/screen: Attribute Set 3D | elements: attribute type energy selected not default, output energy, compute gradient toggle, attribute name still empty, attribute list still empty | states: attribute type changed to Energy (NOT the default Similarity); Output (Energy); …; Time gate (ms) (-28) 28 / [Next Action] (from the workflow edge) - Time gate 를 -28..+28 로 입력하고 Attribute Name 'Energy [-28,+28]' 를 입력하세요 (→ Step 4: …) / Note: 매뉴얼의 예시 값(파일명·파라미터)은 사용자의 데이터와 다를 수 있다. 화면에 이미 설정된 값을 고치도록 안내하지 않는다. (…)`
  - **다른 백엔드의 조립 함수(보고)**: `build_context_block`은 full_system(벤치·프로덕션 `rag_router`)만 쓴다. graph_only는 `bench_backends.backend_graph_only`가 자체 `[Current Step]`(제목+설명)/`[Possible Next]`를 만들고, vision_only도 자체 `[Current Step]`(제목+설명), state_path는 `state_path_retriever.format_step_path`(`[Current step description]` + 매뉴얼 스니펫 + `[Expected next steps]` + "issue the action belonging to the CURRENT step")를 쓴다. 사용자 지시에 따라 이들은 바꾸지 않았다(ablation 백엔드의 컨텍스트 형식 불일치는 사용자 결정 사항).
- **survey s0 표기(사용자 결정)**: visible_elements에 같은 아이콘 컨트롤의 이름으로 `New Survey (+)`와 `Add (+)`를 병기. 전 백엔드 재채점: `rescore_gt_compare_survey_s0_label.md`(수치는 V3-18에 기록).
- **QGIS s3 패턴 되돌림(사용자 결정)**: 검수 세션이 추가한 `|Distance|50|Dissolve`와 키워드 `Distance`, `50`을 외부 검토 전까지 추가 전 상태(`(?i)\b(Input layer|roads_33S|select|선택|드롭다운|dropdown)\b`, `["Input layer", "roads_33S"]`)로 되돌림. visual_state_gt의 화면 상태 정정(Input layer 이미 채워짐)은 유지. 보류 11건과 함께 외부 검토 후 결정.
- **QGIS 재인제스트·linked_chunks(사용자 확인 요청)**: 재인제스트 완료(745청크, 1,507 s, V3-11), linked_chunks 연결 완료(노드 5개 → §6.2.6 청크 3개씩, 스크립트 15.8 s, V3-11). 추가 실행 없음. QGIS 시나리오는 미실행.
- iteration 5(조립 v4) dry-run ×5와 개발 벤치 4건 결과는 V3-18. 이후 개발 변경 없음(사용자가 동결).

### V3-18. GT 확정 — 외부 검토 결정 반영, 구·신 GT 재채점 (2026-09-18)
- **절차**: 모델 응답을 보지 않은 별도 세션이 고정 규칙(RULES.md)으로 검수(V3-16) → 사용자가 스크린샷 24장과 Add 버튼 확대 2장을 대조한 외부 검토에서 변경 19건 중 18건 확인, 1건(#19 QGIS s3 keywords에 Distance·50 추가) 되돌림(keywords는 AND 판정) → 보류 11건 결정(H1·H4·H8 부재 서술은 visible_elements에서 빼고 data_state로; H2 삭제 + 화면 사실(기본 유형 Similarity 파라미터가 채워진 활성 상태) 추가; H3 `OK / Save button` → `Save as (icon)`; H5 `Edit button` 유지; H6 복합 항목 삭제; H7 허용 대안 미추가; H9 중복 6건 제거; H10 표기 오류를 화면 문자열대로; H11 QGIS s3·s4 capture_instructions·`_gt_provenance` 갱신). survey s0 아이콘 요소명은 `New Survey (+)`와 `Add (+)` 병기.
- **H10 수치 재확인**: 스크린샷만 보는 별도 세션이 QGIS 8스텝 + attribute s3의 수치 문자열 33건을 3배 이상 확대 크롭(`gt_review_session/numeric_crops/`, 36장)으로 대조 — 14건 상이(소수점 쉼표·공백 13건, s3 좌표 `1026658`→`1028658` 1건), 19건 동일, 화면에 없음 0건. 사용자 명시 수정과 정확히 일치해 추가 수정 없음(`NUMERIC_CHECK_RESULT.md`).
- **적용**: 라이브 트리 커밋 2f3db66, 편집 59건을 `gt_review_session/GT_final_applied_log.md`에 항목별 기록. 기대 패턴·키워드·허용 대안은 명시된 것(#18 재적용) 외 변경 없음; 3d_viz step_3 허용 대안 패턴, QGIS signature·워크플로우 불변; QGIS 미실행.
- **구·신 GT 재채점**(채점기 v3 불변; `rescore_gt_final_vs_fcfa184.md`, `rescore_gt_final_vs_44fa1ab_1.md`): (a) 최종 결정 전(fcfa184: 검수 반영 + Add (+) 병기 + QGIS 패턴 되돌림) 대비 **변화 0**(step accuracy·환각 플래그 모두). (b) 검수 이전 원 GT(44fa1ab~1) 대비 step accuracy 변화 0, 환각률 unified4·dev iteration 0·1·4 대부분 −6.2 pp(attribute s4 `Name (my first attribute set)` 라벨 원문화), Claude no_rag −7.5, 표기 병기로 survey s0 부작용 상쇄. 이후 GT·채점기는 사전등록 서명 전까지 변경하지 않는다.
- **기록 사항(사전등록 초안 반영)**: QGIS s3 GT 정정의 근거는 화면 사실(Input layer 자동 채움)이며 화면을 읽는 백엔드에 유리할 수 있음; QGIS s3와 s4의 화면이 같아 같은 정답 응답이 s4에서 loop로 집계될 수 있음(loop는 판정 지표 아님); 3d_viz step_3 허용 대안이 요소 언급만으로 통과될 수 있음(한계).

### V3-19. iteration 5(컨텍스트 조립 v4) 결과 — Gemini 2회까지; Gemini 크레딧 소진으로 Claude·GPT 미완 (2026-09-18)
- **dry-run ×5(커밋 fcfa184)**: 16/16 ×5, 종료 상태 발동 rep당 4(survey s3·attribute s7 정상, attribute s5·s6 조기). 라우팅 코드는 iteration 4와 동일하므로 변화 없음(조립 v4는 생성기 컨텍스트만 바꿈).
- **개발 벤치**: Gemini rep 0 full / vv / vb / no_rag = (3d 0.75, attr **1.00**, survey 0.75) 평균 0.833 / 0.833 / 0.708 / 0.708; rep 1 = (0.75, **0.88**, 1.00) 0.875 / 0.875 / 0.792 / 0.792. 2회 평균 **full 0.854 = vanilla_vector 0.854 > vanilla_budget 0.750**. iteration 4에서 Gemini의 attribute s1 손실 2건(정답 라우팅 후 "Input Data 드롭다운" 응답)은 **0건**으로 사라졌고(s1~s3 전부 ✓), 새로 생긴 손실 유형은 없음. 남은 손실 4 = 생성 3(3d_viz s3 sentinel ×2: "Add Default Data"; attribute s5 ×1: "250 우클릭") + 표기 1(survey s0 "새 서베이 추가 아이콘"). 조기 발동 4건에서 조기 '완료' 0건. 최종 GT로 재채점 시 변화 0(`rescore_gt_final_iter5.md`).
- **중단**: Claude 벤치의 attribute full_system 도중 Gemini API 프리페이 크레딧 소진(429 RESOURCE_EXHAUSTED "prepayment credits are depleted") → vision·rerank 호출이 실패해 이후 full_system 결과가 무효가 되므로 체인을 즉시 중단(Claude JSON 미작성, 로그만 남음; GPT 미시작). Claude ×1·GPT ×1 벤치는 크레딧 충전 후 같은 커밋(fcfa184 코드, 최종 GT 2f3db66)으로 재실행해야 한다. 그 전까지 iteration 5의 모델별 방향은 Gemini만 보고.
- iteration 5 이후 개발 변경 없음(사용자 원칙). 동결은 사용자 결정.

### V3-20. iteration 5 완료 — Claude·GPT 재실행(크레딧 충전 후), 4건 종합 (2026-09-18)
- **재실행**: Gemini 크레딧 충전 후 API 프로브(Gemini·Claude·GPT 모두 정상) → worktree를 최종 GT 포함 커밋(34c06aa)으로 맞춰 Claude ×1·GPT ×1 재실행(코드 fcfa184와 동일, GT 2f3db66). Gemini ×2는 사전 GT로 실행 후 최종 GT 재채점 변화 0.
- **step accuracy(시나리오 평균) full / vanilla_vector / vanilla_budget / no_rag**: Gemini(2회) 0.854 / 0.854 / 0.750 / 0.750 (vv 동률, vb 우위); Claude 1.000 / 0.875 / 0.875 / 0.875 (양쪽 우위); GPT 0.792 / 0.833 / 0.667 / 0.750 (vv 열세, vb 우위). 라우팅 64/64 정답, fallback 0, 조기 발동 8건 중 조기 '완료' 0건.
- **손실 분류(full_system ✗, 7건)**: 라우팅 0 · 컨텍스트 0 · 생성 6 · 표기 1. iteration 4의 attribute s1~s3 손실 5건(정답 라우팅 후 "Input Data를 4 Dip steered median filter로 변경")은 **4건 모두에서 0건** — 조립 v4의 목표였던 손실 유형은 사라짐. 남은 손실: 3d_viz s3 sentinel(Gemini ×2, "Add Default Data"; 종전과 같음), attribute s5(Gemini ×1, "250 우클릭"; 종전과 같음), survey s0 표기(Gemini ×1), GPT 3d s2(종전과 같음).
- **새로 생긴 손실 2건(GPT)**: (1) attribute s7 — 응답 "표시된 속성의 통계·분포를 QC 하세요": 라우팅 06_display(정답)에서 [Next Action]이 06→07(verification 노드) 엣지 지시를 제시해 생성기가 sentinel 대신 그 지시를 냈다(iteration 4 조립에서는 ✓). (2) survey s1 — 응답 "'Scan SEG-Y file(s)'를 선택하고 'Next'를 클릭": 라우팅 03(워크플로우 정답, 노드 GT 없음; 화면은 이름 입력 전 대화상자라 상태 관례상 02)에서 [Next Action]이 03→04 엣지("Next를 눌러…")를 제시. 종전 조립은 03의 서술형 설명("Survey name을 입력하고…")이 노드 단위 오차를 덮어 주었으나, v4는 엣지 지시만 주므로 노드 단위 라우팅 오차가 그대로 드러난다. **개발 변경은 종료**(사용자 원칙)이므로 적용하지 않고 기록만: 후보 대응 (a) verification 노드로 가는 엣지는 [Next Action]에 넣지 않고 완료 확인 안내로 대체, (b) 노드 단위 라우팅 정밀도(survey 02/03 구별)는 signature·GT 문제. 동결 시점의 알려진 한계로 사전등록 초안에 기재.
- **코드 해시**: Gemini r0/r1 fcfa184, Claude/GPT 34c06aa(코드 동일, GT 최종). 병합 후 v3-rerun HEAD가 동결 후보.

### V3-21. iteration 6(조립 v5: 규칙 1·2) — 기준 미충족, iteration 5(c01fdda)로 되돌림 (2026-09-19)
- **변경(worktree 커밋 d326838, `CONTEXT_ASSEMBLY=v5`; v4·v3 재현 가능)**: 규칙 1 — step_type이 verification/terminal인 노드로 가는 엣지는 [Next Action]에 동작으로 제시하지 않고, 종료 상태 블록 발동 시 또는 동작 엣지가 없으면 "[Next Action] 결과를 확인하고, 목표가 달성된 화면이면 완료로 응답한다."만 둔다. 규칙 2 — "[This Step]" 블록에 현재 노드의 하위 동작(노드 설명)과 관련 필드(expected_ui_elements·parameters 이름)를 제시하되 따옴표 문자열·"= 값"(라틴/숫자)·숫자 범위를 "(예시)"로 표시하고, [Next Action]에 "[This Step]의 입력이 화면에서 모두 끝났을 때만"이라는 조건을 붙인다. 노드 id·스텝 번호 조건 없음, 전 워크플로우 공통(QGIS 코드 적용만, 미실행).
- **전후 블록 예시(attribute s7 케이스, 종료 상태 발동)**: v4 `[Next Action] (from the workflow edge) - 표시된 속성의 통계·분포를 QC 하세요 (→ Step 7: 결과 QC 분석)` → v5 `[This Step] Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 … Sub-actions … 'Select Layer 2'(예시) … 'Energy [-28,+28]'(예시) … / [Next Action] 결과를 확인하고, 목표가 달성된 화면이면 완료로 응답한다.` (attribute s1 케이스: v5는 `[This Step] … Attribute Type = Energy(예시) 선택 완료, Input Data = 4 Dip steered median filter(예시) 선택 완료 … / [Next Action] (…ONLY when every input of [This Step] is already visibly complete on screen) - Time gate 를 -28..+28 로 입력하고 …`; survey s1 케이스: v5는 Enter X/Y 분기(verification 노드 05행)를 [Next Action]에서 제외.)
- **dry-run ×5**: 16/16 ×5 (기준 a 충족; 라우팅 코드 불변).
- **개발 벤치(Gemini ×2, Claude, GPT; 커밋 d326838, 최종 GT)**: step accuracy full / vv / vb — Gemini 0.875 / 0.792 / 0.792, Claude 1.000 / 0.875 / 0.875, GPT 0.833 / 0.750 / 0.667(세 모델 모두 양쪽 우위). 손실 6 = 생성 3 · 표기 2 · 라우팅 1. iteration 5의 새 손실 2건(GPT survey s1, attribute s7)은 해소(기준 c 충족).
- **기준 미충족**: (b) Gemini rep 1 attribute s1 — 라우팅 정답(03)에서 응답 "Seismic_data 드롭다운을 클릭하세요"(Input Data를 바꾸려는 같은 유형; [This Step]에 "Input Data = 4 Dip steered median filter(예시)"가 다시 들어간 결과로 판단) → 실패. (d) 새 손실 2건 — 위 attribute s1과 GPT survey s3(메인 창 화면에서 d3_visualization_01로 교차 워크플로우 오라우팅; dry-run에서는 5/5 정답이었으나 벤치의 rerank가 이 화면에서 낮은 빈도로 흔들림 — iteration 3·4 dry-run에서도 관측된 불안정) → 실패. 규칙 4에 따라 **추가 수정 없이 iteration 5(c01fdda)로 되돌림**: v3-rerun에 병합하지 않음(라이브 코드 = c01fdda 그대로), iteration 6 코드·결과는 branch `v3-iter2`(d326838, 587881a)에 보존, 보고서 사본(`dev_iter6_report.md`, `dev_iter6_criteria.txt`, `routing_dryrun_v3_iter6_x5.md`)만 라이브 결과 디렉터리에 둠. `run_v3.sh`에 `CONTEXT_ASSEMBLY=v4`를 명시.
- 개발 변경 종료. 동결 후보 = c01fdda(코드) + 이후 문서 커밋. 사용자가 동결한다.

### V3-22. iteration 6 채택 전 확인 — 조립 변경이 rerank 입력에 영향을 줌, 채택 보류 (2026-09-18)
- 사용자가 iteration 6(조립 v5) 채택을 결정하면서 조건을 붙였다: 라우팅 코드 경로와 rerank 입력이 v4/v5에서 동일한지 API 호출 없이 확인하고, 동일하지 않으면 채택을 중단한다.
- 결과(`assembly_routing_coupling_check_iter6.md`): 라우팅 코드 경로는 동일(diff는 `build_context_block` 분기와 상수뿐). 그러나 rerank 프롬프트의 "Instructions already given to the user in this session" 블록이 직전 생성기 응답(`completed_steps`)으로 만들어지고 결정 규칙이 이를 참조하므로, 조립 변경 → 직전 응답 → rerank 입력의 간접 경로가 있다(16스텝 중 13스텝). dry-run은 `completed_steps=[]`라 이 결합을 검사하지 못한다.
- 수치 정정(V3-21은 수정하지 않음): V3-21의 "벤치 라우팅 63/64"는 라우팅 원인 손실만 센 값. dry-run과 같은 판정 규칙으로 다시 세면 iteration 5(v4) 64/64, iteration 6(v5) 61/64 — Claude attribute s2(03, 손실 없음; 세션 블록 동일·vision 다름), Gemini r1 survey s3(d3_01, 손실 없음; vision·세션 블록 모두 다름), GPT survey s3(d3_01, 손실; 고정부 동일·세션 블록만 다름). 최종 라우팅 코드(21f0dec 이후)에서 survey s3 → d3_01은 dry-run 15/15·iteration 5 벤치 4/4 정답, iteration 6 벤치 2/4 정답으로, 이 오라우팅이 관측된 것은 v5 벤치 2건뿐이다. 인과는 오프라인으로 확정 불가(rerank 재생 실험은 API 비용 발생).
- 조치: 사용자 조건에 따라 채택 중단. 병합·`run_v3.sh` 변경·dry-run 없음. 라이브 코드 c01fdda 그대로, GT 2f3db66 그대로. 사전등록 초안 §2.5 iteration 6 행의 라우팅 수치를 61/64로 정정. 다음 결정은 사용자에게.

### V3-23. 동결: c01fdda(조립 v4) — 태그 `v3-freeze-c01fdda` @ a03ca59 (2026-09-18)
- 사용자 결정: V3-22의 확인 결과(조립 변경이 세션 블록을 거쳐 rerank 입력에 들어감, v5 벤치 라우팅 61/64 대 v4 64/64)에 따라 v5를 채택하지 않고 v4로 동결. rerank 재생 실험은 하지 않음. 이후 개발 변경 없음.
- 태그 대상 HEAD a03ca59는 문서 커밋만 포함하며 코드(`api/`, `data/workflows/`)는 c01fdda, GT(`data/eval/scenarios/`)는 2f3db66과 바이트 단위로 동일함을 `git diff --stat`으로 확인. branch `v3-iter2`(iteration 6, d326838·587881a)는 병합하지 않고 기록용으로 보존.
- 다음: 사전등록 초안 최종화(이 항목 뒤의 문서 커밋) → 사용자 검토·서명 → `scripts/run_v3.sh`. 서명 전 실행 없음.
- 날짜 정정: V3-21 제목의 '2026-09-19'는 오기이며 2026-09-18(KST)이 맞다(V3-21 본문은 사용자 지시로 수정하지 않음; V3-22·V3-23 제목은 정정).
- 사전등록 최종화(V3-23 뒤 커밋): 판정 = QGIS step accuracy를 vanilla_budget(비교 A)·vanilla_vector(비교 B) 각각과 비교(사용자 결정; hall·비용·지연은 기술 지표 — §6.1 hall 규칙 결과 중앙값 6.2%는 그대로 기재), §5.x 위험 (i)–(v), §2.3 G8 동결 구성, §2.5 벤치 모드 라우팅 표. 재집계 정정: iteration 4 벤치 라우팅은 62/64(Gemini r0 attribute s2→03, survey s3→d3_01, 둘 다 손실 없음; V3-15 보고서의 '라우팅 손실 0'은 손실만 센 값)이며 초안의 64/64를 정정. iteration 5 64/64는 재집계로 확인.

### V3-24. 사전등록 외부 검토 반영 — 문서만 (2026-09-18)
- 코드·GT·워크플로우 불변(HEAD의 `api/`·`data/workflows/`·`data/eval/scenarios/`는 태그 `v3-freeze-c01fdda`와 동일). run_v3.sh 미실행.
- 반영: (1) §6.1의 사전 고정 규칙(재채점 hall 중앙값 < 5%일 때만 제외)의 결과가 6.2%이므로 hall을 판정 지표로 유지하고 초안 v2의 hall 조건·A′ 등급을 복원(V3-23의 "판정 = step accuracy만" 서술은 이 항목으로 대체). 비용·지연·goal completion은 기술 지표. (2) 비교 1(vs vanilla_budget)·비교 2(vs vanilla_vector) 명명; 방향 카운트 분모 3·동률 미가산; A = 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음(+hall 조건), A′ = step 조건만, B, C; "3/3이면 검정 없이 A" 삭제; 두 1차 검정 Holm(패밀리 2) 병기. (3) held-out 예비 문단·"(held-out 저작자 확보 전까지)" 삭제. (4) §8에 QGIS 파일럿(2026-08-13) 이력 한계 추가. (5) P8: QGIS 비교 2 방향은 예측하지 않음(iteration 5: Gemini 동률·Claude 우위·GPT 열세). (6) 구조: 2.5·2.6 → §2, 5.x → §5 뒤, 8.x → §8, §9 맨 끝(내용 불변, 제목 수준만 ###). (7) D8 실측: 구 인덱스 1,254청크를 MiniLM 토크나이저로 세어 800토큰 가득 찬 청크 114개는 피스 중앙값 OpendTect 952·QGIS 847 → 256 피스 = 앞 27–30%(접두 약 76 피스 포함); 554/1,254는 256 이내. 초안의 "앞 ~10%"는 오기(임베더 주석의 "~2,500 피스" 추정에서 유래).

### V3-25. 사전등록 서명과 확인적 실행 시작 (2026-09-18)
- 서명: 최종안 2c85e22 승인 후 §9 기입(작성 유지윤; 검토 외부 검토 Claude(채팅), 2026-09-18; 확정 2026-09-18T08:09:04Z = 서명 커밋 시각). 서명 커밋 0f52154, 태그 `v3-prereg-signed`. 코드·scripts·GT는 태그 `v3-freeze-c01fdda`와 동일.
- 실행 전 확인(병렬 안전성): vision 캐시는 프로세스 내 메모리 dict(이미지 바이트 SHA-256 키)이며 파일 캐시가 없어 프로세스 간 공유·경합이 없다(캐시 적중도 호출과 같게 과금·지연 재생). 결과 JSON은 실행마다 `run_<model><tag>_r<rep>_<UTC초>.json`으로 한 번 쓰이므로 공급자 간 충돌이 없다. 그러나 동결된 래퍼 `run_v3.sh`는 (a) 시작 시 공유 디렉터리 `.dev_opendtect`를 rm/cp 하고, (b) long_context(Gemini ×10)를 MODELS와 무관하게 실행하며, (c) 로그 파일 하나에 tee 하므로, 공급자별 인스턴스 3개를 동시에 돌리면 (a) 경합·(b) long_context 3배 실행이 생긴다. 래퍼를 고치지 않고는 병렬이 안전하지 않아 **순차 실행**한다. 최종 표의 지연은 §8.x대로 별도 clean run의 단계 분해로 보고한다.
- 실행 시작(UTC): 2026-09-18T08:09:34Z. 실행 중 코드·GT·워크플로우·사전등록 본문 불변; 재실행 시 §6.4; 크레딧 소진 시 즉시 중단·보고.
