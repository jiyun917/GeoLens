# Benchmark Results

Started: 2026-08-07T07:25:11.922553Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.833 | 0.250 | 0.000 | 1.000 | — | 1.000 |
| vanilla_vector | 0.875 | 0.208 | 0.000 | 1.000 | — | 1.000 |
| graph_only | 0.750 | 0.208 | 0.000 | 0.667 | — | 1.000 |
| vision_only | 0.833 | 0.292 | 0.083 | 1.000 | — | 1.000 |
| full_system | 0.833 | 0.292 | 0.042 | 1.000 | — | 1.000 |
| state_path | 0.833 | 0.083 | 0.000 | 1.000 | — | 0.667 |
