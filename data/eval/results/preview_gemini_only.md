# Final 4-Model × 6-Backend Matrix (n=5 replicates each)

Statistical unit = replicate. Each cell reports mean ± std across 5 replicates, where each replicate averages the 2 scenarios (survey_setup + 3d_visualization).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

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
| Step Acc (%) ↑ | — | — | — | — | — | — |
| Hall Rate (%) ↓ | — | — | — | — | — | — |
| Loop Rate (%) ↓ | — | — | — | — | — | — |
| Goal Comp (%) ↑ | — | — | — | — | — | — |
| Latency (s) ↓ | — | — | — | — | — | — |
| Cost/step ($) ↓ | — | — | — | — | — | — |

## gpt

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | — | — | — | — | — | — |
| Hall Rate (%) ↓ | — | — | — | — | — | — |
| Loop Rate (%) ↓ | — | — | — | — | — | — |
| Goal Comp (%) ↑ | — | — | — | — | — | — |
| Latency (s) ↓ | — | — | — | — | — | — |
| Cost/step ($) ↓ | — | — | — | — | — | — |

## qwen

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | — | — | — | — | — | — |
| Hall Rate (%) ↓ | — | — | — | — | — | — |
| Loop Rate (%) ↓ | — | — | — | — | — | — |
| Goal Comp (%) ↑ | — | — | — | — | — | — |
| Latency (s) ↓ | — | — | — | — | — | — |
| Cost/step ($) ↓ | — | — | — | — | — | — |

