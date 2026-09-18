# dev iteration report — dev_iter4_v3_gemini

Runs: dev_iter4_v3_gemini_r0.json, dev_iter4_v3_gemini_r1.json (n_rep=2); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).
**Note: iteration 4 (corrected group prior); run alone**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.708 | 0.656 | 0.094 | 0.00620 | 0.00620 | 0.00000 | 8.81 | 8.81 | 0 | 0.00 |
| vanilla_vector | 0.771 | 0.719 | 0.125 | 0.01455 | 0.01455 | 0.00000 | 10.24 | 10.24 | 17780 | 0.75 |
| vanilla_budget | 0.771 | 0.719 | 0.125 | 0.00783 | 0.00783 | 0.00000 | 9.23 | 9.23 | 3900 | 0.75 |
| full_system | 0.792 | 0.781 | 0.125 | 0.01231 | 0.00953 | 0.00278 | 21.47 | 21.47 | 4744 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 0.875 | 0.875 | 1.000 | 0.750 |
| opendtect__3d_visualization__01 | 0.750 | 0.875 | 0.750 | 0.875 |
| opendtect__attribute_computation__01 | 0.500 | 0.562 | 0.562 | 0.750 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: iteration 4 (corrected group prior); run alone — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 8.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 8.81 | 0.00 | 0.00 | 0.00 | 8.81 |
| vanilla_vector | 10.24 | 0.00 | 0.65 | 0.00 | 0.00 | 0.02 | 0.25 | 9.32 | 0.00 | 0.00 | 0.00 | 10.24 |
| vanilla_budget | 9.23 | 0.00 | 0.20 | 0.00 | 0.00 | 0.01 | 0.26 | 8.76 | 0.00 | 0.00 | 0.00 | 9.23 |
| full_system | 21.47 | 5.69 | 2.09 | 1.26 | 1.32 | 0.01 | 0.30 | 10.12 | 3.77 | 0.53 | 0.06 | 20.79 |

- extra latency of full_system over vanilla_vector (charged): **+11.23 s/step**; over vanilla_budget: +12.24 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 0 | 1 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 1 | d3_visualization | d3_visualization_03_add_crossline | 0.80 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✗ | ✗ | ✗ |  |
| 3d_visualization__01 | 3 | 1 | d3_visualization | d3_visualization_04_add_zslice | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✗ | ✓ | ✗ | ✗ | context_or_generation |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 0 | 1 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 1 | 1 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_03_select_type | 0.90 | llm |  | ✗ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 1 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 1 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 4 | 1 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✗ | ✓ | ✗ | context_or_generation |
| attribute_computation__01 | 5 | 1 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✓ | ✗ | context_or_generation |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.85 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 6 | 1 | seismic_attribute_06_display | seismic_attribute_06_display | 0.75 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.80 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✗ | ✓ |  |
| attribute_computation__01 | 7 | 1 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✗ | ✓ | ✗ | context_or_generation |
| survey_setup__01 | 0 | 1 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✓ | ✓ | context_or_generation |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 1 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✗ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 1 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |

## (a) Routing summary (full_system)

