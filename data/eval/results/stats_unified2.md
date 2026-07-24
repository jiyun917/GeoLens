
# Pipeline health — routing confidence + fallback rate

Fallback activates when rerank confidence < 0.7. Zero on backends that don't call the router (no_rag, vanilla_vector, graph_only, vision_only if it doesn't hit the reranker).

| model | backend | mean_route_conf | fallback_rate (of routed steps) |
|---|---|---|---|
| gemini | no_rag | — | 0% |
| gemini | vanilla_vector | — | 0% |
| gemini | graph_only | — | 0% |
| gemini | vision_only | — | 0% |
| gemini | full_system | 0.91 | 0% |
| gemini | state_path | — | 0% |
| claude | no_rag | — | 0% |
| claude | vanilla_vector | — | 0% |
| claude | graph_only | — | 0% |
| claude | vision_only | — | 0% |
| claude | full_system | 0.90 | 0% |
| claude | state_path | — | 0% |
| gpt | no_rag | — | 0% |
| gpt | vanilla_vector | — | 0% |
| gpt | graph_only | — | 0% |
| gpt | vision_only | — | 0% |
| gpt | full_system | 0.89 | 0% |
| gpt | state_path | — | 0% |
| qwen | no_rag | — | 0% |
| qwen | vanilla_vector | — | 0% |
| qwen | graph_only | — | 0% |
| qwen | vision_only | — | 0% |
| qwen | full_system | 0.90 | 0% |
| qwen | state_path | — | 0% |
# Pairwise backend tests — Unified matrix (n=5 per side)

Welch's unequal-variance t + 10,000-resample permutation p.


## step_accuracy (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.550 | 0.600 | -0.050 | -0.89 | 6.9 | 0.402 | 0.684 | vanilla_vector |
| gemini | no_rag vs full_system | 0.550 | 0.600 | -0.050 | -0.89 | 6.9 | 0.402 | 0.690 | full_system |
| gemini | vanilla_vector vs full_system | 0.600 | 0.600 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 0.725 | 0.725 | +0.000 | 0.00 | 6.1 | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 0.725 | 0.775 | -0.050 | -0.94 | 6.1 | 0.383 | 0.636 | full_system |
| claude | vanilla_vector vs full_system | 0.725 | 0.775 | -0.050 | -1.41 | 8.0 | 0.196 | 0.551 | full_system |
| gpt | no_rag vs vanilla_vector | 0.425 | 0.375 | +0.050 | 0.67 | 6.7 | 0.528 | 0.765 | no_rag |
| gpt | no_rag vs full_system | 0.425 | 0.700 | -0.275 | -3.89 | 5.8 | 0.014 | 0.025 | full_system ✓ |
| gpt | vanilla_vector vs full_system | 0.375 | 0.700 | -0.325 | -6.50 | 7.5 | 0.001 | 0.009 | full_system ✓ |
| qwen | no_rag vs vanilla_vector | 0.575 | 0.350 | +0.225 | 2.01 | 7.8 | 0.082 | 0.122 | no_rag |
| qwen | no_rag vs full_system | 0.575 | 0.500 | +0.075 | 0.74 | 6.9 | 0.485 | 0.636 | no_rag |
| qwen | vanilla_vector vs full_system | 0.350 | 0.500 | -0.150 | -1.63 | 7.5 | 0.146 | 0.228 | full_system |

## hallucination_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.075 | 0.100 | -0.025 | -0.37 | 8.0 | 0.725 | 1.000 | no_rag |
| gemini | no_rag vs full_system | 0.075 | 0.050 | +0.025 | 0.43 | 6.6 | 0.684 | 1.000 | full_system |
| gemini | vanilla_vector vs full_system | 0.100 | 0.050 | +0.050 | 0.89 | 6.9 | 0.402 | 0.680 | full_system |
| claude | no_rag vs vanilla_vector | 0.250 | 0.250 | +0.000 | 0.00 | 4.0 | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 0.250 | 0.150 | +0.100 | 4.00 | 4.0 | 0.030 | 0.048 | full_system ✓ |
| claude | vanilla_vector vs full_system | 0.250 | 0.150 | +0.100 | 2.14 | 6.8 | 0.075 | 0.167 | full_system |
| gpt | no_rag vs vanilla_vector | 0.400 | 0.475 | -0.075 | -0.97 | 4.9 | 0.377 | 0.723 | no_rag |
| gpt | no_rag vs full_system | 0.400 | 0.550 | -0.150 | -1.90 | 5.4 | 0.117 | 0.157 | no_rag |
| gpt | vanilla_vector vs full_system | 0.475 | 0.550 | -0.075 | -1.90 | 7.7 | 0.098 | 0.274 | vanilla_vector |
| qwen | no_rag vs vanilla_vector | 0.625 | 0.725 | -0.100 | -1.00 | 5.4 | 0.361 | 0.482 | no_rag |
| qwen | no_rag vs full_system | 0.625 | 0.475 | +0.150 | 2.45 | 7.8 | 0.044 | 0.099 | full_system ✓ |
| qwen | vanilla_vector vs full_system | 0.725 | 0.475 | +0.250 | 2.43 | 5.9 | 0.057 | 0.078 | full_system |

