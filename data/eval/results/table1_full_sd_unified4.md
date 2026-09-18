# Paper Table 1 — full mean ± sample SD for all 25 cells (unified4)

> **Annotation (V3-9, 2026-09-18)**: the unified2–4 `full_system` (and `state_path`) figures in this file were measured WITHOUT linked_chunks text — every linked_chunks id in the workflow JSONs had been dangling since the 2026-07-27 re-ingest, so graph_context held only the per-node title/description vector search. See `methodology_audit_trail.md` V3-9.

Statistical unit = replicate (n=5 per cell). Each replicate value is the mean across the scenarios (survey_setup + 3d_visualization + attribute_computation). SD is sample SD (n-1 denominator).

Cells: 4 models × 6 backends + Gemini × long_context = 25.
long_context runs Gemini only. The manual is ~226K tokens; Claude Sonnet 4.6 (200K) and GPT-4o (128K) advertised windows are below this, and the Qwen3-235B endpoint used for the benchmark is served at max-model-len=32,768 (a vLLM deployment setting, not the model's theoretical maximum), so long_context cannot be evaluated on any of the three.

Qwen cost uses the cloud-equivalent (time-based) `mean_cost_usd_effective` value; the self-hosted marginal cost is $0 and would be misleading.

## Table 1 (compact) — core metrics

5 core metrics reported here. Goal Completion is reported separately below (Appendix A) because its effective n differs — see the footnote on that table.

| Cell (Model / Backend) | Step Acc (%) ↑ | Hall Rate (%) ↓ | Loop Rate (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓ |
|---|---|---|---|---|---|
| gemini / no_rag | 66.7±17.9 | 0.8±1.9 | 0.0±0.0 | 10.6±1.3 | $0.75±0.01m |
| gemini / vanilla_vector | 75.0±11.4 | 7.5±4.6 | 1.7±2.3 | 10.3±0.9 | $9.27±0.01m |
| gemini / graph_only | 70.0±12.3 | 9.2±9.5 | 0.0±0.0 | 19.3±2.5 | $0.84±0.01m |
| gemini / vision_only | 77.5±9.6 | 4.2±7.2 | 1.7±2.3 | 14.0±1.4 | $0.87±0.01m |
| gemini / full_system | 72.5±9.6 | 7.5±7.5 | 0.8±1.9 | 40.9±1.3 | $2.13±0.05m |
| gemini / state_path | 76.7±6.3 | 1.7±3.7 | 0.0±0.0 | 40.6±4.3 | $1.05±0.01m |
| claude / no_rag | 85.0±2.3 | 25.0±5.1 | 2.5±2.3 | 3.0±0.3 | $6.46±0.05m |
| claude / vanilla_vector | 84.2±1.9 | 24.2±3.5 | 0.8±1.9 | 3.9±0.4 | $27.10±0.02m |
| claude / graph_only | 80.0±4.6 | 23.3±3.7 | 0.8±1.9 | 11.8±0.7 | $6.79±0.06m |
| claude / vision_only | 83.3±0.0 | 26.7±5.6 | 1.7±3.7 | 4.8±0.5 | $6.82±0.04m |
| claude / full_system | 85.0±2.3 | 22.5±3.7 | 2.5±3.7 | 32.4±1.8 | $10.60±0.14m |
| claude / state_path | 83.3±0.0 | 19.2±7.6 | 2.5±3.7 | 31.1±1.8 | $7.42±0.05m |
| gpt / no_rag | 50.8±12.6 | 30.8±18.3 | 0.0±0.0 | 2.0±0.1 | $3.54±0.03m |
| gpt / vanilla_vector | 60.0±6.3 | 36.7±11.6 | 1.7±3.7 | 5.1±0.3 | $17.93±0.02m |
| gpt / graph_only | 67.5±6.2 | 35.0±3.7 | 0.0±0.0 | 10.3±0.3 | $3.70±0.02m |
| gpt / vision_only | 54.2±14.4 | 36.7±9.0 | 0.0±0.0 | 3.5±0.2 | $3.75±0.03m |
| gpt / full_system | 69.2±3.7 | 30.8±7.0 | 0.0±0.0 | 31.2±2.4 | $6.08±0.10m |
| gpt / state_path | 72.5±7.6 | 20.8±8.8 | 0.0±0.0 | 31.0±2.3 | $4.09±0.04m |
| qwen / no_rag | 49.2±8.0 | 40.0±12.0 | 21.7±7.5 | 5.9±0.7 | $5.48±0.67m |
| qwen / vanilla_vector | 55.0±6.8 | 61.7±13.0 | 15.0±6.3 | 9.7±0.5 | $9.05±0.48m |
| qwen / graph_only | 49.2±9.9 | 67.5±6.8 | 2.5±5.6 | 14.2±0.5 | $13.26±0.45m |
| qwen / vision_only | 62.5±12.5 | 54.2±22.2 | 10.0±7.0 | 9.3±0.5 | $8.72±0.43m |
| qwen / full_system | 56.7±9.1 | 50.0±8.8 | 6.7±8.6 | 35.5±1.1 | $33.10±1.05m |
| qwen / state_path | 55.0±10.8 | 56.7±9.6 | 5.8±7.0 | 33.4±1.4 | $31.20±1.30m |
| gemini / long_context | 59.2±9.9 | 20.8±11.8 | 0.0±0.0 | 13.9±1.5 | $315.56±0.01m |

## Appendix A — Goal Completion

**Effective n footnote (unified3)**: 3d_visualization step_3 was refined to a goal-reached state (all three slices displayed) for this run, so it now contributes to Goal Completion. attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). Effective n per cell = 3 scenarios × 5 replicates = 15 observations. Cross-tag comparison with unified2 Goal Comp is prohibited (see methodology_audit_trail.md — scenario refinement #1).

| Cell (Model / Backend) | Goal Comp (%) ↑ |
|---|---|
| gemini / no_rag | 80.0±18.3 |
| gemini / vanilla_vector | 93.3±14.9 |
| gemini / graph_only | 80.0±18.3 |
| gemini / vision_only | 80.0±18.3 |
| gemini / full_system | 80.0±18.3 |
| gemini / state_path | 93.3±14.9 |
| claude / no_rag | 100.0±0.0 |
| claude / vanilla_vector | 100.0±0.0 |
| claude / graph_only | 93.3±14.9 |
| claude / vision_only | 100.0±0.0 |
| claude / full_system | 100.0±0.0 |
| claude / state_path | 80.0±18.3 |
| gpt / no_rag | 73.3±14.9 |
| gpt / vanilla_vector | 73.3±14.9 |
| gpt / graph_only | 100.0±0.0 |
| gpt / vision_only | 86.7±29.8 |
| gpt / full_system | 93.3±14.9 |
| gpt / state_path | 86.7±18.3 |
| qwen / no_rag | 53.3±18.3 |
| qwen / vanilla_vector | 40.0±14.9 |
| qwen / graph_only | 20.0±18.3 |
| qwen / vision_only | 13.3±18.3 |
| qwen / full_system | 40.0±27.9 |
| qwen / state_path | 40.0±27.9 |
| gemini / long_context | 93.3±14.9 |
