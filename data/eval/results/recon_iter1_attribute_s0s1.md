# routing dry-run v3 — recon_iter1_attribute_s0s1

code: f3ee78a90c38484865288c1f4c4c7fd38d7bc751 dirty=False; knobs: {"AUX_THINKING_BUDGET": "0", "CHROMADB_PATH": "C:/Users/user/Downloads/GeoLens-paper/data/chromadb_v4", "CONFIDENCE_THRESHOLD": "0.7", "EMBED_MODEL": "BAAI/bge-m3", "FALLBACK_CTX_CHARS": "3900", "GEN_PROMPT_VERSION": "v2", "GOAL_STATE_HINT": "0", "GRAPH_VECTOR_AUX": "0", "PARALLEL_RETRIEVAL": "1", "POST_COMPLETION_MODE": "soft", "RAG_KG_ENABLED": "0", "RERANK_PROMPT_VERSION": "v3", "ROUTED_VECTOR_QUERY": "goal", "ROUTER_EVIDENCE_GATE": "0", "ROUTER_GRAPH_PRIOR": "1", "ROUTER_MATCHER": "embedding", "ROUTER_POOL_K": "5", "ROUTER_TWO_STAGE": "0", "VISION_PROMPT_VERSION": "v3"}

## rep 0: correct 0/2; fallback 0; goal-state hints 0

