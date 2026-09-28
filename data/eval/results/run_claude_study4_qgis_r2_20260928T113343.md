# Benchmark Results

Started: 2026-09-28T11:33:43.798843Z
Scenarios: 2

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.683 | 0.050 | 0.111 | — | — | 1.000 |
| vanilla_budget | 0.783 | 0.000 | 0.106 | — | — | 1.000 |
| vanilla_vector | 0.783 | 0.050 | 0.161 | — | — | 0.500 |
| full_system | 0.894 | 0.050 | 0.000 | — | — | 1.000 |