- steps × reps: 32; routed (passed gate): 32; routed correct: 30 (0.94); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **2**
- confidence of correct routed picks: [0.7, 0.7, 0.7, 0.7, 0.75, 0.8, 0.8, 0.85, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- confidence of wrong routed picks: [0.9, 0.9]

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.7, 0.7, 0.7, 0.7, 0.75, 0.8, 0.8, 0.85, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- wrong picks (all): [0.9, 0.9]

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 30 | 2 | 0 |
| 0.65 | 30 | 2 | 0 |
| 0.70 | 30 | 2 | 0 |
| 0.75 | 26 | 2 | 4 |
| 0.80 | 25 | 2 | 5 |
| 0.85 | 23 | 2 | 7 |
| 0.90 | 22 | 2 | 8 |
| 0.95 | 0 | 0 | 30 |

- smallest t with zero wrong picks kept: **0.95** (keeps 0 correct, drops 30 correct to fallback).

## (b) Target-section retrieval hit (context contains the scenario's target section)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| survey_setup__01 | 0/8 | 8/8 | 8/8 | 8/8 |
| 3d_visualization__01 | 0/8 | 0/8 | 0/8 | 8/8 |
| attribute_computation__01 | 0/16 | 16/16 | 16/16 | 16/16 |

## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): {'context_or_generation': 5}

## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)

- no fallback steps in this iteration.
- vanilla_vector untruncated context: mean 17780 chars, max 21002, median 16768.

## Steps every backend failed (same rep) — response text and GT pattern

### attribute_computation__01 step 1 rep 0

- GT pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b`
- GT keywords: ['Time gate']; allowed alternatives: [{'pattern': '(?i)\\b(입력|Enter|설정|Set).*(Time gate|Name|이름)\\b', 'note': 'Enter/set verb + target.'}, {'pattern': '(?i)\\b(Compute gradient)\\b', 'note': 'Compute gradient parameter is a valid focus (kept at No).'}]
- **no_rag** (target hit ✗; sections —): `Select... 버튼을 클릭하세요.`
- **vanilla_vector** (target hit ✓; sections 1.5.1a, 2.3.1c, 2.5.1a): `Select... 버튼을 클릭하십시오.`
- **vanilla_budget** (target hit ✓; sections 1.5.1a): `Input Data 옆에 있는 Seismic_data 드롭다운 메뉴를 클릭합니다.`
- **full_system** (target hit ✓; sections 1.5.1a): `Input Data 옆에 있는 Seismic_data 드롭다운 메뉴를 클릭하세요.`

### attribute_computation__01 step 1 rep 1

- GT pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b`
- GT keywords: ['Time gate']; allowed alternatives: [{'pattern': '(?i)\\b(입력|Enter|설정|Set).*(Time gate|Name|이름)\\b', 'note': 'Enter/set verb + target.'}, {'pattern': '(?i)\\b(Compute gradient)\\b', 'note': 'Compute gradient parameter is a valid focus (kept at No).'}]
- **no_rag** (target hit ✗; sections —): `Select... 버튼을 클릭하세요.`
- **vanilla_vector** (target hit ✓; sections 1.5.1a, 2.3.1c, 2.5.1a): `Select... 버튼을 클릭합니다.`
- **vanilla_budget** (target hit ✓; sections 1.5.1a): `Input Data 옆에 있는 Seismic_data 드롭다운 메뉴를 클릭합니다.`
- **full_system** (target hit ✓; sections 1.5.1a): `Input Data 드롭다운 메뉴에서 4 Dip steered median filter를 선택하세요.`

## Criteria check

- FAIL — (a) confident-wrong routes == 0 (2)
- FAIL — (a) routing accuracy (routed steps) (30/32)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 0.75)
- FAIL — (c) no loss vs vanilla ({'context_or_generation': 5})

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 0.792 vs 0.771; cost_total 0.01231 vs 0.01455; latency 21.47 vs 10.24 s (extra +11.23 s)
- step_acc fs vs vanilla_budget: 0.792 vs 0.771; cost_total 0.01231 vs 0.00783; latency 21.47 vs 9.23 s (extra +12.24 s)

**Primary criteria NOT met.**

## Loss detail (full_system lost to a vanilla baseline)

### 3d_visualization__01 step 3 rep 1 — context_or_generation (picked=d3_visualization_04_add_zslice conf=0.90 expected=d3_visualization)

