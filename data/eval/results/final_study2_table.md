# Final 3-Model × 4-Backend Matrix (n=10 replicates each, tag=study2)

Statistical unit = replicate. Each cell reports mean ± std across 10 replicates, where each replicate averages the 3 scenarios (survey_setup + 3d_visualization + attribute_computation).

Goal completion uses the 3-gate check: sentinel + grounded + visual_state confirms goal-reached.

**Goal Comp footnote (study2)**: study2 refined the 3d_visualization step_3 capture to a goal-reached state (all three orthogonal slices displayed) and added the attribute_computation scenario whose step_7 also captures the goal state (Energy attribute rendered on In-line 250). All three scenarios therefore contribute to goal_completion. Effective n per (model, backend) = 3 scenarios × 5 replicates = 15 observations. **Cross-tag comparison with unified2 Goal Comp is prohibited** — the scoring target changed (see methodology_audit_trail.md § scenario refinement #1).

## gemini

| metric | no_rag | vanilla_budget | vanilla_vector | full_system |
|---|---|---|---|---|
| Step Acc (%) ↑ | 50.8±15.4 | 70.6±6.9 | 76.9±12.3 | 90.7±8.2 |
| Hall Rate (%) ↓ | 10.0±7.6 | 12.7±5.6 | 7.1±0.0 | 9.4±5.4 |
| Loop Rate (%) ↓ | 2.0±3.2 | 4.0±4.6 | 2.5±3.3 | 1.4±3.0 |
| Goal Comp (%) ↑ | 35.0±24.2 | 40.0±31.6 | 20.0±25.8 | 40.0±21.1 |
| Latency (s) ↓ | 11.0±0.4 | 12.3±0.6 | 11.7±0.6 | 25.7±2.0 |
| Cost/step ($) ↓ | $7.83±0.30m | $10.47±0.41m | $13.81±0.64m | $10.60±0.36m |
| Cost total/step (gen+aux) ($) ↓ | $7.83±0.30m | $10.47±0.41m | $13.81±0.64m | $13.86±0.53m |

## claude

| metric | no_rag | vanilla_budget | vanilla_vector | full_system |
|---|---|---|---|---|
| Step Acc (%) ↑ | 37.1±1.8 | 47.5±4.6 | 80.6±6.7 | 72.3±6.4 |
| Hall Rate (%) ↓ | 13.3±10.5 | 0.0±0.0 | 14.2±9.0 | 2.2±5.4 |
| Loop Rate (%) ↓ | 15.2±6.0 | 15.4±2.3 | 0.0±0.0 | 16.7±11.1 |
| Goal Comp (%) ↑ | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 | 30.0±25.8 |
| Latency (s) ↓ | 3.4±0.8 | 4.2±0.7 | 4.2±0.8 | 15.0±0.5 |
| Cost/step ($) ↓ | $6.41±0.05m | $10.45±0.05m | $18.67±0.06m | $11.89±0.07m |
| Cost total/step (gen+aux) ($) ↓ | $6.41±0.05m | $10.45±0.05m | $18.67±0.06m | $14.88±0.12m |

## gpt

| metric | no_rag | vanilla_budget | vanilla_vector | full_system |
|---|---|---|---|---|
| Step Acc (%) ↑ | 27.5±14.9 | 46.0±11.6 | 59.9±11.3 | 88.1±6.9 |
| Hall Rate (%) ↓ | 1.4±3.0 | 5.7±5.6 | 3.5±3.0 | 14.4±2.7 |
| Loop Rate (%) ↓ | 11.7±1.8 | 7.2±4.9 | 20.1±10.6 | 1.1±2.3 |
| Goal Comp (%) ↑ | 30.0±25.8 | 5.0±15.8 | 50.0±0.0 | 0.0±0.0 |
| Latency (s) ↓ | 1.9±0.2 | 2.6±0.3 | 2.3±0.3 | 15.7±2.9 |
| Cost/step ($) ↓ | $3.40±0.01m | $6.26±0.01m | $11.79±0.01m | $7.33±0.02m |
| Cost total/step (gen+aux) ($) ↓ | $3.40±0.01m | $6.26±0.01m | $11.79±0.01m | $10.37±0.05m |

