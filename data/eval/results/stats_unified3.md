
# Pipeline health — routing confidence + fallback rate

Fallback activates when rerank confidence < 0.7. Zero on backends that don't call the router (no_rag, vanilla_vector, graph_only, vision_only if it doesn't hit the reranker).

| model | backend | mean_route_conf | fallback_rate (of routed steps) |
|---|---|---|---|
| gemini | no_rag | — | 0% |
| gemini | vanilla_vector | — | 0% |
| gemini | graph_only | — | 0% |
| gemini | vision_only | — | 0% |
| gemini | full_system | 0.82 | 18% |
| gemini | state_path | — | 0% |
| claude | no_rag | — | 0% |
| claude | vanilla_vector | — | 0% |
| claude | graph_only | — | 0% |
| claude | vision_only | — | 0% |
| claude | full_system | 0.83 | 14% |
| claude | state_path | — | 0% |
| gpt | no_rag | — | 0% |
| gpt | vanilla_vector | — | 0% |
| gpt | graph_only | — | 0% |
| gpt | vision_only | — | 0% |
| gpt | full_system | 0.82 | 16% |
| gpt | state_path | — | 0% |
| qwen | no_rag | — | 0% |
| qwen | vanilla_vector | — | 0% |
| qwen | graph_only | — | 0% |
| qwen | vision_only | — | 0% |
| qwen | full_system | 0.81 | 17% |
| qwen | state_path | — | 0% |
# Pairwise backend tests — Unified matrix (n=5 per side)

Welch's unequal-variance t + 10,000-resample permutation p.


## step_accuracy (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.558 | 0.675 | -0.117 | -2.29 | 8.0 | 0.055 | 0.083 | vanilla_vector |
| gemini | no_rag vs full_system | 0.558 | 0.742 | -0.183 | -4.40 | 6.3 | 0.008 | 0.009 | full_system ✓ |
| gemini | vanilla_vector vs full_system | 0.675 | 0.742 | -0.067 | -1.62 | 6.3 | 0.157 | 0.177 | full_system |
| claude | no_rag vs vanilla_vector | 0.858 | 0.833 | +0.025 | 2.45 | 4.0 | 0.083 | 0.169 | no_rag |
| claude | no_rag vs full_system | 0.858 | 0.842 | +0.017 | 1.26 | 7.7 | 0.244 | 0.527 | no_rag |
| claude | vanilla_vector vs full_system | 0.833 | 0.842 | -0.008 | -1.00 | 4.0 | 0.377 | 1.000 | full_system |
| gpt | no_rag vs vanilla_vector | 0.567 | 0.608 | -0.042 | -0.52 | 5.9 | 0.623 | 0.758 | vanilla_vector |
| gpt | no_rag vs full_system | 0.567 | 0.642 | -0.075 | -0.92 | 6.1 | 0.393 | 0.540 | full_system |
| gpt | vanilla_vector vs full_system | 0.608 | 0.642 | -0.033 | -0.63 | 8.0 | 0.548 | 0.639 | full_system |
| qwen | no_rag vs vanilla_vector | 0.433 | 0.417 | +0.017 | 0.25 | 7.8 | 0.809 | 0.823 | no_rag |
| qwen | no_rag vs full_system | 0.433 | 0.608 | -0.175 | -2.96 | 6.7 | 0.027 | 0.031 | full_system ✓ |
| qwen | vanilla_vector vs full_system | 0.417 | 0.608 | -0.192 | -3.57 | 7.2 | 0.012 | 0.024 | full_system ✓ |

## hallucination_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.000 | 0.050 | -0.050 | -1.50 | 4.0 | 0.214 | 0.446 | no_rag |
| gemini | no_rag vs full_system | 0.000 | 0.017 | -0.017 | -1.00 | 4.0 | 0.377 | 1.000 | no_rag |
| gemini | vanilla_vector vs full_system | 0.050 | 0.017 | +0.033 | 0.89 | 5.9 | 0.407 | 0.717 | full_system |
| claude | no_rag vs vanilla_vector | 0.258 | 0.300 | -0.042 | -1.13 | 7.9 | 0.292 | 0.394 | no_rag |
| claude | no_rag vs full_system | 0.258 | 0.250 | +0.008 | 0.27 | 7.5 | 0.793 | 1.000 | full_system |
| claude | vanilla_vector vs full_system | 0.300 | 0.250 | +0.050 | 1.50 | 7.0 | 0.179 | 0.272 | full_system |
| gpt | no_rag vs vanilla_vector | 0.333 | 0.400 | -0.067 | -1.04 | 4.6 | 0.352 | 0.388 | no_rag |
| gpt | no_rag vs full_system | 0.333 | 0.325 | +0.008 | 0.11 | 7.1 | 0.915 | 0.952 | full_system |
| gpt | vanilla_vector vs full_system | 0.400 | 0.325 | +0.075 | 1.64 | 5.2 | 0.163 | 0.166 | full_system |
| qwen | no_rag vs vanilla_vector | 0.433 | 0.550 | -0.117 | -1.09 | 6.6 | 0.315 | 0.341 | no_rag |
| qwen | no_rag vs full_system | 0.433 | 0.608 | -0.175 | -2.65 | 6.9 | 0.038 | 0.025 | no_rag ✓ |
| qwen | vanilla_vector vs full_system | 0.550 | 0.608 | -0.058 | -0.59 | 5.2 | 0.580 | 0.572 | vanilla_vector |

