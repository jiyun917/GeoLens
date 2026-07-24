# Benchmark Results

Started: 2026-07-15T07:49:07.457983Z
Scenarios: 2

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.750 | 0.125 | 0.000 | 0.833 | — | 0.000 |
| vanilla_vector | 0.125 | 0.000 | 0.000 | 0.167 | — | 0.000 |
| graph_only | 0.375 | 0.000 | 0.000 | 0.167 | — | 0.000 |
| vision_only | 0.625 | 0.125 | 0.000 | 0.333 | — | 0.000 |
| full_system | 0.375 | 0.000 | 0.000 | 0.000 | — | 0.000 |
| state_path | 0.750 | 0.000 | 0.000 | 0.333 | — | 0.500 |