## loop_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 0.050 | 0.125 | -0.075 | -2.45 | 4.0 | 0.083 | 0.168 | no_rag |
| claude | no_rag vs full_system | 0.050 | 0.100 | -0.050 | -1.26 | 7.7 | 0.244 | 0.523 | no_rag |
| claude | vanilla_vector vs full_system | 0.125 | 0.100 | +0.025 | 1.00 | 4.0 | 0.377 | 1.000 | full_system |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | no_rag vs vanilla_vector | 0.075 | 0.075 | +0.000 | 0.00 | 6.6 | 1.000 | 1.000 | tie |
| qwen | no_rag vs full_system | 0.075 | 0.000 | +0.075 | 2.45 | 4.0 | 0.083 | 0.169 | full_system |
| qwen | vanilla_vector vs full_system | 0.075 | 0.000 | +0.075 | 1.50 | 4.0 | 0.214 | 0.444 | full_system |

## goal_completion_rate (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.500 | 0.500 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | no_rag vs full_system | 0.500 | 0.300 | +0.200 | 1.63 | 4.0 | 0.185 | 0.449 | no_rag |
| gemini | vanilla_vector vs full_system | 0.500 | 0.300 | +0.200 | 1.63 | 4.0 | 0.185 | 0.449 | vanilla_vector |
| claude | no_rag vs vanilla_vector | 0.500 | 0.500 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 0.500 | 0.500 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 0.500 | 0.500 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.200 | -0.200 | -1.63 | 4.0 | 0.185 | 0.447 | vanilla_vector |
| gpt | no_rag vs full_system | 0.000 | 0.300 | -0.300 | -2.45 | 4.0 | 0.083 | 0.170 | full_system |
| gpt | vanilla_vector vs full_system | 0.200 | 0.300 | -0.100 | -0.58 | 8.0 | 0.580 | 1.000 | full_system |
| qwen | no_rag vs vanilla_vector | 0.300 | 0.100 | +0.200 | 1.26 | 7.7 | 0.244 | 0.519 | no_rag |
| qwen | no_rag vs full_system | 0.300 | 0.100 | +0.200 | 1.26 | 7.7 | 0.244 | 0.523 | no_rag |
| qwen | vanilla_vector vs full_system | 0.100 | 0.100 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |

## mean_latency_sec (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 7.075 | 8.648 | -1.574 | -4.87 | 5.2 | 0.011 | 0.009 | no_rag ✓ |
| gemini | no_rag vs full_system | 7.075 | 34.281 | -27.206 | -16.61 | 4.3 | 0.007 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 8.648 | 34.281 | -25.632 | -15.88 | 4.0 | 0.009 | 0.009 | vanilla_vector ✓ |
| claude | no_rag vs vanilla_vector | 2.778 | 3.986 | -1.208 | -5.45 | 5.1 | 0.009 | 0.009 | no_rag ✓ |
| claude | no_rag vs full_system | 2.778 | 27.455 | -24.677 | -23.86 | 4.3 | 0.006 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 3.986 | 27.455 | -23.469 | -23.09 | 4.0 | 0.008 | 0.009 | vanilla_vector ✓ |
| gpt | no_rag vs vanilla_vector | 2.288 | 3.513 | -1.225 | -5.55 | 5.5 | 0.007 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 2.288 | 29.713 | -27.425 | -32.85 | 4.1 | 0.007 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 3.513 | 29.713 | -26.200 | -30.66 | 4.5 | 0.005 | 0.009 | vanilla_vector ✓ |
| qwen | no_rag vs vanilla_vector | 7.350 | 42.174 | -34.824 | -1.09 | 4.0 | 0.340 | 0.018 | no_rag ✓ |
| qwen | no_rag vs full_system | 7.350 | 30.907 | -23.557 | -22.44 | 5.9 | 0.001 | 0.009 | no_rag ✓ |
| qwen | vanilla_vector vs full_system | 42.174 | 30.907 | +11.267 | 0.35 | 4.0 | 0.743 | 1.000 | full_system |