## loop_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.008 | 0.017 | -0.008 | -0.45 | 5.9 | 0.671 | 1.000 | no_rag |
| gemini | no_rag vs full_system | 0.008 | 0.008 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.017 | 0.008 | +0.008 | 0.45 | 5.9 | 0.671 | 1.000 | full_system |
| claude | no_rag vs vanilla_vector | 0.033 | 0.017 | +0.017 | 0.89 | 6.9 | 0.402 | 0.687 | vanilla_vector |
| claude | no_rag vs full_system | 0.033 | 0.033 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 0.017 | 0.033 | -0.017 | -0.89 | 6.9 | 0.402 | 0.685 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.008 | -0.008 | -1.00 | 4.0 | 0.377 | 1.000 | no_rag |
| gpt | no_rag vs full_system | 0.000 | 0.025 | -0.025 | -1.50 | 4.0 | 0.214 | 0.451 | no_rag |
| gpt | vanilla_vector vs full_system | 0.008 | 0.025 | -0.017 | -0.89 | 5.9 | 0.407 | 0.732 | vanilla_vector |
| qwen | no_rag vs vanilla_vector | 0.242 | 0.133 | +0.108 | 1.95 | 7.8 | 0.091 | 0.131 | vanilla_vector |
| qwen | no_rag vs full_system | 0.242 | 0.067 | +0.175 | 4.20 | 6.5 | 0.009 | 0.017 | full_system ✓ |
| qwen | vanilla_vector vs full_system | 0.133 | 0.067 | +0.067 | 1.40 | 5.9 | 0.214 | 0.288 | full_system |

## goal_completion_rate (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.800 | 0.800 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |
| gemini | no_rag vs full_system | 0.800 | 0.800 | +0.000 | 0.00 | 6.6 | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.800 | 0.800 | +0.000 | 0.00 | 6.6 | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 1.000 | 0.933 | +0.067 | 1.00 | 4.0 | 0.377 | 1.000 | no_rag |
| claude | vanilla_vector vs full_system | 1.000 | 0.933 | +0.067 | 1.00 | 4.0 | 0.377 | 1.000 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.667 | 0.800 | -0.133 | -1.00 | 7.5 | 0.349 | 0.649 | vanilla_vector |
| gpt | no_rag vs full_system | 0.667 | 0.733 | -0.067 | -0.53 | 6.8 | 0.610 | 1.000 | full_system |
| gpt | vanilla_vector vs full_system | 0.800 | 0.733 | +0.067 | 0.63 | 7.7 | 0.546 | 1.000 | vanilla_vector |
| qwen | no_rag vs vanilla_vector | 0.467 | 0.200 | +0.267 | 1.23 | 7.6 | 0.255 | 0.379 | no_rag |
| qwen | no_rag vs full_system | 0.467 | 0.200 | +0.267 | 1.41 | 5.8 | 0.212 | 0.353 | no_rag |
| qwen | vanilla_vector vs full_system | 0.200 | 0.200 | +0.000 | 0.00 | 6.6 | 1.000 | 1.000 | tie |

## mean_latency_sec (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 8.861 | 11.571 | -2.710 | -3.61 | 6.3 | 0.015 | 0.009 | no_rag ✓ |
| gemini | no_rag vs full_system | 8.861 | 37.417 | -28.556 | -54.93 | 8.0 | 0.000 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 11.571 | 37.417 | -25.846 | -34.35 | 6.3 | 0.001 | 0.009 | vanilla_vector ✓ |
| claude | no_rag vs vanilla_vector | 3.096 | 4.258 | -1.163 | -4.38 | 7.8 | 0.004 | 0.009 | no_rag ✓ |
| claude | no_rag vs full_system | 3.096 | 28.584 | -25.488 | -40.83 | 4.9 | 0.003 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 4.258 | 28.584 | -24.326 | -39.54 | 4.7 | 0.004 | 0.009 | vanilla_vector ✓ |
| gpt | no_rag vs vanilla_vector | 2.055 | 5.110 | -3.055 | -24.80 | 6.8 | 0.000 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 2.055 | 26.677 | -24.622 | -30.92 | 4.1 | 0.008 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 5.110 | 26.677 | -21.567 | -26.95 | 4.1 | 0.007 | 0.009 | vanilla_vector ✓ |
| qwen | no_rag vs vanilla_vector | 6.727 | 9.646 | -2.918 | -5.07 | 8.0 | 0.002 | 0.009 | no_rag ✓ |
| qwen | no_rag vs full_system | 6.727 | 32.572 | -25.845 | -40.60 | 7.7 | 0.000 | 0.009 | no_rag ✓ |
| qwen | vanilla_vector vs full_system | 9.646 | 32.572 | -22.927 | -35.62 | 7.8 | 0.000 | 0.009 | vanilla_vector ✓ |

