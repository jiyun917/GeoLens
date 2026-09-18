# v3 재실행 사전등록 (최종안 — 서명 전)

**작성 시점**: 2026-09-18, 0단계(수정·재채점·dry-run·스모크) 완료, 메커니즘 동결 커밋 직후(초안 v2). v3 벤치 숫자는 아직 하나도 없음.
**최종화 시점**: 2026-09-18 (KST), 개발 루프 종료 후. 동결 태그 `v3-freeze-c01fdda` @ a03ca59 — 코드(`api/`, `data/workflows/`)는 c01fdda, GT(`data/eval/scenarios/`)는 2f3db66과 동일(§2.5). QGIS 테스트 세트는 dry-run 포함 한 번도 실행하지 않았다. v3 확인적 벤치(run_v3.sh) 숫자는 없다; 개발 세트의 개발 벤치 수치는 §2.5에 있다.
**외부 검토 반영**: 2026-09-18, 문서만 수정(코드·GT·워크플로우 불변): §6.1 hall 규칙 결과대로 hall 판정 지표 유지·A′ 복원, 비교 1/2 명명과 판정 조건 문구, held-out 삭제, QGIS 파일럿 이력 한계, P8, D8 수치 실측, 절 구조 정리.
**상태**: **서명됨** (2026-09-18T08:09:04Z, 커밋 = 태그 `v3-prereg-signed`; 승인 대상 최종안 2c85e22). 이후 이 문서는 add-only(§9 아래 실행 기록만 append).
**원칙**: (1) 모든 수정은 실행 전에 확정한다. (2) 수정은 모든 백엔드·모델에 같이 적용한다. (3) 판정 기준을 먼저 고정한다. (4) 시스템 쪽 결함과 baseline 쪽 결함을 함께 고친다. (5) 결과 예상은 양방향으로 열어 두고, 불리한 결과도 그대로 보고한다.

---

## 0. 세트 구분과 이력

| 세트 | 시나리오 | 이력 | 역할 |
|---|---|---|---|
| 개발 세트 | opendtect__survey_setup__01, opendtect__3d_visualization__01 | unified2부터 사용. 라우팅 결함 진단·수정, 캡처 정제(3d_viz step 3, unified3)에 사용됨 | 라우팅 진단·메커니즘 수정은 여기서만 |
| 개발 세트 | opendtect__attribute_computation__01 | unified3에서 사전등록 예측과 함께 처음 실행(당시 테스트). unified4에서 seismic_attribute signature를 재작성한 뒤로는 개발용 | 위와 같음 |
| 테스트 세트 | qgis__vector_buffer__01 (8스텝) | 2026-08-13 파일럿 1회. 결과를 보고 시스템·signature를 고친 적 없음. v3에서는 메커니즘 동결 커밋 이후에만 실행. **2026-09-18, QGIS 결과를 보기 전에 수행한 배포 설정**: QGIS 매뉴얼 v4 재인제스트(그림 OCR 규칙, bge-m3)와 `qgis_vector_buffer` 노드 5개의 linked_chunks 연결(절 출처 §6.2.6, OpendTect와 같은 규칙, 스크립트 15.8 s + 사람 약 5분; V3-11). signature·제목·설명·시나리오 파일 불변 | 라우팅 관련 판정의 기준 세트 |

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
| D8 | 임베더 MiniLM: 256 word-piece 절단, 영어 중심, 질의는 한국어. 실측(구 인덱스 `data/chromadb` 1,254청크, MiniLM 토크나이저, 저장된 문서 = `[Section: …, Page: …, Source: …]` 접두 약 76 피스 + 본문): 800토큰(tiktoken ≥ 700) 가득 찬 청크 114개는 MiniLM 피스 중앙값 OpendTect 952·QGIS 847 → 256 피스는 앞 27–30%(본문은 약 180 피스); 페이지 경계로 짧은 청크가 많아 554/1,254는 256 이내(OpendTect 190/521, QGIS 364/733). 초안 v2의 "앞 ~10%"는 오기 | vanilla 검색 실패(attribute 0/15, 3d_viz 0/11, QGIS 2/5) → baseline 과소 | retrieval_replay_minilm.md |
| D9 | 생성 설정 불일치(max_tokens 512/1024/미설정, temperature Qwen만 0.2) | 모델 간 비교 오염 | bench_backends v2 |
| D10 | QGIS 파일럿이 OpendTect 워크플로우를 격리한 채 실행 | 라우팅 난이도 과소 | run_qgis_pilot v2 |
| D11 | graph_only 청크 본문 미주입, state_path 텔레메트리 미기록, rerank 'none'이 fallback으로 라벨되지 않음 | ablation 해석 오류 | v2 코드 |
| D12 | 라우팅 후보 단계가 signature 문자열의 부분문자열 일치 비율이라 서술형 signature(seismic_attribute)는 후보 풀에 들어가지 못함 | attribute 0/8 (전부 후보 단계 탈락) | routing_diag_dev_v2.md |

Qwen 제외 사유: Qwen3-VL 서빙 불가(NAS 미접속), 텍스트 전용 Qwen은 입력 조건(스크린샷)을 맞출 수 없음. 따라서 |M| = 3 (Gemini 2.5 Pro, Claude Sonnet 4.6, GPT-4o).

---

