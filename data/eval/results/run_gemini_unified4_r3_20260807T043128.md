# Benchmark Results

Started: 2026-08-07T04:31:28.723425Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.708 | 0.000 | 0.000 | 0.778 | — | 0.667 |
| vanilla_vector | 0.875 | 0.083 | 0.000 | 1.000 | — | 1.000 |
| graph_only | 0.667 | 0.083 | 0.000 | 0.778 | — | 0.667 |
| vision_only | 0.833 | 0.042 | 0.000 | 0.778 | — | 0.667 |
| full_system | 0.875 | 0.083 | 0.000 | 1.000 | — | 1.000 |
| state_path | 0.667 | 0.000 | 0.000 | 0.778 | — | 1.000 |
