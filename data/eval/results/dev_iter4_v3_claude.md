# dev iteration report — dev_iter4_v3_claude

Runs: dev_iter4_v3_claude_r0.json (n_rep=1); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).
**Note: iteration 4; run alone**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.875 | 0.812 | 0.125 | 0.00655 | 0.00655 | 0.00000 | 3.44 | 3.44 | 0 | 0.00 |
| vanilla_vector | 0.875 | 0.812 | 0.125 | 0.02533 | 0.02533 | 0.00000 | 4.09 | 4.09 | 17780 | 0.75 |
| vanilla_budget | 0.875 | 0.812 | 0.125 | 0.01050 | 0.01050 | 0.00000 | 4.65 | 4.65 | 3900 | 0.75 |
| full_system | 0.875 | 0.812 | 0.125 | 0.01445 | 0.01168 | 0.00278 | 15.18 | 15.18 | 4740 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 1.000 | 1.000 | 1.000 | 1.000 |
| opendtect__3d_visualization__01 | 1.000 | 1.000 | 1.000 | 1.000 |
| opendtect__attribute_computation__01 | 0.625 | 0.625 | 0.625 | 0.625 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: iteration 4; run alone — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 3.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.44 | 0.00 | 0.00 | 0.00 | 3.44 |
| vanilla_vector | 4.09 | 0.00 | 0.63 | 0.00 | 0.00 | 0.02 | 0.24 | 3.19 | 0.00 | 0.00 | 0.00 | 4.09 |
| vanilla_budget | 4.65 | 0.00 | 0.21 | 0.00 | 0.00 | 0.01 | 0.25 | 4.18 | 0.00 | 0.00 | 0.00 | 4.65 |
| full_system | 15.18 | 6.19 | 2.10 | 1.32 | 1.28 | 0.01 | 0.31 | 3.29 | 3.72 | 0.54 | 0.06 | 14.50 |

- extra latency of full_system over vanilla_vector (charged): **+11.09 s/step**; over vanilla_budget: +10.53 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_02_add_inline | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.75 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.80 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.80 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |

## (a) Routing summary (full_system)

- steps × reps: 16; routed (passed gate): 16; routed correct: 16 (1.00); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **0**
- confidence of correct routed picks: [0.75, 0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- confidence of wrong routed picks: []

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.75, 0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- wrong picks (all): []

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 16 | 0 | 0 |
| 0.65 | 16 | 0 | 0 |
| 0.70 | 16 | 0 | 0 |
| 0.75 | 16 | 0 | 0 |
| 0.80 | 15 | 0 | 1 |
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

## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): none

## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)

- no fallback steps in this iteration.
- vanilla_vector untruncated context: mean 17780 chars, max 21002, median 16768.

## Steps every backend failed (same rep) — response text and GT pattern

### attribute_computation__01 step 1 rep 0

- GT pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b`
- GT keywords: ['Time gate']; allowed alternatives: [{'pattern': '(?i)\\b(입력|Enter|설정|Set).*(Time gate|Name|이름)\\b', 'note': 'Enter/set verb + target.'}, {'pattern': '(?i)\\b(Compute gradient)\\b', 'note': 'Compute gradient parameter is a valid focus (kept at No).'}]
- **no_rag** (target hit ✗; sections —): `Input Data 드롭다운을 클릭하여 '4 Dip steered median filter'를 선택한다.`
- **vanilla_vector** (target hit ✓; sections 1.5.1a, 2.3.1c, 2.5.1a): `Input Data를 "4 Dip steered median filter"로 변경하기 위해 Input Data 드롭다운("Seismic_data")을 클릭하세요.`
- **vanilla_budget** (target hit ✓; sections 1.5.1a): `Input Data를 "4 Dip steered median filter"로 변경하기 위해 Input Data 드롭다운을 클릭하세요.`
- **full_system** (target hit ✓; sections 1.5.1a): `Input Data를 "4 Dip steered median filter"로 변경하기 위해 Input Data 드롭다운(현재 "Seismic_data")을 클릭하세요.`

### attribute_computation__01 step 2 rep 0

- GT pattern: `(?i)\b(Add as new|Add|추가|new)\b`
- GT keywords: ['Add as new']; allowed alternatives: [{'pattern': '(?i)\\b(Add)\\b', 'note': "The Add / 'Add as new' button commits this attribute to the set."}]
- **no_rag** (target hit ✗; sections —): `Input Data 드롭다운을 클릭하여 '4 Dip steered median filter'를 선택합니다.`
- **vanilla_vector** (target hit ✓; sections 1.5.1a, 2.3.1c, 2.5.1a): `Input Data 드롭다운("Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.`
- **vanilla_budget** (target hit ✓; sections 1.5.1a): `Input Data 드롭다운("Seismic_data")을 클릭하여 "4 Dip steered median filter"로 변경하세요.`
- **full_system** (target hit ✓; sections 1.5.1a): `Input Data 드롭다운(현재 "Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.`

### attribute_computation__01 step 3 rep 0

- GT pattern: `(?i)\b(Close|Save on Close|Save|닫기|저장)\b`
- GT keywords: ['Close']; allowed alternatives: [{'pattern': '(?i)\\b(Save on Close)\\b', 'note': 'Confirming the checkbox is set is acceptable.'}]
- **no_rag** (target hit ✗; sections —): `Input Data 드롭다운을 클릭하여 '4 Dip steered median filter'를 선택합니다.`
- **vanilla_vector** (target hit ✓; sections 1.5.1a, 2.3.1c, 2.5.1a): `Input Data 드롭다운("Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.`
- **vanilla_budget** (target hit ✓; sections 1.5.1a): `Input Data가 아직 "Seismic_data"로 되어 있으므로, Input Data 드롭다운을 클릭하여 "4 Dip steered median filter"로 변경하세요.`
- **full_system** (target hit ✓; sections 1.5.1a): `Input Data 드롭다운(현재 "Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.`

## Criteria check

- PASS — (a) confident-wrong routes == 0 (0)
- PASS — (a) routing accuracy (routed steps) (16/16)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 0.75)
- PASS — (c) no loss vs vanilla (0)

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 0.875 vs 0.875; cost_total 0.01445 vs 0.02533; latency 15.18 vs 4.09 s (extra +11.09 s)
- step_acc fs vs vanilla_budget: 0.875 vs 0.875; cost_total 0.01445 vs 0.01050; latency 15.18 vs 4.65 s (extra +10.53 s)

**Primary criteria MET.**
