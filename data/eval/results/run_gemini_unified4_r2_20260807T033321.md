# Benchmark Results

Started: 2026-08-07T03:33:21.585730Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.833 | 0.000 | 0.000 | 1.000 | — | 1.000 |
| vanilla_vector | 0.833 | 0.125 | 0.000 | 1.000 | — | 1.000 |
| graph_only | 0.625 | 0.000 | 0.000 | 0.667 | — | 0.667 |
| vision_only | 0.875 | 0.167 | 0.042 | 1.000 | — | 1.000 |
| full_system | 0.750 | 0.167 | 0.000 | 0.889 | — | 1.000 |
| state_path | 0.750 | 0.000 | 0.000 | 0.889 | — | 0.667 |
