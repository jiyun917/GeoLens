# GeoLens 보고서 보강 자료 — 2장 Design and Implementation · 3.1절 평가 설계

작성일 2026-09-17. 새 실험·집계 없이 저장소(C:\Users\user\Downloads\GeoLens-paper, branch paper)의 코드, 사전등록 문서(v2_pre_registration.md, qgis_pilot_prereg.md), 감사 기록(methodology_audit_trail.md), 매뉴얼 메타데이터(data/manuals.json), 실행 JSON(started_at)에서 확인한 값만 정리했습니다. 각 표의 ‘근거’ 열이 출처입니다.

## A. 2장 Design and Implementation

### A.1 구현 파라미터

| 항목 | 값 | 근거(파일:위치) |
|---|---|---|
| 임베딩 모델 | sentence-transformers all-MiniLM-L6-v2 (384차원, 로컬 추론, 배치 100). 청크는 ‘[Section: …, Page: …, Source: …]’ 접두를 붙인 상태로 임베딩. | api/services/embedder.py:23 _get_model(), _contextualize_chunk(); ChromaDB 인덱스 임베딩 차원 384 확인 |
| 벡터 DB | ChromaDB 1.0.7 PersistentClient, 경로 data/chromadb (CHROMADB_PATH), 매뉴얼당 컬렉션 manual_{manual_id}, 거리 = Chroma 기본(L2, HNSW), 결과는 distance 오름차순 정렬 | api/services/vectorstore.py; rag.py _specific_search |
| 청크 크기·오버랩 | 800 토큰 / 오버랩 100 토큰, 토크나이저 tiktoken 0.9.0 encoding_for_model('gpt-4o') (o200k_base). 섹션 경계를 넘지 않음(섹션별 독립 분할, chunk_index는 섹션 내 순번). | embedder.py:13-14 CHUNK_SIZE/CHUNK_OVERLAP, _chunk_single_text, split_into_chunks |
| top-k | 벡터 검색 top_k = 5 (get_manual_context 기본값, vanilla_vector·fallback·full_system 공통). 워크플로우 노드 질의(노드 제목+설명) 벡터 검색 top_k = 3. 라우팅 후보: 키워드 top-3 + CLIP top-3(이미지 top-6에서 매핑). | rag.py get_manual_context; graph_retriever.py retrieve_by_graph; guide_pipeline.py localize_to_graph |
| neighbor expansion 범위 | specific 청크와 같은 section의 chunk_index ±1 (앞·뒤 각 1개), 중복 제거, distance 미부여 | rag.py _expand_neighbors, vectorstore.search_by_section |
| 지식그래프 조회 | 질의 + 상위 3 청크(앞 500자)에서 개체 추출 → 2-hop 서브그래프 → weight 내림차순 → 상위 20 triplet을 컨텍스트 맨 앞 ‘[Knowledge Graph]’ 블록으로 배치. 매뉴얼 그래프 triplet은 weight ≥ 2만 통과, base graph는 항상 통과. | rag.py _abstract_search/_format_graph_context; graphstore.py query_subgraph_with_base |
| confidence 임계값 | CONFIDENCE_THRESHOLD = 0.7. rerank 확신도 < 0.7이면 선택 노드를 버리고 vector-only(질의 = 사용자 목표)로 후퇴(fallback_activated=True). rerank가 ‘none’을 반환하면 노드 없음(NONE, 플래그 없이 같은 vector-only). | guide_pipeline.py:25, 547-556; 도입 경위 methodology_audit_trail.md 결함 #4 |
| 컨텍스트 절단 예산(글자 수) | full_system 컨텍스트 블록(build_context_block): [POST-COMPLETION override] 무절단 / [Current Step] 무절단 / [Possible Next Steps] 무절단 / [Correction] 500자 / [Manual Context (graph)] 상위 3건 × 800자 / [Manual Context (vector)] 1,500자. state_path: 현재 노드 청크 3개 × 600자, next 2개 × 300자(+설명 200자), sibling 2개 × 청크 1개. vanilla_vector·long_context: 절단 없음(검색 결과 전문 14.6~21.8K자 / 매뉴얼 전문). | guide_pipeline.py build_context_block (674-683); state_path_retriever.py StatePathRetriever(next_horizon=2, chunks_per_step=3, max_siblings=2), format_step_path(max_chars_per_chunk=600); bench_backends.py backend_vanilla_vector |
| 기타 상수 | post-completion 감지 창 = 최근 방문 노드 3개; 재-localize로 visited 복원; intent 키워드(explain/qa/next) 분류; vision 결과 SHA-256 캐시 512개. | guide_pipeline.py:590-595, 57-63, _detect_intent |
| 생성기 프롬프트(벤치) | _inline_action_prompt: 역할 1줄 + 언어 + ‘ONE action’ + 완료 sentinel(‘Done’/‘완료’) + Goal + 최근 완료 스텝 6개 + ‘# Reference Manual Context’(백엔드별 context_block) + 형식 지시. 사용자 메시지 = 스크린샷 + ‘What is the next single action?’. | bench_backends.py _inline_action_prompt, _build_messages |

