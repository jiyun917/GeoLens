# Study 2 verdict — mechanical application of the pre-registration (tag study2)

runs: gemini n=10, claude n=10, gpt n=10

## §5 judgement (replicate-level, strata = model)

### 비교 1 (full_system vs vanilla_budget)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.907 | 0.706 | +0.201 | 0.000 | 0.094 | 0.127 | ✓ |
| claude | 0.723 | 0.475 | +0.248 | 0.000 | 0.022 | 0.000 | ✗ |
| gpt | 0.881 | 0.460 | +0.421 | 0.000 | 0.144 | 0.057 | ✗ |

- step: direction 3/3 (ties 0), stratified raw p = 0.0001, Δ = +0.2899, significant reverse: none → 성립
- hall: full ≤ comparator in 1/3 → 불성립
- **grade: A′**

### 비교 2 (full_system vs vanilla_vector)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.907 | 0.769 | +0.138 | 0.010 | 0.094 | 0.071 | ✗ |
| claude | 0.723 | 0.806 | -0.083 | 0.016 | 0.022 | 0.142 | ✓ |
| gpt | 0.881 | 0.599 | +0.282 | 0.000 | 0.144 | 0.035 | ✗ |

- step: direction 2/3 (ties 0), stratified raw p = 0.0003, Δ = +0.1122, significant reverse: ['claude'] → 불성립
- hall: full ≤ comparator in 1/3 → 불성립
- **grade: B**

Holm (family 2): 비교 1 0.0001 → 0.0002; 비교 2 0.0003 → 0.0003. **Grades: 비교 1 = A′, 비교 2 = B.**

## Descriptive (mean over replicates)

| model | backend | step_acc | hall | goal_completion | cost_total $/step | latency s/step |
|---|---|---|---|---|---|---|
| gemini | no_rag | 0.508 | 0.100 | 0.350 | 0.0078 | 11.0 |
| gemini | vanilla_budget | 0.706 | 0.127 | 0.400 | 0.0105 | 12.3 |
| gemini | vanilla_vector | 0.769 | 0.071 | 0.200 | 0.0138 | 11.7 |
| gemini | full_system | 0.907 | 0.094 | 0.400 | 0.0139 | 25.7 |
| claude | no_rag | 0.371 | 0.133 | 0.000 | 0.0064 | 3.4 |
| claude | vanilla_budget | 0.475 | 0.000 | 0.000 | 0.0105 | 4.2 |
| claude | vanilla_vector | 0.806 | 0.142 | 0.000 | 0.0187 | 4.2 |
| claude | full_system | 0.723 | 0.022 | 0.300 | 0.0149 | 15.0 |
| gpt | no_rag | 0.275 | 0.014 | 0.300 | 0.0034 | 1.9 |
| gpt | vanilla_budget | 0.460 | 0.057 | 0.050 | 0.0063 | 2.6 |
| gpt | vanilla_vector | 0.599 | 0.035 | 0.500 | 0.0118 | 2.3 |
| gpt | full_system | 0.881 | 0.144 | 0.000 | 0.0104 | 15.7 |

## Predictions

- Q1 no_rag mean step_acc per model: gemini 0.508, claude 0.371, gpt 0.275
- Q2 vanilla_budget − no_rag: gemini +0.198, claude +0.105, gpt +0.185 → ≥ +3pp in 3/3 → 적중
- Q3 비교 1 direction 3/3 → 적중
- Q4 비교 2 direction (no prediction): gemini +0.138, claude -0.083, gpt +0.282
- Q5 hall full ≤ vanilla_budget in 1/3 → 반증
- Q6 routing gemini: fault_sticks__01 wf 90/90, node 54/90; horizon_autotrack__01 wf 70/70, node 40/70
- Q6 routing claude: fault_sticks__01 wf 87/90, node 38/90; horizon_autotrack__01 wf 70/70, node 40/70
- Q6 routing gpt: fault_sticks__01 wf 90/90, node 80/90; horizon_autotrack__01 wf 70/70, node 40/70
