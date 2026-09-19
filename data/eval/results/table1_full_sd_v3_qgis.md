# Paper Table 1 — full mean ± sample SD for all 25 cells (v3_qgis)

Statistical unit = replicate (n=5 per cell). Each replicate value is the mean across the scenarios (survey_setup + 3d_visualization + attribute_computation). SD is sample SD (n-1 denominator).

Cells: 4 models × 6 backends + Gemini × long_context = 25.
long_context runs Gemini only. The manual is ~226K tokens; Claude Sonnet 4.6 (200K) and GPT-4o (128K) advertised windows are below this, and the Qwen3-235B endpoint used for the benchmark is served at max-model-len=32,768 (a vLLM deployment setting, not the model's theoretical maximum), so long_context cannot be evaluated on any of the three.

Qwen cost uses the cloud-equivalent (time-based) `mean_cost_usd_effective` value; the self-hosted marginal cost is $0 and would be misleading.

## Table 1 (compact) — core metrics

5 core metrics reported here. Goal Completion is reported separately below (Appendix A) because its effective n differs — see the footnote on that table.

| Cell (Model / Backend) | Step Acc (%) ↑ | Hall Rate (%) ↓ | Loop Rate (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓ | Cost total/step ($) ↓ |
|---|---|---|---|---|---|---|
| gemini / no_rag | 100.0±0.0 | 12.5±0.0 | 0.0±0.0 | 8.6±0.6 | $5.40±0.56m | $5.40±0.56m |
| gemini / vanilla_vector | 100.0±0.0 | 16.2±6.0 | 0.0±0.0 | 10.2±0.8 | $10.18±0.70m | $10.18±0.70m |
| gemini / vanilla_budget | 98.8±4.0 | 13.8±4.0 | 0.0±0.0 | 9.1±0.5 | $6.93±0.44m | $6.93±0.44m |
| gemini / graph_only | 100.0±0.0 | 12.5±5.9 | 0.0±0.0 | 32.6±2.1 | $7.24±0.42m | $9.28±0.71m |
| gemini / vision_only | 98.8±4.0 | 13.8±4.0 | 0.0±0.0 | 10.1±0.8 | $5.38±0.41m | $5.38±0.41m |
| gemini / full_system | 100.0±0.0 | 12.5±0.0 | 0.0±0.0 | 33.1±3.0 | $8.70±0.53m | $11.47±1.08m |
| gemini / state_path | 97.5±5.3 | 12.5±0.0 | 0.0±0.0 | 32.1±3.4 | $7.49±0.44m | $10.45±0.98m |
| claude / no_rag | 100.0±0.0 | 35.0±7.9 | 0.0±0.0 | 2.9±0.4 | $7.10±0.03m | $7.10±0.03m |
| claude / vanilla_vector | 87.5±0.0 | 27.5±12.9 | 0.0±0.0 | 4.2±0.4 | $17.92±0.06m | $17.92±0.06m |
| claude / vanilla_budget | 87.5±0.0 | 22.5±12.9 | 0.0±0.0 | 3.3±0.3 | $10.43±0.06m | $10.43±0.06m |
| claude / graph_only | 88.8±4.0 | 12.5±0.0 | 0.0±0.0 | 26.4±4.7 | $9.69±0.13m | $11.77±0.68m |
| claude / vision_only | 97.5±5.3 | 15.0±7.9 | 0.0±0.0 | 4.5±0.3 | $7.16±0.04m | $7.16±0.04m |
| claude / full_system | 88.8±4.0 | 35.0±7.9 | 0.0±0.0 | 26.4±3.6 | $11.46±0.05m | $14.27±0.63m |
| claude / state_path | 96.2±6.0 | 12.5±0.0 | 0.0±0.0 | 25.1±4.8 | $10.18±0.19m | $13.19±0.99m |
| gpt / no_rag | 98.8±4.0 | 12.5±0.0 | 0.0±0.0 | 1.9±0.1 | $3.76±0.00m | $3.76±0.00m |
| gpt / vanilla_vector | 91.2±6.0 | 12.5±0.0 | 0.0±0.0 | 3.1±0.2 | $11.55±0.01m | $11.55±0.01m |
| gpt / vanilla_budget | 95.0±6.5 | 12.5±0.0 | 0.0±0.0 | 2.2±0.1 | $6.26±0.01m | $6.26±0.01m |
| gpt / graph_only | 96.2±6.0 | 12.5±0.0 | 0.0±0.0 | 25.4±0.5 | $5.54±0.01m | $7.41±0.08m |
| gpt / vision_only | 100.0±0.0 | 12.5±0.0 | 7.5±6.5 | 3.3±0.1 | $3.92±0.01m | $3.92±0.01m |
| gpt / full_system | 83.8±6.0 | 12.5±0.0 | 7.5±12.1 | 25.5±3.6 | $7.04±0.03m | $9.83±0.63m |
| gpt / state_path | 100.0±0.0 | 12.5±0.0 | 0.0±0.0 | 24.6±4.0 | $5.88±0.14m | $9.05±1.08m |
| gemini / long_context | n/a | n/a | n/a | n/a | n/a | n/a |

## Appendix A — Goal Completion

**Effective n footnote (unified3)**: 3d_visualization step_3 was refined to a goal-reached state (all three slices displayed) for this run, so it now contributes to Goal Completion. attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). Effective n per cell = 3 scenarios × 5 replicates = 15 observations. Cross-tag comparison with unified2 Goal Comp is prohibited (see methodology_audit_trail.md — scenario refinement #1).

| Cell (Model / Backend) | Goal Comp (%) ↑ |
|---|---|
| gemini / no_rag | 100.0±0.0 |
| gemini / vanilla_vector | 100.0±0.0 |
| gemini / vanilla_budget | 100.0±0.0 |
| gemini / graph_only | 100.0±0.0 |
| gemini / vision_only | 100.0±0.0 |
| gemini / full_system | 100.0±0.0 |
| gemini / state_path | 100.0±0.0 |
| claude / no_rag | 100.0±0.0 |
| claude / vanilla_vector | 100.0±0.0 |
| claude / vanilla_budget | 100.0±0.0 |
| claude / graph_only | 100.0±0.0 |
| claude / vision_only | 100.0±0.0 |
| claude / full_system | 100.0±0.0 |
| claude / state_path | 100.0±0.0 |
| gpt / no_rag | 100.0±0.0 |
| gpt / vanilla_vector | 100.0±0.0 |
| gpt / vanilla_budget | 100.0±0.0 |
| gpt / graph_only | 90.0±31.6 |
| gpt / vision_only | 100.0±0.0 |
| gpt / full_system | 100.0±0.0 |
| gpt / state_path | 100.0±0.0 |
| gemini / long_context | n/a |
