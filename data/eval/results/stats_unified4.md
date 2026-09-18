
# Pipeline health — routing confidence + fallback rate

Fallback activates when rerank confidence < 0.7. Zero on backends that don't call the router (no_rag, vanilla_vector, graph_only, vision_only if it doesn't hit the reranker).

| model | backend | mean_route_conf | fallback_rate (of routed steps) |
|---|---|---|---|
| gemini | no_rag | — | 0% |
| gemini | vanilla_vector | — | 0% |
| gemini | graph_only | — | 0% |
| gemini | vision_only | — | 0% |
| gemini | full_system | 0.72 | 18% |
| gemini | state_path | — | 0% |
| claude | no_rag | — | 0% |
| claude | vanilla_vector | — | 0% |
| claude | graph_only | — | 0% |
| claude | vision_only | — | 0% |
| claude | full_system | 0.74 | 19% |
| claude | state_path | — | 0% |
| gpt | no_rag | — | 0% |
| gpt | vanilla_vector | — | 0% |
| gpt | graph_only | — | 0% |
| gpt | vision_only | — | 0% |
| gpt | full_system | 0.70 | 20% |
| gpt | state_path | — | 0% |
| qwen | no_rag | — | 0% |
| qwen | vanilla_vector | — | 0% |
| qwen | graph_only | — | 0% |
| qwen | vision_only | — | 0% |
| qwen | full_system | 0.68 | 20% |
| qwen | state_path | — | 0% |
# Pairwise backend tests — Unified matrix (n=5 per side)

Welch's unequal-variance t + 10,000-resample permutation p.


## step_accuracy (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.667 | 0.750 | -0.083 | -0.88 | 6.8 | 0.411 | 0.431 | vanilla_vector |
| gemini | no_rag vs full_system | 0.667 | 0.725 | -0.058 | -0.64 | 6.1 | 0.545 | 0.561 | full_system |
| gemini | vanilla_vector vs full_system | 0.750 | 0.725 | +0.025 | 0.38 | 7.8 | 0.718 | 0.808 | vanilla_vector |
| claude | no_rag vs vanilla_vector | 0.850 | 0.842 | +0.008 | 0.63 | 7.7 | 0.546 | 1.000 | no_rag |
| claude | no_rag vs full_system | 0.850 | 0.850 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 0.842 | 0.850 | -0.008 | -0.63 | 7.7 | 0.546 | 1.000 | full_system |
| gpt | no_rag vs vanilla_vector | 0.508 | 0.600 | -0.092 | -1.45 | 5.9 | 0.201 | 0.240 | vanilla_vector |
| gpt | no_rag vs full_system | 0.508 | 0.692 | -0.183 | -3.11 | 4.7 | 0.039 | 0.032 | full_system ✓ |
| gpt | vanilla_vector vs full_system | 0.600 | 0.692 | -0.092 | -2.79 | 6.5 | 0.034 | 0.034 | full_system ✓ |
| qwen | no_rag vs vanilla_vector | 0.492 | 0.550 | -0.058 | -1.24 | 7.8 | 0.253 | 0.349 | vanilla_vector |
| qwen | no_rag vs full_system | 0.492 | 0.567 | -0.075 | -1.38 | 7.9 | 0.207 | 0.265 | full_system |
| qwen | vanilla_vector vs full_system | 0.550 | 0.567 | -0.017 | -0.33 | 7.4 | 0.753 | 0.864 | full_system |

## hallucination_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.008 | 0.075 | -0.067 | -3.02 | 5.3 | 0.035 | 0.048 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.008 | 0.075 | -0.067 | -1.94 | 4.5 | 0.124 | 0.172 | no_rag |
| gemini | vanilla_vector vs full_system | 0.075 | 0.075 | +0.000 | 0.00 | 6.6 | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 0.250 | 0.242 | +0.008 | 0.30 | 7.1 | 0.772 | 1.000 | vanilla_vector |
| claude | no_rag vs full_system | 0.250 | 0.225 | +0.025 | 0.88 | 7.3 | 0.405 | 0.567 | full_system |
| claude | vanilla_vector vs full_system | 0.242 | 0.225 | +0.017 | 0.73 | 8.0 | 0.487 | 0.681 | full_system |
| gpt | no_rag vs vanilla_vector | 0.308 | 0.367 | -0.058 | -0.60 | 6.8 | 0.567 | 0.592 | no_rag |
| gpt | no_rag vs full_system | 0.308 | 0.308 | -0.000 | -0.00 | 5.1 | 1.000 | 0.938 | no_rag |
| gpt | vanilla_vector vs full_system | 0.367 | 0.308 | +0.058 | 0.97 | 6.6 | 0.369 | 0.437 | full_system |
| qwen | no_rag vs vanilla_vector | 0.400 | 0.617 | -0.217 | -2.74 | 8.0 | 0.029 | 0.040 | no_rag ✓ |
| qwen | no_rag vs full_system | 0.400 | 0.500 | -0.100 | -1.50 | 7.4 | 0.177 | 0.208 | no_rag |
| qwen | vanilla_vector vs full_system | 0.617 | 0.500 | +0.117 | 1.66 | 7.1 | 0.143 | 0.171 | full_system |

