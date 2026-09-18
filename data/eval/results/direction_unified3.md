# Direction consistency — v2 unified matrix

For each metric and each candidate pair (A vs B), we count how many of the 4 models have A winning over B in the metric's correct direction. **4/4 = universal**, **3/4 = majority**, **2/4 = mixed**, **≤1/4 = A loses**.

Statistical unit = replicate. Each cell in the underlying table is a per-model mean over 5 replicates; the winner per model is decided by comparing those means (no per-model significance requirement — that's the point of direction consistency at small n).


## step_accuracy (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.74/0.68) | A (0.84/0.83) | A (0.64/0.61) | A (0.61/0.42) | 4/4 models: A wins — **universal** |
| full_system vs no_rag | A (0.74/0.56) | B (0.84/0.86) | A (0.64/0.57) | A (0.61/0.43) | 3/4 models: A wins — majority |
| vanilla_vector vs no_rag | A (0.68/0.56) | B (0.83/0.86) | A (0.61/0.57) | B (0.42/0.43) | 2/4 models: A wins — mixed |
| graph_only vs vanilla_vector | B (0.63/0.68) | B (0.80/0.83) | A (0.66/0.61) | A (0.47/0.42) | 2/4 models: A wins — mixed |
| graph_only vs full_system | B (0.63/0.74) | B (0.80/0.84) | A (0.66/0.64) | B (0.47/0.61) | 1/4 models: A wins — A loses |
| state_path vs full_system | B (0.73/0.74) | B (0.83/0.84) | A (0.77/0.64) | A (0.62/0.61) | 2/4 models: A wins — mixed |

## faithfulness (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.98/0.95) | A (0.75/0.70) | A (0.68/0.60) | B (0.39/0.45) | 3/4 models: A wins — majority |
| full_system vs no_rag | B (0.98/1.00) | A (0.75/0.74) | A (0.68/0.67) | B (0.39/0.57) | 2/4 models: A wins — mixed |
| vanilla_vector vs no_rag | B (0.95/1.00) | B (0.70/0.74) | B (0.60/0.67) | B (0.45/0.57) | 0/4 models: A wins — A loses |
| graph_only vs vanilla_vector | A (0.97/0.95) | A (0.79/0.70) | A (0.64/0.60) | B (0.40/0.45) | 3/4 models: A wins — majority |
| graph_only vs full_system | B (0.97/0.98) | A (0.79/0.75) | B (0.64/0.68) | A (0.40/0.39) | 2/4 models: A wins — mixed |
| state_path vs full_system | B (0.97/0.98) | B (0.74/0.75) | A (0.83/0.68) | A (0.40/0.39) | 2/4 models: A wins — mixed |

## hallucination_rate (lower better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.02/0.05) | A (0.25/0.30) | A (0.33/0.40) | B (0.61/0.55) | 3/4 models: A wins — majority |
| full_system vs no_rag | B (0.02/0.00) | A (0.25/0.26) | A (0.33/0.33) | B (0.61/0.43) | 2/4 models: A wins — mixed |
| vanilla_vector vs no_rag | B (0.05/0.00) | B (0.30/0.26) | B (0.40/0.33) | B (0.55/0.43) | 0/4 models: A wins — A loses |
| graph_only vs vanilla_vector | A (0.03/0.05) | A (0.21/0.30) | A (0.36/0.40) | B (0.60/0.55) | 3/4 models: A wins — majority |
| graph_only vs full_system | B (0.03/0.02) | A (0.21/0.25) | B (0.36/0.33) | A (0.60/0.61) | 2/4 models: A wins — mixed |
| state_path vs full_system | B (0.03/0.02) | B (0.26/0.25) | A (0.17/0.33) | A (0.60/0.61) | 2/4 models: A wins — mixed |

## goal_completion_rate (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | = (0.80/0.80) | B (0.93/1.00) | B (0.73/0.80) | = (0.20/0.20) | 0/2 models: A wins |
| full_system vs no_rag | = (0.80/0.80) | B (0.93/1.00) | A (0.73/0.67) | B (0.20/0.47) | 1/3 models: A wins |
| vanilla_vector vs no_rag | = (0.80/0.80) | = (1.00/1.00) | A (0.80/0.67) | B (0.20/0.47) | 1/2 models: A wins |
| graph_only vs vanilla_vector | = (0.80/0.80) | B (0.93/1.00) | A (0.87/0.80) | A (0.40/0.20) | 2/3 models: A wins |
| graph_only vs full_system | = (0.80/0.80) | = (0.93/0.93) | A (0.87/0.73) | A (0.40/0.20) | 2/2 models: A wins |
| state_path vs full_system | B (0.73/0.80) | = (0.93/0.93) | B (0.67/0.73) | A (0.33/0.20) | 1/3 models: A wins |

## mean_latency_sec (lower better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | B (37.42/11.57) | B (28.58/4.26) | B (26.68/5.11) | B (32.57/9.65) | 0/4 models: A wins — A loses |
| full_system vs no_rag | B (37.42/8.86) | B (28.58/3.10) | B (26.68/2.06) | B (32.57/6.73) | 0/4 models: A wins — A loses |
| vanilla_vector vs no_rag | B (11.57/8.86) | B (4.26/3.10) | B (5.11/2.06) | B (9.65/6.73) | 0/4 models: A wins — A loses |
| graph_only vs vanilla_vector | B (18.92/11.57) | B (11.29/4.26) | B (9.77/5.11) | B (14.91/9.65) | 0/4 models: A wins — A loses |
| graph_only vs full_system | A (18.92/37.42) | A (11.29/28.58) | A (9.77/26.68) | A (14.91/32.57) | 4/4 models: A wins — **universal** |
| state_path vs full_system | A (36.60/37.42) | A (27.51/28.58) | A (26.32/26.68) | A (32.37/32.57) | 4/4 models: A wins — **universal** |

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