## 2. 실행 전에 확정된 수정 (양쪽) — 메커니즘 동결 커밋 `bacfde7f` (branch v3-rerun, 2026-09-18 09:46 KST) → 개발 루프(§2.5) 후 최종 동결 c01fdda (태그 `v3-freeze-c01fdda` @ a03ca59, 2026-09-18 16:46 KST; 동결 구성은 G8)

### 2.1 채점·평가 (전 백엔드 동일)
| S1 | step_match: 패턴 `\b( … )\b` → ASCII 경계 (`GEOLENS_SCORER=v2`로 구 채점기 재현) |
|---|---|
| S2 | 환각 판정 v3: 따옴표 무관 라틴 라벨 구 추출(영어 기능어·명령 동사 제외); 근거 어휘 = visible_elements + current_dialog + active_menu + data_state + current_action + screen_state(느슨한 정규화 부분문자열); 목표 문장의 값은 제외 |
| S3 | 미폐쇄 `<think>` 제거(빈 응답 처리) |
| S4 | cost_total = 생성기(입력+출력+thinking) + 보조(vision·rerank, 캐시 적중 포함). 판정 비용 = cost_total |
| S5 | faithfulness는 1−hall의 동어반복 → 판정에서 제외, 표에는 보고만 |
| S6 | GT visible_elements 전수 보정 절차(작업 5): 24장 전부에 같은 절차 — gemini-2.5-pro, temperature 0, 고정 프롬프트로 화면의 라벨·버튼·다이얼로그 제목·메뉴·트리 항목을 전부 열거(`scripts/gt_enumerate_visible_elements.py`), 모델 응답 로그는 참조하지 않음. 현 GT와의 diff를 `gt_visible_elements_review_v3.md`로 만들고 사용자가 검수한 뒤 반영. 반영 후 unified4 로그를 구·신 GT로 재채점해 백엔드별 변화량을 §4에 추가 (완료: 검수 V3-16, 외부 검토·확정 V3-18, 커밋 2f3db66, §2.6). survey_setup s0는 'New Survey (+)'와 'Add (+)' 병기, QGIS s3는 Input layer가 자동 채워진 화면 상태에 맞춰 GT 필드만 정정 |

### 2.2 baseline 측
| B1 | 임베더 BAAI/bge-m3(8,192토큰, 1,024-d, 정규화), 같은 청크 id로 재임베딩한 `data/chromadb_v3` (OpendTect 521, QGIS 733청크) → 개발 루프 전에 그림 면적 OCR 규칙으로 양쪽 매뉴얼을 재인제스트한 `data/chromadb_v4`로 대체(G7, V3-8; run_v3.sh `CHROMADB_PATH=./data/chromadb_v4`) |
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
| G8 | **동결 구성(c01fdda, 개발 루프 iteration 1~5의 결과; V3-9 … V3-20)**: 후보 풀 = bge-m3 임베딩 top-5 ∪ CLIP top-3 ∪ 직전 확정 노드의 그래프 후속(`ROUTER_MATCHER=embedding`, `ROUTER_POOL_K=5`, `ROUTER_GRAPH_PRIOR=1`); vision 프롬프트 v3(창 제목·메뉴·버튼·라벨 원문 + field_values); rerank 프롬프트 v4(도달 상태 일치 기준) + 같은 expected_dialog 묶음의 워크플로우 내 그래프 순서 prior(`ROUTER_TIE_PRIOR=1`, `ROUTER_GROUP_PRIOR=1`); rerank 프롬프트는 세션의 직전 생성기 응답(최근 6개)을 'Instructions already given' 블록으로 포함(iteration 1부터; §5.x (iv)); 종료 상태 블록(`GOAL_STATE_HINT=1`, margin 0.02); 병렬 검색(`PARALLEL_RETRIEVAL=1`, 목표 질의 벡터 검색 + CLIP을 vision과 병렬); 컨텍스트 = 그래프 3×800자 + 벡터 1,500자, fallback 3,900자, KG 제외(`RAG_KG_ENABLED=0`); soft post-completion; 컨텍스트 조립 v4([Current State (reached)] = signature 상태, [Next Action] = 엣지 지시, 예시 값 주의 문구); 생성 프롬프트 v2; 비활성: 2단계 라우팅·증거 gate·다수결(`ROUTER_TWO_STAGE=0`, `ROUTER_EVIDENCE_GATE=0`, `RERANK_VOTES=1`); confidence 0.7은 기록만. 워크플로우 JSON: 개발 세트에 한해 seismic_attribute 02·03·04의 visual_signature를 실제 화면의 도달 상태(03 = 유형이 Energy로 바뀐 비기본 상태, 04 = Attribute Name 채워진 상태)로 재작성(iteration 3·4, V3-14; 이전 signature는 `signature_audit`에 보존). QGIS signature 불변. 채택하지 않은 iteration 6(조립 v5)은 §2.5 |

