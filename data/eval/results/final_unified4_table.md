# Final 4-Model × 6-Backend Matrix (n=5 replicates each, tag=unified4)

> **Annotation (V3-9, 2026-09-18)**: the unified2–4 `full_system` (and `state_path`) figures in this file were measured WITHOUT linked_chunks text — every linked_chunks id in the workflow JSONs had been dangling since the 2026-07-27 re-ingest, so graph_context held only the per-node title/description vector search. See `methodology_audit_trail.md` V3-9.

Statistical unit = replicate. Each cell reports mean ± std across 5 replicates, where each replicate averages the 3 scenarios (survey_setup + 3d_visualization + attribute_computation).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

**Goal Comp footnote (unified4)**: unified4 refined the 3d_visualization step_3 capture to a goal-reached state (all three orthogonal slices displayed) and added the attribute_computation scenario whose step_7 also captures the goal state (Energy attribute rendered on In-line 250). All three scenarios therefore contribute to goal_completion. Effective n per (model, backend) = 3 scenarios × 5 replicates = 15 observations. **Cross-tag comparison with unified2 Goal Comp is prohibited** — the scoring target changed (see methodology_audit_trail.md § scenario refinement #1).

## gemini

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 66.7±17.9 | 75.0±11.4 | 70.0±12.3 | 77.5±9.6 | 72.5±9.6 | 76.7±6.3 |
| Hall Rate (%) ↓ | 0.8±1.9 | 7.5±4.6 | 9.2±9.5 | 4.2±7.2 | 7.5±7.5 | 1.7±3.7 |
| Loop Rate (%) ↓ | 0.0±0.0 | 1.7±2.3 | 0.0±0.0 | 1.7±2.3 | 0.8±1.9 | 0.0±0.0 |
| Goal Comp (%) ↑ | 80.0±18.3 | 93.3±14.9 | 80.0±18.3 | 80.0±18.3 | 80.0±18.3 | 93.3±14.9 |
| Latency (s) ↓ | 10.6±1.3 | 10.3±0.9 | 19.3±2.5 | 14.0±1.4 | 40.9±1.3 | 40.6±4.3 |
| Cost/step ($) ↓ | $0.75±0.01m | $9.27±0.01m | $0.84±0.01m | $0.87±0.01m | $2.13±0.05m | $1.05±0.01m |

## claude

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 85.0±2.3 | 84.2±1.9 | 80.0±4.6 | 83.3±0.0 | 85.0±2.3 | 83.3±0.0 |
| Hall Rate (%) ↓ | 25.0±5.1 | 24.2±3.5 | 23.3±3.7 | 26.7±5.6 | 22.5±3.7 | 19.2±7.6 |
| Loop Rate (%) ↓ | 2.5±2.3 | 0.8±1.9 | 0.8±1.9 | 1.7±3.7 | 2.5±3.7 | 2.5±3.7 |
| Goal Comp (%) ↑ | 100.0±0.0 | 100.0±0.0 | 93.3±14.9 | 100.0±0.0 | 100.0±0.0 | 80.0±18.3 |
| Latency (s) ↓ | 3.0±0.3 | 3.9±0.4 | 11.8±0.7 | 4.8±0.5 | 32.4±1.8 | 31.1±1.8 |
| Cost/step ($) ↓ | $6.46±0.05m | $27.10±0.02m | $6.79±0.06m | $6.82±0.04m | $10.60±0.14m | $7.42±0.05m |

## gpt

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 50.8±12.6 | 60.0±6.3 | 67.5±6.2 | 54.2±14.4 | 69.2±3.7 | 72.5±7.6 |
| Hall Rate (%) ↓ | 30.8±18.3 | 36.7±11.6 | 35.0±3.7 | 36.7±9.0 | 30.8±7.0 | 20.8±8.8 |
| Loop Rate (%) ↓ | 0.0±0.0 | 1.7±3.7 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| Goal Comp (%) ↑ | 73.3±14.9 | 73.3±14.9 | 100.0±0.0 | 86.7±29.8 | 93.3±14.9 | 86.7±18.3 |
| Latency (s) ↓ | 2.0±0.1 | 5.1±0.3 | 10.3±0.3 | 3.5±0.2 | 31.2±2.4 | 31.0±2.3 |
| Cost/step ($) ↓ | $3.54±0.03m | $17.93±0.02m | $3.70±0.02m | $3.75±0.03m | $6.08±0.10m | $4.09±0.04m |

## qwen

| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |
|---|---|---|---|---|---|---|
| Step Acc (%) ↑ | 49.2±8.0 | 55.0±6.8 | 49.2±9.9 | 62.5±12.5 | 56.7±9.1 | 55.0±10.8 |
| Hall Rate (%) ↓ | 40.0±12.0 | 61.7±13.0 | 67.5±6.8 | 54.2±22.2 | 50.0±8.8 | 56.7±9.6 |
| Loop Rate (%) ↓ | 21.7±7.5 | 15.0±6.3 | 2.5±5.6 | 10.0±7.0 | 6.7±8.6 | 5.8±7.0 |
| Goal Comp (%) ↑ | 53.3±18.3 | 40.0±14.9 | 20.0±18.3 | 13.3±18.3 | 40.0±27.9 | 40.0±27.9 |
| Latency (s) ↓ | 5.9±0.7 | 9.7±0.5 | 14.2±0.5 | 9.3±0.5 | 35.5±1.1 | 33.4±1.4 |
| Cost/step ($) ↓ | $5.48±0.67m | $9.05±0.48m | $13.26±0.45m | $8.72±0.43m | $33.10±1.05m | $31.20±1.30m |

