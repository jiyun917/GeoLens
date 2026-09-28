# Study 4 verdict — mechanical application of the pre-registration (tags study4_opendtect + study4_qgis merged per replicate)

runs: gemini n=10, claude n=10, gpt n=10

## §5 judgement (replicate-level, strata = model; hall = v6 as scored)

### 비교 1 (full_system vs vanilla_budget)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.944 | 0.724 | +0.220 | 0.000 | 0.000 | 0.005 | ✓ |
| claude | 0.939 | 0.704 | +0.235 | 0.000 | 0.006 | 0.000 | ✗ |
| gpt | 0.993 | 0.693 | +0.300 | 0.000 | 0.009 | 0.000 | ✗ |

- step: direction 3/3 (ties 0), stratified raw p = 0.0001, Δ = +0.2516, significant reverse: none → 성립
- hall: full ≤ comparator in 1/3 → 불성립
- **grade: A′**

### 비교 2 (full_system vs vanilla_vector)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.944 | 0.742 | +0.201 | 0.000 | 0.000 | 0.004 | ✓ |
| claude | 0.939 | 0.807 | +0.132 | 0.000 | 0.006 | 0.018 | ✓ |
| gpt | 0.993 | 0.707 | +0.286 | 0.000 | 0.009 | 0.000 | ✗ |

- step: direction 3/3 (ties 0), stratified raw p = 0.0001, Δ = +0.2065, significant reverse: none → 성립
- hall: full ≤ comparator in 2/3 → 성립
- **grade: A**

Holm (family 2): 비교 1 0.0001 → 0.0002; 비교 2 0.0001 → 0.0002. **Grades: 비교 1 = A′, 비교 2 = A.**

## Descriptive (mean over replicates, 3 scenarios equally weighted)

| model | backend | step_acc | hall v6 | goal_completion | cost_total $/step | latency s/step |
|---|---|---|---|---|---|---|
| gemini | no_rag | 0.564 | 0.016 | 0.720 | 0.0083 | 11.0 |
| gemini | vanilla_budget | 0.724 | 0.005 | 0.780 | 0.0105 | 11.9 |
| gemini | vanilla_vector | 0.742 | 0.004 | 0.640 | 0.0130 | 12.0 |
| gemini | full_system | 0.944 | 0.000 | 0.780 | 0.0149 | 29.6 |
| claude | no_rag | 0.573 | 0.020 | 0.600 | 0.0066 | 3.1 |
| claude | vanilla_budget | 0.704 | 0.000 | 0.600 | 0.0105 | 3.8 |
| claude | vanilla_vector | 0.807 | 0.018 | 0.580 | 0.0170 | 3.8 |
| claude | full_system | 0.939 | 0.006 | 0.800 | 0.0163 | 21.4 |
| gpt | no_rag | 0.644 | 0.000 | 0.240 | 0.0036 | 1.9 |
| gpt | vanilla_budget | 0.693 | 0.000 | 0.280 | 0.0064 | 2.7 |
| gpt | vanilla_vector | 0.707 | 0.000 | 0.300 | 0.0109 | 2.5 |
| gpt | full_system | 0.993 | 0.009 | 0.680 | 0.0114 | 19.1 |

## Per-scenario step accuracy (mean over replicates)

| model | backend | fault_sticks__01 | horizon_2dviewer__01 | horizon_autotrack__01 | q:reclassify_raster__01 | q:rule_classification__01 |
|---|---|---|---|---|---|---|
| gemini | no_rag | 0.367 | 0.867 | 0.471 | 0.656 | 0.460 |
| gemini | vanilla_budget | 0.411 | 0.833 | 0.843 | 0.911 | 0.620 |
| gemini | vanilla_vector | 0.600 | 0.800 | 0.829 | 0.933 | 0.550 |
| gemini | full_system | 0.978 | 1.000 | 1.000 | 1.000 | 0.740 |
| claude | no_rag | 0.344 | 0.867 | 0.286 | 0.667 | 0.700 |
| claude | vanilla_budget | 0.589 | 0.900 | 0.486 | 0.667 | 0.880 |
| claude | vanilla_vector | 0.856 | 0.933 | 0.729 | 0.667 | 0.850 |
| claude | full_system | 0.944 | 1.000 | 0.871 | 0.900 | 0.980 |
| gpt | no_rag | 0.733 | 0.678 | 0.400 | 0.889 | 0.520 |
| gpt | vanilla_budget | 0.622 | 0.778 | 0.429 | 0.756 | 0.880 |
| gpt | vanilla_vector | 0.744 | 0.667 | 0.414 | 0.878 | 0.830 |
| gpt | full_system | 1.000 | 1.000 | 0.986 | 0.978 | 1.000 |

## Predictions

- Q1/Q7 no_rag mean step_acc per model: gemini 0.564, claude 0.573, gpt 0.644
- Q2 vanilla_budget − no_rag: gemini +0.160, claude +0.132, gpt +0.049 → ≥ +3pp in 3/3 → 적중
- Q3 비교 1 direction 3/3, p 0.0001 → 적중
- Q4 비교 2 direction 3/3, reverse none → 적중
- Q5 hall(v6) full ≤ vanilla_budget 1/3, ≤ vanilla_vector 2/3 → 반증
- Q6 routing gemini: fault_sticks__01 wf 90/90, node 87/90, R2 11, R1 0; horizon_2dviewer__01 wf 80/90, node 70/90, R2 0, R1 1; horizon_autotrack__01 wf 70/70, node 70/70, R2 30, R1 0; q:reclassify_raster__01 wf 90/90, node 82/90, R2 0, R1 0; q:rule_classification__01 wf 90/100, node 50/100, R2 0, R1 0
- Q6 routing claude: fault_sticks__01 wf 90/90, node 78/90, R2 8, R1 0; horizon_2dviewer__01 wf 80/90, node 70/90, R2 5, R1 0; horizon_autotrack__01 wf 70/70, node 58/70, R2 18, R1 0; q:reclassify_raster__01 wf 90/90, node 88/90, R2 0, R1 0; q:rule_classification__01 wf 90/100, node 45/100, R2 0, R1 0
- Q6 routing gpt: fault_sticks__01 wf 90/90, node 90/90, R2 9, R1 0; horizon_2dviewer__01 wf 80/90, node 70/90, R2 2, R1 1; horizon_autotrack__01 wf 70/70, node 55/70, R2 15, R1 0; q:reclassify_raster__01 wf 90/90, node 80/90, R2 0, R1 0; q:rule_classification__01 wf 90/100, node 88/100, R2 18, R1 0
