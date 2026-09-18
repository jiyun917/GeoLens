# dev iteration report — dev_iter1_v3_gemini

Runs: dev_iter1_v3_gemini_r0.json (n_rep=1); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).
**Note: QGIS re-ingest finished before this run; QGIS relink (15.8 s CPU) ran during the first minutes; stage-instrumented**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.750 | 0.750 | 0.062 | 0.00637 | 0.00637 | 0.00000 | 9.61 | 9.61 | 0 | 0.00 |
| vanilla_vector | 0.792 | 0.750 | 0.125 | 0.01593 | 0.01593 | 0.00000 | 11.57 | 11.57 | 17780 | 0.75 |
| vanilla_budget | 0.792 | 0.812 | 0.125 | 0.00795 | 0.00795 | 0.00000 | 9.60 | 9.60 | 3900 | 0.75 |
| full_system | 0.917 | 0.938 | 0.062 | 0.01105 | 0.00887 | 0.00217 | 21.96 | 21.96 | 4526 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 0.750 | 0.750 | 0.750 | 1.000 |
| opendtect__3d_visualization__01 | 0.750 | 1.000 | 0.750 | 0.750 |
| opendtect__attribute_computation__01 | 0.750 | 0.625 | 0.875 | 1.000 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: QGIS re-ingest finished before this run; QGIS relink (15.8 s CPU) ran during the first minutes; stage-instrumented — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 9.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.61 | 0.00 | 0.00 | 0.00 | 9.61 |
| vanilla_vector | 11.57 | 0.00 | 0.63 | 0.00 | 0.00 | 0.02 | 0.26 | 10.66 | 0.00 | 0.00 | 0.00 | 11.57 |
| vanilla_budget | 9.60 | 0.00 | 0.20 | 0.00 | 0.00 | 0.01 | 0.26 | 9.13 | 0.00 | 0.00 | 0.00 | 9.60 |
| full_system | 21.96 | 5.20 | 1.57 | 1.05 | 1.20 | 0.01 | 0.31 | 11.25 | 4.53 | 0.49 | 0.06 | 20.58 |

- extra latency of full_system over vanilla_vector (charged): **+10.40 s/step**; over vanilla_budget: +12.37 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_02_add_inline | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_04_add_zslice | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✗ | ✓ | ✗ | ✗ | context_or_generation |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.95 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✓ | ✓ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✓ | ✓ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✗ |  |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.95 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |

## (a) Routing summary (full_system)

- steps × reps: 16; routed (passed gate): 16; routed correct: 16 (1.00); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **0**
- confidence of correct routed picks: [0.7, 0.7, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.95, 0.95, 0.95, 0.95]
- confidence of wrong routed picks: []

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.7, 0.7, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.95, 0.95, 0.95, 0.95]
- wrong picks (all): []

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 16 | 0 | 0 |
| 0.65 | 16 | 0 | 0 |
| 0.70 | 16 | 0 | 0 |
| 0.75 | 14 | 0 | 2 |
| 0.80 | 14 | 0 | 2 |
| 0.85 | 14 | 0 | 2 |
| 0.90 | 14 | 0 | 2 |
| 0.95 | 4 | 0 | 12 |

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

- none.

## Criteria check

- PASS — (a) confident-wrong routes == 0 (0)
- PASS — (a) routing accuracy (routed steps) (16/16)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 0.75)
- FAIL — (c) no loss vs vanilla ({'context_or_generation': 1})

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 0.917 vs 0.792; cost_total 0.01105 vs 0.01593; latency 21.96 vs 11.57 s (extra +10.40 s)
- step_acc fs vs vanilla_budget: 0.917 vs 0.792; cost_total 0.01105 vs 0.00795; latency 21.96 vs 9.60 s (extra +12.37 s)

**Primary criteria NOT met.**

## Loss detail (full_system lost to a vanilla baseline)

### 3d_visualization__01 step 3 rep 0 — context_or_generation (picked=d3_visualization_04_add_zslice conf=0.90 expected=d3_visualization)

full_system response:
```
Add Default Data를 클릭하세요.
```
vanilla_vector response:
```
Tree scene 1에서 Z-slice를 마우스 오른쪽 버튼으로 클릭하세요.
```
full_system context sections: 1.3.1 Tree, 1.3.1a Display An Inline, 2.3.2b Volume Curvature And Others, 1.3 Basic Interaction, 1.3 Basic Interaction
full_system context head:
```
[Current Step] d3_visualization > Step 4: Z-slice 슬라이스 추가
Description: Tree scene의 Elements > Z-slice 카테고리 노드를 우클릭하고 'Add Data' 또는 'Add Default Data'를 선택하여 3D Scene에 Z-slice(시간/깊이 슬라이스)를 추가.

[Possible Next Steps]
  - Next (sequential): Step 5 3D Scene에 3개 슬라이스 모두 표시 — 목표 달성 — 세 슬라이스가 모두 표시되면 목표 달성 — '완료'를 출력하세요

[Manual Context (graph)]
[Section: 1.3.1 Tree, Scene & Elements, Page: 45, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf]
1.3.1 Tree, Scene & Elements
Each 3D scene has a tree and each tree controls a set of display elements: In-
lines, Cross-lines, Horizons, Wells etc. Via the tree a user controls what is dis-
played in the 3D scene. (OpendTect Pro users can also do this via the basemap.)
Display elements can be toggled on and off and display parameters can be
changed from the tree menu, which is opened by right-clicking on the element.
Section elements such as In-line, Cross-line can be filled up to 8 layers deep with
data for co-rendering. The layers can be moved up and down in the tree. For co-
rendering the user can change the layer's

[Manual Context (graph)]
[Section: 1.3.1a Display An Inlin
```
