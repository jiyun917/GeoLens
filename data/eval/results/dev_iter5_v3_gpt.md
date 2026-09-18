# dev iteration report — dev_iter5_v3_gpt

Runs: dev_iter5_v3_gpt_r0.json (n_rep=1); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).
**Note: iteration 5 (final GT); run alone**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.750 | 0.750 | 0.062 | 0.00357 | 0.00357 | 0.00000 | 2.78 | 2.78 | 0 | 0.00 |
| vanilla_vector | 0.833 | 0.875 | 0.062 | 0.01684 | 0.01684 | 0.00000 | 6.09 | 6.09 | 17780 | 0.75 |
| vanilla_budget | 0.667 | 0.688 | 0.062 | 0.00639 | 0.00639 | 0.00000 | 5.38 | 5.38 | 3900 | 0.75 |
| full_system | 0.792 | 0.812 | 0.125 | 0.01004 | 0.00734 | 0.00270 | 12.54 | 12.54 | 5161 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 0.750 | 0.750 | 0.500 | 0.750 |
| opendtect__3d_visualization__01 | 0.750 | 0.750 | 0.750 | 0.750 |
| opendtect__attribute_computation__01 | 0.750 | 1.000 | 0.750 | 0.875 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: iteration 5 (final GT); run alone — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 2.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.78 | 0.00 | 0.00 | 0.00 | 2.78 |
| vanilla_vector | 6.09 | 0.00 | 0.62 | 0.00 | 0.00 | 0.02 | 0.24 | 5.21 | 0.00 | 0.00 | 0.00 | 6.09 |
| vanilla_budget | 5.38 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | 0.26 | 4.91 | 0.00 | 0.00 | 0.00 | 5.38 |
| full_system | 12.54 | 5.63 | 1.96 | 1.27 | 1.29 | 0.01 | 0.30 | 1.59 | 3.62 | 0.53 | 0.06 | 12.06 |

- extra latency of full_system over vanilla_vector (charged): **+6.45 s/step**; over vanilla_budget: +7.16 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_02_add_inline | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.80 | llm |  | ✓ | ✓/✗/✗ | ✗ | ✗ | ✗ | ✗ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✓ | ✓ | context_or_generation |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✗ | ✓ |  |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✓ | ✓ | context_or_generation |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |

## (a) Routing summary (full_system)

- steps × reps: 16; routed (passed gate): 16; routed correct: 16 (1.00); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **0**
- confidence of correct routed picks: [0.7, 0.7, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- confidence of wrong routed picks: []

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.7, 0.7, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- wrong picks (all): []

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 16 | 0 | 0 |
| 0.65 | 16 | 0 | 0 |
| 0.70 | 16 | 0 | 0 |
| 0.75 | 14 | 0 | 2 |
| 0.80 | 14 | 0 | 2 |
| 0.85 | 13 | 0 | 3 |
| 0.90 | 13 | 0 | 3 |
| 0.95 | 0 | 0 | 16 |

- smallest t with zero wrong picks kept: **0.60** (keeps 16 correct, drops 0 correct to fallback).

## (b) Target-section retrieval hit (context contains the scenario's target section)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| survey_setup__01 | 0/4 | 4/4 | 4/4 | 4/4 |
| 3d_visualization__01 | 0/4 | 0/4 | 0/4 | 4/4 |
| attribute_computation__01 | 0/8 | 8/8 | 8/8 | 8/8 |

## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): {'context_or_generation': 2}

## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)

- no fallback steps in this iteration.
- vanilla_vector untruncated context: mean 17780 chars, max 21002, median 16768.

## Steps every backend failed (same rep) — response text and GT pattern

### 3d_visualization__01 step 2 rep 0

- GT pattern: `(?i)\b(Cross[- ]?line|Add.*Select.*Data|Add Default Data)\b`
- GT keywords: ['Cross-line', 'Add']; allowed alternatives: []
- **no_rag** (target hit ✗; sections —): `'Z-slice'에서 우클릭하여 'Add Data'를 선택하세요.`
- **vanilla_vector** (target hit ✗; sections 1.2.2a, 1.3, 2.3.1c, 2.6.3): `'Z-slice'에서 우클릭하여 'Add Data'를 선택하세요.`
- **vanilla_budget** (target hit ✗; sections 1.2.2a, 1.3, 2.6.3): `'Z-slice'에서 우클릭하여 'Add Data'를 선택하세요.`
- **full_system** (target hit ✓; sections 1.3, 1.3.1, 1.3.1a, 2.3.2b): `Z-slice 카테고리를 우클릭하고 'Add Data'를 선택하세요.`

## Criteria check

- PASS — (a) confident-wrong routes == 0 (0)
- PASS — (a) routing accuracy (routed steps) (16/16)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 0.75)
- FAIL — (c) no loss vs vanilla ({'context_or_generation': 2})

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 0.792 vs 0.833; cost_total 0.01004 vs 0.01684; latency 12.54 vs 6.09 s (extra +6.45 s)
- step_acc fs vs vanilla_budget: 0.792 vs 0.667; cost_total 0.01004 vs 0.00639; latency 12.54 vs 5.38 s (extra +7.16 s)

