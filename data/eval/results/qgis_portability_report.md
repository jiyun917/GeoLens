# GeoLens → QGIS Portability Report

**작성 시점**: 2026-08-05 (unified3 캡처 대기 중 병렬 조사)
**후속 이관**: 2026-08-07 (unified3 recovery 대기 중 별건 정리)
**목적**: 교수님 요청 (2) "다른 소프트웨어 대응 계획" — QGIS 를 사례로 이식성
기술 조사. **구현 착수 아님, read-only 조사·보고서.**

---

## 1. Executive summary

- **매우 이식 가능**. RAG/graph/embedding/eval 인프라 전체가 소프트웨어
  독립적. 6 파일에만 OpendTect UI 어휘가 하드코딩됨.
- **실제 blocker 2 개, 둘 다 소규모**:
  (a) `guide_pipeline.py:81` 의 `VISUAL_STATE_PROMPT` 가 OpendTect 를
      명시적으로 언급,
  (b) `evaluation.py:578-582` 의 `_COMPLETION_CLAIM_PATTERNS` regex
      리스트가 OpendTect UI 토큰 화이트리스트.
- **프롬프트 계층 결합이 가장 큰 숨은 비용**. `lib/prompts/action.ts:134-163`
  이 OpendTect 특화 "3D Scene right-click" 정책 30줄 — 파라미터화 아니라
  일반화 필요.
- **QGIS 인제스트 완전 실현 가능**. 기존 PDF 파이프라인 (pdfplumber +
  pypdf outline + Gemini OCR fallback) 은 OpendTect 가정 무. URL 파서도
  이미 온라인 HTML 매뉴얼 depth-2 크롤링 지원. QGIS 매뉴얼 PDF ~1,000쪽,
  ingest 시간 문제 없음.
- **예상 소요: ~7-10 인일** for QGIS 작동 변형 (§ 7 참조). 대부분 시나리오·
  워크플로우 JSON 작성 + 스크린샷 캡처, 코드 변경은 ~1일.

---

## 2. OpendTect 특화 결합 인벤토리

