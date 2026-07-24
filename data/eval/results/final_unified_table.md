# Final 4-Model × 3-Backend Unified Matrix (n=5 replicates each)

Statistical unit = replicate. Each cell reports mean ± std across 5 replicates, where each replicate averages the 2 scenarios (survey_setup + 3d_visualization).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

## gemini

| metric | no_rag | vanilla_vector | full_system |
|---|---|---|---|
| Step Acc (%) ↑ | 52.5±10.5 | 60.0±10.5 | 55.0±11.2 |
| Hall Rate (%) ↓ | 0.0±0.0 | 15.0±13.7 | 10.0±10.5 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 50.0±0.0 | 40.0±22.4 | 50.0±0.0 |
| Latency (s) ↓ | 6.7±0.3 | 8.1±0.7 | 53.5±7.2 |
| Cost/step ($) ↓ | $0.69±0.02m | $9.31±0.01m | $2.34±0.28m |

## claude

| metric | no_rag | vanilla_vector | full_system |
|---|---|---|---|
| Step Acc (%) ↑ | 75.0±8.8 | 72.5±5.6 | 65.0±5.6 |
| Hall Rate (%) ↓ | 20.0±6.8 | 22.5±10.5 | 35.0±5.6 |
| Loop Rate (%) ↓ | 5.0±6.8 | 10.0±5.6 | 12.5±0.0 |
| Goal Comp (%) ↑ | 50.0±0.0 | 50.0±0.0 | 50.0±0.0 |
| Latency (s) ↓ | 2.8±0.4 | 4.5±1.9 | 73.9±9.0 |
| Cost/step ($) ↓ | $6.07±0.10m | $27.10±0.11m | $9.02±0.91m |

## gpt

| metric | no_rag | vanilla_vector | full_system |
|---|---|---|---|
| Step Acc (%) ↑ | 47.5±20.5 | 40.0±5.6 | 47.5±18.5 |
| Hall Rate (%) ↓ | 32.5±16.8 | 55.0±11.2 | 40.0±10.5 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Latency (s) ↓ | 2.1±0.2 | 3.5±1.5 | 73.4±7.6 |
| Cost/step ($) ↓ | $3.45±0.03m | $18.13±0.01m | $5.31±0.52m |

## qwen

| metric | no_rag | vanilla_vector | full_system |
|---|---|---|---|
| Step Acc (%) ↑ | 37.5±8.8 | 45.0±6.8 | 35.0±27.1 |
| Hall Rate (%) ↓ | 50.0±12.5 | 67.5±14.3 | 47.5±10.5 |
| Loop Rate (%) ↓ | 7.5±6.8 | 0.0±0.0 | 2.5±5.6 |
| Goal Comp (%) ↑ | 10.0±22.4 | 0.0±0.0 | 20.0±27.4 |
| Latency (s) ↓ | 6.3±0.9 | 7.4±0.3 | 80.1±6.5 |
| Cost/step ($) ↓ | $0.00±0.00m | $0.00±0.00m | $0.00±0.00m |