### 2.4 변경하지 않는 것 / 금지
- 시나리오 4개, 스크린샷 24장, 목표 문장, 워크플로우 JSON 7개의 모든 visual_signature·제목·설명(QGIS 포함). 개별 signature를 스크린샷에 맞춰 고치지 않는다. (v3가 워크플로우 JSON에서 바꾼 것: 전 노드의 `linked_chunks`·`manual_sections`·`linked_chunks_provenance`(V3-9/V3-11)와, 개발 세트에 한해 seismic_attribute 02·03·04의 visual_signature(iteration 3·4, V3-14; §2.3 G8). QGIS 워크플로우의 signature·제목·설명은 불변.)
- 사전등록 서명 전 벤치 실행 금지(dry-run·스모크만). QGIS는 동결 커밋 전 dry-run 포함 실행 금지(준수: v3에서 QGIS 미실행). 동결 후 QGIS 결과를 보고 메커니즘을 다시 고치지 않는다.
- 결과를 본 뒤 판정 기준·채점 규칙을 바꾸지 않는다. v4(개발 재개) 없음. 동결 이후 QGIS 결과를 보고 메커니즘·조립·signature·GT·채점기를 고치지 않는다.
- 모든 변경은 `methodology_audit_trail.md`에 append (§V3-*).
- 3d_visualization의 목표 절 결손(§4 작업 3)은 KB(OCR 임계) 문제였고, 사용자 결정(2026-09-18)으로 양쪽 매뉴얼을 같은 그림 면적 OCR 규칙으로 재인제스트한 `chromadb_v4`를 쓴다(V3-8). §1.3.1a의 그림 속 절차가 인덱스에 들어갔음을 확인(`relink_chunks_v4.md`, `retrieval_replay_bgem3_v4.md`).

### 2.5 개발 이력 요약 (v3 개발 루프, 2026-09-18; 상세 methodology_audit_trail.md V3-8 … V3-23)

개발 세트 = OpendTect 3 시나리오(16스텝). 테스트 세트(QGIS)는 동결 전까지 실행하지 않았다(dry-run 포함). 개발 판단의 1차 근거는 step accuracy가 아니라 (a) 라우팅 정답률·confident-wrong 건수, (b) 목표 절 검색 적중, (c) 스텝별 손실 분류였다. 모든 실행 결과 JSON에 코드 커밋 해시가 기록된다(iteration 0·1은 사후 표기).

| iteration | 코드 | 주요 변경 | 라우팅 정답(16스텝) | confident-wrong | 목표 절 적중 full / vanilla | 비고 |
|---|---|---|---|---|---|---|
| 0 (v2mech knob) | c15259f(사후) | 동결 시점 메커니즘 재현 + v4 KB + linked_chunks 재연결 | 11/14 통과 | 3 | 15/16 / 12/16 | 3d_viz s3·attribute s1 전 백엔드 실패; 지연 오염 가능 |
| 1 (v3) | c15259f | 임베딩 풀 5 + CLIP + 그래프 prior, vision/rerank 프롬프트 v3, 병렬 검색, fallback 예산 3,900, soft post-completion, KG 제외 | 16/16 | 0 | 16/16 / 12/16 | 손실 1 (3d_viz s3, 패턴 기인) |
| 2 (dry-run ×3) | f3ee78a | 종료 상태 블록, CLIP‖vision, 텔레메트리, 코드 해시 기록 | 16, 14, 16 | attribute s0·s1 → 04 (1회) | — | 벤치 미실행(사용자 규칙) |
| 3 (dry-run ×5) | 820e993 | seismic_attribute 02·03·04 signature 관찰 상태 재작성, vision field_values, 근소차 prior, 종료 상태 앵커 | 14, 14, 14, 14, 13 | attribute s0 5/5 (04·03), s1 5/5 (04), survey s3 1/5 | — | 일관된 편향 → 다수결 미사용; rerank 기준 불일치 가설 확인 |
| 4 (dry-run ×5) | d064577 → 21f0dec | rerank 프롬프트 v4(상태 일치 기준), 같은 다이얼로그 묶음 그래프 순서 prior(워크플로우 내), 03·04 비기본 상태 요구 | 첫 run 16,16,15,15,15 → 정정 후 **16/16 ×5** | 0 (정정 후) | — | 첫 run의 survey s3 오라우팅 3건은 묶음 범위 버그(교차 워크플로우) |
| 4 개발 벤치 (조립 v3) | 21f0dec | Gemini ×2, Claude ×1, GPT ×1 (단독 실행) | 62/64 (최종화 시 재집계, dry-run과 같은 규칙: Gemini r0 attribute s2→03, survey s3→d3_01, 둘 다 응답은 정답; 보고서의 '라우팅 손실 0'은 손실만 센 값) | 0 | 16/16 / 12/16 | 아래 표 |
| 5 (조립 v4 — **동결 구성**) | fcfa184 / 34c06aa | [Current State (reached)] = signature 상태만, [Next Action] = 엣지 지시, 예시 값 주의 문구 | dry-run 16/16 ×5; 벤치 64/64(재집계 확인) | 0 | 16/16 / 12/16 | Gemini 2회 full 0.854 = vv 0.854 > vb 0.750; Claude 1.000 > 0.875 = 0.875; GPT 0.792 < vv 0.833, > vb 0.667. attribute s1~s3 손실 5건 → 0; 신규 손실 2(GPT attribute s7·survey s1: verification 엣지·노드 단위 라우팅 오차가 [Next Action]으로 드러남, 미수정) |
| 6 (조립 v5: verification 엣지 제외 + [This Step]) — **미채택** | d326838 (branch v3-iter2, 미병합) | 규칙 1·2 | dry-run 16/16 ×5; 벤치 라우팅 61/64(V3-22 정정; v4는 64/64) | 0 | — | full 0.875/1.000/0.833 vs vv 0.792/0.875/0.750, vb 0.792/0.875/0.667(세 모델 우위)이나 기준 (b)(d) 미충족(Gemini attribute s1 'Seismic_data 드롭다운', GPT survey s3 교차 워크플로우 오라우팅) → iteration 5로 되돌림 |
| 6 채택 검토 → 동결 | — | 사용자가 v5 채택을 결정했으나 조건부(rerank 입력이 v4/v5에서 동일할 것). 확인(V3-22): 라우팅 코드는 동일하지만 rerank 프롬프트의 세션 블록(직전 생성기 응답)이 조립에 따라 달라짐 → 채택 중단. 사용자 결정으로 **c01fdda(조립 v4) 동결**, rerank 재생 실험 없음(V3-23) | — | — | — | 태그 `v3-freeze-c01fdda` @ a03ca59 |

