# Benchmark Results

Started: 2026-09-28T03:34:50.681227Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.789 | 0.075 | 0.074 | 1.000 | — | 1.000 |
| vanilla_budget | 0.822 | 0.042 | 0.037 | 1.000 | — | 1.000 |
| vanilla_vector | 0.856 | 0.075 | 0.074 | 1.000 | — | 1.000 |
| full_system | 1.000 | 0.042 | 0.037 | 1.000 | — | 1.000 |
