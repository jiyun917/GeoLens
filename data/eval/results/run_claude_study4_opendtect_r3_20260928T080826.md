# Benchmark Results

Started: 2026-09-28T08:08:26.669465Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.503 | 0.000 | 0.169 | — | — | 0.333 |
| vanilla_budget | 0.661 | 0.000 | 0.169 | — | — | 0.333 |
| vanilla_vector | 0.831 | 0.000 | 0.000 | — | — | 0.333 |
| full_system | 0.952 | 0.000 | 0.048 | — | — | 0.667 |
