# v3 재실행 사전등록 (초안 — 서명 전)

**작성 시점**: 2026-09-17, 0단계(수정·재채점·dry-run) 진행 중. v3 벤치 숫자는 아직 하나도 없음.
**상태**: 초안. `[TBD]` 항목을 채우고 검토자·저자가 확정한 뒤 서명 시각을 적고 나서 2단계(스모크) → 3단계(전체 실행)로 진행한다. 서명 후 이 문서는 add-only.
**원칙 (검토자 합의)**: (1) 모든 수정은 실행 전에 확정한다. (2) 수정은 모든 백엔드에 같이 적용한다. (3) 판정 기준을 먼저 고정한다. (4) GeoLens 쪽 결함과 baseline 쪽 결함을 함께 고친다. (5) 결과 예상은 양방향으로 열어 둔다.

---

## 1. 재개 사유 (unified4 → v3)

unified4 사전등록의 정지 규칙("unified5 없음")을 다음 결함 때문에 프로토콜 이탈로 재개한다. 어느 하나만으로도 표의 숫자가 바뀐다.

| # | 결함 | 영향 방향 | 근거 |
|---|---|---|---|
| D1 | Qwen 트랙이 텍스트 전용 모델(qwen3-235b-a22b-instruct)로 실행되어 스크린샷을 받지 못함 | Qwen 열 전체 무효 | bench_backends `_messages_to_text_only`; no_rag 입력 토큰 Qwen 514 vs Gemini 550/GPT 1,394/Claude 2,056 |
| D2 | 채점기 `\b`가 한글 조사를 단어 문자로 취급 → 'name에', 'Cross-line에서' 불일치 | 모든 백엔드; Gemini·GPT에 더 큼(126/1,920 + longctx 8/80 + QGIS 28/120 뒤집힘) | rescore_v3_*.md |
| D3 | 환각 판정이 따옴표 사용 여부에 의존(따옴표·'X 버튼'만 추출) | 모델별 표기 습관에 따라 값이 달라짐 | evaluation.hallucinated_elements(v2) |
| D4 | Qwen의 잘린 `<think>` 블록이 응답으로 채점됨(55/480, 100% matched·100% hallucinated) | Qwen Step Acc·Hall 동시 부풀림 | `_strip_thinking` v2 |
| D5 | 비용이 생성기의 입력·candidates 토큰만 집계: vision·rerank Flash 호출 미기록, Gemini 생성기 thinking 토큰(출력 단가 과금) 미기록 | full_system·state_path·graph_only 보조비용 과소; Gemini 전 백엔드 생성기 비용 과소(no_rag 약 6배) | `_record_usage`; 2026-09-17 프로브 vision $2.6m·rerank $4.4m/호출(thinking 켜짐); 스모크 Gemini no_rag $4.65m vs unified4 $0.75m |
| D6 | 검색 컨텍스트가 [Knowledge Graph] triplet 블록을 맨 앞에 두어 1,500자 예산의 ~1,100자를 지질 개념 관계가 차지 | full_system fallback 스텝이 매뉴얼 본문을 ~300자만 받음 | rag._merge_contexts v2 |
| D7 | 벤치 하네스가 매 스텝 이전 스텝 전부를 재-localize (rerank i+1회/스텝, 실행당 75회) | full_system·state_path 지연·보조비용 3.5배 과대 | bench_backends v2 |
| D8 | 임베더 all-MiniLM-L6-v2: 영어 중심, 256 word-piece에서 절단(800토큰 청크 → MiniLM 2,500토큰 중 앞 10%만 임베딩), 질의는 한국어 | vanilla_vector 검색 실패(attribute §1.5.1a 0/15, 3d_viz 0/11, QGIS 0/9) → baseline 과소 | retrieval_replay_minilm.md |
| D9 | 생성 설정 불일치: max_tokens Claude/GPT 512, Qwen 1024, Gemini 미설정; temperature Qwen만 0.2 | 모델 간 비교 오염 | bench_backends v2 |
| D10 | QGIS 파일럿이 OpendTect 워크플로우를 격리한 채 실행(방해 후보 없음) | full_system 라우팅 난이도 과소 | run_qgis_pilot v2 |
| D11 | graph_only가 청크 본문을 주입하지 않음(docstring과 불일치), state_path 라우팅 텔레메트리 미기록, rerank 'none' 경로가 fallback으로 라벨되지 않음(NONE bucket) | ablation 해석 오류 | bench_backends, guide_pipeline v2 |

