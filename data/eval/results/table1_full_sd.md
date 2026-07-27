# Paper Table 1 — full mean ± sample SD for all 25 cells

Statistical unit = replicate (n=5 per cell). Each replicate value is the mean across the 2 scenarios (survey_setup + 3d_visualization). SD is sample SD (n-1 denominator).

Cells: 4 models × 6 backends + Gemini × long_context = 25.
long_context runs Gemini only because the manual (~226K tokens) exceeds the 128K–200K context windows of the other three models.

Qwen cost uses the cloud-equivalent (time-based) `mean_cost_usd_effective` value; the self-hosted marginal cost is $0 and would be misleading.

## Table 1 (compact) — core metrics

5 core metrics reported here. Goal Completion is reported separately below (Appendix A) because its effective n differs — see the footnote on that table.

| Cell (Model / Backend) | Step Acc (%) ↑ | Hall Rate (%) ↓ | Loop Rate (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓ |
|---|---|---|---|---|---|
| gemini / no_rag | 55.0±6.8 | 7.5±11.2 | 0.0±0.0 | 7.1±0.7 | $0.70±0.01m |
| gemini / vanilla_vector | 60.0±10.5 | 10.0±10.5 | 0.0±0.0 | 8.6±0.3 | $9.30±0.01m |
| gemini / graph_only | 52.5±5.6 | 2.5±5.6 | 0.0±0.0 | 14.8±0.9 | $0.79±0.01m |
| gemini / vision_only | 55.0±6.8 | 5.0±6.8 | 0.0±0.0 | 9.5±1.0 | $0.81±0.02m |
| gemini / full_system | 60.0±10.5 | 5.0±6.8 | 0.0±0.0 | 34.3±3.6 | $2.66±0.06m |
| gemini / state_path | 55.0±6.8 | 7.5±11.2 | 0.0±0.0 | 30.4±3.4 | $1.56±0.05m |
| claude / no_rag | 72.5±10.5 | 25.0±0.0 | 5.0±6.8 | 2.8±0.5 | $6.06±0.10m |
| claude / vanilla_vector | 72.5±5.6 | 25.0±8.8 | 12.5±0.0 | 4.0±0.2 | $27.13±0.05m |
| claude / graph_only | 77.5±10.5 | 20.0±11.2 | 2.5±5.6 | 10.7±0.5 | $6.37±0.06m |
| claude / vision_only | 72.5±5.6 | 30.0±11.2 | 12.5±0.0 | 5.7±0.6 | $6.42±0.02m |
| claude / full_system | 77.5±5.6 | 15.0±5.6 | 10.0±5.6 | 27.5±2.3 | $11.66±0.13m |
| claude / state_path | 85.0±5.6 | 10.0±5.6 | 0.0±0.0 | 26.7±2.1 | $8.67±0.12m |
| gpt / no_rag | 42.5±14.3 | 40.0±16.3 | 0.0±0.0 | 2.3±0.2 | $3.45±0.04m |
| gpt / vanilla_vector | 37.5±8.8 | 47.5±5.6 | 0.0±0.0 | 3.5±0.5 | $18.11±0.01m |
| gpt / graph_only | 77.5±10.5 | 27.5±20.5 | 0.0±0.0 | 9.8±0.4 | $3.61±0.04m |
| gpt / vision_only | 57.5±14.3 | 27.5±16.3 | 0.0±0.0 | 4.4±0.1 | $3.64±0.02m |
| gpt / full_system | 70.0±6.8 | 55.0±6.8 | 0.0±0.0 | 29.7±1.9 | $7.01±0.07m |
| gpt / state_path | 57.5±6.8 | 50.0±0.0 | 0.0±0.0 | 28.4±1.6 | $4.94±0.16m |
| qwen / no_rag | 57.5±19.0 | 62.5±8.8 | 7.5±6.8 | 7.3±1.1 | $10.53±1.52m |
| qwen / vanilla_vector | 35.0±16.3 | 72.5±20.5 | 7.5±11.2 | 42.2±71.4 | $60.45±102.33m |
| qwen / graph_only | 52.5±16.3 | 70.0±14.3 | 2.5±5.6 | 13.9±2.1 | $19.94±3.00m |
| qwen / vision_only | 52.5±10.5 | 70.0±11.2 | 2.5±5.6 | 11.0±1.5 | $15.80±2.15m |
| qwen / full_system | 50.0±12.5 | 47.5±10.5 | 0.0±0.0 | 30.9±2.1 | $44.30±3.00m |
| qwen / state_path | 50.0±8.8 | 60.0±5.6 | 0.0±0.0 | 29.9±1.5 | $42.90±2.20m |
| gemini / long_context | 42.5±11.2 | 37.5±19.8 | 0.0±0.0 | 10.8±1.6 | $283.45±0.03m |

## Appendix A — Goal Completion

**Effective n footnote**: 3d_visualization captures the penultimate state, so no backend can pass the 3-gate check on that scenario. Goal Completion in each replicate is therefore effectively a survey_setup-only measurement (n=5 per cell, not n=10). Interpret differences with reduced power in mind.

| Cell (Model / Backend) | Goal Comp (%) ↑ |
|---|---|
| gemini / no_rag | 50.0±0.0 |
| gemini / vanilla_vector | 50.0±0.0 |
| gemini / graph_only | 50.0±0.0 |
| gemini / vision_only | 50.0±0.0 |
| gemini / full_system | 30.0±27.4 |
| gemini / state_path | 20.0±27.4 |
| claude / no_rag | 50.0±0.0 |
| claude / vanilla_vector | 50.0±0.0 |
| claude / graph_only | 50.0±0.0 |
| claude / vision_only | 50.0±0.0 |
| claude / full_system | 50.0±0.0 |
| claude / state_path | 30.0±27.4 |
| gpt / no_rag | 0.0±0.0 |
| gpt / vanilla_vector | 20.0±27.4 |
| gpt / graph_only | 50.0±0.0 |
| gpt / vision_only | 40.0±22.4 |
| gpt / full_system | 30.0±27.4 |
| gpt / state_path | 20.0±27.4 |
| qwen / no_rag | 30.0±27.4 |
| qwen / vanilla_vector | 10.0±22.4 |
| qwen / graph_only | 20.0±27.4 |
| qwen / vision_only | 10.0±22.4 |
| qwen / full_system | 10.0±22.4 |
| qwen / state_path | 10.0±22.4 |
| gemini / long_context | 40.0±22.4 |
