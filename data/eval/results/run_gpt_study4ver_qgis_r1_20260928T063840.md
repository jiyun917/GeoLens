# Benchmark Results

Started: 2026-09-28T06:38:40.884737Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.763 | 0.075 | 0.033 | 1.000 | — | 0.667 |
| vanilla_budget | 0.856 | 0.042 | 0.074 | 1.000 | — | 0.667 |
| vanilla_vector | 0.930 | 0.042 | 0.033 | 1.000 | — | 0.667 |
| full_system | 0.958 | 0.042 | 0.037 | 1.000 | — | 1.000 |
