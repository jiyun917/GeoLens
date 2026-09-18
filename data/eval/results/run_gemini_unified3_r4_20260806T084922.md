# Benchmark Results

Started: 2026-08-06T08:49:22.910598Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.500 | 0.000 | 0.000 | 0.667 | — | 1.000 |
| vanilla_vector | 0.667 | 0.000 | 0.000 | 0.889 | — | 0.667 |
| graph_only | 0.500 | 0.000 | 0.000 | 0.667 | — | 1.000 |
| vision_only | 0.792 | 0.000 | 0.000 | 0.778 | — | 0.667 |
| full_system | 0.708 | 0.000 | 0.000 | 0.778 | — | 1.000 |
| state_path | 0.750 | 0.042 | 0.000 | 0.778 | — | 0.667 |
