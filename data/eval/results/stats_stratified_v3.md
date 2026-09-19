# Stratified permutation tests — v3 (strata = model: gemini, claude, gpt; 10000 permutations, seed 42, two-sided)

| pair | metric | direction | observed Δ (mean over models) | stratified p | per-model Δ (raw p) | direction count |
|---|---|---|---|---|---|---|
| full_system vs vanilla_budget | step_accuracy | higher | +0.0986 | 0.0001 | gemini +0.092 (0.025); claude +0.125 (0.000); gpt +0.079 (0.009) | 3/3 |
| full_system vs vanilla_budget | hallucination_rate | lower | +0.0236 | 0.0004 | gemini +0.008 (0.648); claude +0.000 (1.000); gpt +0.062 (0.000) | 0/3 |
| full_system vs vanilla_budget | goal_completion_rate | higher | -0.1556 | 0.0064 | gemini +0.100 (0.368); claude -0.067 (0.479); gpt -0.500 (0.000) | 1/3 |
| full_system vs vanilla_budget | mean_cost_total_usd | lower | +0.0040 | 0.0001 | gemini +0.005 (0.000); claude +0.004 (0.000); gpt +0.004 (0.000) | 0/3 |
| full_system vs vanilla_budget | mean_latency_sec | lower | +10.0762 | 0.0001 | gemini +11.236 (0.000); claude +9.742 (0.000); gpt +9.251 (0.000) | 0/3 |
| full_system vs vanilla_vector | step_accuracy | higher | +0.0861 | 0.0001 | gemini +0.096 (0.020); claude +0.125 (0.000); gpt +0.037 (0.154) | 3/3 |
| full_system vs vanilla_vector | hallucination_rate | lower | +0.0181 | 0.0068 | gemini -0.004 (1.000); claude +0.000 (1.000); gpt +0.058 (0.000) | 1/3 |
| full_system vs vanilla_vector | goal_completion_rate | higher | -0.0667 | 0.1442 | gemini +0.133 (0.171); claude -0.067 (0.479); gpt -0.267 (0.001) | 1/3 |
| full_system vs vanilla_vector | mean_cost_total_usd | lower | -0.0072 | 0.0001 | gemini -0.003 (0.000); claude -0.012 (0.000); gpt -0.007 (0.000) | 3/3 |
| full_system vs vanilla_vector | mean_latency_sec | lower | +9.1268 | 0.0001 | gemini +9.791 (0.000); claude +9.091 (0.000); gpt +8.499 (0.000) | 0/3 |
| full_system vs no_rag | step_accuracy | higher | +0.1333 | 0.0001 | gemini +0.179 (0.000); claude +0.125 (0.000); gpt +0.096 (0.001) | 3/3 |
| full_system vs no_rag | hallucination_rate | lower | +0.0153 | 0.0482 | gemini +0.000 (1.000); claude -0.008 (0.473); gpt +0.054 (0.002) | 1/3 |
| full_system vs no_rag | goal_completion_rate | higher | -0.0556 | 0.2403 | gemini +0.167 (0.059); claude -0.067 (0.479); gpt -0.267 (0.001) | 1/3 |
| full_system vs no_rag | mean_cost_total_usd | lower | +0.0070 | 0.0001 | gemini +0.007 (0.000); claude +0.008 (0.000); gpt +0.006 (0.000) | 0/3 |
| full_system vs no_rag | mean_latency_sec | lower | +10.5114 | 0.0001 | gemini +11.990 (0.000); claude +9.886 (0.000); gpt +9.658 (0.000) | 0/3 |
| state_path vs vanilla_budget | step_accuracy | higher | +0.0472 | 0.0281 | gemini -0.017 (0.749); claude -0.025 (0.211); gpt +0.183 (0.000) | 1/3 |
| state_path vs vanilla_budget | hallucination_rate | lower | +0.0097 | 0.0873 | gemini +0.013 (0.350); claude +0.000 (1.000); gpt +0.017 (0.474) | 0/3 |
| state_path vs vanilla_budget | goal_completion_rate | higher | -0.2111 | 0.0001 | gemini -0.167 (0.201); claude -0.200 (0.011); gpt -0.267 (0.002) | 0/3 |
| state_path vs vanilla_budget | mean_cost_total_usd | lower | +0.0029 | 0.0001 | gemini +0.004 (0.000); claude +0.002 (0.000); gpt +0.002 (0.000) | 0/3 |
| state_path vs vanilla_budget | mean_latency_sec | lower | +9.6350 | 0.0001 | gemini +10.498 (0.000); claude +9.687 (0.000); gpt +8.720 (0.000) | 0/3 |
| graph_only vs vanilla_budget | step_accuracy | higher | +0.0319 | 0.0750 | gemini -0.033 (0.408); claude +0.000 (1.000); gpt +0.129 (0.000) | 1/3 |
| graph_only vs vanilla_budget | hallucination_rate | lower | -0.0014 | 1.0000 | gemini -0.004 (1.000); claude +0.000 (1.000); gpt +0.000 (1.000) | 1/3 |
| graph_only vs vanilla_budget | goal_completion_rate | higher | +0.0444 | 0.3006 | gemini +0.067 (0.642); claude +0.000 (1.000); gpt +0.067 (0.580) | 2/3 |
| graph_only vs vanilla_budget | mean_cost_total_usd | lower | +0.0013 | 0.0001 | gemini +0.002 (0.000); claude +0.001 (0.000); gpt +0.001 (0.000) | 0/3 |
| graph_only vs vanilla_budget | mean_latency_sec | lower | +8.6567 | 0.0001 | gemini +9.145 (0.000); claude +8.983 (0.000); gpt +7.842 (0.000) | 0/3 |

