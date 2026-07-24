# Benchmark Results

Started: 2026-07-16T05:06:34.566278Z
Scenarios: 2

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.750 | 0.250 | 0.000 | 0.667 | — | 0.500 |
| vanilla_vector | 0.750 | 0.250 | 0.125 | 0.833 | — | 0.500 |
| graph_only | 0.750 | 0.250 | 0.000 | 0.667 | — | 0.500 |
| vision_only | 0.750 | 0.375 | 0.125 | 0.833 | — | 0.500 |
| full_system | 0.750 | 0.125 | 0.125 | 0.833 | — | 0.500 |
| state_path | 0.875 | 0.000 | 0.000 | 0.833 | — | 0.500 |
