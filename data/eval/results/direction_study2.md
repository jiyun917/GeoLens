# Direction consistency — v2 unified matrix

For each metric and each candidate pair (A vs B), we count how many of the 4 models have A winning over B in the metric's correct direction. **4/4 = universal**, **3/4 = majority**, **2/4 = mixed**, **≤1/4 = A loses**.

Statistical unit = replicate. Each cell in the underlying table is a per-model mean over 5 replicates; the winner per model is decided by comparing those means (no per-model significance requirement — that's the point of direction consistency at small n).


## step_accuracy (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.91/0.77) | B (0.72/0.81) | A (0.88/0.60) | 2/3 models: A wins — mixed |
| full_system vs no_rag | A (0.91/0.51) | A (0.72/0.37) | A (0.88/0.27) | 3/3 models: A wins — **universal** |
| vanilla_vector vs no_rag | A (0.77/0.51) | A (0.81/0.37) | A (0.60/0.27) | 3/3 models: A wins — **universal** |
| graph_only vs vanilla_vector | — | — | — | 0/0 models: A wins |
| graph_only vs full_system | — | — | — | 0/0 models: A wins |
| state_path vs full_system | — | — | — | 0/0 models: A wins |

## faithfulness (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | B (0.91/0.93) | A (0.98/0.86) | B (0.86/0.97) | 1/3 models: A wins — mixed |
| full_system vs no_rag | A (0.91/0.90) | A (0.98/0.87) | B (0.86/0.99) | 2/3 models: A wins — mixed |
| vanilla_vector vs no_rag | A (0.93/0.90) | B (0.86/0.87) | B (0.97/0.99) | 1/3 models: A wins — mixed |
| graph_only vs vanilla_vector | — | — | — | 0/0 models: A wins |
| graph_only vs full_system | — | — | — | 0/0 models: A wins |
| state_path vs full_system | — | — | — | 0/0 models: A wins |

## hallucination_rate (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | B (0.09/0.07) | A (0.02/0.14) | B (0.14/0.03) | 1/3 models: A wins — mixed |
| full_system vs no_rag | A (0.09/0.10) | A (0.02/0.13) | B (0.14/0.01) | 2/3 models: A wins — mixed |
| vanilla_vector vs no_rag | A (0.07/0.10) | B (0.14/0.13) | B (0.03/0.01) | 1/3 models: A wins — mixed |
| graph_only vs vanilla_vector | — | — | — | 0/0 models: A wins |
| graph_only vs full_system | — | — | — | 0/0 models: A wins |
| state_path vs full_system | — | — | — | 0/0 models: A wins |

## goal_completion_rate (higher better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.40/0.20) | A (0.30/0.00) | B (0.00/0.50) | 2/3 models: A wins — mixed |
| full_system vs no_rag | A (0.40/0.35) | A (0.30/0.00) | B (0.00/0.30) | 2/3 models: A wins — mixed |
| vanilla_vector vs no_rag | B (0.20/0.35) | = (0.00/0.00) | A (0.50/0.30) | 1/2 models: A wins |
| graph_only vs vanilla_vector | — | — | — | 0/0 models: A wins |
| graph_only vs full_system | — | — | — | 0/0 models: A wins |
| state_path vs full_system | — | — | — | 0/0 models: A wins |

## mean_latency_sec (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | B (25.74/11.71) | B (15.02/4.22) | B (15.69/2.32) | 0/3 models: A wins — A loses |
| full_system vs no_rag | B (25.74/10.97) | B (15.02/3.45) | B (15.69/1.87) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (11.71/10.97) | B (4.22/3.45) | B (2.32/1.87) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | — | — | — | 0/0 models: A wins |
| graph_only vs full_system | — | — | — | 0/0 models: A wins |
| state_path vs full_system | — | — | — | 0/0 models: A wins |

## mean_cost_usd (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | A (0.01/0.01) | A (0.01/0.02) | A (0.01/0.01) | 3/3 models: A wins — **universal** |
| full_system vs no_rag | B (0.01/0.01) | B (0.01/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (0.01/0.01) | B (0.02/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | — | — | — | 0/0 models: A wins |
| graph_only vs full_system | — | — | — | 0/0 models: A wins |
| state_path vs full_system | — | — | — | 0/0 models: A wins |

## mean_cost_total_usd (lower better)

| pair | gemini | claude | gpt | direction consistency |
|---|---|---|---|---|
| full_system vs vanilla_vector | B (0.01/0.01) | A (0.01/0.02) | A (0.01/0.01) | 2/3 models: A wins — mixed |
| full_system vs no_rag | B (0.01/0.01) | B (0.01/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| vanilla_vector vs no_rag | B (0.01/0.01) | B (0.02/0.01) | B (0.01/0.00) | 0/3 models: A wins — A loses |
| graph_only vs vanilla_vector | — | — | — | 0/0 models: A wins |
| graph_only vs full_system | — | — | — | 0/0 models: A wins |
| state_path vs full_system | — | — | — | 0/0 models: A wins |

## Note on goal_completion_rate interpretation

unified3 refined the 3d_visualization step_3 capture to a goal-reached state (all three orthogonal slices displayed) and the new attribute_computation step_7 also captures the goal state (Energy layer displayed on In-line > 250). All three scenarios therefore contribute to goal_completion. Effective n per (model, backend) = 3 scenarios × 5 replicates = 15 observations. **Cross-tag comparison with unified2 goal_completion is prohibited** — the scoring target changed (see methodology_audit_trail.md § scenario refinement #1).

