# Benchmark Results

Started: 2026-09-18T03:28:22.090008Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.667 | 0.042 | 0.000 | 0.889 | — | 0.667 |
| vanilla_vector | 0.667 | 0.083 | 0.000 | 0.889 | — | 0.667 |
| vanilla_budget | 0.750 | 0.083 | 0.000 | 0.556 | — | 0.667 |
| full_system | 0.833 | 0.083 | 0.000 | 1.000 | — | 1.000 |
