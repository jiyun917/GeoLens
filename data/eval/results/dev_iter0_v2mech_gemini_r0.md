# Benchmark Results

Started: 2026-09-18T01:41:01.323494Z
Scenarios: 3

## Aggregate (mean across scenarios)

| backend | step_accuracy | hallucination_rate | dwell_loop_rate | trap_pass_rate | recovery_rate | goal_completion_rate |
|---|---|---|---|---|---|---|
| no_rag | 0.792 | 0.083 | 0.000 | 0.889 | — | 0.667 |
| vanilla_vector | 0.750 | 0.083 | 0.000 | 0.889 | — | 0.667 |
| vanilla_budget | 0.792 | 0.083 | 0.000 | 0.889 | — | 0.667 |
| full_system | 0.750 | 0.083 | 0.000 | 0.556 | — | 0.333 |
