# Stratified permutation tests — study2 (strata = model: gemini, claude, gpt; 10000 permutations, seed 42, two-sided)

| pair | metric | direction | observed Δ (mean over models) | stratified p | per-model Δ (raw p) | direction count |
|---|---|---|---|---|---|---|
| full_system vs vanilla_budget | step_accuracy | higher | +0.2899 | 0.0001 | gemini +0.201 (0.000); claude +0.248 (0.000); gpt +0.421 (0.000) | 3/3 |
| full_system vs vanilla_budget | hallucination_rate | lower | +0.0251 | 0.0720 | gemini -0.033 (0.213); claude +0.022 (0.472); gpt +0.087 (0.000) | 1/3 |
| full_system vs vanilla_budget | goal_completion_rate | higher | +0.0833 | 0.2227 | gemini +0.000 (1.000); claude +0.300 (0.012); gpt -0.050 (1.000) | 1/3 |
| full_system vs vanilla_budget | mean_cost_total_usd | lower | +0.0040 | 0.0001 | gemini +0.003 (0.000); claude +0.004 (0.000); gpt +0.004 (0.000) | 0/3 |
| full_system vs vanilla_budget | mean_latency_sec | lower | +12.4267 | 0.0001 | gemini +13.394 (0.000); claude +10.837 (0.000); gpt +13.050 (0.000) | 0/3 |
| full_system vs vanilla_vector | step_accuracy | higher | +0.1122 | 0.0003 | gemini +0.138 (0.010); claude -0.083 (0.016); gpt +0.282 (0.000) | 2/3 |
| full_system vs vanilla_vector | hallucination_rate | lower | +0.0037 | 0.8682 | gemini +0.022 (0.467); claude -0.120 (0.003); gpt +0.109 (0.000) | 1/3 |
| full_system vs vanilla_vector | goal_completion_rate | higher | +0.0000 | 1.0000 | gemini +0.200 (0.172); claude +0.300 (0.012); gpt -0.500 (0.000) | 2/3 |
| full_system vs vanilla_vector | mean_cost_total_usd | lower | -0.0017 | 0.0001 | gemini +0.000 (0.862); claude -0.004 (0.000); gpt -0.001 (0.000) | 2/3 |
| full_system vs vanilla_vector | mean_latency_sec | lower | +12.7363 | 0.0001 | gemini +14.032 (0.000); claude +10.805 (0.000); gpt +13.372 (0.000) | 0/3 |
| full_system vs no_rag | step_accuracy | higher | +0.4526 | 0.0001 | gemini +0.399 (0.000); claude +0.352 (0.000); gpt +0.606 (0.000) | 3/3 |
| full_system vs no_rag | hallucination_rate | lower | +0.0040 | 0.8616 | gemini -0.006 (0.845); claude -0.111 (0.014); gpt +0.129 (0.000) | 2/3 |
| full_system vs no_rag | goal_completion_rate | higher | +0.0167 | 1.0000 | gemini +0.050 (1.000); claude +0.300 (0.012); gpt -0.300 (0.011) | 2/3 |
| full_system vs no_rag | mean_cost_total_usd | lower | +0.0072 | 0.0001 | gemini +0.006 (0.000); claude +0.008 (0.000); gpt +0.007 (0.000) | 0/3 |
| full_system vs no_rag | mean_latency_sec | lower | +13.3871 | 0.0001 | gemini +14.770 (0.000); claude +11.576 (0.000); gpt +13.816 (0.000) | 0/3 |

## Holm correction over the 15-test family (stratified p)

| pair | metric | p | Holm p |
|---|---|---|---|
| full_system vs vanilla_budget | step_accuracy | 0.0001 | 0.0015 |
| full_system vs vanilla_budget | hallucination_rate | 0.0720 | 0.4320 |
| full_system vs vanilla_budget | goal_completion_rate | 0.2227 | 1.0000 |
| full_system vs vanilla_budget | mean_cost_total_usd | 0.0001 | 0.0015 |
| full_system vs vanilla_budget | mean_latency_sec | 0.0001 | 0.0015 |
| full_system vs vanilla_vector | step_accuracy | 0.0003 | 0.0021 |
| full_system vs vanilla_vector | hallucination_rate | 0.8682 | 1.0000 |
| full_system vs vanilla_vector | goal_completion_rate | 1.0000 | 1.0000 |
| full_system vs vanilla_vector | mean_cost_total_usd | 0.0001 | 0.0015 |
| full_system vs vanilla_vector | mean_latency_sec | 0.0001 | 0.0015 |
| full_system vs no_rag | step_accuracy | 0.0001 | 0.0015 |
| full_system vs no_rag | hallucination_rate | 0.8616 | 1.0000 |
| full_system vs no_rag | goal_completion_rate | 1.0000 | 1.0000 |
| full_system vs no_rag | mean_cost_total_usd | 0.0001 | 0.0015 |
| full_system vs no_rag | mean_latency_sec | 0.0001 | 0.0015 |
