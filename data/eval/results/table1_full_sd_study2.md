# Paper Table 1 — full mean ± sample SD for all 25 cells (study2)

Statistical unit = replicate (n=10 per cell). Each replicate value is the mean across the scenarios (survey_setup + 3d_visualization + attribute_computation). SD is sample SD (n-1 denominator).

Cells: 3 models × 6 backends + Gemini × long_context = 19.
long_context runs Gemini only. The manual is ~226K tokens; Claude Sonnet 4.6 (200K) and GPT-4o (128K) advertised windows are below this, and the Qwen3-235B endpoint used for the benchmark is served at max-model-len=32,768 (a vLLM deployment setting, not the model's theoretical maximum), so long_context cannot be evaluated on any of the three.

Qwen cost uses the cloud-equivalent (time-based) `mean_cost_usd_effective` value; the self-hosted marginal cost is $0 and would be misleading.

## Table 1 (compact) — core metrics

5 core metrics reported here. Goal Completion is reported separately below (Appendix A) because its effective n differs — see the footnote on that table.

| Cell (Model / Backend) | Step Acc (%) ↑ | Hall Rate (%) ↓ | Loop Rate (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓ | Cost total/step ($) ↓ |
|---|---|---|---|---|---|---|
| gemini / no_rag | 50.8±15.4 | 10.0±7.6 | 2.0±3.2 | 11.0±0.4 | $7.83±0.30m | $7.83±0.30m |
| gemini / vanilla_vector | 76.9±12.3 | 7.1±0.0 | 2.5±3.3 | 11.7±0.6 | $13.81±0.64m | $13.81±0.64m |
| gemini / vanilla_budget | 70.6±6.9 | 12.7±5.6 | 4.0±4.6 | 12.3±0.6 | $10.47±0.41m | $10.47±0.41m |
| gemini / graph_only | n/a | n/a | n/a | n/a | n/a | n/a |
| gemini / vision_only | n/a | n/a | n/a | n/a | n/a | n/a |
| gemini / full_system | 90.7±8.2 | 9.4±5.4 | 1.4±3.0 | 25.7±2.0 | $10.60±0.36m | $13.86±0.53m |
| gemini / state_path | n/a | n/a | n/a | n/a | n/a | n/a |
| claude / no_rag | 37.1±1.8 | 13.3±10.5 | 15.2±6.0 | 3.4±0.8 | $6.41±0.05m | $6.41±0.05m |
| claude / vanilla_vector | 80.6±6.7 | 14.2±9.0 | 0.0±0.0 | 4.2±0.8 | $18.67±0.06m | $18.67±0.06m |
| claude / vanilla_budget | 47.5±4.6 | 0.0±0.0 | 15.4±2.3 | 4.2±0.7 | $10.45±0.05m | $10.45±0.05m |
| claude / graph_only | n/a | n/a | n/a | n/a | n/a | n/a |
| claude / vision_only | n/a | n/a | n/a | n/a | n/a | n/a |
| claude / full_system | 72.3±6.4 | 2.2±5.4 | 16.7±11.1 | 15.0±0.5 | $11.89±0.07m | $14.88±0.12m |
| claude / state_path | n/a | n/a | n/a | n/a | n/a | n/a |
| gpt / no_rag | 27.5±14.9 | 1.4±3.0 | 11.7±1.8 | 1.9±0.2 | $3.40±0.01m | $3.40±0.01m |
| gpt / vanilla_vector | 59.9±11.3 | 3.5±3.0 | 20.1±10.6 | 2.3±0.3 | $11.79±0.01m | $11.79±0.01m |
| gpt / vanilla_budget | 46.0±11.6 | 5.7±5.6 | 7.2±4.9 | 2.6±0.3 | $6.26±0.01m | $6.26±0.01m |
| gpt / graph_only | n/a | n/a | n/a | n/a | n/a | n/a |
| gpt / vision_only | n/a | n/a | n/a | n/a | n/a | n/a |
| gpt / full_system | 88.1±6.9 | 14.4±2.7 | 1.1±2.3 | 15.7±2.9 | $7.33±0.02m | $10.37±0.05m |
| gpt / state_path | n/a | n/a | n/a | n/a | n/a | n/a |
| gemini / long_context | 59.2±9.9 | 20.8±11.8 | 0.0±0.0 | 13.9±1.5 | $315.56±0.01m | n/a |

## Appendix A — Goal Completion

**Effective n footnote (unified3)**: 3d_visualization step_3 was refined to a goal-reached state (all three slices displayed) for this run, so it now contributes to Goal Completion. attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). Effective n per cell = 3 scenarios × 5 replicates = 15 observations. Cross-tag comparison with unified2 Goal Comp is prohibited (see methodology_audit_trail.md — scenario refinement #1).

| Cell (Model / Backend) | Goal Comp (%) ↑ |
|---|---|
| gemini / no_rag | 35.0±24.2 |
| gemini / vanilla_vector | 20.0±25.8 |
| gemini / vanilla_budget | 40.0±31.6 |
| gemini / graph_only | n/a |
| gemini / vision_only | n/a |
| gemini / full_system | 40.0±21.1 |
| gemini / state_path | n/a |
| claude / no_rag | 0.0±0.0 |
| claude / vanilla_vector | 0.0±0.0 |
| claude / vanilla_budget | 0.0±0.0 |
| claude / graph_only | n/a |
| claude / vision_only | n/a |
| claude / full_system | 30.0±25.8 |
| claude / state_path | n/a |
| gpt / no_rag | 30.0±25.8 |
| gpt / vanilla_vector | 50.0±0.0 |
| gpt / vanilla_budget | 5.0±15.8 |
| gpt / graph_only | n/a |
| gpt / vision_only | n/a |
| gpt / full_system | 0.0±0.0 |
| gpt / state_path | n/a |
| gemini / long_context | 93.3±14.9 |
