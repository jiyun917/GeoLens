# dev iteration report — latency_baseline_survey_iter1

Runs: latency_baseline_survey_iter1_r0.json (n_rep=1); scorer v3; dev set = opendtect__survey_setup__01 (4 steps).
**Note: clean latency baseline: nothing else running (iteration-1 code)**

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| vanilla_vector | 1.000 | 1.000 | 0.000 | 0.01219 | 0.01219 | 0.00000 | 9.55 | 9.55 | 16582 | 1.00 |
| vanilla_budget | 1.000 | 1.000 | 0.000 | 0.00578 | 0.00578 | 0.00000 | 7.84 | 7.84 | 3900 | 1.00 |
| full_system | 1.000 | 1.000 | 0.000 | 0.01030 | 0.00872 | 0.00158 | 24.10 | 24.10 | 4095 | 1.00 |

## Per-scenario step accuracy (mean over reps)

| scenario | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|
| opendtect__survey_setup__01 | 1.000 | 1.000 | 1.000 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)
Measured while: clean latency baseline: nothing else running (iteration-1 code) — treat absolute values as possibly contaminated; the stage *shares* are still informative.

| backend | wall | vision | embed | clip | rerank | vector_search | neighbor_fetch | generate | localize ⊃ | goal_retrieval ⊃ | routed_retrieval ⊃ | sum(exclusive) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vanilla_vector | 9.55 | 0.00 | 1.86 | 0.00 | 0.00 | 0.06 | 0.22 | 7.42 | 0.00 | 0.00 | 0.00 | 9.55 |
| vanilla_budget | 7.84 | 0.00 | 0.17 | 0.00 | 0.00 | 0.01 | 0.24 | 7.43 | 0.00 | 0.00 | 0.00 | 7.84 |
| full_system | 24.10 | 4.51 | 3.16 | 4.04 | 1.33 | 0.01 | 0.39 | 8.96 | 9.50 | 0.41 | 0.24 | 22.41 |

- extra latency of full_system over vanilla_vector (charged): **+14.55 s/step**; over vanilla_budget: +16.26 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_01_open_selection | 0.95 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | — |  |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | — |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | — |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | — |  |

## (a) Routing summary (full_system)

- steps × reps: 4; routed (passed gate): 4; routed correct: 4 (1.00); fallback: 0 (0.00)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **0**
- confidence of correct routed picks: [0.9, 0.95, 0.95, 0.95]
- confidence of wrong routed picks: []

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.9, 0.95, 0.95, 0.95]
- wrong picks (all): []

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 4 | 0 | 0 |
| 0.65 | 4 | 0 | 0 |
| 0.70 | 4 | 0 | 0 |
| 0.75 | 4 | 0 | 0 |
| 0.80 | 4 | 0 | 0 |
| 0.85 | 4 | 0 | 0 |
| 0.90 | 4 | 0 | 0 |
| 0.95 | 3 | 0 | 1 |

- smallest t with zero wrong picks kept: **0.60** (keeps 4 correct, drops 0 correct to fallback).

## (b) Target-section retrieval hit (context contains the scenario's target section)

| scenario | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|
| survey_setup__01 | 4/4 | 4/4 | 4/4 |

## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): none

## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)

- no fallback steps in this iteration.
- vanilla_vector untruncated context: mean 16582 chars, max 16582, median 16582.

## Steps every backend failed (same rep) — response text and GT pattern

- none.

## Criteria check

- PASS — (a) confident-wrong routes == 0 (0)
- PASS — (a) routing accuracy (routed steps) (4/4)
- PASS — (b) target-section hit fs ≥ vanilla_vector (1.00 vs 1.00)
- PASS — (b) target-section hit fs ≥ vanilla_budget (1.00 vs 1.00)
- PASS — (c) no loss vs vanilla (0)

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 1.000 vs 1.000; cost_total 0.01030 vs 0.01219; latency 24.10 vs 9.55 s (extra +14.55 s)
- step_acc fs vs vanilla_budget: 1.000 vs 1.000; cost_total 0.01030 vs 0.00578; latency 24.10 vs 7.84 s (extra +16.26 s)

**Primary criteria MET.**