## loop_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.000 | 0.017 | -0.017 | -1.63 | 4.0 | 0.185 | 0.436 | no_rag |
| gemini | no_rag vs full_system | 0.000 | 0.008 | -0.008 | -1.00 | 4.0 | 0.377 | 1.000 | no_rag |
| gemini | vanilla_vector vs full_system | 0.017 | 0.008 | +0.008 | 0.63 | 7.7 | 0.546 | 1.000 | full_system |
| claude | no_rag vs vanilla_vector | 0.025 | 0.008 | +0.017 | 1.26 | 7.7 | 0.244 | 0.520 | vanilla_vector |
| claude | no_rag vs full_system | 0.025 | 0.025 | +0.000 | 0.00 | 6.6 | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 0.008 | 0.025 | -0.017 | -0.89 | 5.9 | 0.407 | 0.717 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.017 | -0.017 | -1.00 | 4.0 | 0.377 | 1.000 | no_rag |
| gpt | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | vanilla_vector vs full_system | 0.017 | 0.000 | +0.017 | 1.00 | 4.0 | 0.377 | 1.000 | full_system |
| qwen | no_rag vs vanilla_vector | 0.217 | 0.150 | +0.067 | 1.53 | 7.8 | 0.168 | 0.188 | vanilla_vector |
| qwen | no_rag vs full_system | 0.217 | 0.067 | +0.150 | 2.94 | 7.8 | 0.022 | 0.039 | full_system ✓ |
| qwen | vanilla_vector vs full_system | 0.150 | 0.067 | +0.083 | 1.74 | 7.3 | 0.126 | 0.167 | full_system |

## goal_completion_rate (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.800 | 0.933 | -0.133 | -1.26 | 7.7 | 0.244 | 0.529 | vanilla_vector |
| gemini | no_rag vs full_system | 0.800 | 0.800 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.933 | 0.800 | +0.133 | 1.26 | 7.7 | 0.244 | 0.517 | vanilla_vector |
| claude | no_rag vs vanilla_vector | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs vanilla_vector | 0.733 | 0.733 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 0.733 | 0.933 | -0.200 | -2.12 | 8.0 | 0.069 | 0.207 | full_system |
| gpt | vanilla_vector vs full_system | 0.733 | 0.933 | -0.200 | -2.12 | 8.0 | 0.069 | 0.210 | full_system |
| qwen | no_rag vs vanilla_vector | 0.533 | 0.400 | +0.133 | 1.26 | 7.7 | 0.244 | 0.523 | no_rag |
| qwen | no_rag vs full_system | 0.533 | 0.400 | +0.133 | 0.89 | 6.9 | 0.402 | 0.685 | no_rag |
| qwen | vanilla_vector vs full_system | 0.400 | 0.400 | +0.000 | 0.00 | 6.1 | 1.000 | 1.000 | tie |

## mean_latency_sec (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 10.629 | 10.310 | +0.319 | 0.46 | 7.1 | 0.660 | 0.756 | vanilla_vector |
| gemini | no_rag vs full_system | 10.629 | 40.904 | -30.274 | -36.82 | 8.0 | 0.000 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 10.310 | 40.904 | -30.594 | -43.04 | 7.0 | 0.000 | 0.009 | vanilla_vector ✓ |
| claude | no_rag vs vanilla_vector | 3.015 | 3.859 | -0.844 | -3.85 | 8.0 | 0.007 | 0.009 | no_rag ✓ |
| claude | no_rag vs full_system | 3.015 | 32.373 | -29.359 | -34.98 | 4.3 | 0.006 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 3.859 | 32.373 | -28.514 | -33.93 | 4.3 | 0.006 | 0.009 | vanilla_vector ✓ |
| gpt | no_rag vs vanilla_vector | 2.015 | 5.069 | -3.054 | -20.23 | 4.8 | 0.004 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 2.015 | 31.169 | -29.154 | -27.42 | 4.0 | 0.008 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 5.069 | 31.169 | -26.101 | -24.35 | 4.1 | 0.007 | 0.009 | vanilla_vector ✓ |
| qwen | no_rag vs vanilla_vector | 5.869 | 9.692 | -3.823 | -9.65 | 7.2 | 0.001 | 0.009 | no_rag ✓ |
| qwen | no_rag vs full_system | 5.869 | 35.467 | -29.597 | -49.62 | 6.8 | 0.000 | 0.009 | no_rag ✓ |
| qwen | vanilla_vector vs full_system | 9.692 | 35.467 | -25.775 | -46.68 | 5.6 | 0.001 | 0.009 | vanilla_vector ✓ |

