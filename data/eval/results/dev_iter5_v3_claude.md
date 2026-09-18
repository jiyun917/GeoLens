# dev iteration report — dev_iter5_v3_claude

Runs: dev_iter5_v3_claude_r0.json (n_rep=1); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).
**Note: iteration 5 (context assembly v4, final GT 2f3db66); rerun after Gemini credit recharge; run alone**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.875 | 0.812 | 0.062 | 0.00670 | 0.00670 | 0.00000 | 2.44 | 2.44 | 0 | 0.00 |
| vanilla_vector | 0.875 | 0.812 | 0.062 | 0.02539 | 0.02539 | 0.00000 | 3.48 | 3.48 | 17780 | 0.75 |
| vanilla_budget | 0.875 | 0.812 | 0.062 | 0.01057 | 0.01057 | 0.00000 | 2.96 | 2.96 | 3900 | 0.75 |
| full_system | 1.000 | 1.000 | 0.062 | 0.01456 | 0.01179 | 0.00278 | 13.97 | 13.97 | 5183 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 1.000 | 1.000 | 1.000 | 1.000 |
| opendtect__3d_visualization__01 | 1.000 | 1.000 | 1.000 | 1.000 |
| opendtect__attribute_computation__01 | 0.625 | 0.625 | 0.625 | 1.000 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: iteration 5 (context assembly v4, final GT 2f3db66); rerun after Gemini credit recharge; run alone — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 2.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.44 | 0.00 | 0.00 | 0.00 | 2.44 |
| vanilla_vector | 3.48 | 0.00 | 0.63 | 0.00 | 0.00 | 0.02 | 0.25 | 2.59 | 0.00 | 0.00 | 0.00 | 3.48 |
| vanilla_budget | 2.96 | 0.00 | 0.20 | 0.00 | 0.00 | 0.01 | 0.25 | 2.50 | 0.00 | 0.00 | 0.00 | 2.96 |
| full_system | 13.97 | 5.76 | 2.05 | 1.30 | 1.30 | 0.01 | 0.31 | 2.62 | 3.70 | 0.53 | 0.06 | 13.34 |

- extra latency of full_system over vanilla_vector (charged): **+10.49 s/step**; over vanilla_budget: +11.01 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_02_add_inline | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_04_add_zslice | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_02_open_attribute_tool | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_03_select_type | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.75 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.75 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |

## (a) Routing summary (full_system)

- steps × reps: 16; routed (passed gate): 16; routed correct: 16 (1.00); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **0**
- confidence of correct routed picks: [0.7, 0.7, 0.7, 0.7, 0.75, 0.75, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- confidence of wrong routed picks: []

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.7, 0.7, 0.7, 0.7, 0.75, 0.75, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
- wrong picks (all): []

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 16 | 0 | 0 |
| 0.65 | 16 | 0 | 0 |
| 0.70 | 16 | 0 | 0 |
| 0.75 | 12 | 0 | 4 |
| 0.80 | 10 | 0 | 6 |
| 0.85 | 10 | 0 | 6 |
| 0.90 | 10 | 0 | 6 |
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

- none.

## Criteria check

- PASS — (a) confident-wrong routes == 0 (0)
- PASS — (a) routing accuracy (routed steps) (16/16)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 0.75)
- PASS — (c) no loss vs vanilla (0)

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 1.000 vs 0.875; cost_total 0.01456 vs 0.02539; latency 13.97 vs 3.48 s (extra +10.49 s)
- step_acc fs vs vanilla_budget: 1.000 vs 0.875; cost_total 0.01456 vs 0.01057; latency 13.97 vs 2.96 s (extra +11.01 s)

**Primary criteria MET.**
