# Benchmark Results

Started: 2026-09-28T09:45:11.426189Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.503 | 0.000 | 0.132 | — | — | 0.333 |
| vanilla_budget | 0.661 | 0.000 | 0.132 | — | — | 0.333 |
| vanilla_vector | 0.841 | 0.000 | 0.037 | — | — | 0.333 |
| full_system | 0.878 | 0.000 | 0.000 | — | — | 0.667 |
