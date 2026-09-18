# dev iteration report — dev_iter5_v3_gemini

Runs: dev_iter5_v3_gemini_r0.json, dev_iter5_v3_gemini_r1.json (n_rep=2); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).
**Note: iteration 5 (context assembly v4); run alone**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.750 | 0.719 | 0.031 | 0.00646 | 0.00646 | 0.00000 | 8.96 | 8.96 | 0 | 0.00 |
| vanilla_vector | 0.854 | 0.781 | 0.062 | 0.01477 | 0.01477 | 0.00000 | 10.50 | 10.50 | 17780 | 0.75 |
| vanilla_budget | 0.750 | 0.719 | 0.062 | 0.00795 | 0.00795 | 0.00000 | 9.63 | 9.63 | 3900 | 0.75 |
| full_system | 0.854 | 0.875 | 0.062 | 0.01223 | 0.00944 | 0.00279 | 21.13 | 21.13 | 5170 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 0.875 | 1.000 | 0.875 | 0.875 |
| opendtect__3d_visualization__01 | 0.750 | 1.000 | 0.750 | 0.750 |
| opendtect__attribute_computation__01 | 0.625 | 0.562 | 0.625 | 0.938 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: iteration 5 (context assembly v4); run alone — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 8.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 8.96 | 0.00 | 0.00 | 0.00 | 8.96 |
| vanilla_vector | 10.50 | 0.00 | 0.64 | 0.00 | 0.00 | 0.02 | 0.25 | 9.59 | 0.00 | 0.00 | 0.00 | 10.50 |
| vanilla_budget | 9.63 | 0.00 | 0.20 | 0.00 | 0.00 | 0.01 | 0.25 | 9.17 | 0.00 | 0.00 | 0.00 | 9.63 |
| full_system | 21.13 | 5.83 | 2.06 | 1.26 | 1.24 | 0.01 | 0.30 | 9.80 | 3.66 | 0.52 | 0.06 | 20.50 |

- extra latency of full_system over vanilla_vector (charged): **+10.63 s/step**; over vanilla_budget: +11.51 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 0 | 1 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_02_add_inline | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.75 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✗ | ✓ | ✗ | ✗ | context_or_generation |
| 3d_visualization__01 | 3 | 1 | d3_visualization | d3_visualization_03_add_crossline | 0.80 | llm |  | ✓ | ✓/✗/✗ | ✗ | ✓ | ✗ | ✗ | context_or_generation |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 0 | 1 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 1 | 1 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 1 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 1 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 4 | 1 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 1 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✓ | ✓ | context_or_generation |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 6 | 1 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.80 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 1 | seismic_attribute_06_display | seismic_attribute_06_display | 0.80 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✗ | ✗ | context_or_generation |
| survey_setup__01 | 0 | 1 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 1 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 1 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |

## (a) Routing summary (full_system)

- steps × reps: 32; routed (passed gate): 32; routed correct: 32 (1.00); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **0**
- confidence of correct routed picks: [0.7, 0.7, 0.7, 0.7, 0.75, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- confidence of wrong routed picks: []

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.7, 0.7, 0.7, 0.7, 0.75, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- wrong picks (all): []

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 32 | 0 | 0 |
| 0.65 | 32 | 0 | 0 |
| 0.70 | 32 | 0 | 0 |
| 0.75 | 28 | 0 | 4 |
| 0.80 | 27 | 0 | 5 |
| 0.85 | 24 | 0 | 8 |
| 0.90 | 24 | 0 | 8 |
| 0.95 | 0 | 0 | 32 |

- smallest t with zero wrong picks kept: **0.60** (keeps 32 correct, drops 0 correct to fallback).

## (b) Target-section retrieval hit (context contains the scenario's target section)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| survey_setup__01 | 0/8 | 8/8 | 8/8 | 8/8 |
| 3d_visualization__01 | 0/8 | 0/8 | 0/8 | 8/8 |
| attribute_computation__01 | 0/16 | 16/16 | 16/16 | 16/16 |

## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): {'context_or_generation': 4}

## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)

- no fallback steps in this iteration.
- vanilla_vector untruncated context: mean 17780 chars, max 21002, median 16768.

## Steps every backend failed (same rep) — response text and GT pattern

- none.

## Criteria check

- PASS — (a) confident-wrong routes == 0 (0)
- PASS — (a) routing accuracy (routed steps) (32/32)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 0.75)
- FAIL — (c) no loss vs vanilla ({'context_or_generation': 4})

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 0.854 vs 0.854; cost_total 0.01223 vs 0.01477; latency 21.13 vs 10.50 s (extra +10.63 s)
- step_acc fs vs vanilla_budget: 0.854 vs 0.750; cost_total 0.01223 vs 0.00795; latency 21.13 vs 9.63 s (extra +11.51 s)

**Primary criteria NOT met.**

## Loss detail (full_system lost to a vanilla baseline)

### 3d_visualization__01 step 3 rep 0 — context_or_generation (picked=d3_visualization_03_add_crossline conf=0.70 expected=d3_visualization)

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
[Same Step As Previous Turn]
The matched workflow step is the same one matched in a previous turn. A step can span several actions. Using the list of instructions already given, continue with the NEXT action of this step that has not been given yet; do not repeat an instruction already given. If every action of this step is done, tell the user to confirm or close the dialog with the button actually visible on screen and move on to the next step.

