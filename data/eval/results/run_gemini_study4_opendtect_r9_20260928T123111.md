# Benchmark Results

Started: 2026-09-28T12:31:11.482295Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.587 | 0.037 | 0.000 | — | — | 1.000 |
| vanilla_budget | 0.730 | 0.037 | 0.048 | — | — | 0.333 |
| vanilla_vector | 0.878 | 0.000 | 0.000 | — | — | 0.333 |
| full_system | 1.000 | 0.000 | 0.000 | — | — | 0.667 |