full_system response:
```
Add Default Data를 클릭하세요.
```
vanilla_vector response:
```
완료
```
full_system context sections: 1.3.1 Tree, 1.3.1a Display An Inline, 2.3.2b Volume Curvature And Others, 1.3 Basic Interaction, 1.3 Basic Interaction
full_system context head:
```
[Goal State Check]
The workflow's final step appears to be reached: 'Z-slice 슬라이스 추가' — Tree scene의 Elements > Z-slice 카테고리 노드를 우클릭하고 'Add Data' 또는 'Add Default Data'를 선택하여 3D Scene에 Z-slice(시간/깊이 슬라이스)를 추가.
Completion state of this step: expected dialog/screen: OpendTect Main Window (In-line + Cross-line displayed) / Context menu on Z-slice; expected elements: inline slice visible, crossline slice visible, zslice context menu, add data item, add default data item
If the screenshot shows that the goal is achieved, respond with the completion sentinel only ('완료' / 'Done'). If one action is still missing, give only that action.

[Current Step] d3_visualization > Step 4: Z-slice 슬라이스 추가
Description: Tree scene의 Elements > Z-slice 카테고리 노드를 우클릭하고 'Add Data' 또는 'Add Default Data'를 선택하여 3D Scene에 Z-slice(시간/깊이 슬라이스)를 추가.

[Possible Next Steps]
  - Next (sequential): Step 5 3D Scene에 3개 슬라이스 모두 표시 — 목표 달성 — 세 슬라이스가 모두 표시되면 목표 달성 — '완료'를 출력하세요

[Manual Context (graph)]
[Section: 1.3.1 Tree, Scene & Elements, Page: 45, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf]
1.3.1 Tree, Scene & Elements
Each 3D scene has a tre
```

### attribute_computation__01 step 5 rep 0 — context_or_generation (picked=seismic_attribute_06_display conf=0.70 expected=seismic_attribute_06_display)

full_system response:
```
Tree scene 1의 250을 마우스 오른쪽 버튼으로 클릭하세요.
```
vanilla_vector response:
```
250을 마우스 오른쪽 버튼으로 클릭하십시오.
```
full_system context sections: 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot
full_system context head:
```
[Goal State Check]
The workflow's final step appears to be reached: 'Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)' — 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 선택으로 Select dialog 오픈 (label 'Select Layer 2'), Attributes radio (on-the-fly) 선택 시 'Energy [-28,+28]' 표시, (c) OK 로 렌더링 확정 → In-line 250 에 Energy 속성 색상 매핑 오버레이 (color bar 표시, bright-spot 하이라이트). 이 세 스텝 (5, 6, 7) 을 담당.
Completion state of this step: expected dialog/screen: 3D Scene; expected elements: select dialog attributes radio, attribute color overlay
If the screenshot shows that the goal is achieved, respond with the completion sentinel only ('완료' / 'Done'). If one action is still missing, give only that action.

[Current Step] seismic_attribute > Step 6: Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)
Description: 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 선택으로 Select dialog 오픈 (label 'Select Layer 2'), Attributes radio (on-the-fly) 선택 시 'Energy [-28,+28]' 표시, (c) OK 로 렌더링 확정 → In-line 250 에 Ene
```

### attribute_computation__01 step 5 rep 1 — context_or_generation (picked=seismic_attribute_06_display conf=0.70 expected=seismic_attribute_06_display)

full_system response:
```
Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.
```
vanilla_vector response:
```
Tree scene에서 In-line 아래에 있는 250을 마우스 오른쪽 버튼으로 클릭합니다.
```
full_system context sections: 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot
full_system context head:
```
[Goal State Check]
The workflow's final step appears to be reached: 'Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)' — 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 선택으로 Select dialog 오픈 (label 'Select Layer 2'), Attributes radio (on-the-fly) 선택 시 'Energy [-28,+28]' 표시, (c) OK 로 렌더링 확정 → In-line 250 에 Energy 속성 색상 매핑 오버레이 (color bar 표시, bright-spot 하이라이트). 이 세 스텝 (5, 6, 7) 을 담당.
Completion state of this step: expected dialog/screen: 3D Scene; expected elements: select dialog attributes radio, attribute color overlay
If the screenshot shows that the goal is achieved, respond with the completion sentinel only ('완료' / 'Done'). If one action is still missing, give only that action.

[Current Step] seismic_attribute > Step 6: Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)
Description: 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 선택으로 Select dialog 오픈 (label 'Select Layer 2'), Attributes radio (on-the-fly) 선택 시 'Energy [-28,+28]' 표시, (c) OK 로 렌더링 확정 → In-line 250 에 Ene
```

