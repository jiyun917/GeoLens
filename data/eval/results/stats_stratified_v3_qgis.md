# Stratified permutation tests — v3_qgis (strata = model: gemini, claude, gpt; 10000 permutations, seed 42, two-sided)

| pair | metric | direction | observed Δ (mean over models) | stratified p | per-model Δ (raw p) | direction count |
|---|---|---|---|---|---|---|
| full_system vs vanilla_budget | step_accuracy | higher | -0.0292 | 0.0684 | gemini +0.012 (1.000); claude +0.012 (1.000); gpt -0.112 (0.003) | 2/3 |
| full_system vs vanilla_budget | hallucination_rate | lower | +0.0375 | 0.0517 | gemini -0.013 (1.000); claude +0.125 (0.058); gpt +0.000 (1.000) | 1/3 |
| full_system vs vanilla_budget | goal_completion_rate | higher | +0.0000 | 1.0000 | gemini +0.000 (1.000); claude +0.000 (1.000); gpt +0.000 (1.000) | 0/3 |
| full_system vs vanilla_budget | mean_cost_total_usd | lower | +0.0040 | 0.0001 | gemini +0.005 (0.000); claude +0.004 (0.000); gpt +0.004 (0.000) | 0/3 |
| full_system vs vanilla_budget | mean_latency_sec | lower | +23.4485 | 0.0001 | gemini +23.984 (0.000); claude +23.059 (0.000); gpt +23.302 (0.000) | 0/3 |
| full_system vs vanilla_vector | step_accuracy | higher | -0.0208 | 0.1384 | gemini +0.000 (1.000); claude +0.012 (1.000); gpt -0.075 (0.035) | 1/3 |
| full_system vs vanilla_vector | hallucination_rate | lower | +0.0125 | 0.6502 | gemini -0.038 (0.213); claude +0.075 (0.306); gpt +0.000 (1.000) | 1/3 |
| full_system vs vanilla_vector | goal_completion_rate | higher | +0.0000 | 1.0000 | gemini +0.000 (1.000); claude +0.000 (1.000); gpt +0.000 (1.000) | 0/3 |
| full_system vs vanilla_vector | mean_cost_total_usd | lower | -0.0014 | 0.0002 | gemini +0.001 (0.001); claude -0.004 (0.000); gpt -0.002 (0.000) | 2/3 |
| full_system vs vanilla_vector | mean_latency_sec | lower | +22.4812 | 0.0001 | gemini +22.896 (0.000); claude +22.225 (0.000); gpt +22.323 (0.000) | 0/3 |
| full_system vs no_rag | step_accuracy | higher | -0.0875 | 0.0001 | gemini +0.000 (1.000); claude -0.113 (0.000); gpt -0.150 (0.000) | 0/3 |
| full_system vs no_rag | hallucination_rate | lower | +0.0000 | 1.0000 | gemini +0.000 (1.000); claude +0.000 (1.000); gpt +0.000 (1.000) | 0/3 |
| full_system vs no_rag | goal_completion_rate | higher | +0.0000 | 1.0000 | gemini +0.000 (1.000); claude +0.000 (1.000); gpt +0.000 (1.000) | 0/3 |
| full_system vs no_rag | mean_cost_total_usd | lower | +0.0064 | 0.0001 | gemini +0.006 (0.000); claude +0.007 (0.000); gpt +0.006 (0.000) | 0/3 |
| full_system vs no_rag | mean_latency_sec | lower | +23.8388 | 0.0001 | gemini +24.406 (0.000); claude +23.527 (0.000); gpt +23.583 (0.000) | 0/3 |
| state_path vs vanilla_budget | step_accuracy | higher | +0.0417 | 0.0060 | gemini -0.013 (1.000); claude +0.088 (0.003); gpt +0.050 (0.086) | 2/3 |
| state_path vs vanilla_budget | hallucination_rate | lower | -0.0375 | 0.0421 | gemini -0.013 (1.000); claude -0.100 (0.083); gpt +0.000 (1.000) | 2/3 |
| state_path vs vanilla_budget | goal_completion_rate | higher | +0.0000 | 1.0000 | gemini +0.000 (1.000); claude +0.000 (1.000); gpt +0.000 (1.000) | 0/3 |
| state_path vs vanilla_budget | mean_cost_total_usd | lower | +0.0030 | 0.0001 | gemini +0.004 (0.000); claude +0.003 (0.000); gpt +0.003 (0.000) | 0/3 |
| state_path vs vanilla_budget | mean_latency_sec | lower | +22.4069 | 0.0001 | gemini +23.032 (0.000); claude +21.785 (0.000); gpt +22.404 (0.000) | 0/3 |
| graph_only vs vanilla_budget | step_accuracy | higher | +0.0125 | 0.4395 | gemini +0.012 (1.000); claude +0.012 (1.000); gpt +0.013 (1.000) | 3/3 |
| graph_only vs vanilla_budget | hallucination_rate | lower | -0.0375 | 0.0439 | gemini -0.013 (1.000); claude -0.100 (0.083); gpt +0.000 (1.000) | 2/3 |
| graph_only vs vanilla_budget | goal_completion_rate | higher | -0.0333 | 1.0000 | gemini +0.000 (1.000); claude +0.000 (1.000); gpt -0.100 (1.000) | 0/3 |
| graph_only vs vanilla_budget | mean_cost_total_usd | lower | +0.0016 | 0.0001 | gemini +0.002 (0.000); claude +0.001 (0.000); gpt +0.001 (0.000) | 0/3 |
| graph_only vs vanilla_budget | mean_latency_sec | lower | +23.3219 | 0.0001 | gemini +23.561 (0.000); claude +23.120 (0.000); gpt +23.284 (0.000) | 0/3 |

