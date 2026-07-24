# Direction consistency — v2 unified matrix

For each metric and each candidate pair (A vs B), we count how many of the 4 models have A winning over B in the metric's correct direction. **4/4 = universal**, **3/4 = majority**, **2/4 = mixed**, **≤1/4 = A loses**.

Statistical unit = replicate. Each cell in the underlying table is a per-model mean over 5 replicates; the winner per model is decided by comparing those means (no per-model significance requirement — that's the point of direction consistency at small n).


## step_accuracy (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | = (0.60/0.60) | A (0.78/0.72) | A (0.70/0.38) | A (0.50/0.35) | 3/3 models: A wins |
| full_system vs no_rag | A (0.60/0.55) | A (0.78/0.72) | A (0.70/0.42) | B (0.50/0.57) | 3/4 models: A wins — majority |
| vanilla_vector vs no_rag | A (0.60/0.55) | = (0.72/0.72) | B (0.38/0.42) | B (0.35/0.57) | 1/3 models: A wins |
| graph_only vs vanilla_vector | B (0.53/0.60) | A (0.78/0.72) | A (0.78/0.38) | A (0.53/0.35) | 3/4 models: A wins — majority |
| graph_only vs full_system | B (0.53/0.60) | = (0.78/0.78) | A (0.78/0.70) | A (0.53/0.50) | 2/3 models: A wins |
| state_path vs full_system | B (0.55/0.60) | A (0.85/0.78) | B (0.57/0.70) | = (0.50/0.50) | 1/3 models: A wins |

## faithfulness (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.95/0.90) | A (0.85/0.75) | B (0.45/0.53) | A (0.53/0.28) | 3/4 models: A wins — majority |
| full_system vs no_rag | A (0.95/0.93) | A (0.85/0.75) | B (0.45/0.60) | A (0.53/0.38) | 3/4 models: A wins — majority |
| vanilla_vector vs no_rag | B (0.90/0.93) | = (0.75/0.75) | B (0.53/0.60) | B (0.28/0.38) | 0/3 models: A wins |
| graph_only vs vanilla_vector | A (0.97/0.90) | A (0.80/0.75) | A (0.72/0.53) | A (0.30/0.28) | 4/4 models: A wins — **universal** |
| graph_only vs full_system | A (0.97/0.95) | B (0.80/0.85) | A (0.72/0.45) | B (0.30/0.53) | 2/4 models: A wins — mixed |
| state_path vs full_system | B (0.93/0.95) | A (0.90/0.85) | A (0.50/0.45) | B (0.40/0.53) | 2/4 models: A wins — mixed |

## hallucination_rate (lower better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.05/0.10) | A (0.15/0.25) | B (0.55/0.47) | A (0.47/0.72) | 3/4 models: A wins — majority |
| full_system vs no_rag | A (0.05/0.07) | A (0.15/0.25) | B (0.55/0.40) | A (0.47/0.62) | 3/4 models: A wins — majority |
| vanilla_vector vs no_rag | B (0.10/0.07) | = (0.25/0.25) | B (0.47/0.40) | B (0.72/0.62) | 0/3 models: A wins |
| graph_only vs vanilla_vector | A (0.03/0.10) | A (0.20/0.25) | A (0.28/0.47) | A (0.70/0.72) | 4/4 models: A wins — **universal** |
| graph_only vs full_system | A (0.03/0.05) | B (0.20/0.15) | A (0.28/0.55) | B (0.70/0.47) | 2/4 models: A wins — mixed |
| state_path vs full_system | B (0.07/0.05) | A (0.10/0.15) | A (0.50/0.55) | B (0.60/0.47) | 2/4 models: A wins — mixed |

## goal_completion_rate (higher better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | B (0.30/0.50) | = (0.50/0.50) | A (0.30/0.20) | = (0.10/0.10) | 1/2 models: A wins |
| full_system vs no_rag | B (0.30/0.50) | = (0.50/0.50) | A (0.30/0.00) | B (0.10/0.30) | 1/3 models: A wins |
| vanilla_vector vs no_rag | = (0.50/0.50) | = (0.50/0.50) | A (0.20/0.00) | B (0.10/0.30) | 1/2 models: A wins |
| graph_only vs vanilla_vector | = (0.50/0.50) | = (0.50/0.50) | A (0.50/0.20) | A (0.20/0.10) | 2/2 models: A wins |
| graph_only vs full_system | A (0.50/0.30) | = (0.50/0.50) | A (0.50/0.30) | A (0.20/0.10) | 3/3 models: A wins |
| state_path vs full_system | B (0.20/0.30) | B (0.30/0.50) | B (0.20/0.30) | = (0.10/0.10) | 0/3 models: A wins |

## mean_latency_sec (lower better)

| pair | gemini | claude | gpt | qwen | direction consistency |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | B (34.28/8.65) | B (27.46/3.99) | B (29.71/3.51) | A (30.91/42.17) | 1/4 models: A wins — A loses |
| full_system vs no_rag | B (34.28/7.07) | B (27.46/2.78) | B (29.71/2.29) | B (30.91/7.35) | 0/4 models: A wins — A loses |
| vanilla_vector vs no_rag | B (8.65/7.07) | B (3.99/2.78) | B (3.51/2.29) | B (42.17/7.35) | 0/4 models: A wins — A loses |
| graph_only vs vanilla_vector | B (14.83/8.65) | B (10.69/3.99) | B (9.84/3.51) | A (13.91/42.17) | 1/4 models: A wins — A loses |
| graph_only vs full_system | A (14.83/34.28) | A (10.69/27.46) | A (9.84/29.71) | A (13.91/30.91) | 4/4 models: A wins — **universal** |
| state_path vs full_system | A (30.36/34.28) | A (26.73/27.46) | A (28.40/29.71) | A (29.93/30.91) | 4/4 models: A wins — **universal** |

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

The 3d_visualization scenario captures the *penultimate* state (In-line + Cross-line displayed, Z-slice not yet added). Its final visual_state does NOT indicate goal-reached, so under the 3-gate check, no backend can achieve goal_completion for that scenario. Effectively goal_completion_rate is a **single-scenario measurement** on survey_setup only — n=5 per (model, backend) instead of n=10. This is a scenario capture limitation, not a metric flaw. Any goal_completion differences observed should be interpreted with this reduced power in mind.