| 파일 | 라인 | 현재 텍스트 | 카테고리 | 비고 |
|---|---|---|---|---|
| `api/services/guide_pipeline.py` | 81 | `"...screenshot of the OpendTect geophysics software."` | **config-swap** | 프롬프트 문자열; `{software_name}` 템플릿 변수로 파라미터화 |
| `api/services/guide_pipeline.py` | 249 | comment: `generic chrome like "Scene", "OpendTect window"` | 주석만 | 동작 영향 없음 |
| `api/services/guide_pipeline.py` | 257 | comment: `OpendTect panes routinely cosine ≥0.85` | 주석만 | |
| `api/services/guide_pipeline.py` | 332 | comment: `Scene, Window, Cross-line` | 주석만 | |
| `api/services/evaluation.py` | 578-582 | `_COMPLETION_CLAIM_PATTERNS = [r"(In[- ]?line\|Inline\|Cross[- ]?line...)", r"(3D Scene\|Main Window\|Tree scene)", r"(Seismic_data\|F3[_ ]?Demo\|Similarity\|Curvature\|Frequency)"]` | **code-change** (small) | 완료 채점용 하드코드 화이트리스트. `{software_id: [patterns]}` dict 로 리팩터 |
| `api/services/evaluation.py` | 599 | docstring 예시 "In-line, Cross-line, Z-slice" | 주석만 | 미학적 |
| `api/services/parser/pdf_parser.py` | 11, 30 | 주석에 `Requiredlicenses:OpendTect` 를 x_tolerance regression 예시로 언급 | 주석만 | 파서 자체 완전 generic |
| `api/services/state_path_retriever.py` | 26 | docstring: `"Enter survey root path"` | 주석만 | 예시 |
| `api/services/rag.py` | 40 | regex geo-term extractor: `seismic\|well\|log\|horizon\|thrust\|normal fault\|...` | **code-change** (medium) | 그래프 쿼리용 entity extractor; 시스믹 편향, QGIS 에 무용하나 무해 (엔티티 몇 개 덜 뽑을 뿐) |
| `api/services/graphstore.py` | 178-185 | `DATA_TYPE_GRAPH_MAP = {"seismic":..., "well_log":..., "gpr":...}` | **config-swap** | Base-graph 선택기; QGIS 관련 키 추가 (`raster`, `vector`, `wms`) |
| `api/services/graph_builder.py` | 26, 63-65, 85, 105-110 | `GEOSCIENCE_PROMPT` + `SOFTWARE_KEYWORDS` + example triplet uses SEG-Y/inline/survey | 대부분 generic | `SOFTWARE_PROMPT` 는 이미 소프트웨어 중립; JSON example triplet 만 OpendTect 언급. 예시 재작성 |
| `lib/prompts/action.ts` | 45, 71-81 | "Numbered identifiers (Scene 1/2/3, Window 1/2, Tab 3, Plot 4, panel 'Tree scene 2', in-001.sgy)" | 대부분 generic | 예시가 OpendTect 이나 규칙은 일반 |
| `lib/prompts/action.ts` | 134-163 | 30-line section: "██ DISPLAYING DATA IN A 3D SCENE — Right-Click is the Primary Path ██" | **code-change** (medium) | OpendTect Scene tree taxonomy (Inline/Crossline/Z-slice/Horizon/Well/2D Line). QGIS 에 무관·오도 가능성. software_id 조건부 fragment 또는 별도 파일 |
| `lib/prompts/assistant.ts` | 10 | example: `"Menu: Survey &gt; Import &gt; Seismic &gt; SEG-Y"` | 미학 | 예시만 |
| `components/multimodal-input.tsx` | 81, 83 | UI placeholder: `"Pick horizons in OpendTect"`, `"Create seismic cross-section"` | **config-swap** | 프론트엔드 placeholder |

**요약: 실질 코드 변경 필요 touch-point = 4** (guide_pipeline VISUAL_STATE_PROMPT,
evaluation._COMPLETION_CLAIM_PATTERNS, action.ts 3D-scene section,
multimodal-input placeholders). 나머지 모두 주석/docstring/파라미터화 가능.

---

## 3. 시나리오 스키마 이식성

`data/eval/scenarios/SCENARIO_SCHEMA.md` + 2 라이브 시나리오 + `evaluation.py`
의 `ScenarioEvaluator` 대조:

| 필드 | 소프트웨어 중립? | QGIS 대응 |
|---|---|---|
| `scenario_id` | Yes | 규약 `{software}__{slug}__{variant}` — `opendtect` → `qgis`. **코드에서 prefix 파싱 안 함**. filename glob 은 `*.json` |
| `manual_id`, `manual_name` | Yes | 재사용 |
| `manual_reference` | Yes | 챕터 참조 — QGIS 매뉴얼 섹션 |
| `category`, `difficulty`, `language` | Yes | 자유 문자열 |
| `goal` | Yes | 자유 텍스트 |
| `initial_state.description`, `must_be_true` | Yes | 산문 assertions |
| `steps[i].screenshot_path` | Yes | Generic path |
| `steps[i].visual_state_gt` (current_dialog, active_menu, visible_elements, ...) | Yes | 키만 중립, 값은 QGIS 어휘로 |
| `steps[i].expected_action_text_pattern`, `expected_action_keywords`, `allowed_alternatives` | Yes | Regex/keyword 매칭 — 시나리오별 콘텐츠 |
| `steps[i].expected_workflow_node` | Yes | Node id — QGIS workflow node id 로 |
| `steps[i].capture_instructions` | Yes | 산문 |
| `steps[i].trap.type` | Yes | Trap taxonomy generic UI-behaviour |
| `completion.expected_done_sentinel` | Yes | Language-token 이미 `language` 로 파라미터화됨 |

