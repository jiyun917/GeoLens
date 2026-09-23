# Benchmark Results

Started: 2026-09-23T21:17:48.738558Z
Scenarios: 2

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.644 | 0.050 | 0.106 | — | — | 0.500 |
| vanilla_budget | 0.567 | 0.000 | 0.161 | — | — | 1.000 |
| vanilla_vector | 0.789 | 0.000 | 0.167 | — | — | 0.500 |
| full_system | 0.844 | 0.000 | 0.050 | — | — | 1.000 |
