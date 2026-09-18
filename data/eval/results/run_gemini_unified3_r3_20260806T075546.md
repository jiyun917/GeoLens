# Benchmark Results

Started: 2026-08-06T07:55:47.123405Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.667 | 0.000 | 0.000 | 0.778 | — | 0.667 |
| vanilla_vector | 0.708 | 0.083 | 0.083 | 0.778 | — | 0.667 |
| graph_only | 0.875 | 0.000 | 0.000 | 1.000 | — | 1.000 |
| vision_only | 0.625 | 0.125 | 0.000 | 0.667 | — | 1.000 |
| full_system | 0.792 | 0.083 | 0.000 | 0.889 | — | 0.667 |
| state_path | 0.875 | 0.000 | 0.000 | 0.889 | — | 0.667 |