## Holm correction over the 25-test family (stratified p)

| pair | metric | p | Holm p |
|---|---|---|---|
| full_system vs vanilla_budget | step_accuracy | 0.0684 | 0.6839 |
| full_system vs vanilla_budget | hallucination_rate | 0.0517 | 0.5686 |
| full_system vs vanilla_budget | goal_completion_rate | 1.0000 | 1.0000 |
| full_system vs vanilla_budget | mean_cost_total_usd | 0.0001 | 0.0025 |
| full_system vs vanilla_budget | mean_latency_sec | 0.0001 | 0.0025 |
| full_system vs vanilla_vector | step_accuracy | 0.1384 | 1.0000 |
| full_system vs vanilla_vector | hallucination_rate | 0.6502 | 1.0000 |
| full_system vs vanilla_vector | goal_completion_rate | 1.0000 | 1.0000 |
| full_system vs vanilla_vector | mean_cost_total_usd | 0.0002 | 0.0030 |
| full_system vs vanilla_vector | mean_latency_sec | 0.0001 | 0.0025 |
| full_system vs no_rag | step_accuracy | 0.0001 | 0.0025 |
| full_system vs no_rag | hallucination_rate | 1.0000 | 1.0000 |
| full_system vs no_rag | goal_completion_rate | 1.0000 | 1.0000 |
| full_system vs no_rag | mean_cost_total_usd | 0.0001 | 0.0025 |
| full_system vs no_rag | mean_latency_sec | 0.0001 | 0.0025 |
| state_path vs vanilla_budget | step_accuracy | 0.0060 | 0.0840 |
| state_path vs vanilla_budget | hallucination_rate | 0.0421 | 0.5472 |
| state_path vs vanilla_budget | goal_completion_rate | 1.0000 | 1.0000 |
| state_path vs vanilla_budget | mean_cost_total_usd | 0.0001 | 0.0025 |
| state_path vs vanilla_budget | mean_latency_sec | 0.0001 | 0.0025 |
| graph_only vs vanilla_budget | step_accuracy | 0.4395 | 1.0000 |
| graph_only vs vanilla_budget | hallucination_rate | 0.0439 | 0.5472 |
| graph_only vs vanilla_budget | goal_completion_rate | 1.0000 | 1.0000 |
| graph_only vs vanilla_budget | mean_cost_total_usd | 0.0001 | 0.0025 |
| graph_only vs vanilla_budget | mean_latency_sec | 0.0001 | 0.0025 |
