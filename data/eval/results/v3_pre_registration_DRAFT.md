# v3 재실행 사전등록 (초안 v2 — 서명 전)

**작성 시점**: 2026-09-18, 0단계(수정·재채점·dry-run·스모크) 완료, 메커니즘 동결 커밋 직후. v3 벤치 숫자는 아직 하나도 없음.
**상태**: 초안. `[사용자 결정]` 항목을 확정하고 서명 시각을 적은 뒤에만 3단계(전체 실행)로 진행한다. 서명 후 이 문서는 add-only.
**원칙**: (1) 모든 수정은 실행 전에 확정한다. (2) 수정은 모든 백엔드·모델에 같이 적용한다. (3) 판정 기준을 먼저 고정한다. (4) 시스템 쪽 결함과 baseline 쪽 결함을 함께 고친다. (5) 결과 예상은 양방향으로 열어 두고, 불리한 결과도 그대로 보고한다.

---

## 0. 세트 구분과 이력

| 세트 | 시나리오 | 이력 | 역할 |
|---|---|---|---|
| 개발 세트 | opendtect__survey_setup__01, opendtect__3d_visualization__01 | unified2부터 사용. 라우팅 결함 진단·수정, 캡처 정제(3d_viz step 3, unified3)에 사용됨 | 라우팅 진단·메커니즘 수정은 여기서만 |
| 개발 세트 | opendtect__attribute_computation__01 | unified3에서 사전등록 예측과 함께 처음 실행(당시 테스트). unified4에서 seismic_attribute signature를 재작성한 뒤로는 개발용 | 위와 같음 |
| 테스트 세트 | qgis__vector_buffer__01 (8스텝) | 2026-08-13 파일럿 1회. 결과를 보고 시스템·signature를 고친 적 없음. v3에서는 메커니즘 동결 커밋 이후에만 실행. **2026-09-18, QGIS 결과를 보기 전에 수행한 배포 설정**: QGIS 매뉴얼 v4 재인제스트(그림 OCR 규칙, bge-m3)와 `qgis_vector_buffer` 노드 5개의 linked_chunks 연결(절 출처 §6.2.6, OpendTect와 같은 규칙, 스크립트 15.8 s + 사람 약 5분; V3-11). signature·제목·설명·시나리오 파일 불변 | 라우팅 관련 판정의 기준 세트 |

held-out 예비: horizon_tracking·fault_interpretation 시나리오 초안(`data/eval/scenarios/excluded/heldout_drafts/`). 워크플로우 JSON을 보지 않은 연구원이 저작·캡처한 뒤 signature 수정 없이 별도 표로 실행 `[사용자 결정: 담당자·일정]`.

---

## 1. 재개 사유 (unified4 → v3)

unified4 사전등록의 정지 규칙("unified5 없음")을 다음 결함 때문에 프로토콜 이탈로 재개한다.

| # | 결함 | 방향 | 근거 |
|---|---|---|---|
| D1 | Qwen 트랙이 텍스트 전용 모델로 실행되어 스크린샷을 받지 못함 | Qwen 열 무효 | `_messages_to_text_only`; no_rag 입력 토큰 Qwen 514 vs 550/1,394/2,056 |
| D2 | 채점기 `\b`가 한글 조사를 단어 문자로 취급 → 'name에', 'Cross-line에서' 불일치 | 전 백엔드(Gemini·GPT에 더 큼); unified4 126/1,920, long_context 8/80, QGIS 28/120 뒤집힘 | rescore_v3_*.md |
| D3 | 환각 판정이 따옴표 사용 여부에 의존 | 모델별 표기 습관 편향 | evaluation v2 |
| D4 | Qwen의 잘린 `<think>` 블록이 응답으로 채점(55/480, 100% matched·hallucinated) | Qwen 부풀림 | `_strip_thinking` v2 |
| D5 | 비용이 생성기 입력·candidates 토큰만 집계: 보조 Flash 호출 미기록, Gemini 생성기 thinking 미기록(no_rag 약 6배 과소) | 시스템 비용 과소 | 프로브·스모크 |
| D6 | 검색 컨텍스트가 KG triplet 블록을 맨 앞에 두어 1,500자 예산의 ~1,100자를 지질 개념이 차지 | fallback 스텝이 매뉴얼 본문 ~300자만 받음 | rag v2 |
| D7 | 하네스가 매 스텝 이전 스텝 전부를 재-localize(rerank i+1회/스텝) | 지연·보조비용 3.5배 과대 | bench_backends v2 |
| D8 | 임베더 MiniLM: 256 토큰 절단(800토큰 청크의 앞 ~10%), 영어 중심, 질의는 한국어 | vanilla 검색 실패(attribute 0/15, 3d_viz 0/11, QGIS 2/5) → baseline 과소 | retrieval_replay_minilm.md |
| D9 | 생성 설정 불일치(max_tokens 512/1024/미설정, temperature Qwen만 0.2) | 모델 간 비교 오염 | bench_backends v2 |
| D10 | QGIS 파일럿이 OpendTect 워크플로우를 격리한 채 실행 | 라우팅 난이도 과소 | run_qgis_pilot v2 |
| D11 | graph_only 청크 본문 미주입, state_path 텔레메트리 미기록, rerank 'none'이 fallback으로 라벨되지 않음 | ablation 해석 오류 | v2 코드 |
| D12 | 라우팅 후보 단계가 signature 문자열의 부분문자열 일치 비율이라 서술형 signature(seismic_attribute)는 후보 풀에 들어가지 못함 | attribute 0/8 (전부 후보 단계 탈락) | routing_diag_dev_v2.md |