**Primary criteria NOT met.**

## Loss detail (full_system lost to a vanilla baseline)

### attribute_computation__01 step 7 rep 0 — context_or_generation (picked=seismic_attribute_06_display conf=0.90 expected=seismic_attribute_06_display)

full_system response:
```
표시된 속성의 통계·분포를 QC 하세요.
```
vanilla_vector response:
```
완료
```
full_system context sections: 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot
full_system context head:
```
[Goal State Check]
The workflow's final step appears to be reached: 'Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)' — 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 선택으로 Select dialog 오픈 (label 'Select Layer 2'), Attributes radio (on-the-fly) 선택 시 'Energy [-28,+28]' 표시, (c) OK 로 렌더링 확정 → In-line 250 에 Energy 속성 색상 매핑 오버레이 (color bar 표시, bright-spot 하이라이트). 이 세 스텝 (5, 6, 7) 을 담당.
Completion state of this step: expected dialog/screen: 3D Scene; expected elements: select dialog attributes radio, attribute color overlay
If the screenshot shows that the goal is achieved, respond with the completion sentinel only ('완료' / 'Done'). If one action is still missing, give only that action.

[Same Step As Previous Turn]
The matched workflow step is the same one matched in a previous turn. A step can span several actions. Using the list of instructions already given, continue with the NEXT action of this step that has not been given yet; do not repeat an instruction already given. If every action of this step is done, tell the user to confirm or close the dialog with the button actually
```

### survey_setup__01 step 1 rep 0 — context_or_generation (picked=survey_setup_03_choose_initial_setup conf=0.90 expected=survey_setup)

full_system response:
```
'Scan SEG-Y file(s)'를 선택하고 'Next'를 클릭하세요.
```
vanilla_vector response:
```
Survey name에 "My_F3_Survey"를 입력하세요.
```
full_system context sections: 1.2.2b Load SEG-Y, 1.2.2b Load SEG-Y, 2.1.1b Set up Survey using PetrelDirect, 2.1.1b Set up Survey using PetrelDirect, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y
full_system context head:
```
[Current State (reached)] survey_setup > Step 3: Survey 이름 입력 및 Initial setup 선택
The screen at this step shows — dialog/screen: Create New Survey | elements: survey name filled, initial setup options, scan segy option, enter xy option, next button | states: Create New Survey; My_F3_Survey; Initial setup; Scan SEG-Y; Enter X/Y ranges; Copy from other survey; Next

[Next Action] (from the workflow edge)
  - Next를 눌러 SEG-Y 파일 스캔 단계로 진행하세요 [if: initial_setup == 'Scan SEG-Y file(s)']  (→ Step 4: SEG-Y 파일 스캔 및 geometry 추출)
  - 수동으로 X/Y range 입력 후 survey를 선택하고 Select를 눌러 Main Window로 진입하세요 [if: initial_setup == 'Enter X/Y ranges' (수동 geometry 입력 완료 후)]  (→ Step 5: Survey Select — Main Window 진입)

Note: 매뉴얼의 예시 값(파일명·파라미터)은 사용자의 데이터와 다를 수 있다. 화면에 이미 설정된 값을 고치도록 안내하지 않는다. (Manual example values may differ from the user's data; do not instruct the user to change a value that is already set on screen.)

[Manual Context (graph)]
[Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf, Section: 1.2.2b Load SEG-Y]
[Section: 1.2.2b Load SEG-Y, Page: 31, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTec
```