---

## 2. 실행 전에 확정하는 수정 목록 (양쪽)

### 2.1 채점기·평가 (모든 백엔드 동일)
| 항목 | 변경 | 코드 |
|---|---|---|
| S1 | step_match: 시나리오 패턴의 `\b( … )\b`를 ASCII 경계 `(?<![A-Za-z0-9])( … )(?![A-Za-z0-9])`로 재작성(v3). v2는 `GEOLENS_SCORER=v2`로 재현 가능 | evaluation.py `_ascii_boundary`, `step_match_v2/v3` |
| S2 | hallucinated_elements v3: 따옴표와 무관하게 대문자로 시작하는 라틴 라벨 구를 모두 추출(영어 기능어·명령 동사 제외), 근거 어휘 = visible_elements + current_dialog + active_menu + data_state + current_action + screen_state(느슨한 정규화 부분문자열), 목표 문장에 적힌 값(입력할 이름·경로)은 제외 | evaluation.py `_hallucinated_elements_impl` |
| S3 | `<think>` 미폐쇄 블록은 응답에서 제거(빈 응답 처리) | bench_backends `_strip_thinking` |
| S4 | 비용: `cost_usd`(생성기, thinking 포함) + `aux_cost_usd`(vision·rerank Flash, thinking 포함) = `cost_total_usd`. **판정에 쓰는 비용은 cost_total** | evaluation.py per_step, guide_pipeline `record_aux_usage` |
| S5 | faithfulness는 1−hall의 동어반복이므로 판정 지표에서 제외, 표에는 보고만 | 본 문서 §6 |
| S6 | GT 보정(실행 전, 독립 저자): (a) 4 시나리오 visible_elements를 화면의 실제 라벨로 완성(v3 환각 판정이 따옴표 없는 라벨도 검사하므로), (b) survey_setup s0에 텍스트 없는 아이콘 대안('+|플러스|더하기|plus') 추가, (c) QGIS s3(Input layer)는 캡처 화면에서 레이어가 이미 채워져 있는지 확인 후 GT 또는 캡처를 정정. 구 GT·신 GT 양쪽으로 unified4 로그를 재채점해 백엔드별 변화량을 §4에 싣는다 | data/eval/scenarios/*.json `[TBD: 담당자·일자]` |

### 2.2 baseline 측 (vanilla가 손해 보던 결함)
| 항목 | 변경 | 코드 |
|---|---|---|
| B1 | 임베더 BAAI/bge-m3(8,192토큰 창, 1,024-d, 정규화), 같은 청크 id·본문으로 재임베딩한 data/chromadb_v3 사용(OpendTect 521, QGIS 733청크) | embedder.py EMBED_MODEL; scripts/reembed_index.py |
| B2 | 생성 설정 통일: temperature 0.2, 답변 max_tokens 1,024 전 모델; Gemini는 thinking_budget 1,024 고정(끌 수 없음) + max_output_tokens 2,048 | bench_backends GEN_* |
| B3 | 환각 지표 따옴표 의존 제거 (=S2) | |
| B4 | QGIS 파일럿 비격리: 7개 워크플로우 전부 적재한 채 실행. 반대로 OpendTect 실행에서도 qgis_vector_buffer·auto_bf2804… 워크플로우가 후보에 남는다(대칭) | run_qgis_pilot.py `--isolate` 기본 off |
| B5 | vanilla_budget 백엔드 추가: vanilla와 같은 검색, 컨텍스트를 full_system의 매뉴얼 예산(3×800 + 1,500 = 3,900자)으로 절단 | bench_backends `backend_vanilla_budget` |
| B6 | graph_only에 linked_chunks 본문(3×800자) 주입 | bench_backends |

### 2.3 GeoLens 측
| 항목 | 변경 | 코드 |
|---|---|---|
| G1 | 검색 컨텍스트에서 KG triplet 블록을 맨 뒤로(`RAG_KG_POSITION=last`) — vanilla·vanilla_budget·full 공통 | rag.py |
| G2 | 하네스 세션 상태: visited_node_ids를 스텝 간 유지(재-localize 제거) | bench_backends `_session_visited` |
| G3 | vision·rerank 호출 thinking off(`AUX_THINKING_BUDGET=0`), 토큰·비용 기록 | guide_pipeline |
| G4 | rerank 'none' 경로를 fallback으로 라벨(검색 의미는 동일) | guide_pipeline |
| G5 | state_path 텔레메트리 기록 | guide_pipeline `_set_localize_meta` |
| G6 | Qwen을 Qwen3-VL로 서빙하고 스크린샷 전달(`QWEN_TEXT_ONLY=0`) | bench_backends `_call_qwen` |

### 2.4 변경하지 않는 것
- 시나리오 4개(OpendTect 3 + QGIS 1)와 스크린샷 24장, 목표 문장.
- 워크플로우 JSON 7개와 모든 visual_signature. **seismic_attribute signature는 재작성하지 않는다** (같은 스크린샷에 맞추는 튜닝 = 시험지 튜닝). attribute 라우팅이 낮게 나오면 그대로 보고한다.
- 판정 프레임의 구조(A/B/C, 방향 일관성 1차, 개별 p 2차), 3-gate 목표 판정, confidence 임계 0.7, 절단 예산 값.
- 프롬프트 골격(_inline_action_prompt).

---

## 3. 채점기 변경만의 효과 — unified4·long_context·QGIS 로그 재채점 (API 비용 0)

v2 재구현은 저장된 matched/hallucinated와 2,120/2,120 스텝 일치. 아래는 같은 응답을 v3로 다시 채점한 값(매크로 %, Δ = v3 − v2). GT 보정(S6) 전 값이며, S6 후 다시 갱신한다 `[TBD]`.

| 자료 | 파일 |
|---|---|
| unified4 24셀 | data/eval/results/rescore_v3_unified4.md |
| long_context | data/eval/results/rescore_v3_longctx.md |
| QGIS 파일럿 | data/eval/results/rescore_v3_qgis_pilot.md |

요약 (Step Acc v2 → v3; Hall v2 → v3):
- Gemini: no_rag 66.7→78.3 / 0.8→7.5; vanilla 75.0→81.7 / 7.5→11.7; full 72.5→84.2 / 7.5→10.8; state 76.7→91.7 / 1.7→11.7
- Claude: no_rag 85.0→87.5 / 25.0→16.7; vanilla 84.2→87.5 / 24.2→15.0; full 85.0→87.5 / 22.5→21.7
- GPT: no_rag 50.8→65.0 / 30.8→1.7; vanilla 60.0→70.8 / 36.7→3.3; full 69.2→81.7 / 30.8→1.7
- Qwen(think 제거 포함): no_rag 49.2→40.8 / 40.0→18.3; vanilla 55.0→42.5 / 61.7→36.7; full 56.7→43.3 / 50.0→10.0
- long_context 59.2→72.5 (Gemini 백엔드 중 여전히 최저); QGIS no_rag 62.5→82.5, vanilla 62.5→82.5, full 57.5→87.5
- full vs vanilla 방향(step_acc): v2 3/4(Gemini 반대) → v3 Gemini full, Claude 동률, GPT full, Qwen full. hall: v3에서 Claude는 vanilla 우세(21.7 vs 15.0).
- 해석 주의: GPT hall 30.8→1.7은 v2가 따옴표로 감싼 목표 값('My_F3_Survey', 'Energy [-28,+28]', 파일 경로)을 환각으로 세던 것이 사라진 효과. 남은 v3 환각의 상당수('Similarity', 'Seismic_data', 'Save Attribute as')는 화면에 있으나 GT visible_elements에 적히지 않은 라벨로 보이며, S6에서 처리한다.

---

## 4. 실행 전 게이트 결과

| 게이트 | 결과 | 파일 |
|---|---|---|
| 임베더 리플레이(MiniLM, 구 인덱스): 목표 절 적중 | survey 6/9, 3d_viz 0/11, attribute 0/15, QGIS 0/9(절 이름 미상) | retrieval_replay_minilm.md |
| 임베더 리플레이(bge-m3, chromadb_v3, KG 블록 후순위) | 목표 절 적중 survey 7/8, 3d_viz 0/13(여전히 §1.3.1a 미적중 — 2.3.1c/1.3/2.6.3 계열 회수), attribute **7/12**(0/15에서 개선), QGIS top-5 페이지 214/218/216/217/219 = §6.2.6 'Analyzing the Problem: Distances From Schools and Roads'(pp. 214–218) 4/5 적중(MiniLM은 222/220/314/217/218 = 2/5; 인덱스의 절 이름이 ★☆☆ 등급 문자열로 저장되어 페이지로 판정); 앞 1,500자가 매뉴얼 본문으로 시작함(4/4) | retrieval_replay_bgem3.md |
| vision 기반 라우팅 dry-run, thinking off (7개 워크플로우 전부 적재, 2026-09-17) | 정답 워크플로우 선택: survey 4/4, 3d_viz 3/4, attribute 0/8, QGIS 5/8 (합 12/24); 유지(conf≥0.7) 17/24; none 6/24; 보조비용 $1.29m/스텝(vision+rerank 2회), 지연 10.8 s/스텝 | routing_dryrun_vision_think0.md |
| 같은 dry-run, thinking 기본값(dynamic) | 정답 4/4, 3/4, 0/8, 6/8 (합 13/24); 유지 18/24; none 3/24; 보조비용 $6.81m/스텝(thinking 1,700~2,600 토큰/스텝), 지연 21.5 s/스텝. 두 실행에서 노드 선택이 같은 스텝 12/24 — rerank 자체의 실행 간 변동이 큼 | routing_dryrun_vision_thinkdyn.md |
| thinking off 채택 여부 | **채택.** 정답 선택 차이 1 스텝(12 vs 13, 기준 ≤2) 이내이고 보조비용 5.3배·지연 2배 절감. attribute 라우팅은 두 설정 모두 0/8이며(signature 미수정 원칙), QGIS 자동 생성 워크플로우(auto_bf2804…)가 OpendTect attribute 스텝의 방해 후보로 작동함을 기록 | |
| 스모크(Gemini × 7 백엔드 × survey_setup 1회, 2026-09-17 09:32Z) | 빈 응답 0/28, judge 정상, 라우팅 텔레메트리가 full_system·state_path 모두 기록(survey_setup conf 0.8~0.9), 세션 visited로 rerank 스텝당 1회(aux_calls 4/4스텝), Gemini 생성기 thinking 391~669 토큰/스텝 기록, 지연 8~14 s/스텝, 백엔드당 44~67 s(5 호출). 스모크 후 발견·수정: 같은 프로세스에서 먼저 실행된 백엔드(graph_only)만 vision 비용을 부담하던 캐시 회계를 고쳐 캐시 적중도 요청 백엔드에 과금(vision_cached). 스모크 값은 게이트용이며 표에 쓰지 않음 | run_gemini_v3smoke_r1_20260917T093224.json |
| Qwen3-VL 서빙 | `[TBD: 엔드포인트 /v1/models 응답, 모델 id, vLLM 버전, TP]` | |

---

## 5. 사전 예측 (양방향, 결과 관측 전)

| # | 예측 | 근거 | 반증되면 |
|---|---|---|---|
| P1 | bge-m3로 vanilla_vector의 목표 절 적중이 오르고(attribute 0/15 → 7/12, QGIS 2/5 → 4/5는 §4에서 확인; 3d_viz는 0/13으로 불변), vanilla Step Acc가 unified4 재채점값보다 오른다 | D8 | 임베더가 원인이 아니었음 → 검색 실패의 다른 원인(청킹·질의문; 3d_viz 목표문의 UI 어휘가 §1.3.1a 청크와 어휘적으로 겹치지 않음) 기록 |
| P2 | 보조 호출을 포함한 총비용에서 full_system은 vanilla_vector보다 저렴하지 않을 수 있다(2026-09-17 프로브: thinking off 시 스텝당 약 $1.2m 추가) | D5 | 비용 우위 주장 철회, "예산 효과"로 서술 |
| P3 | vanilla_budget은 vanilla_vector와 비용은 full 수준, Step Acc는 vanilla_vector와 같거나 낮다. full_system − vanilla_budget 차이가 라우팅의 순효과 | B5 | 라우팅 효과 없음으로 보고 |
| P4 | seismic_attribute 라우팅은 여전히 낮다(dry-run 0/8, fallback·none 5/8); attribute 시나리오에서 full ≈ vanilla_budget | signature 미수정 | — |
| P5 | Qwen3-VL은 텍스트 전용 Qwen보다 환각률이 내려간다 | D1 | 모달리티 설명 재검토 |
| P6 | thinking off는 라우팅 정답률을 2 스텝 이하로만 바꾼다 — **§4에서 확인(12 vs 13/24), off 채택** | dry-run | (해당 없음) |
| P7 | GeoLens가 열세일 수 있는 축: hall(v3에서 Claude 역전), Step Acc(Gemini·Claude는 동률권) | §3 | §7 보고 방식대로 보고 |

---

## 6. 판정 기준 (재정의, 실행 전 고정)

### 6.1 지표
- 1차: step_accuracy(v3), hallucination_rate(v3), goal_completion_rate(3-gate), **cost_total_usd/step**(생성기 + 보조, thinking 포함). faithfulness는 보고만.
- 2차: loop_rate, latency, fallback_rate, route telemetry, judge_step_accuracy(보조), cost_usd(생성기만; unified4와의 비교용).
- 집계: 스텝 → 시나리오 → replicate → 셀(mean ± 표본 SD). 검정 단위 replicate.

### 6.2 비교 대상
- 주 비교 A: full_system vs vanilla_budget (같은 예산; 라우팅 효과).
- 주 비교 B: full_system vs vanilla_vector (관행적 baseline; 비용은 총비용).
- 보조: vs no_rag, graph_only, vision_only, state_path, long_context(Gemini).

### 6.3 스토리 판정 (모델 집합 M = `[TBD: 4 (Qwen3-VL 서빙 성공) | 3 (실패)]`)
- **A (시스템 우위)**: (i) step_accuracy에서 full > vanilla_budget 방향이 |M|−1 이상 모델(4→3/4, 3→2/3… `[TBD: |M|=3이면 3/3 요구로 할지 확정]`), (ii) hallucination_rate에서 full ≤ vanilla_budget 방향이 |M|−1 이상, (iii) 최소 1개 모델에서 step_accuracy full vs vanilla_budget 순열검정 raw p < 0.10 (Holm 보정값 병기, 보정 후 유의를 주장하지 않음), (iv) cost_total에서 full_system ≤ vanilla_vector가 API 유료 모델 전부(라우팅이 예산 효과를 상쇄하는지) — (iv)가 실패해도 (i)~(iii)이 성립하면 "A′: 품질 우위, 비용 동등 이상"으로 보고.
- **B (조건부)**: (i)(ii) 중 하나만 성립하거나 모델 의존적 역전.
- **C (비등/열세)**: (i)(ii) 모두 |M|−2 이하.
- 방향 일관성 카운트 규칙: 4/4 일관, 3/4 다수, 2/4 혼재, ≤1/4 역효과(|M|=3이면 3/3, 2/3, ≤1/3).

### 6.4 통계
- 순열검정 10,000회(seed 42, 양측, |평균차|), Welch t 병기. 패밀리 = pairs × metrics × models 전체를 명시하고 Holm·Bonferroni 보정값을 표에 병기. 최소 p = 2/C(2n, n).
- **n = 10 replicates**(사전 고정). 4번 수정으로 실행 시간이 줄어 가능.

### 6.5 정지 규칙과 열세 시 보고
- v4 없음. v3 결과가 어떻게 나오든 이 문서 기준으로 A/A′/B/C를 판정하고 그대로 보고한다.
- GeoLens가 열세(B·C)이면: (1) Table 1에 vanilla_budget을 권장 구성으로 표시, (2) 라우팅의 순효과(full − vanilla_budget)를 축별로 부호 그대로 보고, (3) 총비용에서 보조 호출 몫을 분해해 보고, (4) 제목·초록의 "우위" 표현을 "조건부"로 바꾼다. 재실행·시나리오 교체·채점기 재조정 금지.
- 귀속: 채점기 변경 효과는 §3 재채점으로 귀속한다. 나머지(임베더·예산·하네스·보조비용·Qwen VL)는 한 번에 바뀌므로 "v3 전체의 변화"로만 서술한다.

---

## 7. 실행 계획
- 래퍼: `bash scripts/run_v3.sh` (환경변수: CHROMADB_PATH=./data/chromadb_v3, EMBED_MODEL=BAAI/bge-m3, GEOLENS_SCORER=v3, RAG_KG_POSITION=last, AUX_THINKING_BUDGET=0, GEN_TEMPERATURE=0.2, GEN_MAX_TOKENS=1024, GEMINI_THINKING_BUDGET=1024, VANILLA_BUDGET_CHARS=3900, QWEN_MODEL/QWEN_BASE_URL).
- 매트릭스: |M| 모델 × 7 백엔드(no_rag, vanilla_vector, vanilla_budget, graph_only, vision_only, full_system, state_path) × 3 OpendTect 시나리오 × 10회 + Gemini long_context × 10회 + QGIS 파일럿(Gemini × no_rag/vanilla_vector/full_system × 10회, 비격리).
- held-out: horizon_tracking·fault_interpretation 시나리오(초안 data/eval/scenarios/excluded/heldout_drafts/)를 워크플로우 JSON을 보지 않은 연구원이 저작·캡처한 뒤 **signature 수정 없이** 실행. 본 매트릭스 이후 별도 표. `[TBD: 담당자·완료일]`
- 예상 비용·시간(스모크 기준 산정): 실행 1회 = 7 백엔드 × (16 스텝 + 3 완료 호출) = 133 생성기 호출 ≈ 30분(judge 포함). 4 모델 × 10회 = 40회 → 순차 약 20시간, 공급자별 병렬(Gemini/Claude/GPT/Qwen 프로세스 분리) 시 약 6~7시간. long_context 10회 ≈ 50분, QGIS 10회 ≈ 50분. API 비용(flat rate) ≈ Gemini 메인 $10 + Claude $15 + GPT $9 + long_context $62(190회 × $0.32; Gemini >200K 티어 실과금 시 약 2배) + QGIS $2 + judge $10 + Qwen 보조 Flash $2 ≈ **$110 (실과금 최대 약 $170)**. Qwen 생성기는 셀프호스팅(GPU 시간).
- 비용 회계 변경 요약: v3의 cost_total = 생성기(입력 + 출력 + thinking) + 보조(vision + rerank, 캐시 적중 포함). unified4의 Gemini 생성기 비용은 thinking 토큰(스텝당 약 400~700, 출력 단가 $10/M)을 빼고 집계되어 no_rag 기준 약 6배 과소였다(스모크 $4.65m vs unified4 $0.75m). 따라서 v3 비용 열은 unified4 비용 열과 직접 비교하지 않는다.
- 태그: 파일명 run_{model}_v3_r{r}_*.json, run_gemini_v3longctx_r{r}_*.json, run_gemini_v3_qgis_r{r}_*.json.
- 환경 기록: google-genai 1.75.0(thinking_budget 지원 위해 1.3.0에서 상향), bge-m3 via sentence-transformers 5.5.1, 그 외 requirements.txt.

---

## 8. 서명
- 작성: `[TBD]` / 검토: `[TBD]` / 확정 시각(UTC): `[TBD]`
- 확정 후 첫 벤치 실행 시각을 아래에 append한다.