Qwen 제외 사유: Qwen3-VL 서빙 불가(NAS 미접속), 텍스트 전용 Qwen은 입력 조건(스크린샷)을 맞출 수 없음. 따라서 |M| = 3 (Gemini 2.5 Pro, Claude Sonnet 4.6, GPT-4o).

---

## 2. 실행 전에 확정된 수정 (양쪽) — 메커니즘 동결 커밋 `bacfde7f` (branch v3-rerun, 2026-09-18 09:46 KST)

### 2.1 채점·평가 (전 백엔드 동일)
| S1 | step_match: 패턴 `\b( … )\b` → ASCII 경계 (`GEOLENS_SCORER=v2`로 구 채점기 재현) |
|---|---|
| S2 | 환각 판정 v3: 따옴표 무관 라틴 라벨 구 추출(영어 기능어·명령 동사 제외); 근거 어휘 = visible_elements + current_dialog + active_menu + data_state + current_action + screen_state(느슨한 정규화 부분문자열); 목표 문장의 값은 제외 |
| S3 | 미폐쇄 `<think>` 제거(빈 응답 처리) |
| S4 | cost_total = 생성기(입력+출력+thinking) + 보조(vision·rerank, 캐시 적중 포함). 판정 비용 = cost_total |
| S5 | faithfulness는 1−hall의 동어반복 → 판정에서 제외, 표에는 보고만 |
| S6 | GT visible_elements 전수 보정 절차(작업 5): 24장 전부에 같은 절차 — gemini-2.5-pro, temperature 0, 고정 프롬프트로 화면의 라벨·버튼·다이얼로그 제목·메뉴·트리 항목을 전부 열거(`scripts/gt_enumerate_visible_elements.py`), 모델 응답 로그는 참조하지 않음. 현 GT와의 diff를 `gt_visible_elements_review_v3.md`로 만들고 사용자가 검수한 뒤 반영. 반영 후 unified4 로그를 구·신 GT로 재채점해 백엔드별 변화량을 §4에 추가 `[사용자 결정: 검수·반영]`. survey_setup s0의 텍스트 없는 '+' 아이콘 대안, QGIS s3(Input layer 기본 채움 여부)도 같은 검수에서 결정 |

### 2.2 baseline 측
| B1 | 임베더 BAAI/bge-m3(8,192토큰, 1,024-d, 정규화), 같은 청크 id로 재임베딩한 `data/chromadb_v3` (OpendTect 521, QGIS 733청크) |
|---|---|
| B2 | 생성 설정 통일: temperature 0.2, 답변 max_tokens 1,024; Gemini는 thinking_budget 1,024 고정 + max_output_tokens 2,048 |
| B3 | 환각 지표 따옴표 의존 제거(=S2) |
| B4 | QGIS 비격리: 워크플로우 7개(OpendTect 5 + QGIS 1 + 자동 생성 1) = 41노드가 후보 풀에 그대로. OpendTect 실행에서도 QGIS 워크플로우 2개가 후보에 남음(대칭) |
| B5 | vanilla_budget: vanilla_vector와 같은 검색, 컨텍스트를 full_system의 매뉴얼 예산 3×800 + 1,500 = 3,900자로 절단 |
| B6 | graph_only에 linked_chunks 본문(3×800자) 주입 |
| B7 | QGIS도 3모델 × 7백엔드 전부 실행(v2 파일럿은 Gemini × 3백엔드) |

