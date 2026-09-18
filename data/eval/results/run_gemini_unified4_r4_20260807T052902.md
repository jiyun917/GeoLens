# Benchmark Results

Started: 2026-08-07T05:29:02.407552Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.458 | 0.042 | 0.000 | 0.667 | — | 0.667 |
| vanilla_vector | 0.708 | 0.000 | 0.000 | 0.889 | — | 1.000 |
| graph_only | 0.917 | 0.167 | 0.000 | 1.000 | — | 1.000 |
| vision_only | 0.750 | 0.000 | 0.000 | 0.778 | — | 0.667 |
| full_system | 0.667 | 0.000 | 0.042 | 0.778 | — | 0.667 |
| state_path | 0.792 | 0.000 | 0.000 | 0.889 | — | 1.000 |