iteration 4 개발 벤치 4건 step accuracy(시나리오 평균): full / vanilla_vector / vanilla_budget / no_rag — Gemini(2회) 0.792 / 0.771 / 0.771 / 0.708, Claude 0.875 / 0.875 / 0.875 / 0.875, GPT 0.833 / 0.833 / 0.667 / 0.750. 방향: Gemini full > 두 vanilla; Claude 동률; GPT vanilla_vector 동률·vanilla_budget 우위. n = 1~2라 잡음 범위이며 판정에 쓰지 않는다. full_system 손실 12건 = 라우팅 0 · 컨텍스트 0 · 생성 9 · 표기 3.

**벤치 모드 라우팅 안정성(개발 세트 16스텝 × 4회; expected_workflow_node가 있는 8스텝은 노드, 나머지는 워크플로우 일치; dry-run 수치는 세션 블록이 없어 쓰지 않음)**:

| 구성 | 코드 | 라우팅 정답 | 오라우팅 |
|---|---|---|---|
| 조립 v3 (iteration 4) | 21f0dec | 62/64 | Gemini r0: attribute s2→03, survey s3→d3_01 |
| **조립 v4 (iteration 5, 동결)** | fcfa184/34c06aa | **64/64** | — |
| 조립 v5 (iteration 6, 미채택) | d326838 | 61/64 | Claude attribute s2→03; Gemini r1 survey s3→d3_01; GPT survey s3→d3_01(손실) |

세 구성의 라우팅 코드는 같고 조립(→ 직전 응답 → rerank 세션 블록)만 다르다. 동결 구성의 64/64는 4회 관측이며 라우팅이 100% 안정적이라는 근거는 아니다.

채택하지 않은 것(근거와 함께):
- **rerank confidence 게이트**: iteration 0에서 오라우팅 3건의 confidence(0.7, 0.9, 0.9)가 정답 분포와 겹쳐 0.95 미만 어떤 임계값도 오라우팅만 걸러내지 못했다(`dev_iter0_v2mech_gemini.md` 보정표). confidence는 기록만 한다.
- **증거 기반 gate**((i) expected_dialog ⊂ 창 제목, (ii) 직전 확정 노드/후속, (iii) 임베딩 1–2위 격차): 오프라인 표(`evidence_gate_offline_iter0.md`, `_iter1.md`)에서 iteration 0 오라우팅 3건 중 최대 1건만 걸러지고(02·03·04가 같은 expected_dialog), 전체 노드 풀에서는 iteration 1 정답 1건이 탈락 → 미채택(코드는 비활성).
- **2단계 라우팅(목표→워크플로우→노드)**: 보류. attribute s0·s1 재구성(`recon_iter1_attribute_s0s1.md`)과 진단(`diag_attribute_s0s1_iter3.md`)에서 문제가 같은 다이얼로그를 공유하는 노드 간 rerank 기준 불일치임이 확인되어 프롬프트 v4·signature 정정으로 대응.
- **다수결 rerank**: iteration 3의 오답이 회차마다 같은 방향이라 규칙상 미사용(코드는 `RERANK_VOTES=1`).
- **종료 상태 블록의 좁힌 발동 조건**: 개발 벤치 4건의 조기 발동 8건에서 조기 '완료' 응답이 0건이라 규칙상 적용하지 않음(오프라인 검사 스크립트만 보관).

GT 검수(2026-09-18): 스크린샷만 본 별도 세션이 고정 규칙(RULES.md)으로 수행 — 실행 로그·모델 응답·채점 결과 접근 없이 24장, 검수 목록, 시나리오, 매뉴얼 발췌만 제공. 표본 오독률 0.96%(< 5%), 변경 19·보류 11, survey s0 Add 버튼 패턴은 보류(매뉴얼 표기 "New Survey icon"), QGIS s3는 Input layer가 이미 채워진 화면 상태에 맞춰 GT 필드만 정정(패턴에 `Distance|50|Dissolve` 추가). 구·신 GT 재채점: step accuracy 변화 0, 환각률 −6.2 pp(라벨 원문화), survey s0에서 `New Survey (+)` 표기로 "Add (+)" 응답이 환각으로 잡히는 부작용 33건 → 사용자 결정으로 두 표기 병기(2f3db66). 상세 `data/eval/gt_review_session/`, V3-16.