### 2.3 시스템 측
| G1 | 검색 컨텍스트에서 KG triplet 블록을 뒤로(`RAG_KG_POSITION=last`; vanilla·vanilla_budget·full 공통) |
|---|---|
| G2 | 하네스 세션 상태(visited_node_ids 유지) |
| G3 | vision·rerank thinking off(`AUX_THINKING_BUDGET=0`), 토큰·비용 기록(캐시 적중도 과금) |
| G4 | rerank 'none' → fallback 라벨 |
| G5 | state_path 텔레메트리 기록 |
| G7 | **KB v4와 linked_chunks 재연결**(V3-8/V3-9/V3-11): 그림 면적 OCR 규칙 + bge-m3로 양쪽 매뉴얼 재인제스트(`data/chromadb_v4`). unified2–4의 linked_chunks id는 전부 무효였음(V3-9)을 확인하고, OpendTect 5개 워크플로우와 QGIS 워크플로우의 노드를 절 출처 기준(`manual_sections`, `chunk_mapper` top-3)으로 재연결. QGIS 연결은 QGIS 결과를 보기 전에 수행한 배포 설정. 개발 루프의 메커니즘 변경(V3-9: 후보 풀·vision/rerank 프롬프트 v3·그래프 prior·병렬 검색·fallback 예산·soft post-completion)은 동결 시점 값과 함께 §2.3에 최종 기재 |
| G6 | **후보 단계 매칭 메커니즘 교체**(작업 1): signature 부분문자열 비율 → vision 출력과 노드 텍스트(제목·설명·expected_dialog·UI 요소·키워드)의 bge-m3 코사인 유사도(`api/services/node_matcher.py`, `ROUTER_MATCHER=embedding`; `substring`으로 v2 재현). CLIP 후보 단계와 rerank는 불변. 진단: 개발 세트 16스텝 중 실패 9 = 후보 단계 탈락 8(전부 attribute) + rerank 거절 1; seismic_attribute 노드의 부분문자열 점수 0.18–0.20 vs 타 워크플로우 0.47–0.67 (`routing_diag_dev_v2.md`). vision 프롬프트 변경(a)은 화면 문자열이 이미 보고되고 있어 원인과 무관하므로 채택하지 않음 |

### 2.4 변경하지 않는 것 / 금지
- 시나리오 4개, 스크린샷 24장, 목표 문장, 워크플로우 JSON 7개의 모든 visual_signature·제목·설명(QGIS 포함). 개별 signature를 스크린샷에 맞춰 고치지 않는다. (워크플로우 JSON에서 v3가 바꾼 필드는 `linked_chunks`·`manual_sections`·`linked_chunks_provenance`뿐이다 — V3-9/V3-11. 개발 루프에서 허용된 OpendTect signature 보강이 있으면 V3-* 항목과 §2.3에 명시한다.)
- 사전등록 서명 전 벤치 실행 금지(dry-run·스모크만). QGIS는 동결 커밋 전 dry-run 포함 실행 금지(준수: v3에서 QGIS 미실행). 동결 후 QGIS 결과를 보고 메커니즘을 다시 고치지 않는다.
- 결과를 본 뒤 판정 기준·채점 규칙을 바꾸지 않는다. v4 없음.
- 모든 변경은 `methodology_audit_trail.md`에 append (§V3-*).
- 3d_visualization의 목표 절 결손(§4 작업 3)은 KB(OCR 임계) 문제였고, 사용자 결정(2026-09-18)으로 양쪽 매뉴얼을 같은 그림 면적 OCR 규칙으로 재인제스트한 `chromadb_v4`를 쓴다(V3-8). §1.3.1a의 그림 속 절차가 인덱스에 들어갔음을 확인(`relink_chunks_v4.md`, `retrieval_replay_bgem3_v4.md`).

---

## 3. 채점기 변경만의 효과 (재채점, API 비용 0)

- unified4 24셀(Qwen 포함): `rescore_v3_unified4.md`; long_context: `rescore_v3_longctx.md`; QGIS 파일럿: `rescore_v3_qgis_pilot.md`; 요약 `rescore_v3_summary.md`. v2 재구현은 저장값과 2,120/2,120 일치.
- Step Acc(v2→v3): Gemini no_rag 66.7→78.3, vanilla 75.0→81.7, full 72.5→84.2; Claude 85.0→87.5 / 84.2→87.5 / 85.0→87.5; GPT 50.8→65.0 / 60.0→70.8 / 69.2→81.7; long_context 59.2→72.5(여전히 Gemini 최저); QGIS no_rag 62.5→82.5, vanilla 62.5→82.5, full 57.5→87.5.
- 3모델 full vs vanilla_vector step_acc 방향: v2 2/3(Claude·GPT) → v3 2/3(Gemini·GPT, Claude 동률).
- Hall(v3, GT 보정 전) 3모델 18셀 분포 {0: 1, 0–5: 3, 5–10: 3, 10–20: 8, >20: 3}. GPT 30.8→1.7은 v2가 목표 값을 환각으로 세던 효과. 남은 환각('Similarity', 'Seismic_data', 'Save Attribute as')은 GT 누락으로 보이며 S6 대상.

---

## 4. 실행 전 게이트 결과

