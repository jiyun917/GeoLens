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

---

## Limitations 섹션 원자재

이 audit trail에서 뽑을 limitations:
1. **시나리오 수가 2개 (survey_setup + 3d_visualization)**로 제한적. 논문
   external validity 서술 시 명시.
2. **3d_visualization의 최종 스크린샷이 실제 goal-reached 상태를 담고
   있지 않음** → 이 시나리오에서는 어떤 시스템도 goal_completion 3-gate
   통과 불가. 이건 시나리오 설계 한계로 명시 (지표 실패가 아님).
3. **Fallback rate이 초기 관측에서 상당** — hybrid의 실제 우위는
   "fallback이 발동하지 않는 스텝"에서만 온다. v2 로그로 이 비율 정량화.
4. **모델별 무관 컨텍스트 강건성 차이 (Claude 비대칭)**의 원인은 이
   벤치로 규명 불가 — 후속 연구.
