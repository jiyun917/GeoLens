# Final 4-Model × 6-Backend Matrix (n=5 replicates each)

Statistical unit = replicate. Each cell reports mean ± std across 5 replicates, where each replicate averages the 2 scenarios (survey_setup + 3d_visualization).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

**Goal Comp footnote**: 3d_visualization captures the penultimate state (In-line + Cross-line displayed, Z-slice not yet added). Its final visual_state does NOT indicate goal-reached, so no backend can achieve goal_completion on that scenario under the 3-gate check. Consequently the Goal Comp column is effectively a single-scenario measurement on survey_setup only — n=5 per (model, backend), not n=10. This is a scenario-capture limitation, not a metric flaw. Interpret Goal Comp differences with this reduced power in mind.

## gemini

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 55.0±6.8 | 60.0±10.5 | 52.5±5.6 | 55.0±6.8 | 60.0±10.5 | 55.0±6.8 |
| Hall Rate (%) ↓ | 7.5±11.2 | 10.0±10.5 | 2.5±5.6 | 5.0±6.8 | 5.0±6.8 | 7.5±11.2 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 50.0±0.0 | 50.0±0.0 | 50.0±0.0 | 50.0±0.0 | 30.0±27.4 | 20.0±27.4 |
| Latency (s) ↓ | 7.1±0.7 | 8.6±0.3 | 14.8±0.9 | 9.5±1.0 | 34.3±3.6 | 30.4±3.4 |
| Cost/step ($) ↓ | $0.70±0.01m | $9.30±0.01m | $0.79±0.01m | $0.81±0.02m | $2.66±0.06m | $1.56±0.05m |

## claude

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 72.5±10.5 | 72.5±5.6 | 77.5±10.5 | 72.5±5.6 | 77.5±5.6 | 85.0±5.6 |
| Hall Rate (%) ↓ | 25.0±0.0 | 25.0±8.8 | 20.0±11.2 | 30.0±11.2 | 15.0±5.6 | 10.0±5.6 |
| Loop Rate (%) ↓ | 5.0±6.8 | 12.5±0.0 | 2.5±5.6 | 12.5±0.0 | 10.0±5.6 | 0.0±0.0 |
| Goal Comp (%) ↑ | 50.0±0.0 | 50.0±0.0 | 50.0±0.0 | 50.0±0.0 | 50.0±0.0 | 30.0±27.4 |
| Latency (s) ↓ | 2.8±0.5 | 4.0±0.2 | 10.7±0.5 | 5.7±0.6 | 27.5±2.3 | 26.7±2.1 |
| Cost/step ($) ↓ | $6.06±0.10m | $27.13±0.05m | $6.37±0.06m | $6.42±0.02m | $11.66±0.13m | $8.67±0.12m |

## gpt

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 42.5±14.3 | 37.5±8.8 | 77.5±10.5 | 57.5±14.3 | 70.0±6.8 | 57.5±6.8 |
| Hall Rate (%) ↓ | 40.0±16.3 | 47.5±5.6 | 27.5±20.5 | 27.5±16.3 | 55.0±6.8 | 50.0±0.0 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 0.0±0.0 | 20.0±27.4 | 50.0±0.0 | 40.0±22.4 | 30.0±27.4 | 20.0±27.4 |
| Latency (s) ↓ | 2.3±0.2 | 3.5±0.5 | 9.8±0.4 | 4.4±0.1 | 29.7±1.9 | 28.4±1.6 |
| Cost/step ($) ↓ | $3.45±0.04m | $18.11±0.01m | $3.61±0.04m | $3.64±0.02m | $7.01±0.07m | $4.94±0.16m |

## qwen

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 57.5±19.0 | 35.0±16.3 | 52.5±16.3 | 52.5±10.5 | 50.0±12.5 | 50.0±8.8 |
| Hall Rate (%) ↓ | 62.5±8.8 | 72.5±20.5 | 70.0±14.3 | 70.0±11.2 | 47.5±10.5 | 60.0±5.6 |
| Loop Rate (%) ↓ | 7.5±6.8 | 7.5±11.2 | 2.5±5.6 | 2.5±5.6 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 30.0±27.4 | 10.0±22.4 | 20.0±27.4 | 10.0±22.4 | 10.0±22.4 | 10.0±22.4 |
| Latency (s) ↓ | 7.3±1.1 | 42.2±71.4 | 13.9±2.1 | 11.0±1.5 | 30.9±2.1 | 29.9±1.5 |
| Cost/step ($) ↓ | $10.53±1.52m | $60.45±102.33m | $19.94±3.00m | $15.80±2.15m | $44.30±3.00m | $42.90±2.20m |