## mean_cost_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.001 | 0.009 | -0.009 | -1617.57 | 7.0 | 0.000 | 0.009 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.001 | 0.002 | -0.001 | -65.97 | 4.2 | 0.007 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.009 | 0.002 | +0.007 | 336.51 | 4.4 | 0.005 | 0.009 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.006 | 0.027 | -0.021 | -941.06 | 5.2 | 0.002 | 0.009 | no_rag ✓ |
| claude | no_rag vs full_system | 0.006 | 0.011 | -0.004 | -63.06 | 4.8 | 0.003 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.027 | 0.011 | +0.017 | 262.82 | 4.1 | 0.007 | 0.009 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.004 | 0.018 | -0.014 | -870.62 | 7.9 | 0.000 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.004 | 0.006 | -0.003 | -56.13 | 4.6 | 0.004 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.018 | 0.006 | +0.012 | 264.29 | 4.5 | 0.005 | 0.009 | full_system ✓ |
| qwen | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |

# GEMINI — hybrid (full_system) vs vanilla_vector focus

Does Gemini show a significant full_system > vanilla_vector trend that other models don't?

| metric | Gemini full_system | Gemini vanilla | Δ | perm p | direction |
|---|---|---|---|---|---|
| step_accuracy | 0.725 | 0.750 | -0.025 | 0.810 | vanilla ↑ (hybrid hurts) |
| hallucination_rate | 0.075 | 0.075 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| loop_rate | 0.008 | 0.017 | -0.008 | 1.000 | full_system ↑ (helps) |
| goal_completion_rate | 0.800 | 0.933 | -0.133 | 0.529 | vanilla ↑ (hybrid hurts) |
| mean_latency_sec | 40.904 | 10.310 | +30.594 | 0.009 ✓ sig | vanilla ↑ (hybrid hurts) |
| mean_cost_usd | 0.002 | 0.009 | -0.007 | 0.009 ✓ sig | full_system ↑ (helps) |

## Same pair, other models — is Gemini's pattern unique?

| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |
|---|---|---|---|---|---|---|
| step_accuracy | gemini | 0.725 | 0.750 | -0.025 | 0.810 | no |
| step_accuracy | claude | 0.850 | 0.842 | +0.008 | 1.000 | yes |
| step_accuracy | gpt | 0.692 | 0.600 | +0.092 | 0.034 ✓ | yes |
| step_accuracy | qwen | 0.567 | 0.550 | +0.017 | 0.865 | yes |
| hallucination_rate | gemini | 0.075 | 0.075 | +0.000 | 1.000 | no |
| hallucination_rate | claude | 0.225 | 0.242 | -0.017 | 0.691 | yes |
| hallucination_rate | gpt | 0.308 | 0.367 | -0.058 | 0.442 | yes |
| hallucination_rate | qwen | 0.500 | 0.617 | -0.117 | 0.166 | yes |
| loop_rate | gemini | 0.008 | 0.017 | -0.008 | 1.000 | yes |
| loop_rate | claude | 0.025 | 0.008 | +0.017 | 0.718 | no |
| loop_rate | gpt | 0.000 | 0.017 | -0.017 | 1.000 | yes |
| loop_rate | qwen | 0.067 | 0.150 | -0.083 | 0.161 | yes |
| goal_completion_rate | gemini | 0.800 | 0.933 | -0.133 | 0.529 | no |
| goal_completion_rate | claude | 1.000 | 1.000 | +0.000 | 1.000 | no |
| goal_completion_rate | gpt | 0.933 | 0.733 | +0.200 | 0.204 | yes |
| goal_completion_rate | qwen | 0.400 | 0.400 | +0.000 | 1.000 | no |
| mean_latency_sec | gemini | 40.904 | 10.310 | +30.594 | 0.009 ✓ | no |
| mean_latency_sec | claude | 32.373 | 3.859 | +28.514 | 0.009 ✓ | no |
| mean_latency_sec | gpt | 31.169 | 5.069 | +26.101 | 0.009 ✓ | no |
| mean_latency_sec | qwen | 35.467 | 9.692 | +25.775 | 0.009 ✓ | no |
| mean_cost_usd | gemini | 0.002 | 0.009 | -0.007 | 0.009 ✓ | yes |
| mean_cost_usd | claude | 0.011 | 0.027 | -0.017 | 0.009 ✓ | yes |
| mean_cost_usd | gpt | 0.006 | 0.018 | -0.012 | 0.009 ✓ | yes |
| mean_cost_usd | qwen | 0.000 | 0.000 | +0.000 | 1.000 | no |