| 게이트 | 결과 | 파일 |
|---|---|---|
| 리플레이 MiniLM(구 인덱스) | 목표 절 적중 survey 6/9, 3d_viz 0/11, attribute 0/15, QGIS 2/5(페이지 기준) | retrieval_replay_minilm.md |
| 리플레이 bge-m3(chromadb_v3, KG 후순위) | survey 7/8, 3d_viz 0/13, attribute 7/12, QGIS 4/5; 앞 1,500자가 매뉴얼 본문 4/4 | retrieval_replay_bgem3.md |
| 작업 3: 3d_viz 0/13 원인 | 인덱스의 §1.3.1a 청크(p.46, 572자)에 절차 문장이 없음. pdfplumber p.46 텍스트 384자+이미지 1, p.47 53자+이미지 2; OCR 규칙 `MIN_TEXT_LENGTH=50` 미만만 OCR → 두 페이지 모두 제외되어 그림 속 절차가 인덱스에 없음. 목표 정의 오류가 아니라 KB 결손 | audit trail V3-3 |
| 라우팅 dry-run 개발 세트, v2 부분문자열, thinking off | 정답 워크플로우 7/16(survey 4/4, 3d_viz 3/4, attribute 0/8), 유지 10, none 5 | routing_dryrun_vision_think0.md |
| 같은 세트, thinking 기본값 | 7/16(attribute 0/8); 노드 선택이 같은 스텝 12/24 → rerank 실행 간 변동 큼; 보조비용 $6.81m vs $1.29m/스텝 → thinking off 채택 | routing_dryrun_vision_thinkdyn.md |
| **라우팅 dry-run 개발 세트, 임베딩 매처(동결 메커니즘), thinking off** | **정답 12/16**(survey 4/4, 3d_viz **2/4**, attribute **6/8**), 유지 13, none 3, 보조비용 $1.30m/스텝, 지연 10.6 s. 3d_viz s2가 정답→none으로 후퇴(불리한 변화 그대로 기록), attribute s5·s7은 d3_visualization/none | routing_dryrun_vision_dev_embed.md |
| 스모크(Gemini × 7 백엔드 × survey_setup 1회, 임베딩 매처 이전) | 빈 응답 0/28, judge 정상, 텔레메트리·aux·thinking 필드 기록, rerank 스텝당 1회. 스모크 값은 표에 쓰지 않음 | run_gemini_v3smoke_r1_20260917T093224.json |
| QGIS 테스트 세트 | v3에서 미실행(동결 전 실행 금지 준수) | — |

---

## 5. 사전 예측 (결과 관측 전, 양방향)

