# Benchmark Results

Started: 2026-08-06T07:00:20.253001Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.625 | 0.000 | 0.042 | 0.889 | — | 1.000 |
| vanilla_vector | 0.792 | 0.167 | 0.000 | 0.889 | — | 0.667 |
| graph_only | 0.583 | 0.000 | 0.000 | 0.667 | — | 0.667 |
| vision_only | 0.583 | 0.000 | 0.000 | 0.667 | — | 0.667 |
| full_system | 0.792 | 0.000 | 0.000 | 0.778 | — | 0.333 |
| state_path | 0.583 | 0.000 | 0.000 | 0.778 | — | 1.000 |
