# Direction consistency — v2 unified matrix

For each metric and each candidate pair (A vs B), we count how many of the 4 models have A winning over B in the metric's correct direction. **4/4 = universal**, **3/4 = majority**, **2/4 = mixed**, **≤1/4 = A loses**.

Statistical unit = replicate. Each cell in the underlying table is a per-model mean over 5 replicates; the winner per model is decided by comparing those means (no per-model significance requirement — that's the point of direction consistency at small n).


## step_accuracy (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | = (1.00/1.00) | A (0.89/0.88) | B (0.84/0.91) | 1/2 models: A wins |
| full_system vs no_rag | = (1.00/1.00) | B (0.89/1.00) | B (0.84/0.99) | 0/2 models: A wins |
| vanilla_vector vs no_rag | = (1.00/1.00) | B (0.88/1.00) | B (0.91/0.99) | 0/2 models: A wins |
| graph_only vs vanilla_vector | = (1.00/1.00) | A (0.89/0.88) | A (0.96/0.91) | 2/2 models: A wins |
| graph_only vs full_system | = (1.00/1.00) | = (0.89/0.89) | A (0.96/0.84) | 1/1 models: A wins |
| state_path vs full_system | B (0.97/1.00) | A (0.96/0.89) | A (1.00/0.84) | 2/3 models: A wins — mixed |

## faithfulness (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.88/0.84) | B (0.65/0.72) | = (0.88/0.88) | 1/2 models: A wins |
| full_system vs no_rag | = (0.88/0.88) | = (0.65/0.65) | = (0.88/0.88) | 0/0 models: A wins |
| vanilla_vector vs no_rag | B (0.84/0.88) | A (0.72/0.65) | = (0.88/0.88) | 1/2 models: A wins |
| graph_only vs vanilla_vector | A (0.88/0.84) | A (0.88/0.72) | = (0.88/0.88) | 2/2 models: A wins |
| graph_only vs full_system | = (0.88/0.88) | A (0.88/0.65) | = (0.88/0.88) | 1/1 models: A wins |
| state_path vs full_system | = (0.88/0.88) | A (0.88/0.65) | = (0.88/0.88) | 1/1 models: A wins |

## hallucination_rate (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.12/0.16) | B (0.35/0.28) | = (0.12/0.12) | 1/2 models: A wins |
| full_system vs no_rag | = (0.12/0.12) | = (0.35/0.35) | = (0.12/0.12) | 0/0 models: A wins |
| vanilla_vector vs no_rag | B (0.16/0.12) | A (0.28/0.35) | = (0.12/0.12) | 1/2 models: A wins |
| graph_only vs vanilla_vector | A (0.12/0.16) | A (0.12/0.28) | = (0.12/0.12) | 2/2 models: A wins |
| graph_only vs full_system | = (0.12/0.12) | A (0.12/0.35) | = (0.12/0.12) | 1/1 models: A wins |
| state_path vs full_system | = (0.12/0.12) | A (0.12/0.35) | = (0.12/0.12) | 1/1 models: A wins |

## goal_completion_rate (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | = (1.00/1.00) | = (1.00/1.00) | = (1.00/1.00) | 0/0 models: A wins |
| full_system vs no_rag | = (1.00/1.00) | = (1.00/1.00) | = (1.00/1.00) | 0/0 models: A wins |
| vanilla_vector vs no_rag | = (1.00/1.00) | = (1.00/1.00) | = (1.00/1.00) | 0/0 models: A wins |
| graph_only vs vanilla_vector | = (1.00/1.00) | = (1.00/1.00) | B (0.90/1.00) | 0/1 models: A wins |
| graph_only vs full_system | = (1.00/1.00) | = (1.00/1.00) | B (0.90/1.00) | 0/1 models: A wins |
| state_path vs full_system | = (1.00/1.00) | = (1.00/1.00) | = (1.00/1.00) | 0/0 models: A wins |

## mean_latency_sec (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | B (33.06/10.16) | B (26.38/4.16) | B (25.46/3.14) | 0/3 models: A wins — A loses |
| full_system vs no_rag | B (33.06/8.65) | B (26.38/2.86) | B (25.46/1.88) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (10.16/8.65) | B (4.16/2.86) | B (3.14/1.88) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | B (32.63/10.16) | B (26.44/4.16) | B (25.44/3.14) | 0/3 models: A wins — A loses |
| graph_only vs full_system | A (32.63/33.06) | B (26.44/26.38) | A (25.44/25.46) | 2/3 models: A wins — mixed |
| state_path vs full_system | A (32.10/33.06) | A (25.11/26.38) | A (24.56/25.46) | 3/3 models: A wins — **universal** |

## mean_cost_usd (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.01/0.01) | A (0.01/0.02) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| full_system vs no_rag | B (0.01/0.01) | B (0.01/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (0.01/0.01) | B (0.02/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | A (0.01/0.01) | A (0.01/0.02) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| graph_only vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| state_path vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |

## mean_cost_total_usd (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | B (0.01/0.01) | A (0.01/0.02) | A (0.01/0.01) | 2/3 models: A wins — mixed |
| full_system vs no_rag | B (0.01/0.01) | B (0.01/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (0.01/0.01) | B (0.02/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | A (0.01/0.01) | A (0.01/0.02) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| graph_only vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| state_path vs full_system | A (0.01/0.01) | A (0.01/0.01) | A (0.01/0.01) | 3/3 models: A wins — **universal** |

## Note on goal_completion_rate interpretation

unified3 refined the 3d_visualization step_3 capture to a goal-reached state (all three orthogonal slices displayed) and the new attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). All three scenarios therefore contribute to goal_completion. Effective n per (model, backend) = 3 scenarios × 5 replicates = 15 observations. **Cross-tag comparison with unified2 goal_completion is prohibited** — the scoring target changed (see methodology_audit_trail.md § scenario refinement #1).