**결론**: 시나리오 스키마 **변경 필요 없음**. QGIS 용은 JSON *콘텐츠* 만
재작성. `_COMPLETION_CLAIM_PATTERNS` 만 시나리오 필드 참조로 리팩터 필요
(§ 2 참조).

---

## 4. 워크플로우 노드 스키마 이식성

`data/workflows/*.json` + `api/services/workflow_graph.py` 검토:

| 필드 | 소프트웨어 중립? | QGIS 대응 |
|---|---|---|
| `workflow_id`, `name`, `description` | Yes | 자유 텍스트 |
| `nodes[i].{id, workflow_id, step_number, title, description, step_type}` | Yes | Generic |
| `nodes[i].visual_signature.expected_dialog` | 키만 (값 대체) | QGIS 다이얼로그 이름 |
| `nodes[i].visual_signature.expected_ui_elements` | Yes | Snake-case UI 토큰 |
| `nodes[i].visual_signature.screenshot_keywords` | Yes | `_score_node_match` 는 순수 lowercase keyword overlap, OpendTect 가정 무 |
| `nodes[i].linked_chunks` | Yes | 해당 매뉴얼 chunk id |
| `nodes[i].parameters` | Yes | Generic |
| `edges[i].{source, target, edge_type, condition, instruction}` | Yes | Generic |

**결론**: 스키마 **변경 필요 없음**. `WorkflowGraph.build_graph()` 는 `*.json`
globbing 후 단일 DAG 병합, QGIS workflow JSON 은 OpendTect 옆에 drop-in.
`hint_workflow_id` 로 세션별 스코프 유지. `_score_node_match` 는 순수 소문자
keyword overlap, QGIS 용어에 동일 작동.

주의: 자동 그래프 빌더 (`auto_graph_builder.py`, `chunk_classifier.py`) 는
역할 태그 (`procedural_step` / `parameter_desc` / `concept_explanation` /
`transition_cue` / `ui_description` / `general`) 와 generic action-verb sets
(`click`, `select`, `클릭`, `선택`, ...) 만 사용 — OpendTect 용어 무.
QGIS 매뉴얼로부터 자동 워크플로우 합성 시 `auto_{opendtect_manual_id}__*.json`
과 동일 shape 의 QGIS 워크플로우 JSON 생성 가능.

---

## 5. QGIS 인제스트 실현 가능성

### 매뉴얼 가용성

- **온라인 HTML**: <https://docs.qgis.org/latest/en/docs/user_manual/> —
  Sphinx-built, 구조 잘 잡힘, CC-BY-SA. `api/services/parser/url_parser.py`
  가 이미 depth-2 크롤링 + main/article 추출 + nav/footer/script/style
  제거 지원 — QGIS docs 깨끗하게 인제스트 예상. 각 챕터 root 로 max_depth
  조정 필요할 수 있음.
- **다운로드 PDF**: 공식 QGIS User Guide PDF LTR 릴리스별 (예:
  `QGIS-3.34-UserGuide-en.pdf`). 약 **1,000-1,100 쪽**, 추출 후 대략
  ~500-700k 토큰. 비교: 현재 OpendTect 매뉴얼 160MB / 486 chunks at 800
  tokens = ~390k 토큰. QGIS 는 ~1.5-2× 큼 — 파이프라인 용량 내, chunk 수
  700-900 예상, 전체 embed + auto-graph build 는 2-3× 시간.

### 아웃라인 추출 (pypdf)

- QGIS User Guide PDF 는 Sphinx-LaTeX 생성으로 완전한 중첩 outline (Part →
  Chapter → Section → Subsection) 제공. `pypdf.PdfReader.outline` in
  `pdf_parser.py:_extract_page_sections` 가 올바르게 walk 함. 섹션 이름이
  `metadata["section"]` 채우고 contextual retrieval prefix
  (`embedder.py:_contextualize_chunk`) 에 적절히 반영 — 코드 변경 필요 없음.