## Holm correction over the 25-test family (stratified p)

| pair | metric | p | Holm p |
|---|---|---|---|
| full_system vs vanilla_budget | step_accuracy | 0.0001 | 0.0025 |
| full_system vs vanilla_budget | hallucination_rate | 0.0004 | 0.0044 |
| full_system vs vanilla_budget | goal_completion_rate | 0.0064 | 0.0640 |
| full_system vs vanilla_budget | mean_cost_total_usd | 0.0001 | 0.0025 |
| full_system vs vanilla_budget | mean_latency_sec | 0.0001 | 0.0025 |
| full_system vs vanilla_vector | step_accuracy | 0.0001 | 0.0025 |
| full_system vs vanilla_vector | hallucination_rate | 0.0068 | 0.0640 |
| full_system vs vanilla_vector | goal_completion_rate | 0.1442 | 0.5767 |
| full_system vs vanilla_vector | mean_cost_total_usd | 0.0001 | 0.0025 |
| full_system vs vanilla_vector | mean_latency_sec | 0.0001 | 0.0025 |
| full_system vs no_rag | step_accuracy | 0.0001 | 0.0025 |
| full_system vs no_rag | hallucination_rate | 0.0482 | 0.3374 |
| full_system vs no_rag | goal_completion_rate | 0.2403 | 0.7208 |
| full_system vs no_rag | mean_cost_total_usd | 0.0001 | 0.0025 |
| full_system vs no_rag | mean_latency_sec | 0.0001 | 0.0025 |
| state_path vs vanilla_budget | step_accuracy | 0.0281 | 0.2248 |
| state_path vs vanilla_budget | hallucination_rate | 0.0873 | 0.4500 |
| state_path vs vanilla_budget | goal_completion_rate | 0.0001 | 0.0025 |
| state_path vs vanilla_budget | mean_cost_total_usd | 0.0001 | 0.0025 |
| state_path vs vanilla_budget | mean_latency_sec | 0.0001 | 0.0025 |
| graph_only vs vanilla_budget | step_accuracy | 0.0750 | 0.4500 |
| graph_only vs vanilla_budget | hallucination_rate | 1.0000 | 1.0000 |
| graph_only vs vanilla_budget | goal_completion_rate | 0.3006 | 0.7208 |
| graph_only vs vanilla_budget | mean_cost_total_usd | 0.0001 | 0.0025 |
| graph_only vs vanilla_budget | mean_latency_sec | 0.0001 | 0.0025 |
