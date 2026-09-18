# Paper Table 1 — full mean ± sample SD for all 25 cells (unified3)

Statistical unit = replicate (n=5 per cell). Each replicate value is the mean across the scenarios (survey_setup + 3d_visualization + attribute_computation). SD is sample SD (n-1 denominator).

Cells: 4 models × 6 backends + Gemini × long_context = 25.
long_context runs Gemini only. The manual is ~226K tokens; Claude Sonnet 4.6 (200K) and GPT-4o (128K) advertised windows are below this, and the Qwen3-235B endpoint used for the benchmark is served at max-model-len=32,768 (a vLLM deployment setting, not the model's theoretical maximum), so long_context cannot be evaluated on any of the three.

Qwen cost uses the cloud-equivalent (time-based) `mean_cost_usd_effective` value; the self-hosted marginal cost is $0 and would be misleading.

## Table 1 (compact) — core metrics

5 core metrics reported here. Goal Completion is reported separately below (Appendix A) because its effective n differs — see the footnote on that table.

| Cell (Model / Backend) | Step Acc (%) ↑ | Hall Rate (%) ↓ | Loop Rate (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓ |
|---|---|---|---|---|---|
| gemini / no_rag | 55.8±8.1 | 0.0±0.0 | 0.8±1.9 | 8.9±0.8 | $0.75±0.01m |
| gemini / vanilla_vector | 67.5±8.0 | 5.0±7.5 | 1.7±3.7 | 11.6±1.5 | $9.27±0.01m |
| gemini / graph_only | 63.3±17.5 | 2.5±5.6 | 0.0±0.0 | 18.9±0.4 | $0.84±0.01m |
| gemini / vision_only | 63.3±10.8 | 4.2±5.9 | 0.8±1.9 | 13.2±2.6 | $0.87±0.02m |
| gemini / full_system | 74.2±4.6 | 1.7±3.7 | 0.8±1.9 | 37.4±0.8 | $2.21±0.03m |
| gemini / state_path | 73.3±10.5 | 3.3±3.5 | 0.0±0.0 | 36.6±1.8 | $1.09±0.01m |
| claude / no_rag | 85.8±2.3 | 25.8±5.4 | 3.3±3.5 | 3.1±0.5 | $6.43±0.06m |
| claude / vanilla_vector | 83.3±0.0 | 30.0±6.2 | 1.7±2.3 | 4.3±0.4 | $27.10±0.04m |
| claude / graph_only | 80.0±4.6 | 20.8±5.9 | 0.8±1.9 | 11.3±0.6 | $6.84±0.14m |
| claude / vision_only | 83.3±0.0 | 25.0±4.2 | 0.0±0.0 | 4.9±0.8 | $6.82±0.05m |
| claude / full_system | 84.2±1.9 | 25.0±4.2 | 3.3±3.5 | 28.6±1.3 | $10.93±0.19m |
| claude / state_path | 83.3±0.0 | 25.8±4.6 | 3.3±3.5 | 27.5±1.4 | $7.62±0.05m |
| gpt / no_rag | 56.7±16.0 | 33.3±13.8 | 0.0±0.0 | 2.1±0.1 | $3.54±0.02m |
| gpt / vanilla_vector | 60.8±8.1 | 40.0±3.7 | 0.8±1.9 | 5.1±0.2 | $17.94±0.01m |
| gpt / graph_only | 65.8±7.5 | 35.8±8.6 | 0.0±0.0 | 9.8±0.5 | $3.71±0.01m |
| gpt / vision_only | 71.7±12.3 | 30.8±10.9 | 0.0±0.0 | 3.6±0.2 | $3.73±0.01m |
| gpt / full_system | 64.2±8.6 | 32.5±9.5 | 2.5±3.7 | 26.7±1.8 | $6.29±0.09m |
| gpt / state_path | 76.7±7.0 | 16.7±7.2 | 0.0±0.0 | 26.3±1.5 | $4.15±0.02m |
| qwen / no_rag | 43.3±11.3 | 43.3±12.4 | 24.2±8.0 | 6.7±0.9 | $6.28±0.84m |
| qwen / vanilla_vector | 41.7±9.8 | 55.0±20.5 | 13.3±9.5 | 9.6±0.9 | $9.00±0.86m |
| qwen / graph_only | 47.5±10.9 | 60.0±5.6 | 3.3±3.5 | 14.9±0.8 | $13.92±0.78m |
| qwen / vision_only | 47.5±11.3 | 60.8±8.6 | 13.3±6.2 | 8.1±0.5 | $7.56±0.48m |
| qwen / full_system | 60.8±7.0 | 60.8±8.1 | 6.7±4.8 | 32.6±1.1 | $30.40±1.03m |
| qwen / state_path | 61.7±13.9 | 60.0±14.9 | 6.7±8.1 | 32.4±1.9 | $30.21±1.74m |
| gemini / long_context | 64.2±11.3 | 10.0±7.0 | 5.8±3.7 | 12.9±1.5 | $315.54±0.01m |

## Appendix A — Goal Completion

**Effective n footnote (unified3)**: 3d_visualization step_3 was refined to a goal-reached state (all three slices displayed) for this run, so it now contributes to Goal Completion. attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). Effective n per cell = 3 scenarios × 5 replicates = 15 observations. Cross-tag comparison with unified2 Goal Comp is prohibited (see methodology_audit_trail.md — scenario refinement #1).

| Cell (Model / Backend) | Goal Comp (%) ↑ |
|---|---|
| gemini / no_rag | 80.0±18.3 |
| gemini / vanilla_vector | 80.0±18.3 |
| gemini / graph_only | 80.0±18.3 |
| gemini / vision_only | 73.3±14.9 |
| gemini / full_system | 80.0±29.8 |
| gemini / state_path | 73.3±14.9 |
| claude / no_rag | 100.0±0.0 |
| claude / vanilla_vector | 100.0±0.0 |
| claude / graph_only | 93.3±14.9 |
| claude / vision_only | 100.0±0.0 |
| claude / full_system | 93.3±14.9 |
| claude / state_path | 93.3±14.9 |
| gpt / no_rag | 66.7±23.6 |
| gpt / vanilla_vector | 80.0±18.3 |
| gpt / graph_only | 86.7±18.3 |
| gpt / vision_only | 93.3±14.9 |
| gpt / full_system | 73.3±14.9 |
| gpt / state_path | 66.7±23.6 |
| qwen / no_rag | 46.7±38.0 |
| qwen / vanilla_vector | 20.0±29.8 |
| qwen / graph_only | 40.0±27.9 |
| qwen / vision_only | 40.0±43.5 |
| qwen / full_system | 20.0±18.3 |
| qwen / state_path | 33.3±23.6 |
| gemini / long_context | 80.0±18.3 |
