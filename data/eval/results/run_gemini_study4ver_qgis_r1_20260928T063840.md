# Benchmark Results

Started: 2026-09-28T06:38:40.963782Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.689 | 0.075 | 0.000 | 1.000 | — | 1.000 |
| vanilla_budget | 0.796 | 0.042 | 0.067 | 1.000 | — | 1.000 |
| vanilla_vector | 0.759 | 0.042 | 0.067 | 1.000 | — | 1.000 |
| full_system | 0.967 | 0.042 | 0.104 | 1.000 | — | 1.000 |
