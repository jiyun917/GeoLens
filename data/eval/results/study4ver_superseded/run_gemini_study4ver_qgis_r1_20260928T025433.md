# Benchmark Results

Started: 2026-09-28T02:54:33.553675Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.719 | 0.042 | 0.033 | 1.000 | — | 1.000 |
| vanilla_budget | 0.830 | 0.042 | 0.000 | 1.000 | — | 1.000 |
| vanilla_vector | 0.796 | 0.042 | 0.033 | 1.000 | — | 1.000 |
| full_system | 0.958 | 0.042 | 0.145 | 1.000 | — | 1.000 |
