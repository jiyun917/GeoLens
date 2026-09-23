# Study 3 verdict — mechanical application of the pre-registration (tags study3_opendtect + study3_qgis merged per replicate)

runs: gemini n=10, claude n=10, gpt n=10

## §5 judgement (replicate-level, strata = model; hall = v5 as scored)

### 비교 1 (full_system vs vanilla_budget)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.782 | 0.710 | +0.072 | 0.150 | 0.007 | 0.003 | ✗ |
| claude | 0.881 | 0.770 | +0.112 | 0.000 | 0.093 | 0.041 | ✗ |
| gpt | 0.780 | 0.634 | +0.146 | 0.000 | 0.007 | 0.010 | ✓ |

- step: direction 3/3 (ties 0), stratified raw p = 0.0001, Δ = +0.1098, significant reverse: none → 성립
- hall: full ≤ comparator in 1/3 → 불성립
- **grade: A′**

### 비교 2 (full_system vs vanilla_vector)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.782 | 0.754 | +0.029 | 0.506 | 0.007 | 0.003 | ✗ |
| claude | 0.881 | 0.776 | +0.105 | 0.000 | 0.093 | 0.033 | ✗ |
| gpt | 0.780 | 0.831 | -0.051 | 0.111 | 0.007 | 0.000 | ✗ |

- step: direction 2/3 (ties 0), stratified raw p = 0.1651, Δ = +0.0274, significant reverse: none → 불성립
- hall: full ≤ comparator in 0/3 → 불성립
- **grade: B**

Holm (family 2): 비교 1 0.0001 → 0.0002; 비교 2 0.1651 → 0.1651. **Grades: 비교 1 = A′, 비교 2 = B.**

## Descriptive (mean over replicates, 3 scenarios equally weighted)

| model | backend | step_acc | hall v5 | goal_completion | cost_total $/step | latency s/step |
|---|---|---|---|---|---|---|
| gemini | no_rag | 0.633 | 0.056 | 0.933 | 0.0081 | 12.2 |
| gemini | vanilla_budget | 0.710 | 0.003 | 0.933 | 0.0097 | 12.8 |
| gemini | vanilla_vector | 0.754 | 0.003 | 0.967 | 0.0122 | 12.7 |
| gemini | full_system | 0.782 | 0.007 | 0.933 | 0.0129 | 34.4 |
| claude | no_rag | 0.779 | 0.033 | 1.000 | 0.0065 | 3.2 |
| claude | vanilla_budget | 0.770 | 0.041 | 1.000 | 0.0104 | 4.5 |
| claude | vanilla_vector | 0.776 | 0.033 | 1.000 | 0.0157 | 4.0 |
| claude | full_system | 0.881 | 0.093 | 1.000 | 0.0147 | 26.1 |
| gpt | no_rag | 0.734 | 0.007 | 0.667 | 0.0036 | 2.0 |
| gpt | vanilla_budget | 0.634 | 0.010 | 0.467 | 0.0063 | 2.8 |
| gpt | vanilla_vector | 0.831 | 0.000 | 0.600 | 0.0101 | 2.4 |
| gpt | full_system | 0.780 | 0.007 | 1.000 | 0.0100 | 23.6 |

## Per-scenario step accuracy (mean over replicates)

| model | backend | horizon_2dviewer__01 | q:reclassify_raster__01 | q:rule_classification__01 |
|---|---|---|---|---|
| gemini | no_rag | 0.889 | 0.589 | 0.420 |
| gemini | vanilla_budget | 0.811 | 0.700 | 0.620 |
| gemini | vanilla_vector | 0.922 | 0.689 | 0.650 |
| gemini | full_system | 1.000 | 0.767 | 0.580 |
| claude | no_rag | 0.889 | 0.667 | 0.780 |
| claude | vanilla_budget | 0.922 | 0.667 | 0.720 |
| claude | vanilla_vector | 0.922 | 0.667 | 0.740 |
| claude | full_system | 0.978 | 0.767 | 0.900 |
| gpt | no_rag | 0.756 | 0.856 | 0.590 |
| gpt | vanilla_budget | 0.778 | 0.344 | 0.780 |
| gpt | vanilla_vector | 0.811 | 0.822 | 0.860 |
| gpt | full_system | 0.911 | 0.578 | 0.850 |

## Predictions

- Q1/Q7 no_rag mean step_acc per model: gemini 0.633, claude 0.779, gpt 0.734
- Q2 vanilla_budget − no_rag: gemini +0.078, claude -0.009, gpt -0.100 → ≥ +3pp in 1/3 → 반증
- Q3 비교 1 direction 3/3, p 0.0001 → 적중
- Q4 비교 2 direction 2/3, reverse none → 적중
- Q5 hall(v5) full ≤ vanilla_budget 1/3, ≤ vanilla_vector 0/3 → 반증
- Q6 routing gemini: horizon_2dviewer__01 wf 80/90, node 68/90, R2 0, R1 2; q:reclassify_raster__01 wf 86/90, node 39/90, R2 0, R1 0; q:rule_classification__01 wf 88/100, node 33/100, R2 0, R1 0
- Q6 routing claude: horizon_2dviewer__01 wf 80/90, node 64/90, R2 2, R1 1; q:reclassify_raster__01 wf 90/90, node 40/90, R2 0, R1 0; q:rule_classification__01 wf 90/100, node 41/100, R2 0, R1 0
- Q6 routing gpt: horizon_2dviewer__01 wf 80/90, node 70/90, R2 1, R1 5; q:reclassify_raster__01 wf 90/90, node 52/90, R2 4, R1 0; q:rule_classification__01 wf 90/100, node 38/100, R2 1, R1 0