## mean_cost_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.001 | 0.009 | -0.009 | -1349.97 | 7.6 | 0.000 | 0.009 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.001 | 0.003 | -0.002 | -71.57 | 4.2 | 0.007 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.009 | 0.003 | +0.007 | 241.27 | 4.3 | 0.006 | 0.009 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.006 | 0.027 | -0.021 | -424.69 | 5.9 | 0.001 | 0.009 | no_rag ✓ |
| claude | no_rag vs full_system | 0.006 | 0.012 | -0.006 | -74.85 | 7.4 | 0.000 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.027 | 0.012 | +0.015 | 241.06 | 5.1 | 0.003 | 0.009 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.003 | 0.018 | -0.015 | -898.79 | 4.2 | 0.007 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.003 | 0.007 | -0.004 | -98.54 | 5.9 | 0.001 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.018 | 0.007 | +0.011 | 342.33 | 4.0 | 0.008 | 0.009 | full_system ✓ |
| qwen | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |

# GEMINI — hybrid (full_system) vs vanilla_vector focus

Does Gemini show a significant full_system > vanilla_vector trend that other models don't?

| metric | Gemini full_system | Gemini vanilla | Δ | perm p | direction |
|---|---|---|---|---|---|
| step_accuracy | 0.600 | 0.600 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| hallucination_rate | 0.050 | 0.100 | -0.050 | 0.681 | full_system ↑ (helps) |
| loop_rate | 0.000 | 0.000 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| goal_completion_rate | 0.300 | 0.500 | -0.200 | 0.453 | vanilla ↑ (hybrid hurts) |
| mean_latency_sec | 34.281 | 8.648 | +25.632 | 0.009 ✓ sig | vanilla ↑ (hybrid hurts) |
| mean_cost_usd | 0.003 | 0.009 | -0.007 | 0.009 ✓ sig | full_system ↑ (helps) |

## Same pair, other models — is Gemini's pattern unique?

| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |
|---|---|---|---|---|---|---|
| step_accuracy | gemini | 0.600 | 0.600 | +0.000 | 1.000 | no |
| step_accuracy | claude | 0.775 | 0.725 | +0.050 | 0.551 | yes |
| step_accuracy | gpt | 0.700 | 0.375 | +0.325 | 0.009 ✓ | yes |
| step_accuracy | qwen | 0.500 | 0.350 | +0.150 | 0.222 | yes |
| hallucination_rate | gemini | 0.050 | 0.100 | -0.050 | 0.681 | yes |
| hallucination_rate | claude | 0.150 | 0.250 | -0.100 | 0.170 | yes |
| hallucination_rate | gpt | 0.550 | 0.475 | +0.075 | 0.281 | no |
| hallucination_rate | qwen | 0.475 | 0.725 | -0.250 | 0.081 | yes |
| loop_rate | gemini | 0.000 | 0.000 | +0.000 | 1.000 | no |
| loop_rate | claude | 0.100 | 0.125 | -0.025 | 1.000 | yes |
| loop_rate | gpt | 0.000 | 0.000 | +0.000 | 1.000 | no |
| loop_rate | qwen | 0.000 | 0.075 | -0.075 | 0.447 | yes |
| goal_completion_rate | gemini | 0.300 | 0.500 | -0.200 | 0.453 | no |
| goal_completion_rate | claude | 0.500 | 0.500 | +0.000 | 1.000 | no |
| goal_completion_rate | gpt | 0.300 | 0.200 | +0.100 | 1.000 | yes |
| goal_completion_rate | qwen | 0.100 | 0.100 | +0.000 | 1.000 | no |
| mean_latency_sec | gemini | 34.281 | 8.648 | +25.632 | 0.009 ✓ | no |
| mean_latency_sec | claude | 27.455 | 3.986 | +23.469 | 0.009 ✓ | no |
| mean_latency_sec | gpt | 29.713 | 3.513 | +26.200 | 0.009 ✓ | no |
| mean_latency_sec | qwen | 30.907 | 42.174 | -11.267 | 1.000 | yes |
| mean_cost_usd | gemini | 0.003 | 0.009 | -0.007 | 0.009 ✓ | yes |
| mean_cost_usd | claude | 0.012 | 0.027 | -0.015 | 0.009 ✓ | yes |
| mean_cost_usd | gpt | 0.007 | 0.018 | -0.011 | 0.009 ✓ | yes |
| mean_cost_usd | qwen | 0.000 | 0.000 | +0.000 | 1.000 | no |