### UI mention 스타일 호환성

Hallucination scorer (`evaluation.py:hallucinated_elements`, lines 539-560)
매칭:
- Single/double-quoted / backticked 최대 40 chars 문자열: `'X'`, `"X"`, `` `X` ``
- role-token 접미: `X 버튼`, `X 메뉴`, `X 탭`, `X button`, `X menu`, `X tab`

QGIS 매뉴얼은 정확히 이 규약 사용 (`the :guilabel:` \`Add Vector Layer\`` HTML
로 **Add Vector Layer**, 텍스트로 `Add Vector Layer`; `:menuselection:`
으로 **Layer ‣ Add Layer ‣ Add Vector Layer…**). Sphinx `:menuselection:`
시퀀스는 "menu > submenu > item" 문자열로 매핑. **호환성: 높음** —
scorer 는 변경 없이 QGIS 스타일 mention 매칭.

### 파이프라인 호환성 요약

| 단계 | 호환? |
|---|---|
| `pdf_parser.parse_pdf` | Yes — 완전 generic |
| pypdf outline / section extraction | Yes — Sphinx outline well-formed |
| Gemini OCR fallback for image pages | Yes — QGIS docs 다이어그램 페이지 다수 |
| Chunking (800 tokens, 100 overlap) | Yes |
| `all-MiniLM-L6-v2` embeddings | Yes — 다국어 OK for en/ko QGIS 시나리오 |
| ChromaDB storage | Yes |
| `ChunkClassifier` (procedural roles) | Yes — action-verb list EN/KO 이중언어 generic |
| `AutoGraphBuilder` | Yes — 섹션 기반 그룹핑 generic |
| `graph_builder.SOFTWARE_PROMPT` for knowledge triplets | Yes — SEG-Y/LAS/DLIS 는 *예시* 만 언급 |
| `visual_matcher.py` (CLIP ViT-B/32 for screenshot ↔ manual image match) | Yes — CLIP 도메인 무관, QGIS docs 스크린샷 figure 다수 |

---

## 6. 권장 진행 계획 (구현 착수 시)

**주의: 이 문서는 조사 전용. 실제 구현 착수하지 않음. 아래는 진행 결정 시
참조.**

1. **소프트웨어 추상 계층 추가**
   - `guide_pipeline.py:81` 의 `VISUAL_STATE_PROMPT` 를 `{software_name}`
     템플릿으로 추출. 시나리오 metadata 또는 매뉴얼 metadata 에서 소싱.
   - `_COMPLETION_CLAIM_PATTERNS` (`evaluation.py:578`) 를 dict
     `{"opendtect": [...], "qgis": [...]}` 로 리팩터, 시나리오의
     software identifier 로 키잉 (SCENARIO_SCHEMA.md 에 `software_id` 필드
     추가).
   - action.ts 의 "3D Scene right-click" 블록 (`action.ts:134-163`) 을
     선택적 per-software prompt fragment 로 추출.
2. **QGIS 매뉴얼 인제스트** — 원샷: 기존 `/api/manual/upload` 엔드포인트로
   QGIS PDF 업로드. chunk_count 및 auto_workflow_count 합리성 검증.
3. **QGIS 시나리오 저작** — 3-5 개 JSON `data/eval/scenarios/qgis__<slug>__01.json`,
   동일 스키마. 시작 세트 제안:
   `qgis__add_vector_layer__01`, `qgis__coordinate_reference_setup__01`,
   `qgis__basic_symbology__01`, `qgis__raster_reclassify__01`,
   `qgis__print_layout__01`. 스크린샷을 `data/eval/screenshots/qgis__*/` 로.
4. **QGIS workflow JSON 저작** — 3-5 개 hand-authored under
   `data/workflows/qgis_<name>.json`, `survey_setup.json` shape mirror,
   QGIS 매뉴얼 chunk_id 참조.
