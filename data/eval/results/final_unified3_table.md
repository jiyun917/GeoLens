# Final 4-Model × 6-Backend Matrix (n=5 replicates each, tag=unified3)

Statistical unit = replicate. Each cell reports mean ± std across 5 replicates, where each replicate averages the 3 scenarios (survey_setup + 3d_visualization + attribute_computation).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

**Goal Comp footnote (unified3)**: unified3 refined the 3d_visualization step_3 capture to a goal-reached state (all three orthogonal slices displayed) and added the attribute_computation scenario whose step_7 also captures the goal state (Energy attribute rendered on In-line 250). All three scenarios therefore contribute to goal_completion. Effective n per (model, backend) = 3 scenarios × 5 replicates = 15 observations. **Cross-tag comparison with unified2 Goal Comp is prohibited** — the scoring target changed (see methodology_audit_trail.md § scenario refinement #1).

## gemini

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 55.8±8.1 | 67.5±8.0 | 63.3±17.5 | 63.3±10.8 | 74.2±4.6 | 73.3±10.5 |
| Hall Rate (%) ↓ | 0.0±0.0 | 5.0±7.5 | 2.5±5.6 | 4.2±5.9 | 1.7±3.7 | 3.3±3.5 |
| Loop Rate (%) ↓ | 0.8±1.9 | 1.7±3.7 | 0.0±0.0 | 0.8±1.9 | 0.8±1.9 | 0.0±0.0 |
| Goal Comp (%) ↑ | 80.0±18.3 | 80.0±18.3 | 80.0±18.3 | 73.3±14.9 | 80.0±29.8 | 73.3±14.9 |
| Latency (s) ↓ | 8.9±0.8 | 11.6±1.5 | 18.9±0.4 | 13.2±2.6 | 37.4±0.8 | 36.6±1.8 |
| Cost/step ($) ↓ | $0.75±0.01m | $9.27±0.01m | $0.84±0.01m | $0.87±0.02m | $2.21±0.03m | $1.09±0.01m |

## claude

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 85.8±2.3 | 83.3±0.0 | 80.0±4.6 | 83.3±0.0 | 84.2±1.9 | 83.3±0.0 |
| Hall Rate (%) ↓ | 25.8±5.4 | 30.0±6.2 | 20.8±5.9 | 25.0±4.2 | 25.0±4.2 | 25.8±4.6 |
| Loop Rate (%) ↓ | 3.3±3.5 | 1.7±2.3 | 0.8±1.9 | 0.0±0.0 | 3.3±3.5 | 3.3±3.5 |
| Goal Comp (%) ↑ | 100.0±0.0 | 100.0±0.0 | 93.3±14.9 | 100.0±0.0 | 93.3±14.9 | 93.3±14.9 |
| Latency (s) ↓ | 3.1±0.5 | 4.3±0.4 | 11.3±0.6 | 4.9±0.8 | 28.6±1.3 | 27.5±1.4 |
| Cost/step ($) ↓ | $6.43±0.06m | $27.10±0.04m | $6.84±0.14m | $6.82±0.05m | $10.93±0.19m | $7.62±0.05m |

## gpt

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 56.7±16.0 | 60.8±8.1 | 65.8±7.5 | 71.7±12.3 | 64.2±8.6 | 76.7±7.0 |
| Hall Rate (%) ↓ | 33.3±13.8 | 40.0±3.7 | 35.8±8.6 | 30.8±10.9 | 32.5±9.5 | 16.7±7.2 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.8±1.9 | 0.0±0.0 | 0.0±0.0 | 2.5±3.7 | 0.0±0.0 |
| Goal Comp (%) ↑ | 66.7±23.6 | 80.0±18.3 | 86.7±18.3 | 93.3±14.9 | 73.3±14.9 | 66.7±23.6 |
| Latency (s) ↓ | 2.1±0.1 | 5.1±0.2 | 9.8±0.5 | 3.6±0.2 | 26.7±1.8 | 26.3±1.5 |
| Cost/step ($) ↓ | $3.54±0.02m | $17.94±0.01m | $3.71±0.01m | $3.73±0.01m | $6.29±0.09m | $4.15±0.02m |

## qwen

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 43.3±11.3 | 41.7±9.8 | 47.5±10.9 | 47.5±11.3 | 60.8±7.0 | 61.7±13.9 |
| Hall Rate (%) ↓ | 43.3±12.4 | 55.0±20.5 | 60.0±5.6 | 60.8±8.6 | 60.8±8.1 | 60.0±14.9 |
| Loop Rate (%) ↓ | 24.2±8.0 | 13.3±9.5 | 3.3±3.5 | 13.3±6.2 | 6.7±4.8 | 6.7±8.1 |
| Goal Comp (%) ↑ | 46.7±38.0 | 20.0±29.8 | 40.0±27.9 | 40.0±43.5 | 20.0±18.3 | 33.3±23.6 |
| Latency (s) ↓ | 6.7±0.9 | 9.6±0.9 | 14.9±0.8 | 8.1±0.5 | 32.6±1.1 | 32.4±1.9 |
| Cost/step ($) ↓ | $6.28±0.84m | $9.00±0.86m | $13.92±0.78m | $7.56±0.48m | $30.40±1.03m | $30.21±1.74m |

