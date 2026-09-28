# Benchmark Results

Started: 2026-09-28T11:53:04.706178Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.646 | 0.000 | 0.048 | — | — | 0.333 |
| vanilla_budget | 0.656 | 0.000 | 0.159 | — | — | 0.667 |
| vanilla_vector | 0.841 | 0.000 | 0.000 | — | — | 0.667 |
| full_system | 1.000 | 0.000 | 0.000 | — | — | 0.667 |
