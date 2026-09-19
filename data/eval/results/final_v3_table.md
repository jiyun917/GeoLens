# Final 3-Model × 7-Backend Matrix (n=10 replicates each, tag=v3)

Statistical unit = replicate. Each cell reports mean ± std across 10 replicates, where each replicate averages the 3 OpendTect dev-set scenarios (survey_setup + 3d_visualization + attribute_computation, 16 steps).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

**Goal Comp footnote (v3)**: 3-gate check on the final step of every scenario (the 3 OpendTect dev-set scenarios (survey_setup + 3d_visualization + attribute_computation, 16 steps)); scorer v3, GT 2f3db66, KB v4 (see v3_pre_registration_DRAFT.md). Cross-tag comparison with unified-era tables is prohibited.

## gemini

| metric | no_rag | vanilla_vector | vanilla_budget | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 73.3±6.9 | 81.7±8.4 | 82.1±8.8 | 78.8±6.6 | 78.3±6.5 | 91.2±6.6 | 80.4±8.8 |
| Hall Rate (%) ↓ | 2.9±2.0 | 3.3±1.8 | 2.1±2.2 | 1.7±2.2 | 2.5±2.2 | 2.9±2.0 | 3.3±1.8 |
| Loop Rate (%) ↓ | 0.4±1.3 | 0.0±0.0 | 0.0±0.0 | 2.1±3.5 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 70.0±10.5 | 73.3±14.1 | 76.7±16.1 | 83.3±17.6 | 76.7±16.1 | 86.7±17.2 | 60.0±26.3 |
| Latency (s) ↓ | 9.2±0.7 | 11.4±0.5 | 9.9±0.5 | 19.1±2.1 | 11.5±0.8 | 21.2±1.6 | 20.4±1.6 |
| Cost/step ($) ↓ | $5.53±0.46m | $14.86±0.24m | $7.62±0.50m | $7.83±0.46m | $6.56±0.41m | $9.66±0.48m | $8.86±0.65m |
| Cost total/step (gen+aux) ($) ↓ | $5.53±0.46m | $14.86±0.24m | $7.62±0.50m | $9.71±0.46m | $6.56±0.41m | $12.36±0.48m | $11.56±0.65m |

## claude

| metric | no_rag | vanilla_vector | vanilla_budget | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 87.5±0.0 | 87.5±0.0 | 87.5±0.0 | 87.5±0.0 | 87.5±0.0 | 100.0±0.0 | 85.0±4.0 |
| Hall Rate (%) ↓ | 5.0±1.8 | 4.2±0.0 | 4.2±0.0 | 4.2±0.0 | 4.6±1.3 | 4.2±0.0 | 4.2±0.0 |
| Loop Rate (%) ↓ | 2.5±2.2 | 1.2±2.0 | 1.2±2.0 | 8.3±0.0 | 2.5±2.2 | 0.0±0.0 | 1.7±2.2 |
| Goal Comp (%) ↑ | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 93.3±14.1 | 80.0±17.2 |
| Latency (s) ↓ | 3.5±0.7 | 4.3±0.4 | 3.7±0.5 | 12.6±0.8 | 4.9±0.6 | 13.4±0.8 | 13.3±0.8 |
| Cost/step ($) ↓ | $6.45±0.01m | $25.85±0.02m | $10.38±0.02m | $9.33±0.03m | $6.72±0.02m | $11.51±0.06m | $10.16±0.09m |
| Cost total/step (gen+aux) ($) ↓ | $6.45±0.01m | $25.85±0.02m | $10.38±0.02m | $11.19±0.05m | $6.72±0.02m | $14.20±0.05m | $12.85±0.10m |

## gpt

| metric | no_rag | vanilla_vector | vanilla_budget | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 70.8±4.4 | 76.7±4.0 | 72.5±5.6 | 85.4±4.9 | 78.3±8.1 | 80.4±5.6 | 90.8±4.7 |
| Hall Rate (%) ↓ | 5.0±2.6 | 4.6±1.3 | 4.2±0.0 | 4.2±0.0 | 4.6±1.3 | 10.4±3.5 | 5.8±3.5 |
| Loop Rate (%) ↓ | 0.0±0.0 | 2.9±2.8 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 2.5±4.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 66.7±0.0 | 66.7±0.0 | 90.0±16.1 | 96.7±10.5 | 93.3±14.1 | 40.0±14.1 | 63.3±10.5 |
| Latency (s) ↓ | 1.7±0.1 | 2.9±0.3 | 2.1±0.1 | 10.0±0.4 | 3.2±0.1 | 11.4±0.4 | 10.8±0.4 |
| Cost/step ($) ↓ | $3.54±0.01m | $17.26±0.01m | $6.37±0.00m | $5.59±0.01m | $3.71±0.01m | $7.25±0.02m | $6.03±0.02m |
| Cost total/step (gen+aux) ($) ↓ | $3.54±0.01m | $17.26±0.01m | $6.37±0.00m | $7.45±0.04m | $3.71±0.01m | $9.92±0.03m | $8.71±0.04m |

