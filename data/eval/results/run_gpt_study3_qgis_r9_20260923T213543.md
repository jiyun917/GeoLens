# Benchmark Results

Started: 2026-09-23T21:35:44.301707Z
Scenarios: 2

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.694 | 0.050 | 0.156 | — | — | 0.500 |
| vanilla_budget | 0.617 | 0.000 | 0.161 | — | — | 0.500 |
| vanilla_vector | 0.844 | 0.000 | 0.056 | — | — | 0.500 |
| full_system | 0.622 | 0.000 | 0.050 | — | — | 1.000 |