| # | 예측 | 임계 | 반증되면 |
|---|---|---|---|
| P1 | bge-m3로 vanilla_vector가 no_rag보다 step_acc가 높다(개발 세트·QGIS 모두) | 3모델 중 2 이상에서 +3pp 이상 | 파라메트릭 마스킹이 임베더 개선 후에도 유지됨을 보고 |
| P2 | 보조 호출 포함 총비용에서 full_system은 vanilla_vector보다 저렴하지 않을 수 있다 | — | 비용 우위 철회, "예산 효과"로 서술 |
| P3 | full_system − vanilla_budget(같은 예산)의 step_acc 차이가 라우팅 순효과; 개발 세트 매크로에서 +0 이상 | 3모델 중 2 이상 | 라우팅 효과 없음으로 보고 |
| P4 | attribute 라우팅은 개발 세트 dry-run 6/8 수준(≥ 5/8)을 벤치에서도 유지 | — | dry-run–벤치 괴리 재기록(관측 #2 재현) |
| **P5 (QGIS, 테스트 세트, 방해 워크플로우 41노드 포함)** | (a) 정답 워크플로우(qgis_vector_buffer) 선택률 ≥ 5/8 스텝(모델 공통, vision·rerank는 모델 무관), (b) fallback+none 비율 ≤ 3/8, (c) full_system ≥ vanilla_budget step_acc 방향이 3모델 중 2 이상, (d) vanilla_vector > no_rag(P1) | 명시 | (a)(b) 반증 시 메커니즘을 고치지 않고 일반화 실패로 보고; (c) 반증 시 §6.5 |
| P6 | 3d_viz 시나리오는 KB 결손(§4) 때문에 vanilla·full 모두 매뉴얼 근거 없이 파라메트릭 지식으로 답한다: no_rag ≈ vanilla ≈ full (±5pp) | — | — |
| P7 | GeoLens가 열세일 수 있는 축: hall(v3에서 Claude vanilla 우세), step_acc(Gemini·Claude 동률권) | — | §6.5대로 보고 |

---

## 6. 판정 기준 (실행 전 고정)

### 6.1 지표
- 1차: step_accuracy(v3), hallucination_rate(v3, S6 GT), goal_completion_rate(3-gate), cost_total_usd/step. faithfulness 보고만.
- hall 처리 규칙(작업 4): 현재 3모델 18셀 hall 분포가 0 근처가 아니므로 hall은 1차 지표로 유지한다. 단, S6 반영 후 unified4 재채점에서 18셀의 중앙값이 5% 미만이면 hall은 판정 조건에서 제외하고 기술 지표로만 보고한다(규칙은 S6 결과를 보기 전인 지금 고정).
- 2차: loop_rate, latency, fallback_rate, 라우팅 텔레메트리(정답 워크플로우 선택률), cost_usd(생성기만), LLM judge 일치도(consensus judge vs v3 step_match의 agreement와 Cohen's κ; unified4 참고값 80.3% / 0.572).
- 집계: 스텝 → 시나리오 → replicate → 셀(mean ± 표본 SD). 검정 단위 replicate. **n = 10**.

### 6.2 비교
- 주 비교 A: full_system vs vanilla_budget(같은 예산, 라우팅 효과). 주 비교 B: full_system vs vanilla_vector. 보조: vs no_rag, graph_only, vision_only, state_path, long_context(Gemini).
- 개발 세트(3 시나리오 매크로)와 테스트 세트(QGIS)를 별도 표로 보고하고, **라우팅 관련 판정(P5, 라우팅 효과 주장)은 테스트 세트 기준**으로 한다.

### 6.3 1차 검정과 스토리 판정 (|M| = 3)
- 1차 검정: 모델을 층으로 하는 층화 순열검정(`scripts/stats_stratified.py`): 모델별로 A/B 라벨을 그 모델의 2n replicate 안에서 섞고, 통계량 = 모델별 (mean_A − mean_B)의 평균, 10,000회, seed 42, 양측. 모델별 raw 순열 p와 패밀리(5 pairs × 5 metrics = 25) Holm 보정값 병기.
- **A (시스템 우위)**: step_accuracy에서 full_system > vanilla_budget 방향이 3/3, 또는 2/3이면서 층화검정 p < 0.05; 그리고 hall에서 full ≤ vanilla_budget 방향이 2/3 이상(hall이 §6.1 규칙으로 제외되면 이 조건 생략). cost_total은 조건이 아니라 함께 보고(P2).
- **A′**: step_acc 조건만 성립.
- **B (조건부)**: 방향 2/3이나 층화 p ≥ 0.05, 또는 모델 의존 역전.
- **C (비등/열세)**: 방향 ≤ 1/3.
- 방향 카운트 규칙: 3/3 일관, 2/3 다수, ≤1/3 역효과. 동률(차이 0)은 카운트하지 않는다.

### 6.4 정지 규칙
- v4 없음. 결과가 어떻게 나오든 이 기준으로 A/A′/B/C를 판정해 그대로 보고한다. 실행 중 장애로 재실행할 때는 사유를 로그와 audit trail에 남긴다.

### 6.5 열세 시 보고
- Table 1에 vanilla_budget을 권장 구성으로 표시; full − vanilla_budget을 축별 부호 그대로 보고; 총비용에서 보조 호출 몫을 분해; 제목·초록의 "우위"를 "조건부"로; 재실행·시나리오 교체·채점기 재조정 금지.
- 귀속: 채점기 효과는 §3 재채점, GT 보정 효과는 S6 재채점으로 귀속. 임베더·예산·하네스·보조비용·매처 교체는 한 번에 바뀌므로 "v3 전체의 변화"로만 서술. unified4 비용 열과 v3 비용 열은 회계가 달라 직접 비교하지 않는다.

---

## 7. 실행 계획
- 래퍼 `bash scripts/run_v3.sh` (CHROMADB_PATH=./data/chromadb_v3, EMBED_MODEL=BAAI/bge-m3, GEOLENS_SCORER=v3, RAG_KG_POSITION=last, ROUTER_MATCHER=embedding, AUX_THINKING_BUDGET=0, GEN_TEMPERATURE=0.2, GEN_MAX_TOKENS=1024, GEMINI_THINKING_BUDGET=1024, VANILLA_BUDGET_CHARS=3900, BENCH_MODELS=gemini,claude,gpt).
- 매트릭스: 3 모델 × 7 백엔드 × 3 개발 시나리오 × 10회 + Gemini long_context × 10회 + QGIS 3 모델 × 7 백엔드 × 10회.
- 예상: 실행 1회 ≈ 30분 → 30회 ≈ 15시간 순차(공급자 병렬 시 ≈ 5시간) + long_context ≈ 50분 + QGIS ≈ 2시간. API ≈ $95 (flat rate; long_context $62 포함; Gemini >200K 티어 실과금 시 최대 약 $155).
- 서명 후 순서: 코드·사전등록 커밋 + 태그 → run_v3.sh → 집계(build_final_table, compute_table1_sd, stats_stratified, stats_unified, direction_consistency, per_scenario_breakdown, output_token_analysis) → audit trail 기록.

## 8. 한계 (명시)
- 시나리오·GT·워크플로우가 단일 저자 작업(held-out 저작자 확보 전까지).
- 테스트 세트가 시나리오 1개·8스텝(QGIS)이라 라우팅 일반화 판정의 검정력이 낮다.
- 3d_visualization은 KB 결손으로 매뉴얼 근거 검색이 구조적으로 불가(P6).
- 매뉴얼이 공개 문서라 파라메트릭 마스킹이 hybrid 이득을 압축한다(unified3 관측 #1 유지).

## 9. 서명
- 작성: `[사용자 결정]` / 검토: `[사용자 결정]` / 확정 시각(UTC): `[사용자 결정]`
- 서명 후 첫 벤치 실행 시각을 아래에 append한다.


---

## 2.5 개발 이력 요약 (v3 개발 루프, 2026-09-18; 상세 methodology_audit_trail.md V3-8 … V3-16)

개발 세트 = OpendTect 3 시나리오(16스텝). 테스트 세트(QGIS)는 동결 전까지 실행하지 않았다(dry-run 포함). 개발 판단의 1차 근거는 step accuracy가 아니라 (a) 라우팅 정답률·confident-wrong 건수, (b) 목표 절 검색 적중, (c) 스텝별 손실 분류였다. 모든 실행 결과 JSON에 코드 커밋 해시가 기록된다(iteration 0·1은 사후 표기).

| iteration | 코드 | 주요 변경 | 라우팅 정답(16스텝) | confident-wrong | 목표 절 적중 full / vanilla | 비고 |
|---|---|---|---|---|---|---|
| 0 (v2mech knob) | c15259f(사후) | 동결 시점 메커니즘 재현 + v4 KB + linked_chunks 재연결 | 11/14 통과 | 3 | 15/16 / 12/16 | 3d_viz s3·attribute s1 전 백엔드 실패; 지연 오염 가능 |
| 1 (v3) | c15259f | 임베딩 풀 5 + CLIP + 그래프 prior, vision/rerank 프롬프트 v3, 병렬 검색, fallback 예산 3,900, soft post-completion, KG 제외 | 16/16 | 0 | 16/16 / 12/16 | 손실 1 (3d_viz s3, 패턴 기인) |
| 2 (dry-run ×3) | f3ee78a | 종료 상태 블록, CLIP‖vision, 텔레메트리, 코드 해시 기록 | 16, 14, 16 | attribute s0·s1 → 04 (1회) | — | 벤치 미실행(사용자 규칙) |
| 3 (dry-run ×5) | 820e993 | seismic_attribute 02·03·04 signature 관찰 상태 재작성, vision field_values, 근소차 prior, 종료 상태 앵커 | 14, 14, 14, 14, 13 | attribute s0 5/5 (04·03), s1 5/5 (04), survey s3 1/5 | — | 일관된 편향 → 다수결 미사용; rerank 기준 불일치 가설 확인 |
| 4 (dry-run ×5) | d064577 → 21f0dec | rerank 프롬프트 v4(상태 일치 기준), 같은 다이얼로그 묶음 그래프 순서 prior(워크플로우 내), 03·04 비기본 상태 요구 | 첫 run 16,16,15,15,15 → 정정 후 **16/16 ×5** | 0 (정정 후) | — | 첫 run의 survey s3 오라우팅 3건은 묶음 범위 버그(교차 워크플로우) |
| 4 개발 벤치 | 21f0dec | Gemini ×2, Claude ×1, GPT ×1 (단독 실행) | 64/64 | 0 | 16/16 / 12/16 | 아래 표 |
| 5 (조립 v4, 마지막 개발 변경) | fcfa184 / 34c06aa | [Current State (reached)] = signature 상태만, [Next Action] = 엣지 지시, 예시 값 주의 문구 | dry-run 16/16 ×5; 벤치 64/64 | 0 | 16/16 / 12/16 | Gemini 2회 full 0.854 = vv 0.854 > vb 0.750; Claude 1.000 > 0.875 = 0.875; GPT 0.792 < vv 0.833, > vb 0.667. attribute s1~s3 손실 5건 → 0; 신규 손실 2(GPT attribute s7·survey s1: verification 엣지·노드 단위 라우팅 오차가 [Next Action]으로 드러남, 미수정) |
| 6 (조립 v5: verification 엣지 제외 + [This Step]) — **미채택** | d326838 (branch v3-iter2, 미병합) | 규칙 1·2 | dry-run 16/16 ×5; 벤치 라우팅 61/64(V3-22 정정; v4는 64/64) | 0 | — | full 0.875/1.000/0.833 vs vv 0.792/0.875/0.750, vb 0.792/0.875/0.667(세 모델 우위)이나 기준 (b)(d) 미충족(Gemini attribute s1 'Seismic_data 드롭다운', GPT survey s3 교차 워크플로우 오라우팅) → iteration 5로 되돌림 |

개발 벤치 4건 step accuracy(시나리오 평균): full / vanilla_vector / vanilla_budget / no_rag — Gemini(2회) 0.792 / 0.771 / 0.771 / 0.708, Claude 0.875 / 0.875 / 0.875 / 0.875, GPT 0.833 / 0.833 / 0.667 / 0.750. 방향: Gemini full > 두 vanilla; Claude 동률; GPT vanilla_vector 동률·vanilla_budget 우위. n = 1~2라 잡음 범위이며 판정에 쓰지 않는다. full_system 손실 12건 = 라우팅 0 · 컨텍스트 0 · 생성 9 · 표기 3.

채택하지 않은 것(근거와 함께):
- **rerank confidence 게이트**: iteration 0에서 오라우팅 3건의 confidence(0.7, 0.9, 0.9)가 정답 분포와 겹쳐 0.95 미만 어떤 임계값도 오라우팅만 걸러내지 못했다(`dev_iter0_v2mech_gemini.md` 보정표). confidence는 기록만 한다.
- **증거 기반 gate**((i) expected_dialog ⊂ 창 제목, (ii) 직전 확정 노드/후속, (iii) 임베딩 1–2위 격차): 오프라인 표(`evidence_gate_offline_iter0.md`, `_iter1.md`)에서 iteration 0 오라우팅 3건 중 최대 1건만 걸러지고(02·03·04가 같은 expected_dialog), 전체 노드 풀에서는 iteration 1 정답 1건이 탈락 → 미채택(코드는 비활성).
- **2단계 라우팅(목표→워크플로우→노드)**: 보류. attribute s0·s1 재구성(`recon_iter1_attribute_s0s1.md`)과 진단(`diag_attribute_s0s1_iter3.md`)에서 문제가 같은 다이얼로그를 공유하는 노드 간 rerank 기준 불일치임이 확인되어 프롬프트 v4·signature 정정으로 대응.
- **다수결 rerank**: iteration 3의 오답이 회차마다 같은 방향이라 규칙상 미사용(코드는 `RERANK_VOTES=1`).
- **종료 상태 블록의 좁힌 발동 조건**: 개발 벤치 4건의 조기 발동 8건에서 조기 '완료' 응답이 0건이라 규칙상 적용하지 않음(오프라인 검사 스크립트만 보관).

GT 검수(2026-09-18): 스크린샷만 본 별도 세션이 고정 규칙(RULES.md)으로 수행 — 실행 로그·모델 응답·채점 결과 접근 없이 24장, 검수 목록, 시나리오, 매뉴얼 발췌만 제공. 표본 오독률 0.96%(< 5%), 변경 19·보류 11, survey s0 Add 버튼 패턴은 보류(매뉴얼 표기 "New Survey icon"), QGIS s3는 Input layer가 이미 채워진 화면 상태에 맞춰 GT 필드만 정정(패턴에 `Distance|50|Dissolve` 추가). 구·신 GT 재채점: step accuracy 변화 0, 환각률 −6.2 pp(라벨 원문화), survey s0에서 `New Survey (+)` 표기로 "Add (+)" 응답이 환각으로 잡히는 부작용 33건(사용자 결정 대기). 상세 `data/eval/gt_review_session/`, V3-16.

## 5.x QGIS 예측에 덧붙이는 위험 (동결 전 기재)
- QGIS 워크플로우는 노드 5개가 8스텝을 다루므로(노드 03·04·05가 여러 스텝 담당) attribute 06_display에서 본 것과 같은 **종료 상태 블록 조기 발동**이 일어날 수 있다(말단 노드 05_run_and_render가 확정된 뒤 렌더 전 화면에서도 발동). 개발 벤치에서는 조기 발동 8건 모두 생성기가 스크린샷을 보고 다음 동작을 냈고 조기 '완료'는 0건이었으나, QGIS에서는 보장하지 않는다. QGIS는 실행하지 않은 상태에서 적는다.
- 같은 이유로 QGIS 라우팅 정답률 예측은 "워크플로우 단위 정답 ≥ 개발 세트 수준"으로 두되, 노드 단위(스텝별 expected_workflow_node)는 다단계 노드 경계에서 낮아질 수 있음을 예측에 포함한다.

## 8.x 한계 (개발 루프에서 드러난 것, 수치)
- **같은 다이얼로그를 공유하는 노드의 구별은 signature와 rerank 기준의 정합에 의존한다.** seismic_attribute 02·03·04는 모두 "Attribute Set 3D" 창이며, 2026-08-07 signature가 실제 화면(열리자마자 기본값 채워짐)과 어긋난 채로 "다음에 하려는 단계" 기준의 rerank가 03/04로 일관되게 밀렸다(iteration 3: s0 5/5·s1 5/5 오답). iteration 4(상태 일치 기준 + 워크플로우 내 그래프 순서 prior + 비기본 상태 signature)에서 dry-run 5회·벤치 4건 모두 정답이었으나, 이는 OpendTect 개발 세트의 signature를 고친 결과이며 QGIS signature는 손대지 않았다.
- **3d_visualization 노드 단위 라우팅**: v4 상태 일치 기준에서 s2·s3 화면이 d3_01(main window ready)로 수렴한다(5회 dry-run 전부). 워크플로우 단위로는 정답이고 노드 GT가 없어 채점에는 영향이 없지만, 그 결과 3d_viz s3에서 종료 상태 블록이 발동하지 않는다.
- **종료 상태 블록 오발동**: 다단계 노드(attribute 06_display, 스텝 5–7)에서 rep당 2/4 발동이 조기(5회 dry-run 합계 10/20; 벤치 4건 8/8 조기 발동에서 조기 '완료' 0건).
- **step 3 sentinel 스텝**: 요소 언급 허용 대안 패턴(2026-08-06 재정의와 함께 의도적으로 추가, 사용자 결정으로 유지)이 sentinel 대신 요소 언급 지시도 정답으로 받아들이므로 이 스텝의 step accuracy는 목표 인식 능력을 직접 재지 않는다(3모델 full_system·vanilla_vector에는 제거 시 변화 없음, `pattern_impact_3dviz_s3.md`).
- **표기 손실**: survey s0의 텍스트 없는 아이콘 버튼("녹색 더하기/플러스 아이콘", "새로운 설문 아이콘")이 패턴(Survey|Create|New|Add)에 걸리지 않아 full_system이 4건 중 3건 실패(vanilla도 일부 실패). 규칙 3 보류로 패턴 불변.
- **생성 손실**: 정답 라우팅에서도 [Current Step] 설명이 화면과 다른 값("Input Data = 4 Dip steered median filter")을 단정하면 생성기가 그것을 고치려 한다(4건 5스텝). 컨텍스트 조립 수정안(도달 상태·다음 동작 분리)은 제시만 하고 미적용(V3-15).
- **지연**: full_system은 vanilla 대비 스텝당 약 +10~15 s(clean run: vision 4.5 + CLIP 4.0 + 임베딩 3.2 + rerank 1.3; CLIP은 iteration 2부터 vision과 병렬). 최종 표의 지연은 별도 clean run의 단계 분해로 보고한다.
- **조립 v4의 노출 효과**: [Next Action]이 엣지 지시만 주므로 verification 노드로 가는 엣지(attribute 06→07 "QC 하세요")가 sentinel 대신 제시될 수 있고, 노드 단위 라우팅 오차(survey s1을 03으로)가 다음 동작 오류로 직결된다(GPT 2건). 개발 종료 시점의 알려진 한계로, 수정하지 않았다.
- **n = 1~2 개발 벤치의 step accuracy 차이는 잡음 범위**이며 확인적 판정은 QGIS 테스트 세트(n = 10, 3모델)에서만 한다.


## 2.6 GT 확정 절차와 채점 관련 기록 (2026-09-18, 동결 전)
- GT 검수: 모델 응답을 보지 않은 별도 세션이 고정 규칙으로 수행(스크린샷 24장·검수 목록·시나리오·매뉴얼 발췌만 제공). 외부 검토(스크린샷 대조)에서 변경 19건 중 18건 확인, 1건(QGIS s3 keywords 추가) 되돌림, 보류 11건 결정. 수치 표기는 별도 세션의 3배 확대 대조(33건 중 14건 수정, 사용자 명시 수정과 일치). 적용 커밋 2f3db66. 구·신 GT 재채점: step accuracy 변화 0, 환각률 대부분 −6.2 pp(라벨 원문화). 이 시점 이후 GT와 채점기는 서명 전까지 변경하지 않는다.
- QGIS s3 GT 정정(Input layer가 이미 채워진 화면 상태 반영, 패턴에 Distance|50|Dissolve 추가)의 근거는 화면 사실이며, 화면을 읽는 백엔드(full_system·vision_only·state_path)에 유리할 수 있다 — 확인적 판정 해석 시 명시한다.
- QGIS s3와 s4는 화면이 같으므로(Input layer 자동 채움) 같은 정답 응답이 s4에서 loop(직전 응답과 동일)로 집계될 수 있다. loop는 판정 지표가 아니다.
- 3d_viz step_3의 허용 대안 패턴(요소 언급)은 sentinel이 아닌 지시도 정답으로 통과시킬 수 있다(한계, 사용자 결정으로 유지).