주의: README §3·§6.2와 CLAUDE.md는 임베딩을 text-embedding-3-small로 적고 있으나 코드와 두 인덱스(384차원)는 all-MiniLM-L6-v2입니다. 보고서에는 MiniLM으로 써야 합니다.

### A.2 지식 그래프

GeoLens에는 그래프가 두 종류 있습니다. (1) 라우팅에 쓰는 워크플로우 그래프(hand-authored DAG, data/workflows/*.json → networkx DiGraph 하나로 적재), (2) 검색 컨텍스트에 triplet을 넣는 엔티티 지식그래프(data/graphs/, LLM 추출 + hand-authored base graph).

(1) 워크플로우 그래프 — 구축: 매뉴얼 절을 사람이 읽고 단계별 노드·엣지·visual_signature·linked_chunks(ChromaDB 청크 id)를 JSON으로 작성. 자동 생성기(auto_graph_builder: 청크 역할 분류 gemini-2.5-flash → 절차 청크 3개 이상인 절을 워크플로우로, 제목 요약 gemini-2.5-pro)도 있으나 벤치 워크플로우는 전부 hand-authored.

| 파일 (data/workflows/) | workflow_id | 노드 | 엣지 | signature 수 | 키워드/노드 | UI요소/노드 | linked_chunks/노드 | edge_type | 용도 |
|---|---|---|---|---|---|---|---|---|---|
| survey_setup.json | survey_setup | 5 | 5 | 5 | 8.6 | 5.0 | 2.0 | sequential, conditional | 시나리오 1 (매뉴얼 1.2.2a) |
| d3_visualization.json | d3_visualization | 5 | 4 | 5 | 8.8 | 5.0 | 2.6 | sequential | 시나리오 2 (1.3.1a) |
| seismic_attribute.json | seismic_attribute | 7 | 7 | 7 | 8.0 | 3.6 | 3.0 | sequential, conditional | 시나리오 3 (1.5.1a); unified4에서 signature 재작성 |
| horizon_tracking.json | horizon_tracking | 8 | 8 | 8 | 4.0 | 2.6 | 3.0 | sequential, optional | 라우팅 후보(시나리오 없음) |
| fault_interpretation.json | fault_interpretation | 8 | 7 | 8 | 3.2 | 2.0 | 3.0 | sequential | 라우팅 후보(시나리오 없음) |
| **OpendTect 소계** | 5 workflows | **33** | **31** | **33** |  |  |  |  | unified4 그래프 |
| qgis_vector_buffer.json | qgis_vector_buffer | 5 | 4 | 5 | 7.6 | 4.2 | 0.0 | sequential | QGIS 파일럿 (hand-authored) |
| auto_bf2804…__follow_along_….json | auto_… | 3 | 2 | 3 | 13.0 | 0.0 | 2.0 | sequential | QGIS 매뉴얼 인제스트 시 자동 생성(파일럿 시 격리) |
| **전체 적재** | 7 workflows | **41** | **37** | **41** |  |  |  |  | WorkflowGraph 로그 ‘41 nodes, 37 edges’ |

노드 스키마: id, workflow_id, step_number, title, description, step_type(setup/action/verification), visual_signature{expected_dialog, expected_ui_elements[], screenshot_keywords[]}, linked_chunks[], parameters[]{name, default, description}. 엣지: source, target, edge_type, condition, instruction. 모든 노드가 signature 하나를 가지므로 signature 수 = 노드 수.

signature 실제 예시 (data/workflows/survey_setup.json, step 2 노드 원문):

```
{
  "id": "survey_setup_02_open_new_survey_dialog",
  "workflow_id": "survey_setup",
  "step_number": 2,
  "title": "Create New Survey 다이얼로그 열기",
  "description": "Survey Setup and Selection 창에서 Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 연다.",
  "step_type": "action",
  "visual_signature": {
    "expected_dialog": "Create New Survey",
    "expected_ui_elements": ["survey_name_input", "available_data_checkboxes",
                             "initial_setup_list", "z_domain_radio", "next_button"],
    "screenshot_keywords": ["Create New Survey", "Survey name", "Available data", "3D", "2D",
                            "Wells", "Initial setup", "Z Domain", "Time", "Depth"]
  },
  "linked_chunks": ["ea79cb7c48754d51a8240b6c5925b5de", "7ecaade7307b4372ad0949fc89d10b37"],
  "parameters": []
}
// 엣지 예시
{ "source": "survey_setup_01_open_selection", "target": "survey_setup_02_open_new_survey_dialog",
  "edge_type": "sequential", "condition": null,
  "instruction": "Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요" }
```

signature 매칭 점수(workflow_graph._score_node_match): vision이 추출한 visual_state를 소문자 문자열로 펼친 뒤 screenshot_keywords·expected_ui_elements(‘_’→공백)·expected_dialog의 부분문자열 포함 여부를 세어 score = 일치 수 / (키워드 수 + UI 요소 수 + dialog 1). 상위 3개가 rerank 후보로 들어갑니다.

(2) 엔티티 지식그래프 — 구축: 인제스트 시 graph_builder.build_graph_from_chunks가 청크마다 gemini-2.5-pro에 triplet 추출을 요청(청크당 10~25개, 5 병렬 워커, 재시도 4회), 앞 10개 청크 키워드로 content_type을 자동 감지해 GEOSCIENCE 또는 SOFTWARE 프롬프트를 선택, (subject, relation, object)를 networkx DiGraph에 누적(같은 triplet 재등장 시 weight 증가)하여 data/graphs/graph_{manual_id}.json에 저장. base graph 6종은 hand-authored 한국어 개념 그래프.

| 그래프 | 노드 | 엣지 | 구축 | 검색 시 기여 |
|---|---|---|---|---|
| graph_645b7cdf… (OpendTect 매뉴얼) | 5,488 | 3,977 | gemini-2.5-pro 자동 추출. 관계명이 used_for 824 / type_of 438 / associated_with 182 … 로 GEOSCIENCE 프롬프트로 분류되어 추출됨 | weight ≥ 2 엣지가 4개뿐이라 필터 후 거의 기여하지 않음(연결된 노드 3,967, 고립 1,521) |
| graph_bf2804… (QGIS 매뉴얼) | 9,130 | 6,588 | gemini-2.5-pro, SOFTWARE 프롬프트(action_on 902 / next_step 835 / contains 719 …) | 동일 weight ≥ 2 필터 |
| base_geoscience.json | 165 | 155 | hand-authored (정단층·형성환경 등 한국어 지질 개념) | 항상 로드(data_types 없이도) → 벤치 컨텍스트의 [Knowledge Graph] 블록은 사실상 이 그래프 |
| base_seismic.json | 133 | 116 | hand-authored | data_types에 ‘seismic’ 지정 시 |
| base_well_log / gravity_magnetic / gpr / resistivity | 24 / 21 / 17 / 16 | 15 / 10 / 9 / 8 | hand-authored | data_types 지정 시 (벤치는 미지정) |

주의: 발표자료의 ‘지식그래프 63개 핵심 개념’은 현재 파일과 맞지 않습니다(base_geoscience 165 노드). 벤치(data_types=None)에서 vanilla·fallback 컨텍스트 맨 앞에 들어가는 triplet은 base_geoscience에서 온 지질 개념 관계(정단층–형성환경 등)이며 매뉴얼 그래프는 weight 필터 때문에 거의 들어가지 않습니다. 2장에 ‘지식그래프’를 쓸 때 이 사실을 그대로 적는 것이 안전합니다.

### A.3 KB 규모

| 항목 | OpendTect | QGIS | 근거 |
|---|---|---|---|
| 매뉴얼 | Introduction to OpendTect and OpendTect Pro — Training Manual, Version 7.0 (dGB Earth Sciences), PDF 파일명 Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf (160 MB) | QGIS Training Manual 3.44 (QGIS project, CC-BY-SA), QGIS-3.44-TrainingManual-en.pdf (90 MB) | data/manuals.json; PDF 메타데이터 title |
| 쪽수 | 454쪽 (pypdf로 확인); 이미지 위주 279쪽은 Gemini Vision OCR | 697쪽 | pypdf 페이지 수; README §6.2·§6.3 |
| 청크 수 | 486 (PyMuPDF 인덱스, unified2 당시; manuals.json chunk_count) / 521 (pdfplumber 인덱스, unified3·unified4·QGIS 파일럿 시점의 data/chromadb) | 733 | ChromaDB count; manuals.json; README §6.2 |
| 토큰 규모(long_context 입력) | ≈226,600 토큰 (PyMuPDF 인덱스, unified2) / ≈252,400 토큰 (pdfplumber 인덱스, unified3·4) | — | run_gemini_longctx_*.json input_tokens; cost_basis.md §3 |
| CLIP 이미지 인덱스 | 765장 (≥100×100 px, data/manual_images/645b7cdf…/) | (파일럿에서는 미집계) | image_extractor.py; 디렉터리 파일 수 |
| 지식그래프 | 5,488 노드 / 3,977 엣지 (+ base_geoscience 165/155) | 9,130 / 6,588 | data/graphs/*.json |
| 워크플로우 그래프 | 5 workflows, 33 노드, 31 엣지, 33 signatures | 1 workflow, 5 노드, 4 엣지 | data/workflows/*.json |
| 인제스트 소요 | ≈20~25분 (pdfplumber 3분 + OCR 15분 + 청킹·임베딩 2분, 4코어 CPU) | 55.6분 (2026-08-13 00:00:52 → 00:56:30, 12.5쪽/분) | README §6.2; 종합결과보고서 §5.1; methodology_audit_trail § P-1 |
| 인덱스 크기 | ≈1 GB (chromadb) + CLIP 캐시 ≈160 MB | — | README §2, §6.2 |
| manual_id | 645b7cdf2690408da843b9ce63c52d5b (등록 2026-06-16) | bf2804feea57434bb79b749134ed1df0 (등록 2026-08-13) | data/manuals.json |

주의: README §8과 초안 Data availability는 ‘headline numbers = PyMuPDF 인덱스(226K 토큰)’라고 쓰지만, unified3·unified4의 long_context 입력이 252K 토큰이므로 활성 매트릭스는 pdfplumber 인덱스(521청크)에서 실행되었습니다. 2장 KB 규모에는 521청크·≈252K 토큰을 쓰고, PyMuPDF 486청크·226K는 unified2 참조값으로 각주 처리해야 합니다.

### A.4 보조 호출 구조 (생성기 외 LLM 호출)

| 호출 | 모델 | 설정 | 입력 | 출력 | 호출 시점·횟수 | 근거 |
|---|---|---|---|---|---|---|
| vision 상태 추출 (recognize_visual_state) | gemini-2.5-flash | temperature=0, response_mime_type='application/json', HTTP timeout 30 s, 일시 오류(429/500/503/504/timeout) 시 최대 3회 재시도(1.5×2^n s 백오프). thinking_config 미설정(모델 기본 dynamic thinking). | 고정 프롬프트(아래) + 스크린샷 원본 바이트(image/jpeg, 1922×1041) | JSON {current_dialog, active_menu, visible_elements[], data_state, current_action} | 스크린샷당 1회. 이미지 바이트 SHA-256 캐시(최대 512개)로 같은 화면 재호출 없음. 사용 백엔드: graph_only, full_system, state_path | guide_pipeline.py:100-120, 158-253 |
| LLM rerank (_llm_rerank_candidates) | gemini-2.5-flash | temperature=0, JSON 응답, timeout 40 s, 최대 3회 재시도. thinking_config 미설정. | 사용자 목표 + visual_state JSON(500자) + 이미 방문한 후보 id + 후보 ≤6개(id, workflow, step, title 80자, desc 120자) + 결정 규칙(‘bias toward picking’, ‘none’은 무관할 때만) | JSON {id: 후보 id 또는 none, confidence 0~1} | localize_to_graph 1회당 1회(후보가 있을 때). 벤치에서는 스텝 i마다 이전 스텝 재-localize로 i+1회. 사용 백엔드: full_system, state_path | guide_pipeline.py:371-490 |
| CLIP 이미지 매칭 | open_clip ViT-B-32 (pretrained ‘openai’), 로컬 | 코사인 유사도, 이미지 top-6 → 노드 top-3 | 스크린샷 | 노드 후보 | localize 1회당 1회 (API 아님) | visual_matcher.py |
| 인제스트: 이미지 페이지 OCR | gemini-2.5-flash | 페이지 200 dpi 렌더, 5 병렬 | 페이지 이미지 | 텍스트 | OpendTect 279쪽(1회성) | parser/pdf_parser.py:36-89 |
| 인제스트: 청크 역할 분류 | gemini-2.5-flash | temperature=0, 배치 호출 | 청크 텍스트 | chunk_role 등 | 청크당(1회성) | chunk_classifier.py:31,128 |
| 인제스트: 지식그래프 triplet 추출 | gemini-2.5-pro | 청크당 1회, 재시도 4회 | 청크 텍스트 + 프롬프트 | triplet JSON 배열 | 청크당(1회성) | graph_builder.py:178 |
| 평가: LLM judge (보조 지표) | claude-haiku-4-5-20251001 (max_tokens 128) + gemini-2.5-flash (temperature 0, JSON) | consensus = 둘 중 max | 스텝 정의 + 응답 앞 500자 | {score 0/1} | 스텝당 2회(벤치 --judge consensus) | bench_judge.py |

vision 프롬프트 원문(opendtect 프로필; qgis 프로필은 소프트웨어명·data_state 예시만 다름):

```
You are analyzing a screenshot of the OpendTect geophysics software.
Extract the current UI state into JSON:

{
  "current_dialog": "name of the currently visible dialog/window",
  "active_menu": "currently active menu or tab, if visible",
  "visible_elements": ["key UI elements visible on screen"],
  "data_state": "state of data loaded (e.g., '3D seismic loaded', 'none')",
  "current_action": "what action appears to be in progress"
}

Respond with JSON only, no markdown fences, no explanation.
```

rerank 프롬프트 골격(guide_pipeline.py:413-433; 전문은 코드 참조):

```
You rank workflow steps by how well they match the user's current UI situation.
User goal: {goal}
Current UI visual_state JSON: {visual_state[:500]}
Already-completed candidate nodes (…DO NOT pick one of these again…): {visited in pool}
Candidate workflow steps (from a software manual):
1. id="…" workflow="…" step=N / title: … / desc: …
Pick the candidate whose step description best matches what the user is CURRENTLY doing or trying to do next …
DECISION RULE — bias toward PICKING a candidate: … Confidence in [0.5, 0.9] is fine for partial matches …
Returning "none" is ONLY for cases where NO candidate is even loosely related …
IMPORTANT — wizard dialogs stay on screen after their action completes: … prefer a NEXT candidate …
Respond with JSON only: {"id": "<candidate_id_or_none>", "confidence": 0.0-1.0}
```

주의: 벤치의 cost_usd는 생성기 호출 토큰만 집계합니다(_record_usage가 생성기 호출에서만 실행). vision·rerank 호출의 토큰·비용은 JSON에 기록되지 않았으므로 2장에 ‘보고 비용은 생성기 기준’임을 명시해야 합니다.

## B. 3.1절 평가 설계

### B.1 지표 정의 (api/services/evaluation.py, 결정적 채점·LLM 개입 없음)

| 지표 | 판정 규칙 | 코드 |
|---|---|---|
| matched (Step Accuracy) | 다음 순서로 판정. (0) 빈 응답 → 불일치. (1) 응답이 ‘완료’/‘Done’ 단독(정규식 (?i)^\s*(완료|done)\.?\s*$)인데 해당 스텝 화면이 목표 달성 상태가 아니면 → 불일치(조기 완료 차단). (2) expected_action_text_pattern(대소문자 무시 정규식) 매치 → 일치. (3) expected_action_keywords 전부(AND)가 소문자 응답에 포함 → 일치. (4) allowed_alternatives[*].pattern 중 하나 매치 → 일치. 그 외 불일치. Step Accuracy = 일치 스텝 / 스텝 수. | step_match() |
| hallucinated (Hallucination Rate) | 응답에서 UI 요소 언급을 두 정규식으로 추출: (a) 따옴표/백틱으로 감싼 1~40자 토큰, (b) 대문자 시작 1~30자 구 + (버튼|메뉴|탭|button|menu|tab). 각 언급(2자 이상)을 스텝의 visual_state_gt.visible_elements와 대소문자 무시 양방향 부분문자열로 대조; 하나라도 근거 없으면 그 스텝 hallucinated. Hall Rate = hallucinated 스텝 / 스텝 수. Faithfulness = round(1 − Hall Rate, 4) (독립 지표 아님). | hallucinated_elements(), evaluate_backend() |
| looped (Loop Rate) | 응답을 소문자화하고 공백·문장부호·밑줄을 모두 제거한 문자열이 직전 스텝 응답과 같으면 looped(첫 스텝 제외). Loop Rate = looped 스텝 / 스텝 수 (dwell_loop_rate와 동일). | _normalize_instruction(), evaluate_backend() |
| goal_completion_rate (3-gate) | completion.expected_done_sentinel=true인 시나리오에서 마지막 스텝 뒤 final_screenshot_path로 백엔드를 한 번 더 호출해 ‘완료 응답’을 얻고, ① has_done_sentinel: 마지막 줄이 done/완료(문장부호 제거 후) 또는 응답이 (done|완료)로 끝남; ② completion_visually_grounded: 응답이 언급한 소프트웨어별 완료-주장 토큰(OpendTect: In-line/Cross-line/Z-slice/Time-slice/Depth-slice, 3D Scene/Main Window/Tree scene, Seismic_data/F3 Demo/Similarity/Curvature/Frequency; QGIS: Layers Panel/Map Canvas/Processing Toolbox/…, Buffer/Dissolve/…, roads_buffer/EPSG:n/…)이 정규화(소문자, 공백·하이픈·밑줄 제거) 후 마지막 스텝 visual_state_gt + capture_instructions 텍스트에 모두 존재(주장 토큰이 없는 bare sentinel은 통과); ③ _visual_state_indicates_goal_reached: 마지막 스텝에 trap.type=goal_completion_sentinel이 있거나 visual_state_gt/screen_state에 goal 마커(goal achieved/reached/complete, achieved, all three slices, all slices, 완료, 달성, goal state, completed, terminal state) 존재. 셋 다 참일 때만 1.0, 아니면 0.0(시나리오당 1값). | has_done_sentinel(), completion_visually_grounded(), _visual_state_indicates_goal_reached(), evaluate_backend() |
| trap_pass_rate | trap 필드가 있는 스텝(category_vs_child_item, post_completion_repeat, goal_completion_sentinel, prefer_verify_over_skip) 중 matched 비율 | evaluate_backend() |
| recovery_rate | is_error_recovery_test=true 스텝 중 matched 비율 (4 시나리오에 해당 스텝 없음 → null) | evaluate_backend() |
| mean_latency_sec | backend 호출 시작~응답까지 벽시계(보조 호출·검색 포함) 스텝 평균 | evaluate_backend() |
| mean_cost_usd | 생성기 호출의 input/output 토큰 × 모델 단가(2026-07 base rate) 스텝 평균; 보조 호출 미포함; Qwen은 0 → qwen_cost_convert.py로 시간 환산 | bench_backends._record_usage; scripts/qwen_cost_convert.py |
| fallback_rate / mean_route_confidence | fallback_activated 스텝 / 스텝 수; route_method가 있는 스텝의 rerank confidence 평균(full_system만 기록됨) | evaluate_backend() |
| judge_step_accuracy (보조) | claude-haiku-4-5 + gemini-2.5-flash consensus(max) 0/1 판정의 평균. 논문 지표가 아님. | bench_judge.py |

3-gate 도입 경위(methodology_audit_trail.md 결함 #2, 2026-07-15): v1에서 Claude·Gemini goal_completion이 전 셀 1.000 — Claude no_rag/3d_visualization의 r2·r4·r5가 화면에 없는 Z-slice를 ‘로드됨’이라 단언하며 ‘완료’를 냈는데 sentinel만 보는 채점이 만점 처리. → sentinel + grounded + visual confirms 3-gate로 교체하고 scripts/rescore_results.py로 전 결과 재채점(claude/gemini unified 1.000 → 0.500 등). 사전등록 문서(v2_pre_registration.md)는 이 3-gate goal_completion을 핵심 지표 3개 중 하나로 고정.

집계 단위: 스텝 → 시나리오(스텝 평균) → replicate(시나리오 평균) → 셀(replicate 5개 mean ± 표본 SD). 통계 단위 = replicate(n=5/측).

### B.2 사전등록 판정 프레임 (v2_pre_registration.md, qgis_pilot_prereg.md)

- 핵심 지표 3개: step_accuracy(↑), faithfulness = 1 − hall_rate(↑), goal_completion_rate 3-gate(↑). 보조: mean_latency_sec, mean_cost_usd, fallback_rate.
- 방향 일관성 규칙: 지표별로 full_system > vanilla_vector인 모델 수를 세어 4/4 일관 우위, 3/4 다수 우위, 2/4 혼재, ≤1/4 역효과.
- 스토리 A(시스템 우위) 조건: (i) step_accuracy 또는 goal_completion에서 3/4 이상 방향 우위, (ii) 그중 최소 1개 모델 permutation p < 0.10, (iii) faithfulness 3/4 이상 우위, (iv) API 유료 3 모델 모두 full_system이 vanilla보다 저렴(cost 역설). B = 일부만 충족, C = 2/4 이하.
- 통계 검정: 순열검정 10,000회(seed 42, 양측, |평균차|) + Welch t; 최소 p = 2/C(10,5) ≈ 0.008; 72검정 패밀리(3 pair × 6 metric × 4 model), Bonferroni/Holm 보정 병기; 1차 판정은 방향 일관성.
- unified3·unified4 추가 사전등록: attribute 시나리오 예측(vanilla가 §1.5.1a 절차 청크를 못 찾고 full은 라우팅으로 확보 → 격차 확대), unified4 signature 재작성 예측(라우팅 ≥70%, 격차 양전환), fallback 예상 위치. QGIS 파일럿: Primary(빈 응답 0, 지표 산출, 로그 무결) + Secondary 예측 A/B/C. 정지 규칙: unified5·qgis_pilot2 없음.

### B.3 재현 정보

| 구성요소 | 모델 버전 문자열 | 생성 설정 | 근거 |
|---|---|---|---|
| 생성기 1 | gemini-2.5-pro (Google GenAI SDK) | temperature 미설정(SDK 기본), max_output_tokens 미설정(thinking 모델 보호), timeout 120 s, 빈 응답 시 3회 재시도(2/4/6 s) | bench_backends.py:354-356, 261-351 |
| 생성기 2 | claude-sonnet-4-6 (anthropic SDK) | max_tokens=512, temperature 미설정(기본), 이미지 base64 첨부 | bench_backends.py:208-258 |
| 생성기 3 | gpt-4o (openai SDK) | max_tokens=512, temperature 미설정(기본), timeout 90 s | bench_backends.py:365-386 |
| 생성기 4 | qwen3-235b-a22b-instruct, GPTQ int4, vLLM tensor-parallel 4, --max-model-len 32768, 4× NVIDIA RTX 6000 Ada 48 GB, 엔드포인트 http://<host>:28000/v1 | max_tokens=1024, temperature=0.2, 텍스트 전용(이미지 제거), <think>…</think> 제거 | bench_backends.py:389-414; README §9; cost_basis.md §5.1 |
| vision / rerank | gemini-2.5-flash | temperature 0, JSON, thinking 기본값 | guide_pipeline.py |
| judge (보조) | claude-haiku-4-5-20251001 + gemini-2.5-flash | max_tokens 128 / temperature 0, consensus=max | bench_judge.py |
| 임베딩 / CLIP | all-MiniLM-L6-v2 / ViT-B-32 (openai) | — | embedder.py; visual_matcher.py |
| 인제스트 OCR / 분류 / KG | gemini-2.5-flash / gemini-2.5-flash / gemini-2.5-pro | OCR 200 dpi; 분류 temperature 0 | pdf_parser.py; chunk_classifier.py; graph_builder.py |

| 항목 | 값 | 근거 |
|---|---|---|
| 실행 날짜(UTC) | unified4 main matrix: 2026-08-07 02:35 (gemini r1 시작) ~ 17:36 (qwen r5 시작), 20 실행 순차. long_context: 2026-08-07 18:24 ~ 18:47 (5회). QGIS 파일럿: 2026-08-13 03:00 ~ 03:50 (5회, 벤치 종료 04:01). 이전 사이클: unified2 2026-07-16, unified3 2026-08-06~07. | run_*.json started_at; 종합결과보고서 §5.1 |
| 매트릭스 | 4 생성기 × 6 core 백엔드 × 3 시나리오(4+4+8 스텝) × 5 replicate = 1,920 스텝 + Gemini long_context 240 스텝 + QGIS 파일럿 Gemini × 3 백엔드 × 8 스텝 × 5 = 120 스텝. 모든 프롬프트·시나리오 한국어(language: ko). | unified4_judgment_template.md §0; README §5·§7 |
| 대상 소프트웨어 | OpendTect V7.0.9 (Windows) — 스크린샷 타이틀바·시나리오 visual_state_gt 기재; 데이터 F3 Demo 2023 (Seismic_data.sgy). QGIS 3.44 + QGIS Training Data 3.44 (레이어 roads_33S, EPSG:32733). | data/eval/scenarios/*.json; data/eval/screenshots/*; README §6.3 |
| 시나리오 | opendtect__survey_setup__01 (medium, 1.2.2a, 4스텝), opendtect__3d_visualization__01 (medium, 1.3.1a, 4스텝), opendtect__attribute_computation__01 (hard, 1.5.1a, 8스텝), qgis__vector_buffer__01 (medium, §6.2.6, 8스텝). 스크린샷 1922×1041 JPEG, 스텝별 1장(총 24장), validate_screenshots.py로 사전 검증. | data/eval/scenarios/SCENARIO_SCHEMA.md; scenarios/*.json |
| 실행 스크립트 | scripts/run_unified4.sh → run_all_models.py --judge consensus → api.services.bench_runner (replicate당 별도 프로세스) ; 집계 build_final_table.py, compute_table1_sd.py, stats_unified.py(seed 42, 10,000), stats_audit.py, direction_consistency.py, faithfulness_audit.py, per_scenario_breakdown.py, qwen_cost_convert.py; QGIS: run_qgis_pilot.py, qgis_pilot_judge.py | README §5.2·§5.3; 종합결과보고서 §8.5 |
| 소프트웨어 환경 | Windows 11, Python 3.12.10; chromadb 1.0.7, sentence-transformers 5.5.1, transformers 5.11.0, torch 2.12.0, open_clip_torch 3.3.0, tiktoken 0.9.0, google-genai 1.3.0, anthropic 0.109.1, openai 2.6.0, networkx 3.6.1, pdfplumber 0.11.10, pypdf 6.14.2 (PyMuPDF 1.25.3은 unified2 참조 인덱스 생성에만) | requirements.txt; .venv 설치 버전 |
| 단가·환율 기준일 | API 단가 2026-07 공표 base rate(캐시 할인·>200K 티어 미적용); Qwen $0.84/GPU-hr × 4 = $3.36/hr (RunPod Secure Cloud, 2026-07-27 조회) | cost_basis.md §2·§5 |
| 비결정성 | 생성기 temperature가 Qwen(0.2) 외에는 SDK 기본값이라 replicate 간 변동은 샘플링에서 옴. 검색·채점·라우팅 점수는 결정적(vision·rerank는 temperature 0이나 모델 출력 자체는 비결정적일 수 있음). | 코드 |

## C. 보고서 서술 시 함께 고쳐야 할 표기

- 임베딩: text-embedding-3-small → all-MiniLM-L6-v2 (README·CLAUDE.md·설계문서).
- KB: OpendTect 454쪽 / 521청크(pdfplumber, 활성 매트릭스) / ≈252K 토큰; 486청크·226K는 unified2 참조값.
- 지식그래프: 매뉴얼 그래프는 weight≥2 필터로 검색에 거의 기여하지 않고, 컨텍스트의 triplet은 base_geoscience(165/155)에서 옴. ‘63개 핵심 개념’ 표기는 구버전.
- 비용: 생성기 토큰 기준이며 vision·rerank 보조 호출은 미포함.
- 채점: 사전등록 채점기(결정적). goal completion은 3-gate이며 unified4에서는 3 시나리오 모두 기여(초안 4.4절 ‘Appendix A capture defect’ 문구는 unified2 시점).