[Current State (reached)] d3_visualization > Step 3: Cross-line 슬라이스 추가
The screen at this step shows — dialog/screen: OpendTect Main Window (In-line displayed) / Context menu on Cross-line | elements: inline slice visible, crossline context menu, add data item, add default data item | states: Cross-line; Crossline; Add Data; Add Default Data; Add and Select Data; In-line; 3D Scene; Elements

[Next Action] (from the workflow edge)
  - Cross-line이 표시되면 Z-slice 카테고리를 우클릭하고 Add Data를 선택하세요  (→ Step 4: Z-slice 슬라이스 추가)

Note: 매뉴얼의 예시 값(파일명·파라미터)은 사용자의 데이터와 다를 수 있다. 화면에 이미 설정된 값을 고치도록 안내하지 않는다. (Manual example values may differ from the user's data; do not instruct the user to change a value that is already set on screen.)

[Manual Context (gra
```

### 3d_visualization__01 step 3 rep 1 — context_or_generation (picked=d3_visualization_03_add_crossline conf=0.80 expected=d3_visualization)

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
[Current State (reached)] d3_visualization > Step 3: Cross-line 슬라이스 추가
The screen at this step shows — dialog/screen: OpendTect Main Window (In-line displayed) / Context menu on Cross-line | elements: inline slice visible, crossline context menu, add data item, add default data item | states: Cross-line; Crossline; Add Data; Add Default Data; Add and Select Data; In-line; 3D Scene; Elements

[Next Action] (from the workflow edge)
  - Cross-line이 표시되면 Z-slice 카테고리를 우클릭하고 Add Data를 선택하세요  (→ Step 4: Z-slice 슬라이스 추가)

Note: 매뉴얼의 예시 값(파일명·파라미터)은 사용자의 데이터와 다를 수 있다. 화면에 이미 설정된 값을 고치도록 안내하지 않는다. (Manual example values may differ from the user's data; do not instruct the user to change a value that is already set on screen.)

[Manual Context (graph)]
[Section: 1.3.1 Tree, Scene & Elements, Page: 45, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf]
1.3.1 Tree, Scene & Elements
Each 3D scene has a tree and each tree controls a set of display elements: In-
lines, Cross-lines, Horizons, Wells etc. Via the tree a user controls what is dis-
played in the 3D scene. (OpendTect Pro users can also do this via the basemap.)
Di
```

### attribute_computation__01 step 5 rep 1 — context_or_generation (picked=seismic_attribute_06_display conf=0.70 expected=seismic_attribute_06_display)

full_system response:
```
Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.
```
vanilla_vector response:
```
Tree scene에서 In-line 카테고리를 마우스 오른쪽 버튼으로 클릭합니다.
```
full_system context sections: 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot
full_system context head:
```
[Goal State Check]
The workflow's final step appears to be reached: 'Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)' — 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 선택으로 Select dialog 오픈 (label 'Select Layer 2'), Attributes radio (on-the-fly) 선택 시 'Energy [-28,+28]' 표시, (c) OK 로 렌더링 확정 → In-line 250 에 Energy 속성 색상 매핑 오버레이 (color bar 표시, bright-spot 하이라이트). 이 세 스텝 (5, 6, 7) 을 담당.
Completion state of this step: expected dialog/screen: 3D Scene; expected elements: select dialog attributes radio, attribute color overlay
If the screenshot shows that the goal is achieved, respond with the completion sentinel only ('완료' / 'Done'). If one action is still missing, give only that action.

[Current State (reached)] seismic_attribute > Step 6: Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)
The screen at this step shows — dialog/screen: 3D Scene | elements: select dialog attributes radio, attribute color overlay | states: on-the-fly; Add > Attribute; Add > Attribute submenu; on-the-fly energy overlay; no attribute overlay on the inline yet; no attribute rendered 
```

### survey_setup__01 step 0 rep 0 — context_or_generation (picked=survey_setup_01_open_selection conf=0.90 expected=survey_setup)

full_system response:
```
새 서베이 추가 아이콘을 클릭하세요.
```
vanilla_vector response:
```
새 survey 아이콘을 클릭합니다.
```
full_system context sections: 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y
full_system context head:
```
[Current State (reached)] survey_setup > Step 1: Survey Setup and Selection 창 열기
The screen at this step shows — dialog/screen: Survey Setup and Selection | elements: survey data root tab, add button, edit button, select button, cancel button | states: Survey Setup and Selection; Survey Data Root; Add; Edit; Select; Information

[Next Action] (from the workflow edge)
  - Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요  (→ Step 2: Create New Survey 다이얼로그 열기)

Note: 매뉴얼의 예시 값(파일명·파라미터)은 사용자의 데이터와 다를 수 있다. 화면에 이미 설정된 값을 고치도록 안내하지 않는다. (Manual example values may differ from the user's data; do not instruct the user to change a value that is already set on screen.)

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
   or click on the Su
```
