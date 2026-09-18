# Benchmark Results

Started: 2026-08-07T10:13:23.176082Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.875 | 0.292 | 0.000 | 1.000 | — | 1.000 |
| vanilla_vector | 0.833 | 0.292 | 0.000 | 1.000 | — | 1.000 |
| graph_only | 0.833 | 0.208 | 0.000 | 1.000 | — | 1.000 |
| vision_only | 0.833 | 0.292 | 0.000 | 1.000 | — | 1.000 |
| full_system | 0.875 | 0.208 | 0.083 | 1.000 | — | 1.000 |
| state_path | 0.833 | 0.208 | 0.000 | 1.000 | — | 0.667 |
