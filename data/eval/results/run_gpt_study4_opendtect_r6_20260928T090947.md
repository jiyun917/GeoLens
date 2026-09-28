# Benchmark Results

Started: 2026-09-28T09:09:48.151877Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.513 | 0.000 | 0.000 | — | — | 0.000 |
| vanilla_budget | 0.624 | 0.000 | 0.180 | — | — | 0.000 |
| vanilla_vector | 0.698 | 0.000 | 0.180 | — | — | 0.333 |
| full_system | 1.000 | 0.037 | 0.000 | — | — | 0.333 |