## mean_cost_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.001 | 0.009 | -0.009 | -2258.64 | 7.6 | 0.000 | 0.009 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.001 | 0.002 | -0.001 | -126.64 | 4.3 | 0.005 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.009 | 0.002 | +0.007 | 606.58 | 4.6 | 0.004 | 0.009 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.006 | 0.027 | -0.021 | -641.98 | 7.4 | 0.000 | 0.009 | no_rag ✓ |
| claude | no_rag vs full_system | 0.006 | 0.011 | -0.004 | -51.62 | 4.8 | 0.004 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.027 | 0.011 | +0.016 | 189.58 | 4.4 | 0.005 | 0.009 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.004 | 0.018 | -0.014 | -1697.39 | 5.2 | 0.002 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.004 | 0.006 | -0.003 | -65.99 | 4.3 | 0.006 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.018 | 0.006 | +0.012 | 283.87 | 4.0 | 0.008 | 0.009 | full_system ✓ |
| qwen | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |

# GEMINI — hybrid (full_system) vs vanilla_vector focus

Does Gemini show a significant full_system > vanilla_vector trend that other models don't?

| metric | Gemini full_system | Gemini vanilla | Δ | perm p | direction |
|---|---|---|---|---|---|
| step_accuracy | 0.742 | 0.675 | +0.067 | 0.169 | full_system ↑ (helps) |
| hallucination_rate | 0.017 | 0.050 | -0.033 | 0.720 | full_system ↑ (helps) |
| loop_rate | 0.008 | 0.017 | -0.008 | 1.000 | full_system ↑ (helps) |
| goal_completion_rate | 0.800 | 0.800 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| mean_latency_sec | 37.417 | 11.571 | +25.846 | 0.009 ✓ sig | vanilla ↑ (hybrid hurts) |
| mean_cost_usd | 0.002 | 0.009 | -0.007 | 0.009 ✓ sig | full_system ↑ (helps) |

## Same pair, other models — is Gemini's pattern unique?

| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |
|---|---|---|---|---|---|---|
| step_accuracy | gemini | 0.742 | 0.675 | +0.067 | 0.169 | yes |
| step_accuracy | claude | 0.842 | 0.833 | +0.008 | 1.000 | yes |
| step_accuracy | gpt | 0.642 | 0.608 | +0.033 | 0.645 | yes |
| step_accuracy | qwen | 0.608 | 0.417 | +0.192 | 0.025 ✓ | yes |
| hallucination_rate | gemini | 0.017 | 0.050 | -0.033 | 0.720 | yes |
| hallucination_rate | claude | 0.250 | 0.300 | -0.050 | 0.273 | yes |
| hallucination_rate | gpt | 0.325 | 0.400 | -0.075 | 0.170 | yes |
| hallucination_rate | qwen | 0.608 | 0.550 | +0.058 | 0.567 | no |
| loop_rate | gemini | 0.008 | 0.017 | -0.008 | 1.000 | yes |
| loop_rate | claude | 0.033 | 0.017 | +0.017 | 0.678 | no |
| loop_rate | gpt | 0.025 | 0.008 | +0.017 | 0.725 | no |
| loop_rate | qwen | 0.067 | 0.133 | -0.067 | 0.284 | yes |
| goal_completion_rate | gemini | 0.800 | 0.800 | +0.000 | 1.000 | no |
| goal_completion_rate | claude | 0.933 | 1.000 | -0.067 | 1.000 | no |
| goal_completion_rate | gpt | 0.733 | 0.800 | -0.067 | 1.000 | no |
| goal_completion_rate | qwen | 0.200 | 0.200 | +0.000 | 1.000 | no |
| mean_latency_sec | gemini | 37.417 | 11.571 | +25.846 | 0.009 ✓ | no |
| mean_latency_sec | claude | 28.584 | 4.258 | +24.326 | 0.009 ✓ | no |
| mean_latency_sec | gpt | 26.677 | 5.110 | +21.567 | 0.009 ✓ | no |
| mean_latency_sec | qwen | 32.572 | 9.646 | +22.927 | 0.009 ✓ | no |
| mean_cost_usd | gemini | 0.002 | 0.009 | -0.007 | 0.009 ✓ | yes |
| mean_cost_usd | claude | 0.011 | 0.027 | -0.016 | 0.009 ✓ | yes |
| mean_cost_usd | gpt | 0.006 | 0.018 | -0.012 | 0.009 ✓ | yes |
| mean_cost_usd | qwen | 0.000 | 0.000 | +0.000 | 1.000 | no |