### 2.6 GT 확정 절차와 채점 관련 기록 (2026-09-18, 동결 전)
- GT 검수: 모델 응답을 보지 않은 별도 세션이 고정 규칙으로 수행(스크린샷 24장·검수 목록·시나리오·매뉴얼 발췌만 제공). 외부 검토(스크린샷 대조)에서 변경 19건 중 18건 확인, 1건(QGIS s3 keywords 추가) 되돌림, 보류 11건 결정. 수치 표기는 별도 세션의 3배 확대 대조(33건 중 14건 수정, 사용자 명시 수정과 일치). 적용 커밋 2f3db66. 구·신 GT 재채점: step accuracy 변화 0, 환각률 대부분 −6.2 pp(라벨 원문화). 이 시점 이후 GT와 채점기는 서명 전까지 변경하지 않는다.
- QGIS s3 GT 정정(Input layer가 이미 채워진 화면 상태 반영, 패턴에 Distance|50|Dissolve 추가)의 근거는 화면 사실이며, 화면을 읽는 백엔드(full_system·vision_only·state_path)에 유리할 수 있다 — 확인적 판정 해석 시 명시한다.
- QGIS s3와 s4는 화면이 같으므로(Input layer 자동 채움) 같은 정답 응답이 s4에서 loop(직전 응답과 동일)로 집계될 수 있다. loop는 판정 지표가 아니다.
- 3d_viz step_3의 허용 대안 패턴(요소 언급)은 sentinel이 아닌 지시도 정답으로 통과시킬 수 있다(한계, 사용자 결정으로 유지).

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
| P8 | **QGIS에서 full_system 대 vanilla_vector(비교 2)의 step_acc 방향은 예측하지 않는다** — 개발 세트 iteration 5(동결 구성)에서 Gemini 동률(0.854 = 0.854)·Claude 우위(1.000 > 0.875)·GPT 열세(0.792 < 0.833)로 모델마다 달랐다 | — | 관측된 방향을 그대로 보고(§6.3 종합 서술) |

최종화 시점 주석(결과 관측 전): P4의 기준값은 개발 루프 후 벤치 모드 라우팅 64/64(동결 구성, §2.5)로 갱신하되 개발 세트이므로 판정에 쓰지 않는다. P5(a)의 "모델 공통" 가정은 근사다 — rerank 프롬프트가 직전 생성기 응답을 포함하므로 라우팅은 생성기에 완전히 독립이 아니다(§5.x (iv)); P5(a)는 모델별로 따로 집계해 보고한다. QGIS에 특유한 위험은 §5.x (i)–(v).

### 5.x QGIS 예측에 덧붙이는 위험 (동결 시점 기재, QGIS 미실행 상태)

QGIS 워크플로우는 노드 5개(01 setup, 02 action, 03 setup, 04 setup, 05 action; 검증 노드 없음, 05가 말단)가 8스텝을 다룬다: s0→01, s1·s2→02, s3·s4·s5→03, s6→04, s7→05. 동결 구성(조립 v4)에서 예측되는 위험:

- **(i) 여러 스텝에 걸친 노드에서 [Next Action]의 조기 제시**: 조립 v4의 [Next Action]은 현재 노드의 나가는 엣지 지시이므로, 노드 03에 머무는 s3·s4(Distance·Dissolve를 아직 설정하는 중)에서 03→04 "출력 저장" 동작을, 노드 02의 s1에서 02→03 동작을 일찍 제시할 수 있다. 개발 세트에서 같은 기제로 GPT survey s1·attribute s7 손실이 났고(V3-20), QGIS는 노드당 스텝이 더 많아 구조적으로 재현될 수 있다. 예측: 이 유형의 손실이 s1·s3·s4 중 적어도 한 스텝에서 모델 1개 이상에 나타난다.
- **(ii) 마지막 스텝(s7)에서 엣지 지시가 '완료'를 대체**: 05는 말단이라 라우팅이 05이면 v4는 "final step … completion sentinel" 문구를 준다. 그러나 s7 화면(렌더된 레이어)이 04로 라우팅되거나 05 확정 전이면 04→05 "Run" 엣지가 [Next Action]으로 제시되어 '완료' 응답을 놓칠 수 있다(개발 세트의 verification 엣지 제시와 같은 기제; QGIS에는 verification 노드가 없으므로 검증 엣지 자체는 없다).
- **(iii) 종료 상태 블록 조기 발동**: 말단 노드 05가 후보 pick이거나 확정된 뒤(s6 Save 다이얼로그, s7 이전 화면) 렌더 전 화면에서도 발동할 수 있다(attribute 06_display에서 본 것과 같음). 개발 벤치에서는 조기 발동 8건 모두 조기 '완료' 0건이었으나 QGIS에서는 보장하지 않는다.
- **(iv) 세션 블록을 통한 생성기→라우팅 결합**: rerank 프롬프트가 직전 생성기 응답을 포함하므로(iteration 1부터, V3-22) 같은 스크린샷에서도 생성기 모델에 따라 라우팅이 달라질 수 있다. QGIS 8스텝 중 s1–s7이 세션 블록을 가진다. 따라서 P5(a)는 모델별로 따로 집계하고, 라우팅 안정성은 벤치 모드 수치로만 서술한다(개발 세트: 조립 v3 62/64, v4 64/64, v5 61/64).
- **(v) s3·s4 화면 동일로 인한 loop 집계**: Input layer가 자동 채워져 s3와 s4 화면이 같으므로 같은 정답 응답이 s4에서 loop(직전 응답과 동일)로 집계될 수 있다. loop_rate는 판정 지표가 아니며 표에 이 사유를 주석으로 단다.
- 라우팅 정답률 예측은 "워크플로우 단위 정답 ≥ 5/8(P5(a))"로 두되, 노드 단위(스텝별 expected_workflow_node)는 다단계 노드 경계(s2, s4·s5, s7)에서 낮아질 수 있음을 예측에 포함한다.