| scenario | step | expected | picked | conf | gate | goal_state | ok | candidates (source:score) | rerank raw |
|---|---|---|---|---|---|---|---|---|---|
| attribute_computation__01 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_04_configure | 0.95 |  |  | ✗ | 01_ready_to_start[emb:0.75]; 02_open_attribute_tool[emb:0.74]; 04_configure[emb:0.73]; 04_add_zslice[emb:0.72]; 01_open_selection[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.88] | `{"id": "seismic_attribute_04_configure", "confidence": 0.95}` |
| attribute_computation__01 | 1 | seismic_attribute_03_select_type | seismic_attribute_04_configure | 0.90 |  |  | ✗ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.75]; 01_ready_to_start[emb:0.74]; 02_open_attribute_tool[emb:0.72]; 04_add_zslice[emb:0.70]; 03_add_crossline[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |

### rerank input — attribute_computation__01 step 0 (rep 0)

```
You rank workflow steps by how well they match the user's current UI situation.

User goal: F3 Demo survey에서 Energy 속성을 정의하고 In-line 250에 on-the-fly로 표시한다. 매뉴얼 1.5.1a에 따라 툴바의 Attribute 3D 아이콘으로 Attribute Set 3D 창을 연 뒤, Energy 유형을 선택하고 Input Data는 4 Dip steered median filter, Time gate는 [-28,+28], Compute gradient는 No, 속성 이름은 'Energy [-28,+28]'로 설정한다. Add as new 클릭 → Save on Close 체크 → Close로 창을 닫으면 attribute set 저장 다이얼로그가 뜨며 'my first attribute set' 이름을 입력하고 OK. Tree scene에서 In-line 카테고리에 Add Default Data로 기본 seismic을 표시한 뒤 inline 번호를 250으로 변경한다. 표시된 inline 번호를 우클릭하여 Add > Attribute를 선택하고 Attributes 카테고리(on-the-fly)에서 'Energy [-28,+28]'를 선택 → OK. Inline 250에 Energy 속성이 색상 매핑되어 표시되면 목표 달성 (매뉴얼 120쪽 결과 이미지 상태).
Current UI visual_state JSON: {"current_dialog": "Attribute Set 3D", "window_titles": ["Attribute Set 3D", "OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]"], "active_menu": null, "menu_items": ["File", "Survey", "Analysis", "Processing", "Scene", "View", "Utilities", "TerraNubus", "Help"], "buttons": ["Select ...", "Add as new", "Close"], "labels": ["Z 924", "Step 4", "-9968", "9968", "OD Seismic 1", "Attribute set (<not saved>)", "<All>", "Similarity", "Input Data (Seismic_data)", "Time gate (ms) (

Candidate workflow steps (from a software manual):
1. id="seismic_attribute_01_ready_to_start" workflow="seismic_attribute" step=1
   title: 속성 작업 시작 전 (아직 창 미개방)
   desc: 매뉴얼 §1.5 시작 문맥: F3 Demo survey 로드 후 OpendTect Main Window 에서 아직 Attribute Set 3D 창도, 배치 다이얼로그도 열려 있지 않은 상태. 사용자가 toolbar
   expected dialog: OpendTect Main Window
   expected elements: main menu bar, attribute 3d toolbar icon, analysis menu, attributes menu item
   keywords: Analysis menu, Attributes menu item, Create Attribute Set (3D), Attribute 3D toolbar icon (unclicked), no attribute dialog open
2. id="seismic_attribute_02_open_attribute_tool" workflow="seismic_attribute" step=2
   title: Attribute Set 3D 창 열림 (on-the-fly 경로 진입)
   desc: 매뉴얼 §1.5.1a step 1 결과: toolbar Attribute 3D 아이콘 클릭으로 Attribute Set 3D 창이 방금 열림. 비어 있는 attribute set 상태, Attribute Type d
   expected dialog: Attribute Set 3D
   expected elements: attribute type dropdown default, empty attribute set list, input data selector empty, parameter panel disabled
   keywords: Attribute Set 3D, freshly opened, empty attribute set, Attribute Type dropdown, default entry, about to choose an Attribute Type
3. id="seismic_attribute_04_configure" workflow="seismic_attribute" step=4
   title: 속성 파라미터 최종 편집 + attribute set 저장
   desc: 매뉴얼 §1.5.1a steps 3-5 결과의 통합 노드: Time gate 값 (-28..+28) 및 Attribute Name ('Energy [-28,+28]') 이미 입력 완료 → Add as new 로 se
   expected dialog: Attribute Set 3D / Save Attribute Set
   expected elements: add as new button highlighted, save on close checkbox checked, save attribute set dialog, attribute set name field, energy entry in list
   keywords: Time gate populated: -28 to +28, Attribute Name field = 'Energy [-28,+28]', Add as new button (highlighted, Save on Close checkbox = CHECKED, Save Attribute Set
4. id="d3_visualization_04_add_zslice" workflow="d3_visualization" step=4
   title: Z-slice 슬라이스 추가
   desc: Tree scene의 Elements > Z-slice 카테고리 노드를 우클릭하고 'Add Data' 또는 'Add Default Data'를 선택하여 3D Scene에 Z-slice(시간/깊이 슬라이스)를 추가.
   expected dialog: OpendTect Main Window (In-line + Cross-line displayed) / Context menu on Z-slice
   expected elements: inline slice visible, crossline slice visible, zslice context menu, add data item, add default data item
   keywords: Z-slice, Time slice, Depth slice, Add Data, Add Default Data, Add and Select Data, In-line, Cross-line, Elements, 3D Scene
5. id="survey_setup_01_open_selection" workflow="survey_setup" step=1
   title: Survey Setup and Selection 창 열기
   desc: OpendTect 첫 실행 시 Survey Setup and Selection 창이 최상단에 열림. Survey Data Root 리스트에서 새 survey를 만들거나 기존 survey를 선택.
   expected dialog: Survey Setup and Selection
   expected elements: survey data root tab, add button, edit button, select button, cancel button
   keywords: Survey Setup and Selection, Survey Data Root, Add, Edit, Select, Information
6. id="auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03" workflow="follow_along_implementing_a_systematic_s" step=3
   title: Save the Output File and Run the Algorithm
   desc: indicate that the value represents the distance between the points.
   keywords: Save, Output, Run, Algorithm, Regular, Lesson, Systematic, Sampling, Design, indicate
7. id="d3_visualization_01_main_window_ready" workflow="d3_visualization" step=1
   title: Main Window / Tree scene 준비 상태
   desc: Survey가 로드된 상태에서 Main Window와 Tree scene 패널이 열려 있고, Elements 그룹 아래 In-line/Cross-line/Z-slice 카테고리 노드가 표시되나 3D Scene 패널은
   expected dialog: OpendTect Main Window
   expected elements: tree scene panel, elements group, inline category node, crossline category node, zslice category node, empty 3d scene panel
   keywords: Tree scene, Elements, In-line, Cross-line, Z-slice, 3D Scene, F3 Demo, OpendTect

Pick the candidate whose step description best matches what the user is CURRENTLY doing or trying to do next — aligned to the goal, the visible UI state, and the instructions already given.

DECISION RULE:
- Compare the EXACT on-screen strings in visual_state (window/dialog titles, button and field labels, tree entries) with each candidate's dialog/elements/keywords. A candidate whose expected dialog or elements literally appear on screen is a strong match.
- Prefer a candidate from the same workflow as the session's previous steps and the graph prior, unless the screen clearly shows a different application module.
- Return "none" when NO candidate is even loosely related (different application, different module, totally unrelated topic), or when every related candidate is already completed and no successor fits.

CONFIDENCE CALIBRATION (used as a gate: below 0.70 the pick is discarded):
- 0.9–1.0: the candidate's expected dialog title or its specific elements are liter
```
rerank answer: `{"id": "seismic_attribute_04_configure", "confidence": 0.95}` → picked seismic_attribute_04_configure (expected seismic_attribute_02_open_attribute_tool); evidence: None

### rerank input — attribute_computation__01 step 1 (rep 0)

```
You rank workflow steps by how well they match the user's current UI situation.

User goal: F3 Demo survey에서 Energy 속성을 정의하고 In-line 250에 on-the-fly로 표시한다. 매뉴얼 1.5.1a에 따라 툴바의 Attribute 3D 아이콘으로 Attribute Set 3D 창을 연 뒤, Energy 유형을 선택하고 Input Data는 4 Dip steered median filter, Time gate는 [-28,+28], Compute gradient는 No, 속성 이름은 'Energy [-28,+28]'로 설정한다. Add as new 클릭 → Save on Close 체크 → Close로 창을 닫으면 attribute set 저장 다이얼로그가 뜨며 'my first attribute set' 이름을 입력하고 OK. Tree scene에서 In-line 카테고리에 Add Default Data로 기본 seismic을 표시한 뒤 inline 번호를 250으로 변경한다. 표시된 inline 번호를 우클릭하여 Add > Attribute를 선택하고 Attributes 카테고리(on-the-fly)에서 'Energy [-28,+28]'를 선택 → OK. Inline 250에 Energy 속성이 색상 매핑되어 표시되면 목표 달성 (매뉴얼 120쪽 결과 이미지 상태).
Current UI visual_state JSON: {"current_dialog": "Attribute Set 3D", "window_titles": ["Attribute Set 3D", "OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]"], "active_menu": null, "menu_items": ["Survey", "Analysis", "Processing", "Scene", "View", "Utilities", "TerraNubus", "Help", "File"], "buttons": ["Select ...", "Add as new", "Close"], "labels": ["Attribute set (<not saved>)", "<All>", "Energy", "Input Data (Seismic_data)", "Time gate (ms) (-28)", "28", "Compute gradient", "Yes", "No", "Output (E
Candidates matched in previous turns of this session (a step can span several actions — pick one of these again if its dialog is still on screen and the instructions already given do not cover all of its actions): seismic_attribute_04_configure
Graph prior: after the last confirmed step, the workflow expects one of these next: seismic_attribute_05_compute, seismic_attribute_06_display. Prefer them when the screen is consistent with them.

Candidate workflow steps (from a software manual):
1. id="seismic_attribute_05_compute" workflow="seismic_attribute" step=5
   title: 속성 계산 실행 (배치 경로 전용)
   desc: 매뉴얼 §1.5 배치 경로: 저장된 attribute set 에 대해 Batch Processing 다이얼로그를 열고 Go 로 실행하여 stored attribute volume 생성. **§1.5.1a on-the
   expected dialog: Batch Processing
   expected elements: go button batch, progress bar batch, batch dialog only
   keywords: Batch Processing dialog, Go button, Running batch, progress bar, stored attribute volume
2. id="seismic_attribute_06_display" workflow="seismic_attribute" step=6
   title: Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)
   desc: 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attr
   expected dialog: 3D Scene
   expected elements: select dialog attributes radio, attribute color overlay
   keywords: on-the-fly, Add > Attribute, Add > Attribute submenu, on-the-fly energy overlay, no attribute overlay on the inline yet, no attribute rendered yet, Attribute Se
3. id="seismic_attribute_04_configure" workflow="seismic_attribute" step=4
   title: 속성 파라미터 최종 편집 + attribute set 저장
   desc: 매뉴얼 §1.5.1a steps 3-5 결과의 통합 노드: Time gate 값 (-28..+28) 및 Attribute Name ('Energy [-28,+28]') 이미 입력 완료 → Add as new 로 se
   expected dialog: Attribute Set 3D / Save Attribute Set
   expected elements: add as new button highlighted, save on close checkbox checked, save attribute set dialog, attribute set name field, energy entry in list
   keywords: Time gate populated: -28 to +28, Attribute Name field = 'Energy [-28,+28]', Add as new button (highlighted, Save on Close checkbox = CHECKED, Save Attribute Set
4. id="seismic_attribute_01_ready_to_start" workflow="seismic_attribute" step=1
   title: 속성 작업 시작 전 (아직 창 미개방)
   desc: 매뉴얼 §1.5 시작 문맥: F3 Demo survey 로드 후 OpendTect Main Window 에서 아직 Attribute Set 3D 창도, 배치 다이얼로그도 열려 있지 않은 상태. 사용자가 toolbar
   expected dialog: OpendTect Main Window
   expected elements: main menu bar, attribute 3d toolbar icon, analysis menu, attributes menu item
   keywords: Analysis menu, Attributes menu item, Create Attribute Set (3D), Attribute 3D toolbar icon (unclicked), no attribute dialog open
5. id="seismic_attribute_02_open_attribute_tool" workflow="seismic_attribute" step=2
   title: Attribute Set 3D 창 열림 (on-the-fly 경로 진입)
   desc: 매뉴얼 §1.5.1a step 1 결과: toolbar Attribute 3D 아이콘 클릭으로 Attribute Set 3D 창이 방금 열림. 비어 있는 attribute set 상태, Attribute Type d
   expected dialog: Attribute Set 3D
   expected elements: attribute type dropdown default, empty attribute set list, input data selector empty, parameter panel disabled
   keywords: Attribute Set 3D, freshly opened, empty attribute set, Attribute Type dropdown, default entry, about to choose an Attribute Type
6. id="d3_visualization_04_add_zslice" workflow="d3_visualization" step=4
   title: Z-slice 슬라이스 추가
   desc: Tree scene의 Elements > Z-slice 카테고리 노드를 우클릭하고 'Add Data' 또는 'Add Default Data'를 선택하여 3D Scene에 Z-slice(시간/깊이 슬라이스)를 추가.
   expected dialog: OpendTect Main Window (In-line + Cross-line displayed) / Context menu on Z-slice
   expected elements: inline slice visible, crossline slice visible, zslice context menu, add data item, add default data item
   keywords: Z-slice, Time slice, Depth slice, Add Data, Add Default Data, Add and Select Data, In-line, Cross-line, Elements, 3D Scene
7. id="d3_visualization_03_add_crossline" workflow="d3_visualization" step=3
   title: Cross-line 슬라이스 추가
   desc: Tree scene의 Elements > Cross-line 카테고리 노드를 우클릭하고 'Add Data' 또는 'Add Default Data'를 선택하여 3D Scene에 Cross-line 슬라이스를 추가.
   expected dialog: OpendTect Main Window (In-line displayed) / Context menu on Cross-line
   expected elements: inline slice visible, crossline context menu, add data item, add default data item
   keywords: Cross-line, Crossline, Add Data, Add Default Data, Add and Select Data, In-line, 3D Scene, Elements
8. id="auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03" workflow="follow_along_implementing_a_systematic_s" step=3
   title: Save the Output File and Run the Algorithm
   desc: indicate that the value represents the distance between the points.
   keywords: Save, Output, Run, Algorithm, Regular, Lesson, Systematic, Sampling, Des
```
rerank answer: `{
  "id": "seismic_attribute_04_configure",
  "confidence": 0.9
}` → picked seismic_attribute_04_configure (expected seismic_attribute_03_select_type); evidence: None

