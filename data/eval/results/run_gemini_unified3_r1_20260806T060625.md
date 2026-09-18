# Benchmark Results

Started: 2026-08-06T06:06:25.382739Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.500 | 0.000 | 0.000 | 0.667 | — | 0.667 |
| vanilla_vector | 0.583 | 0.000 | 0.000 | 0.889 | — | 1.000 |
| graph_only | 0.750 | 0.000 | 0.000 | 0.778 | — | 0.667 |
| vision_only | 0.667 | 0.083 | 0.042 | 0.778 | — | 0.667 |
| full_system | 0.708 | 0.000 | 0.000 | 0.889 | — | 1.000 |
| state_path | 0.708 | 0.083 | 0.000 | 0.778 | — | 0.667 |
