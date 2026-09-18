# dev iteration report — dev_iter4_v3_gpt

Runs: dev_iter4_v3_gpt_r0.json (n_rep=1); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).
**Note: iteration 4; run alone**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.750 | 0.750 | 0.125 | 0.00357 | 0.00357 | 0.00000 | 1.70 | 1.70 | 0 | 0.00 |
| vanilla_vector | 0.833 | 0.875 | 0.125 | 0.01684 | 0.01684 | 0.00000 | 5.92 | 5.92 | 17780 | 0.75 |
| vanilla_budget | 0.667 | 0.688 | 0.125 | 0.00639 | 0.00639 | 0.00000 | 5.32 | 5.32 | 3900 | 0.75 |
| full_system | 0.833 | 0.875 | 0.125 | 0.00987 | 0.00711 | 0.00275 | 12.64 | 12.64 | 4777 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 0.750 | 0.750 | 0.500 | 0.750 |
| opendtect__3d_visualization__01 | 0.750 | 0.750 | 0.750 | 0.750 |
| opendtect__attribute_computation__01 | 0.750 | 1.000 | 0.750 | 1.000 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: iteration 4; run alone — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 1.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.70 | 0.00 | 0.00 | 0.00 | 1.70 |
| vanilla_vector | 5.92 | 0.00 | 0.62 | 0.00 | 0.00 | 0.02 | 0.25 | 5.02 | 0.00 | 0.00 | 0.00 | 5.91 |
| vanilla_budget | 5.32 | 0.00 | 0.20 | 0.00 | 0.00 | 0.01 | 0.26 | 4.86 | 0.00 | 0.00 | 0.00 | 5.32 |
| full_system | 12.64 | 5.54 | 1.99 | 1.26 | 1.23 | 0.01 | 0.31 | 1.55 | 3.60 | 0.53 | 0.06 | 11.89 |

- extra latency of full_system over vanilla_vector (charged): **+6.72 s/step**; over vanilla_budget: +7.31 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✗ | ✗ | ✗ | ✗ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.85 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✗ | ✓ | context_or_generation |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |

## (a) Routing summary (full_system)

- steps × reps: 16; routed (passed gate): 16; routed correct: 16 (1.00); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **0**
- confidence of correct routed picks: [0.7, 0.85, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- confidence of wrong routed picks: []

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.7, 0.85, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- wrong picks (all): []

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 16 | 0 | 0 |
| 0.65 | 16 | 0 | 0 |
| 0.70 | 16 | 0 | 0 |
| 0.75 | 15 | 0 | 1 |
| 0.80 | 15 | 0 | 1 |
| 0.85 | 15 | 0 | 1 |
| 0.90 | 14 | 0 | 2 |
| 0.95 | 0 | 0 | 16 |

- smallest t with zero wrong picks kept: **0.60** (keeps 16 correct, drops 0 correct to fallback).

## (b) Target-section retrieval hit (context contains the scenario's target section)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| survey_setup__01 | 0/4 | 4/4 | 4/4 | 4/4 |
| 3d_visualization__01 | 0/4 | 0/4 | 0/4 | 4/4 |
| attribute_computation__01 | 0/8 | 8/8 | 8/8 | 8/8 |

## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): {'context_or_generation': 1}

## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)

- no fallback steps in this iteration.
- vanilla_vector untruncated context: mean 17780 chars, max 21002, median 16768.

## Steps every backend failed (same rep) — response text and GT pattern

### 3d_visualization__01 step 2 rep 0

- GT pattern: `(?i)\b(Cross[- ]?line|Add.*Select.*Data|Add Default Data)\b`
- GT keywords: ['Cross-line', 'Add']; allowed alternatives: []
- **no_rag** (target hit ✗; sections —): `'Z-slice'에서 우클릭하여 'Add Data'를 선택하세요.`
- **vanilla_vector** (target hit ✗; sections 1.2.2a, 1.3, 2.3.1c, 2.6.3): `Z-slice에서 우클릭하여 'Add Data'를 선택하세요.`
- **vanilla_budget** (target hit ✗; sections 1.2.2a, 1.3, 2.6.3): `'Z-slice'에서 우클릭하여 'Add Data'를 선택하세요.`
- **full_system** (target hit ✓; sections 1.3, 1.3.1, 1.3.1a, 2.3.1c): `Z-slice를 우클릭하고 'Add Data'를 선택하세요.`

## Criteria check

- PASS — (a) confident-wrong routes == 0 (0)
- PASS — (a) routing accuracy (routed steps) (16/16)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 0.75)
- FAIL — (c) no loss vs vanilla ({'context_or_generation': 1})

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 0.833 vs 0.833; cost_total 0.00987 vs 0.01684; latency 12.64 vs 5.92 s (extra +6.72 s)
- step_acc fs vs vanilla_budget: 0.833 vs 0.667; cost_total 0.00987 vs 0.00639; latency 12.64 vs 5.32 s (extra +7.31 s)

**Primary criteria NOT met.**

## Loss detail (full_system lost to a vanilla baseline)

### survey_setup__01 step 0 rep 0 — context_or_generation (picked=survey_setup_01_open_selection conf=0.90 expected=survey_setup)

full_system response:
```
새로운 설문 아이콘을 클릭하세요.
```
vanilla_vector response:
```
새 Survey 아이콘을 클릭하세요.
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