---

## 6. 판정 기준 (실행 전 고정)

### 6.1 지표
- 1차(판정 지표): step_accuracy(v3 채점기, 최종 GT 2f3db66), hallucination_rate(v3, 최종 GT; 아래 규칙의 결과에 따라 유지). 기술 지표(표에 보고하되 판정 조건에 넣지 않음): goal_completion_rate(3-gate), cost_total_usd/step, latency(단계 분해). faithfulness 보고만.
- hall 처리 규칙(작업 4): 현재 3모델 18셀 hall 분포가 0 근처가 아니므로 hall은 1차 지표로 유지한다. 단, S6 반영 후 unified4 재채점에서 18셀의 중앙값이 5% 미만이면 hall은 판정 조건에서 제외하고 기술 지표로만 보고한다(규칙은 S6 결과를 보기 전인 지금 고정). **결과(최종화 시점)**: 최종 GT(2f3db66)로 unified4 3모델 18셀을 재채점한 hall 중앙값은 6.2%(≥ 5%; `rescore_gt_final_vs_fcfa184.md`)이므로 규칙대로 hall은 판정 지표로 유지한다.
- 2차: loop_rate, latency, fallback_rate, 라우팅 텔레메트리(정답 워크플로우 선택률), cost_usd(생성기만), LLM judge 일치도(consensus judge vs v3 step_match의 agreement와 Cohen's κ; unified4 참고값 80.3% / 0.572).
- 집계: 스텝 → 시나리오 → replicate → 셀(mean ± 표본 SD). 검정 단위 replicate. **n = 10**.

### 6.2 비교
- **판정은 QGIS 테스트 세트 기준**이다. 1차 비교 대상 두 개: **비교 1 = full_system vs vanilla_budget**(같은 매뉴얼 예산 3,900자, 라우팅·조립의 순효과), **비교 2 = full_system vs vanilla_vector**(무절단 벡터 검색). 두 비교 각각에 §6.3의 A/A′/B/C를 적용하고 둘 다 보고한다. 보조(기술 보고): vs no_rag, graph_only, vision_only, state_path, long_context(Gemini).
- OpendTect 매트릭스(3 시나리오 × 7 백엔드 × 3 모델 × 10회 + long_context)는 **개발 세트 성능**으로 별도 표에 보고하며 판정에 쓰지 않는다(라우팅·signature·조립을 이 세트로 고쳤다, §2.5).

### 6.3 1차 검정과 스토리 판정 (|M| = 3)
- 1차 검정: 모델을 층으로 하는 층화 순열검정(`scripts/stats_stratified.py`): 모델별로 두 arm의 라벨을 그 모델의 2n replicate 안에서 섞고, 통계량 = 모델별 (mean_full − mean_비교대상)의 평균, 10,000회, seed 42, 양측. 모델별 raw 순열 p도 함께 구한다.
- 방향 카운트 규칙: 분모는 항상 3(모델 수). 모델별 replicate 평균의 차이가 양(+)이면 우위 1, 음(−)이면 역방향 1, 동률(차이 0)은 우위로 세지 않는다(어느 쪽에도 넣지 않고 분모 3은 유지).
- **step accuracy 조건**(비교 1·2 각각): full_system > 비교 대상 방향이 ≥ 2/3이면서 층화 순열검정 raw p < 0.05이고, 어느 모델에서도 유의한 역방향(그 모델의 순열 p < 0.05인 역방향 차이)이 없을 것.
- **hall 조건**(비교 1·2 각각): hallucination_rate에서 full_system ≤ 비교 대상 방향이 2/3 이상.
- **A (시스템 우위)**: step accuracy 조건과 hall 조건이 모두 성립.
- **A′**: step accuracy 조건만 성립(hall 조건 불성립). cost_total은 조건이 아니라 함께 보고(P2).
- **B (조건부)**: 방향 ≥ 2/3이나 raw p ≥ 0.05, 또는 모델 의존 역전(한 모델에서 유의한 역방향).
- **C (비등/열세)**: 방향 ≤ 1/3.
- 다중 비교: 두 1차 검정(비교 1·2의 step accuracy)에 대한 Holm 보정값(패밀리 2)을 raw p와 함께 병기한다. 판정은 raw p로 한다. 보고 패밀리 전체(모든 pair × metric)의 Holm 보정값은 부록 표에 둔다.
- 종합 서술: 비교 1·2 모두 A(또는 A′)이면 "우위"(A′만이면 hall 열세를 함께 명시); 비교 1만 A/A′이고 비교 2가 B/C이면 "같은 예산에서의 라우팅·조립 효과"로만 서술하고 무절단 검색 대비 우위는 주장하지 않는다; 비교 2만 A/A′이면 "검색 대비 우위"로 서술하되 같은 예산에서의 라우팅 순효과 주장은 하지 않는다; 둘 다 B/C이면 §6.5. cost·latency·goal completion은 판정에 들어가지 않고 P2·P7대로 방향을 그대로 보고한다.

### 6.4 정지 규칙
- v4(개발 재개) 없음. 결과가 어떻게 나오든 이 기준으로 A/A′/B/C를 판정해 그대로 보고한다. 실행 중 장애(API 크레딧 소진·네트워크)로 재실행할 때는 사유를 로그와 audit trail에 남기고, 중단된 replicate는 버리고 처음부터 다시 돈다.

### 6.5 열세 시 보고
- Table 1에 열세인 비교 대상(vanilla_budget 또는 vanilla_vector)을 권장 구성으로 표시; full − vanilla_budget, full − vanilla_vector를 축별 부호 그대로 보고; 총비용에서 보조 호출 몫을 분해; 제목·초록의 "우위"를 "조건부"로; 재실행·시나리오 교체·채점기 재조정 금지.
- 귀속: 채점기 효과는 §3 재채점, GT 보정 효과는 S6 재채점으로 귀속. 임베더·예산·하네스·보조비용·매처 교체는 한 번에 바뀌므로 "v3 전체의 변화"로만 서술. unified4 비용 열과 v3 비용 열은 회계가 달라 직접 비교하지 않는다.

---

## 7. 실행 계획
- 래퍼 `bash scripts/run_v3.sh`(동결 태그의 파일 그대로; 모든 knob이 스크립트에 명시됨): CHROMADB_PATH=./data/chromadb_v4, EMBED_MODEL=BAAI/bge-m3, GEOLENS_SCORER=v3, RAG_KG_ENABLED=0, AUX_THINKING_BUDGET=0, GEN_TEMPERATURE=0.2, GEN_MAX_TOKENS=1024, GEMINI_THINKING_BUDGET=1024, VANILLA_BUDGET_CHARS=3900, MODELS=gemini,claude,gpt, REPS=10; 라우팅·조립 knob은 §2.3 G8의 동결 값(CONTEXT_ASSEMBLY=v4 포함). 결과 JSON마다 커밋 해시·dirty diff 해시·knob 스냅샷이 기록된다.
- 매트릭스: 3 모델 × 7 백엔드 × 3 개발 시나리오 × 10회 + Gemini long_context × 10회 + QGIS 3 모델 × 7 백엔드 × 10회.
- 예상: 실행 1회 ≈ 30분 → 30회 ≈ 15시간 순차(공급자 병렬 시 ≈ 5시간) + long_context ≈ 50분 + QGIS ≈ 2시간. API ≈ $95 (flat rate; long_context $62 포함; Gemini >200K 티어 실과금 시 최대 약 $155).
- 서명 후 순서: 서명된 사전등록 커밋(코드 태그 `v3-freeze-c01fdda`는 이미 있음; 서명 커밋에 `v3-prereg-signed` 태그) → run_v3.sh(서명 전 실행 금지) → 집계(build_final_table, compute_table1_sd, stats_stratified, stats_unified, direction_consistency, per_scenario_breakdown, output_token_analysis) → audit trail 기록. 실행 중 API 크레딧 소진 시 즉시 중단·보고(§6.4).

## 8. 한계 (명시)
- 시나리오·GT·워크플로우가 단일 저자 작업.
- 테스트 세트가 시나리오 1개·8스텝(QGIS)이라 라우팅 일반화 판정의 검정력이 낮다.
- 테스트 세트(QGIS)는 2026-08-13 파일럿에서 한 번 실행·분석된 시나리오이며, v3 개발은 그 결과(파일럿 수치와 실패 양상)를 아는 상태에서 이루어졌다. v3 개발 중에는 dry-run을 포함해 실행하지 않았다.
- 3d_visualization은 KB 결손으로 매뉴얼 근거 검색이 구조적으로 불가(P6).
- 매뉴얼이 공개 문서라 파라메트릭 마스킹이 hybrid 이득을 압축한다(unified3 관측 #1 유지).
- rerank confidence는 정오답을 가르지 못한다(iteration 0 오라우팅 3건의 confidence 0.7·0.9·0.9가 정답 분포와 겹침; 개발 벤치의 pick은 사실상 전부 0.9). confidence는 기록만 하고 gate로 쓰지 않는다.
- 생성기→라우팅 결합: rerank 프롬프트가 세션의 직전 생성기 응답을 포함하므로 full_system의 라우팅은 생성기 모델과 조립 버전에 독립이 아니다(V3-22). 라우팅 안정성은 dry-run(세션 블록 없음)이 아니라 벤치 모드 수치로 적는다: 동결 구성(조립 v4) 64/64(4회), 인접 구성 조립 v3 62/64·조립 v5 61/64 — 라우팅은 100% 안정적이지 않다(§2.5 표).
- 개발 루프의 판단은 n = 1~2 개발 벤치와 dry-run에 기반했고, 개발 세트의 signature·조립·GT를 이 결과를 보며 고쳤다(§2.5). 확인적 판정은 QGIS에서만 한다.

### 8.x 한계 (개발 루프에서 드러난 것, 수치)
- **같은 다이얼로그를 공유하는 노드의 구별은 signature와 rerank 기준의 정합에 의존한다.** seismic_attribute 02·03·04는 모두 "Attribute Set 3D" 창이며, 2026-08-07 signature가 실제 화면(열리자마자 기본값 채워짐)과 어긋난 채로 "다음에 하려는 단계" 기준의 rerank가 03/04로 일관되게 밀렸다(iteration 3: s0 5/5·s1 5/5 오답). iteration 4(상태 일치 기준 + 워크플로우 내 그래프 순서 prior + 비기본 상태 signature)에서 dry-run 5회·벤치 4건 모두 정답이었으나, 이는 OpendTect 개발 세트의 signature를 고친 결과이며 QGIS signature는 손대지 않았다.
- **3d_visualization 노드 단위 라우팅**: v4 상태 일치 기준에서 s2·s3 화면이 d3_01(main window ready)로 수렴한다(5회 dry-run 전부). 워크플로우 단위로는 정답이고 노드 GT가 없어 채점에는 영향이 없지만, 그 결과 3d_viz s3에서 종료 상태 블록이 발동하지 않는다.
- **종료 상태 블록 오발동**: 다단계 노드(attribute 06_display, 스텝 5–7)에서 rep당 2/4 발동이 조기(5회 dry-run 합계 10/20; 벤치 4건 8/8 조기 발동에서 조기 '완료' 0건).
- **step 3 sentinel 스텝**: 요소 언급 허용 대안 패턴(2026-08-06 재정의와 함께 의도적으로 추가, 사용자 결정으로 유지)이 sentinel 대신 요소 언급 지시도 정답으로 받아들이므로 이 스텝의 step accuracy는 목표 인식 능력을 직접 재지 않는다(3모델 full_system·vanilla_vector에는 제거 시 변화 없음, `pattern_impact_3dviz_s3.md`).
- **표기 손실**: survey s0의 텍스트 없는 아이콘 버튼("녹색 더하기/플러스 아이콘", "새로운 설문 아이콘")이 패턴(Survey|Create|New|Add)에 걸리지 않아 full_system이 4건 중 3건 실패(vanilla도 일부 실패). 규칙 3 보류로 패턴 불변.
- **생성 손실**: 정답 라우팅에서도 [Current Step] 설명이 화면과 다른 값("Input Data = 4 Dip steered median filter")을 단정하면 생성기가 그것을 고치려 한다(iteration 4 벤치 4건 5스텝). 컨텍스트 조립 v4(도달 상태·다음 동작 분리, iteration 5)로 이 유형은 0건이 됐으나(V3-20), 더 나아간 v5(iteration 6)에서는 1건 재발(Gemini attribute s1)해 v5는 채택하지 않았다(V3-21).
- **지연**: full_system은 vanilla 대비 스텝당 약 +10~15 s(clean run: vision 4.5 + CLIP 4.0 + 임베딩 3.2 + rerank 1.3; CLIP은 iteration 2부터 vision과 병렬). 최종 표의 지연은 별도 clean run의 단계 분해로 보고한다.
- **조립 v4(동결 구성)의 알려진 결함**: [Next Action]이 엣지 지시만 주므로 (1) 여러 스텝에 걸친 노드에서 다음 노드의 동작을 일찍 제시할 수 있고, (2) verification 노드로 가는 엣지(attribute 06→07 "QC 하세요")가 sentinel 대신 제시될 수 있으며, (3) 노드 단위 라우팅 오차(survey s1을 03으로)가 다음 동작 오류로 직결된다(iteration 5 벤치 GPT 2건). 이를 고친 v5는 사전 기준 미충족과 rerank 입력 결합 확인으로 채택하지 않았다(V3-21·V3-22). 노드 단위가 큰 QGIS 워크플로우에서 구조적으로 재현될 수 있다(§5.x (i)(ii)).
- **n = 1~2 개발 벤치의 step accuracy 차이는 잡음 범위**이며 확인적 판정은 QGIS 테스트 세트(n = 10, 3모델)에서만 한다.
- **rerank confidence**: 개발 루프 전체에서 오라우팅과 정답의 confidence가 겹쳐(0.7–0.9 대 0.9) 어떤 임계값도 오라우팅만 걸러내지 못했다. 기록만 한다.
- **세션 블록 결합과 라우팅 안정성(벤치 모드)**: rerank 입력에 직전 생성기 응답이 들어가므로 라우팅은 생성기·조립에 독립이 아니다(V3-22). 동결 구성 64/64(4회), 조립 v3 62/64, 조립 v5 61/64(§2.5 표). 교차 워크플로우 오라우팅(survey s3 → d3_visualization_01)은 최종 라우팅 코드에서 v5 벤치 2건에서만 관측됐고, v4에서 0/4·dry-run 0/15였다.

## 9. 서명
- 작성: 유지윤 / 검토: 외부 검토 Claude(채팅), 2026-09-18 / 확정 시각(UTC): 2026-09-18T08:09:04Z (서명 커밋 시각; 태그 `v3-prereg-signed`)
- 동결 태그: `v3-freeze-c01fdda` @ a03ca59 (2026-09-18 16:46 KST; 코드 c01fdda, GT 2f3db66). 서명 전 run_v3.sh 미실행.
- 서명 후 첫 벤치 실행 시각을 아래에 append한다.
- 첫 벤치 실행 시각(UTC): 2026-09-18T08:09:34Z — `bash scripts/run_v3.sh` (순차: 3 모델 × 10회 → long_context ×10 → QGIS 3 모델 × 10회), 서명 커밋 0f52154 / 태그 `v3-prereg-signed`, 로그 `data/eval/results/v3_bench.log`.
