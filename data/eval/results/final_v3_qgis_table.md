# Final 3-Model × 7-Backend Matrix (n=10 replicates each, tag=v3_qgis)

Statistical unit = replicate. Each cell reports mean ± std across 10 replicates, where each replicate averages the single QGIS test-set scenario (qgis__vector_buffer__01, 8 steps).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

**Goal Comp footnote (v3_qgis)**: 3-gate check on the final step of every scenario (the single QGIS test-set scenario (qgis__vector_buffer__01, 8 steps)); scorer v3, GT 2f3db66, KB v4 (see v3_pre_registration_DRAFT.md). Cross-tag comparison with unified-era tables is prohibited.

## gemini

| metric | no_rag | vanilla_vector | vanilla_budget | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 100.0±0.0 | 100.0±0.0 | 98.8±4.0 | 100.0±0.0 | 98.8±4.0 | 100.0±0.0 | 97.5±5.3 |
| Hall Rate (%) ↓ | 12.5±0.0 | 16.2±6.0 | 13.8±4.0 | 12.5±5.9 | 13.8±4.0 | 12.5±0.0 | 12.5±0.0 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| Latency (s) ↓ | 8.6±0.6 | 10.2±0.8 | 9.1±0.5 | 32.6±2.1 | 10.1±0.8 | 33.1±3.0 | 32.1±3.4 |
| Cost/step ($) ↓ | $5.40±0.56m | $10.18±0.70m | $6.93±0.44m | $7.24±0.42m | $5.38±0.41m | $8.70±0.53m | $7.49±0.44m |
| Cost total/step (gen+aux) ($) ↓ | $5.40±0.56m | $10.18±0.70m | $6.93±0.44m | $9.28±0.71m | $5.38±0.41m | $11.47±1.08m | $10.45±0.98m |

## claude

| metric | no_rag | vanilla_vector | vanilla_budget | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 100.0±0.0 | 87.5±0.0 | 87.5±0.0 | 88.8±4.0 | 97.5±5.3 | 88.8±4.0 | 96.2±6.0 |
| Hall Rate (%) ↓ | 35.0±7.9 | 27.5±12.9 | 22.5±12.9 | 12.5±0.0 | 15.0±7.9 | 35.0±7.9 | 12.5±0.0 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| Latency (s) ↓ | 2.9±0.4 | 4.2±0.4 | 3.3±0.3 | 26.4±4.7 | 4.5±0.3 | 26.4±3.6 | 25.1±4.8 |
| Cost/step ($) ↓ | $7.10±0.03m | $17.92±0.06m | $10.43±0.06m | $9.69±0.13m | $7.16±0.04m | $11.46±0.05m | $10.18±0.19m |
| Cost total/step (gen+aux) ($) ↓ | $7.10±0.03m | $17.92±0.06m | $10.43±0.06m | $11.77±0.68m | $7.16±0.04m | $14.27±0.63m | $13.19±0.99m |

## gpt

| metric | no_rag | vanilla_vector | vanilla_budget | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 98.8±4.0 | 91.2±6.0 | 95.0±6.5 | 96.2±6.0 | 100.0±0.0 | 83.8±6.0 | 100.0±0.0 |
| Hall Rate (%) ↓ | 12.5±0.0 | 12.5±0.0 | 12.5±0.0 | 12.5±0.0 | 12.5±0.0 | 12.5±0.0 | 12.5±0.0 |
| Loop Rate (%) ↓ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 7.5±6.5 | 7.5±12.1 | 0.0±0.0 |
| Goal Comp (%) ↑ | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 | 90.0±31.6 | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| Latency (s) ↓ | 1.9±0.1 | 3.1±0.2 | 2.2±0.1 | 25.4±0.5 | 3.3±0.1 | 25.5±3.6 | 24.6±4.0 |
| Cost/step ($) ↓ | $3.76±0.00m | $11.55±0.01m | $6.26±0.01m | $5.54±0.01m | $3.92±0.01m | $7.04±0.03m | $5.88±0.14m |
| Cost total/step (gen+aux) ($) ↓ | $3.76±0.00m | $11.55±0.01m | $6.26±0.01m | $7.41±0.08m | $3.92±0.01m | $9.83±0.63m | $9.05±1.08m |

