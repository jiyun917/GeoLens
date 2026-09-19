# Paper Table 1 — full mean ± sample SD for all 25 cells (v3)

Statistical unit = replicate (n=5 per cell). Each replicate value is the mean across the scenarios (survey_setup + 3d_visualization + attribute_computation). SD is sample SD (n-1 denominator).

Cells: 4 models × 6 backends + Gemini × long_context = 25.
long_context runs Gemini only. The manual is ~226K tokens; Claude Sonnet 4.6 (200K) and GPT-4o (128K) advertised windows are below this, and the Qwen3-235B endpoint used for the benchmark is served at max-model-len=32,768 (a vLLM deployment setting, not the model's theoretical maximum), so long_context cannot be evaluated on any of the three.

Qwen cost uses the cloud-equivalent (time-based) `mean_cost_usd_effective` value; the self-hosted marginal cost is $0 and would be misleading.

## Table 1 (compact) — core metrics

5 core metrics reported here. Goal Completion is reported separately below (Appendix A) because its effective n differs — see the footnote on that table.

| Cell (Model / Backend) | Step Acc (%) ↑ | Hall Rate (%) ↓ | Loop Rate (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓ | Cost total/step ($) ↓ |
|---|---|---|---|---|---|---|
| gemini / no_rag | 73.3±6.9 | 2.9±2.0 | 0.4±1.3 | 9.2±0.7 | $5.53±0.46m | $5.53±0.46m |
| gemini / vanilla_vector | 81.7±8.4 | 3.3±1.8 | 0.0±0.0 | 11.4±0.5 | $14.86±0.24m | $14.86±0.24m |
| gemini / vanilla_budget | 82.1±8.8 | 2.1±2.2 | 0.0±0.0 | 9.9±0.5 | $7.62±0.50m | $7.62±0.50m |
| gemini / graph_only | 78.8±6.6 | 1.7±2.2 | 2.1±3.5 | 19.1±2.1 | $7.83±0.46m | $9.71±0.46m |
| gemini / vision_only | 78.3±6.5 | 2.5±2.2 | 0.0±0.0 | 11.5±0.8 | $6.56±0.41m | $6.56±0.41m |
| gemini / full_system | 91.2±6.6 | 2.9±2.0 | 0.0±0.0 | 21.2±1.6 | $9.66±0.48m | $12.36±0.48m |
| gemini / state_path | 80.4±8.8 | 3.3±1.8 | 0.0±0.0 | 20.4±1.6 | $8.86±0.65m | $11.56±0.65m |
| claude / no_rag | 87.5±0.0 | 5.0±1.8 | 2.5±2.2 | 3.5±0.7 | $6.45±0.01m | $6.45±0.01m |
| claude / vanilla_vector | 87.5±0.0 | 4.2±0.0 | 1.2±2.0 | 4.3±0.4 | $25.85±0.02m | $25.85±0.02m |
| claude / vanilla_budget | 87.5±0.0 | 4.2±0.0 | 1.2±2.0 | 3.7±0.5 | $10.38±0.02m | $10.38±0.02m |
| claude / graph_only | 87.5±0.0 | 4.2±0.0 | 8.3±0.0 | 12.6±0.8 | $9.33±0.03m | $11.19±0.05m |
| claude / vision_only | 87.5±0.0 | 4.6±1.3 | 2.5±2.2 | 4.9±0.6 | $6.72±0.02m | $6.72±0.02m |
| claude / full_system | 100.0±0.0 | 4.2±0.0 | 0.0±0.0 | 13.4±0.8 | $11.51±0.06m | $14.20±0.05m |
| claude / state_path | 85.0±4.0 | 4.2±0.0 | 1.7±2.2 | 13.3±0.8 | $10.16±0.09m | $12.85±0.10m |
| gpt / no_rag | 70.8±4.4 | 5.0±2.6 | 0.0±0.0 | 1.7±0.1 | $3.54±0.01m | $3.54±0.01m |
| gpt / vanilla_vector | 76.7±4.0 | 4.6±1.3 | 2.9±2.8 | 2.9±0.3 | $17.26±0.01m | $17.26±0.01m |
| gpt / vanilla_budget | 72.5±5.6 | 4.2±0.0 | 0.0±0.0 | 2.1±0.1 | $6.37±0.00m | $6.37±0.00m |
| gpt / graph_only | 85.4±4.9 | 4.2±0.0 | 0.0±0.0 | 10.0±0.4 | $5.59±0.01m | $7.45±0.04m |
| gpt / vision_only | 78.3±8.1 | 4.6±1.3 | 0.0±0.0 | 3.2±0.1 | $3.71±0.01m | $3.71±0.01m |
| gpt / full_system | 80.4±5.6 | 10.4±3.5 | 2.5±4.0 | 11.4±0.4 | $7.25±0.02m | $9.92±0.03m |
| gpt / state_path | 90.8±4.7 | 5.8±3.5 | 0.0±0.0 | 10.8±0.4 | $6.03±0.02m | $8.71±0.04m |
| gemini / long_context | 80.0±10.0 | 4.2±3.9 | 0.8±2.6 | 10.3±0.5 | $269.18±0.43m | $269.18±0.43m |

## Appendix A — Goal Completion

**Effective n footnote (unified3)**: 3d_visualization step_3 was refined to a goal-reached state (all three slices displayed) for this run, so it now contributes to Goal Completion. attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). Effective n per cell = 3 scenarios × 5 replicates = 15 observations. Cross-tag comparison with unified2 Goal Comp is prohibited (see methodology_audit_trail.md — scenario refinement #1).

| Cell (Model / Backend) | Goal Comp (%) ↑ |
|---|---|
| gemini / no_rag | 70.0±10.5 |
| gemini / vanilla_vector | 73.3±14.1 |
| gemini / vanilla_budget | 76.7±16.1 |
| gemini / graph_only | 83.3±17.6 |
| gemini / vision_only | 76.7±16.1 |
| gemini / full_system | 86.7±17.2 |
| gemini / state_path | 60.0±26.3 |
| claude / no_rag | 100.0±0.0 |
| claude / vanilla_vector | 100.0±0.0 |
| claude / vanilla_budget | 100.0±0.0 |
| claude / graph_only | 100.0±0.0 |
| claude / vision_only | 100.0±0.0 |
| claude / full_system | 93.3±14.1 |
| claude / state_path | 80.0±17.2 |
| gpt / no_rag | 66.7±0.0 |
| gpt / vanilla_vector | 66.7±0.0 |
| gpt / vanilla_budget | 90.0±16.1 |
| gpt / graph_only | 96.7±10.5 |
| gpt / vision_only | 93.3±14.1 |
| gpt / full_system | 40.0±14.1 |
| gpt / state_path | 63.3±10.5 |
| gemini / long_context | 73.3±30.6 |
