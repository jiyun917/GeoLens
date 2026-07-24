# Benchmark Results

Started: 2026-07-16T03:21:33.269409Z
Scenarios: 2

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.500 | 0.000 | 0.000 | 0.500 | — | 0.500 |
| vanilla_vector | 0.750 | 0.125 | 0.000 | 0.667 | — | 0.500 |
| graph_only | 0.625 | 0.000 | 0.000 | 0.667 | — | 0.500 |
| vision_only | 0.625 | 0.000 | 0.000 | 0.667 | — | 0.500 |
| full_system | 0.625 | 0.125 | 0.000 | 0.667 | — | 0.000 |
| state_path | 0.500 | 0.000 | 0.000 | 0.500 | — | 0.000 |
