# Direction consistency — v2 unified matrix

For each metric and each candidate pair (A vs B), we count how many of the 4 models have A winning over B in the metric's correct direction. **4/4 = universal**, **3/4 = majority**, **2/4 = mixed**, **≤1/4 = A loses**.

Statistical unit = replicate. Each cell in the underlying table is a per-model mean over 5 replicates; the winner per model is decided by comparing those means (no per-model significance requirement — that's the point of direction consistency at small n).


## step_accuracy (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | B (0.72/0.75) | A (0.85/0.84) | A (0.69/0.60) | A (0.57/0.55) | 3/4 models: A wins — majority |
| full_system vs no_rag | A (0.72/0.67) | = (0.85/0.85) | A (0.69/0.51) | A (0.57/0.49) | 3/3 models: A wins |
| vanilla_vector vs no_rag | A (0.75/0.67) | B (0.84/0.85) | A (0.60/0.51) | A (0.55/0.49) | 3/4 models: A wins — majority |
| graph_only vs vanilla_vector | B (0.70/0.75) | B (0.80/0.84) | A (0.68/0.60) | B (0.49/0.55) | 1/4 models: A wins — A loses |
| graph_only vs full_system | B (0.70/0.72) | B (0.80/0.85) | B (0.68/0.69) | B (0.49/0.57) | 0/4 models: A wins — A loses |
| state_path vs full_system | A (0.77/0.72) | B (0.83/0.85) | A (0.72/0.69) | B (0.55/0.57) | 2/4 models: A wins — mixed |

## faithfulness (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | = (0.93/0.93) | A (0.78/0.76) | A (0.69/0.63) | A (0.50/0.38) | 3/3 models: A wins |
| full_system vs no_rag | B (0.93/0.99) | A (0.78/0.75) | = (0.69/0.69) | B (0.50/0.60) | 1/3 models: A wins |
| vanilla_vector vs no_rag | B (0.93/0.99) | A (0.76/0.75) | B (0.63/0.69) | B (0.38/0.60) | 1/4 models: A wins — A loses |
| graph_only vs vanilla_vector | B (0.91/0.93) | A (0.77/0.76) | A (0.65/0.63) | B (0.33/0.38) | 2/4 models: A wins — mixed |
| graph_only vs full_system | B (0.91/0.93) | B (0.77/0.78) | B (0.65/0.69) | B (0.33/0.50) | 0/4 models: A wins — A loses |
| state_path vs full_system | A (0.98/0.93) | A (0.81/0.78) | A (0.79/0.69) | B (0.43/0.50) | 3/4 models: A wins — majority |

## hallucination_rate (lower better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | = (0.07/0.07) | A (0.23/0.24) | A (0.31/0.37) | A (0.50/0.62) | 3/3 models: A wins |
| full_system vs no_rag | B (0.07/0.01) | A (0.23/0.25) | B (0.31/0.31) | B (0.50/0.40) | 1/4 models: A wins — A loses |
| vanilla_vector vs no_rag | B (0.07/0.01) | A (0.24/0.25) | B (0.37/0.31) | B (0.62/0.40) | 1/4 models: A wins — A loses |
| graph_only vs vanilla_vector | B (0.09/0.07) | A (0.23/0.24) | A (0.35/0.37) | B (0.68/0.62) | 2/4 models: A wins — mixed |
| graph_only vs full_system | B (0.09/0.07) | B (0.23/0.23) | B (0.35/0.31) | B (0.68/0.50) | 0/4 models: A wins — A loses |
| state_path vs full_system | A (0.02/0.07) | A (0.19/0.23) | A (0.21/0.31) | B (0.57/0.50) | 3/4 models: A wins — majority |

## goal_completion_rate (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | B (0.80/0.93) | = (1.00/1.00) | A (0.93/0.73) | = (0.40/0.40) | 1/2 models: A wins |
| full_system vs no_rag | = (0.80/0.80) | = (1.00/1.00) | A (0.93/0.73) | B (0.40/0.53) | 1/2 models: A wins |
| vanilla_vector vs no_rag | A (0.93/0.80) | = (1.00/1.00) | = (0.73/0.73) | B (0.40/0.53) | 1/2 models: A wins |
| graph_only vs vanilla_vector | B (0.80/0.93) | B (0.93/1.00) | A (1.00/0.73) | B (0.20/0.40) | 1/4 models: A wins — A loses |
| graph_only vs full_system | = (0.80/0.80) | B (0.93/1.00) | A (1.00/0.93) | B (0.20/0.40) | 1/3 models: A wins |
| state_path vs full_system | A (0.93/0.80) | B (0.80/1.00) | B (0.87/0.93) | = (0.40/0.40) | 1/3 models: A wins |

## mean_latency_sec (lower better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | B (40.90/10.31) | B (32.37/3.86) | B (31.17/5.07) | B (35.47/9.69) | 0/4 models: A wins — A loses |
| full_system vs no_rag | B (40.90/10.63) | B (32.37/3.01) | B (31.17/2.01) | B (35.47/5.87) | 0/4 models: A wins — A loses |
| vanilla_vector vs no_rag | A (10.31/10.63) | B (3.86/3.01) | B (5.07/2.01) | B (9.69/5.87) | 1/4 models: A wins — A loses |
| graph_only vs vanilla_vector | B (19.30/10.31) | B (11.78/3.86) | B (10.27/5.07) | B (14.21/9.69) | 0/4 models: A wins — A loses |
| graph_only vs full_system | A (19.30/40.90) | A (11.78/32.37) | A (10.27/31.17) | A (14.21/35.47) | 4/4 models: A wins — **universal** |
| state_path vs full_system | A (40.63/40.90) | A (31.11/32.37) | A (31.05/31.17) | A (33.43/35.47) | 4/4 models: A wins — **universal** |

## mean_cost_usd (lower better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.00/0.01) | A (0.01/0.03) | A (0.01/0.02) | = (0.00/0.00) | 3/3 models: A wins |
| full_system vs no_rag | B (0.00/0.00) | B (0.01/0.01) | B (0.01/0.00) | = (0.00/0.00) | 0/3 models: A wins |
| vanilla_vector vs no_rag | B (0.01/0.00) | B (0.03/0.01) | B (0.02/0.00) | = (0.00/0.00) | 0/3 models: A wins |
| graph_only vs vanilla_vector | A (0.00/0.01) | A (0.01/0.03) | A (0.00/0.02) | = (0.00/0.00) | 3/3 models: A wins |
| graph_only vs full_system | A (0.00/0.00) | A (0.01/0.01) | A (0.00/0.01) | = (0.00/0.00) | 3/3 models: A wins |
| state_path vs full_system | A (0.00/0.00) | A (0.01/0.01) | A (0.00/0.01) | = (0.00/0.00) | 3/3 models: A wins |

## Note on goal_completion_rate interpretation

unified3 refined the 3d_visualization step_3 capture to a goal-reached state (all three orthogonal slices displayed) and the new attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). All three scenarios therefore contribute to goal_completion. Effective n per (model, backend) = 3 scenarios × 5 replicates = 15 observations. **Cross-tag comparison with unified2 goal_completion is prohibited** — the scoring target changed (see methodology_audit_trail.md § scenario refinement #1).

