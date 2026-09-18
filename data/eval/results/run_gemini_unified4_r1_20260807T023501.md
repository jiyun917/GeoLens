# Benchmark Results

Started: 2026-08-07T02:35:01.409829Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.500 | 0.000 | 0.000 | 0.778 | — | 1.000 |
| vanilla_vector | 0.583 | 0.083 | 0.042 | 0.778 | — | 1.000 |
| graph_only | 0.625 | 0.208 | 0.000 | 0.778 | — | 1.000 |
| vision_only | 0.625 | 0.000 | 0.042 | 0.778 | — | 0.667 |
| full_system | 0.625 | 0.125 | 0.000 | 0.778 | — | 0.667 |
| state_path | 0.792 | 0.000 | 0.000 | 0.778 | — | 1.000 |
