# Direction consistency — v2 unified matrix

For each metric and each candidate pair (A vs B), we count how many of the 4 models have A winning over B in the metric's correct direction. **4/4 = universal**, **3/4 = majority**, **2/4 = mixed**, **≤1/4 = A loses**.

Statistical unit = replicate. Each cell in the underlying table is a per-model mean over 5 replicates; the winner per model is decided by comparing those means (no per-model significance requirement — that's the point of direction consistency at small n).


## step_accuracy (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.91/0.82) | A (1.00/0.88) | A (0.80/0.77) | 3/3 models: A wins — **universal** |
| full_system vs no_rag | A (0.91/0.73) | A (1.00/0.88) | A (0.80/0.71) | 3/3 models: A wins — **universal** |
| vanilla_vector vs no_rag | A (0.82/0.73) | = (0.88/0.88) | A (0.77/0.71) | 2/2 models: A wins |
| graph_only vs vanilla_vector | B (0.79/0.82) | = (0.88/0.88) | A (0.85/0.77) | 1/2 models: A wins |
| graph_only vs full_system | B (0.79/0.91) | B (0.88/1.00) | A (0.85/0.80) | 1/3 models: A wins — mixed |
| state_path vs full_system | B (0.80/0.91) | B (0.85/1.00) | A (0.91/0.80) | 1/3 models: A wins — mixed |

## faithfulness (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.97/0.97) | = (0.96/0.96) | B (0.90/0.95) | 1/2 models: A wins |
| full_system vs no_rag | = (0.97/0.97) | A (0.96/0.95) | B (0.90/0.95) | 1/2 models: A wins |
| vanilla_vector vs no_rag | B (0.97/0.97) | A (0.96/0.95) | A (0.95/0.95) | 2/3 models: A wins — mixed |
| graph_only vs vanilla_vector | A (0.98/0.97) | = (0.96/0.96) | A (0.96/0.95) | 2/2 models: A wins |
| graph_only vs full_system | A (0.98/0.97) | = (0.96/0.96) | A (0.96/0.90) | 2/2 models: A wins |
| state_path vs full_system | B (0.97/0.97) | = (0.96/0.96) | A (0.94/0.90) | 1/2 models: A wins |

## hallucination_rate (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.03/0.03) | = (0.04/0.04) | B (0.10/0.05) | 1/2 models: A wins |
| full_system vs no_rag | = (0.03/0.03) | A (0.04/0.05) | B (0.10/0.05) | 1/2 models: A wins |
| vanilla_vector vs no_rag | B (0.03/0.03) | A (0.04/0.05) | A (0.05/0.05) | 2/3 models: A wins — mixed |
| graph_only vs vanilla_vector | A (0.02/0.03) | = (0.04/0.04) | A (0.04/0.05) | 2/2 models: A wins |
| graph_only vs full_system | A (0.02/0.03) | = (0.04/0.04) | A (0.04/0.10) | 2/2 models: A wins |
| state_path vs full_system | B (0.03/0.03) | = (0.04/0.04) | A (0.06/0.10) | 1/2 models: A wins |

## goal_completion_rate (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.87/0.73) | B (0.93/1.00) | B (0.40/0.67) | 1/3 models: A wins — mixed |
| full_system vs no_rag | A (0.87/0.70) | B (0.93/1.00) | B (0.40/0.67) | 1/3 models: A wins — mixed |
| vanilla_vector vs no_rag | A (0.73/0.70) | = (1.00/1.00) | = (0.67/0.67) | 1/1 models: A wins |
| graph_only vs vanilla_vector | A (0.83/0.73) | = (1.00/1.00) | A (0.97/0.67) | 2/2 models: A wins |
| graph_only vs full_system | B (0.83/0.87) | A (1.00/0.93) | A (0.97/0.40) | 2/3 models: A wins — mixed |
| state_path vs full_system | B (0.60/0.87) | B (0.80/0.93) | A (0.63/0.40) | 1/3 models: A wins — mixed |

## mean_latency_sec (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | B (21.16/11.37) | B (13.39/4.30) | B (11.37/2.87) | 0/3 models: A wins — A loses |
| full_system vs no_rag | B (21.16/9.17) | B (13.39/3.51) | B (11.37/1.71) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (11.37/9.17) | B (4.30/3.51) | B (2.87/1.71) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | B (19.07/11.37) | B (12.63/4.30) | B (9.96/2.87) | 0/3 models: A wins — A loses |
| graph_only vs full_system | A (19.07/21.16) | A (12.63/13.39) | A (9.96/11.37) | 3/3 models: A wins — **universal** |
| state_path vs full_system | A (20.42/21.16) | A (13.34/13.39) | A (10.84/11.37) | 3/3 models: A wins — **universal** |

## mean_cost_usd (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.01/0.01) | A (0.01/0.03) | A (0.01/0.02) | 3/3 models: A wins — **universal** |
| full_system vs no_rag | B (0.01/0.01) | B (0.01/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (0.01/0.01) | B (0.03/0.01) | B (0.02/0.00) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | A (0.01/0.01) | A (0.01/0.03) | A (0.01/0.02) | 3/3 models: A wins — **universal** |
| graph_only vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| state_path vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |

## mean_cost_total_usd (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.01/0.01) | A (0.01/0.03) | A (0.01/0.02) | 3/3 models: A wins — **universal** |
| full_system vs no_rag | B (0.01/0.01) | B (0.01/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (0.01/0.01) | B (0.03/0.01) | B (0.02/0.00) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | A (0.01/0.01) | A (0.01/0.03) | A (0.01/0.02) | 3/3 models: A wins — **universal** |
| graph_only vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| state_path vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |

## Note on goal_completion_rate interpretation

unified3 refined the 3d_visualization step_3 capture to a goal-reached state (all three orthogonal slices displayed) and the new attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). All three scenarios therefore contribute to goal_completion. Effective n per (model, backend) = 3 scenarios × 5 replicates = 15 observations. **Cross-tag comparison with unified2 goal_completion is prohibited** — the scoring target changed (see methodology_audit_trail.md § scenario refinement #1).