### survey_setup__01 step 0 rep 0 — context_or_generation (picked=survey_setup_01_open_selection conf=0.90 expected=survey_setup)

full_system response:
```
녹색 더하기 아이콘을 클릭하세요.
```
vanilla_vector response:
```
새 서베이 아이콘을 클릭하세요.
```
full_system context sections: 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y
full_system context head:
```
[Current Step] survey_setup > Step 1: Survey Setup and Selection 창 열기
Description: OpendTect 첫 실행 시 Survey Setup and Selection 창이 최상단에 열림. Survey Data Root 리스트에서 새 survey를 만들거나 기존 survey를 선택.

[Possible Next Steps]
  - Next (sequential): Step 2 Create New Survey 다이얼로그 열기 — Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요

[Manual Context (graph)]
[Section: 1.2.2a Survey Setup & Load SEG-Y, Page: 21, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf]
1.2.2a Survey Setup & Load SEG-Y
Required licenses: OpendTect.
For a video of these exercises: OpendTect video resources
- 21 -

[Figure OCR p.21 #1]
Exercise objective:
Set up a new OpendTect survey and load 3D seismic data from SEGY using the SEGY scan wizard.

Workflow:

1. Go to Survey > Select/Setup...
   or click on the Survey Setup icon .
2. Click on the New Survey icon .

Survey Analysis P
Select/Setup ...
Session
Import

List of all Surveys in this Survey Data Root
directory.

Survey Setup and Selection
Survey Data Root: ... C:\Surveys

F3_Demo_2020
F3_Demo_2020_20jul21
F3_Demo_2020_old
My_New_Survey_AL
My_

[Manual Context (graph)]
[Section: 1.2.2a Survey Set
```

### survey_setup__01 step 0 rep 1 — context_or_generation (picked=survey_setup_01_open_selection conf=0.90 expected=survey_setup)

full_system response:
```
초록색 플러스 아이콘을 클릭하세요.
```
vanilla_vector response:
```
새 survey 아이콘을 클릭합니다.
```
full_system context sections: 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y
full_system context head:
```
[Current Step] survey_setup > Step 1: Survey Setup and Selection 창 열기
Description: OpendTect 첫 실행 시 Survey Setup and Selection 창이 최상단에 열림. Survey Data Root 리스트에서 새 survey를 만들거나 기존 survey를 선택.

[Possible Next Steps]
  - Next (sequential): Step 2 Create New Survey 다이얼로그 열기 — Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요

[Manual Context (graph)]
[Section: 1.2.2a Survey Setup & Load SEG-Y, Page: 21, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf]
1.2.2a Survey Setup & Load SEG-Y
Required licenses: OpendTect.
For a video of these exercises: OpendTect video resources
- 21 -

[Figure OCR p.21 #1]
Exercise objective:
Set up a new OpendTect survey and load 3D seismic data from SEGY using the SEGY scan wizard.

Workflow:

1. Go to Survey > Select/Setup...
   or click on the Survey Setup icon .
2. Click on the New Survey icon .

Survey Analysis P
Select/Setup ...
Session
Import

List of all Surveys in this Survey Data Root
directory.

Survey Setup and Selection
Survey Data Root: ... C:\Surveys

F3_Demo_2020
F3_Demo_2020_20jul21
F3_Demo_2020_old
My_New_Survey_AL
My_

[Manual Context (graph)]
[Section: 1.2.2a Survey Set
```