5. **프론트엔드 placeholder 확장** — `components/multimodal-input.tsx:81,83`:
   QGIS 스타일 제안 추가.
6. **검증** — `scripts/validate_screenshots.py` per new scenario, 그다음
   `bench_runner` 를 `--software qgis` 필터로 실행 (`load_all_scenarios` 에
   filename prefix 필터 또는 추가된 `software_id` 필드 필터 소규모 추가
   필요).

---

## 7. 소요 산정

| Phase | Task | 인일 |
|---|---|---|
| A. 코드 리팩터 | VISUAL_STATE_PROMPT 파라미터화, `_COMPLETION_CLAIM_PATTERNS` dict, action.ts fragment 분리, `software_id` 필드 신설, bench_runner `--software` 필터 | 1.0 |
| B. QGIS 매뉴얼 인제스트 & QA | PDF 업로드; chunk_count, section 추출, auto-workflow 합성 검증; ~10 sample 쿼리로 retrieval spot-check | 0.5 |
| C. QGIS workflow JSON 저작 | 3-5 hand-authored workflows with visual_signature, linked_chunks, edges | 1.5 |
| D. QGIS 시나리오 저작 | 3-5 시나리오 JSON with 3-5 스텝 each, trap steps + completion criteria | 1.5 |
| E. QGIS 스크린샷 캡처 | scenario step 별 수동 캡처 (~20-25 shots 총) + `validate_screenshots.py` iteration | 1.5 |
| F. Bench 실행 + 채점 | `run_all_models.py` 3-4 models × 3 reps; 표 재생성 + audit | 1.0 |
| G. 예상 밖 여유 (prompt tuning, 예기치 못한 QGIS 특화 동작 e.g., Processing Toolbox modal quirks) | | 1.0 |
| **총** | | **~8 인일** (7-10 범위) |

Ongoing 유지 비용은 hand-authored workflows/scenarios 수에 대략 선형;
auto-graph JSON 은 유지 필요 없음.

### 핵심 파일 참조 (absolute paths)

- `./api\services\guide_pipeline.py` (VISUAL_STATE_PROMPT line 81)
- `./api\services\evaluation.py` (`_COMPLETION_CLAIM_PATTERNS` 578-582; `hallucinated_elements` 539-560; `load_all_scenarios` 833)
- `./api\services\workflow_graph.py` (완전 generic)
- `./api\services\parser\pdf_parser.py` (완전 generic)
- `./api\services\embedder.py` (완전 generic)
- `./api\services\auto_graph_builder.py` (완전 generic)
- `./api\services\chunk_classifier.py` (완전 generic)
- `./api\services\graph_builder.py` (SOFTWARE_PROMPT / SOFTWARE_KEYWORDS 58-103, generic; only example triplet mentions SEG-Y)
- `./api\services\graphstore.py` (`DATA_TYPE_GRAPH_MAP` lines 178-185)
- `./api\services\rag.py` (geo-term regex line 40)
- `./lib\prompts\action.ts` (3D-scene section lines 134-163)
- `./lib\prompts\assistant.ts` (example line 10)
- `./components\multimodal-input.tsx` (placeholders 81, 83)
- `./data\eval\scenarios\SCENARIO_SCHEMA.md` (스키마 — 변경 필요 없음)
- `./data\workflows\survey_setup.json` (schema exemplar)

---

## 8. 논문 반영 위치 (권장)

- **Discussion / External validity 섹션**: § 1-2 executive summary + 결합
  인벤토리 요약 문장. 3-4 문장으로 이식성 주장 + QGIS 이식 실측 가능
  estimate.
- **Future Work**: § 7 estimate + "QGIS full evaluation is left as future
  work" 명시.
- **Methods 스코프 표시**: 이번 논문은 OpendTect 만 실측, 아키텍처는
  general-pattern. 명시.

**투고 후 후속 트랙**: unified3 완료 → 논문 초고 → 투고 후 QGIS 이식
실측 (별도 short paper 또는 확장 연구).
