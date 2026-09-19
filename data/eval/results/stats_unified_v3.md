
# Pipeline health — routing confidence + fallback rate

Fallback activates when rerank confidence < 0.7. Zero on backends that don't call the router (no_rag, vanilla_vector, graph_only, vision_only if it doesn't hit the reranker).

| model | backend | mean_route_conf | fallback_rate (of routed steps) |
|---|---|---|---|
| gemini | no_rag | — | 0% |
| gemini | vanilla_vector | — | 0% |
| gemini | vanilla_budget | — | 0% |
| gemini | graph_only | — | 0% |
| gemini | vision_only | — | 0% |
| gemini | full_system | 0.86 | 0% |
| gemini | state_path | 0.87 | 0% |
| claude | no_rag | — | 0% |
| claude | vanilla_vector | — | 0% |
| claude | vanilla_budget | — | 0% |
| claude | graph_only | — | 0% |
| claude | vision_only | — | 0% |
| claude | full_system | 0.86 | 0% |
| claude | state_path | 0.86 | 0% |
| gpt | no_rag | — | 0% |
| gpt | vanilla_vector | — | 0% |
| gpt | vanilla_budget | — | 0% |
| gpt | graph_only | — | 0% |
| gpt | vision_only | — | 0% |
| gpt | full_system | 0.87 | 0% |
| gpt | state_path | 0.86 | 0% |
# Pairwise backend tests — Unified matrix (n=5 per side)

Welch's unequal-variance t + 10,000-resample permutation p.


## step_accuracy (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.733 | 0.817 | -0.083 | -2.43 | 17.3 | 0.027 | 0.036 | vanilla_vector ✓ |
| gemini | no_rag vs full_system | 0.733 | 0.912 | -0.179 | -5.93 | 18.0 | 0.000 | 0.000 | full_system ✓ |
| gemini | vanilla_vector vs full_system | 0.817 | 0.912 | -0.096 | -2.83 | 17.1 | 0.012 | 0.019 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.875 | 0.875 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 0.875 | 1.000 | -0.125 | 0.00 | inf | 0.000 | 0.000 | full_system ✓ |
| claude | vanilla_vector vs full_system | 0.875 | 1.000 | -0.125 | 0.00 | inf | 0.000 | 0.000 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.708 | 0.767 | -0.058 | -3.10 | 17.9 | 0.007 | 0.010 | vanilla_vector ✓ |
| gpt | no_rag vs full_system | 0.708 | 0.804 | -0.096 | -4.27 | 17.1 | 0.001 | 0.001 | full_system ✓ |
| gpt | vanilla_vector vs full_system | 0.767 | 0.804 | -0.037 | -1.72 | 16.4 | 0.104 | 0.146 | full_system |

## hallucination_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.029 | 0.033 | -0.004 | -0.49 | 17.7 | 0.628 | 1.000 | no_rag |
| gemini | no_rag vs full_system | 0.029 | 0.029 | +0.000 | 0.00 | 18.0 | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.033 | 0.029 | +0.004 | 0.49 | 17.7 | 0.628 | 1.000 | full_system |
| claude | no_rag vs vanilla_vector | 0.050 | 0.042 | +0.008 | 1.50 | 9.0 | 0.169 | 0.472 | vanilla_vector |
| claude | no_rag vs full_system | 0.050 | 0.042 | +0.008 | 1.50 | 9.0 | 0.169 | 0.472 | full_system |
| claude | vanilla_vector vs full_system | 0.042 | 0.042 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs vanilla_vector | 0.050 | 0.046 | +0.004 | 0.45 | 13.2 | 0.662 | 1.000 | vanilla_vector |
| gpt | no_rag vs full_system | 0.050 | 0.104 | -0.054 | -3.88 | 16.6 | 0.002 | 0.002 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.046 | 0.104 | -0.058 | -4.88 | 11.4 | 0.001 | 0.000 | vanilla_vector ✓ |

## loop_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.004 | 0.000 | +0.004 | 1.00 | 9.0 | 0.344 | 1.000 | vanilla_vector |
| gemini | no_rag vs full_system | 0.004 | 0.000 | +0.004 | 1.00 | 9.0 | 0.344 | 1.000 | full_system |
| gemini | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 0.025 | 0.013 | +0.013 | 1.34 | 17.9 | 0.197 | 0.368 | vanilla_vector |
| claude | no_rag vs full_system | 0.025 | 0.000 | +0.025 | 3.67 | 9.0 | 0.007 | 0.010 | full_system ✓ |
| claude | vanilla_vector vs full_system | 0.013 | 0.000 | +0.013 | 1.96 | 9.0 | 0.083 | 0.214 | full_system |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.029 | -0.029 | -3.28 | 9.0 | 0.012 | 0.010 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.000 | 0.025 | -0.025 | -1.96 | 9.0 | 0.083 | 0.208 | no_rag |
| gpt | vanilla_vector vs full_system | 0.029 | 0.025 | +0.004 | 0.27 | 16.1 | 0.792 | 1.000 | full_system |

## goal_completion_rate (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.700 | 0.733 | -0.033 | -0.60 | 16.7 | 0.557 | 1.000 | vanilla_vector |
| gemini | no_rag vs full_system | 0.700 | 0.867 | -0.167 | -2.61 | 14.9 | 0.021 | 0.059 | full_system ✓ |
| gemini | vanilla_vector vs full_system | 0.733 | 0.867 | -0.133 | -1.90 | 17.3 | 0.075 | 0.168 | full_system |
| claude | no_rag vs vanilla_vector | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 1.000 | 0.933 | +0.067 | 1.50 | 9.0 | 0.169 | 0.476 | no_rag |
| claude | vanilla_vector vs full_system | 1.000 | 0.933 | +0.067 | 1.50 | 9.0 | 0.169 | 0.476 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.667 | 0.667 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 0.667 | 0.400 | +0.267 | 6.00 | 9.0 | 0.001 | 0.001 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.667 | 0.400 | +0.267 | 6.00 | 9.0 | 0.001 | 0.001 | vanilla_vector ✓ |

## mean_latency_sec (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 9.168 | 11.367 | -2.199 | -8.18 | 15.8 | 0.000 | 0.000 | no_rag ✓ |
| gemini | no_rag vs full_system | 9.168 | 21.158 | -11.990 | -21.87 | 12.4 | 0.000 | 0.000 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 11.367 | 21.158 | -9.791 | -18.73 | 10.6 | 0.000 | 0.000 | vanilla_vector ✓ |
| claude | no_rag vs vanilla_vector | 3.507 | 4.302 | -0.795 | -3.27 | 14.9 | 0.006 | 0.004 | no_rag ✓ |
| claude | no_rag vs full_system | 3.507 | 13.393 | -9.886 | -30.00 | 17.2 | 0.000 | 0.000 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 4.302 | 13.393 | -9.091 | -31.79 | 13.2 | 0.000 | 0.000 | vanilla_vector ✓ |
| gpt | no_rag vs vanilla_vector | 1.712 | 2.871 | -1.159 | -11.19 | 10.2 | 0.000 | 0.000 | no_rag ✓ |
| gpt | no_rag vs full_system | 1.712 | 11.370 | -9.658 | -78.09 | 9.8 | 0.000 | 0.000 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 2.871 | 11.370 | -8.499 | -54.11 | 17.4 | 0.000 | 0.000 | vanilla_vector ✓ |

## mean_cost_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.006 | 0.015 | -0.009 | -56.63 | 13.5 | 0.000 | 0.000 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.006 | 0.010 | -0.004 | -19.50 | 18.0 | 0.000 | 0.000 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.015 | 0.010 | +0.005 | 30.44 | 13.1 | 0.000 | 0.000 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.006 | 0.026 | -0.019 | -2626.53 | 15.1 | 0.000 | 0.000 | no_rag ✓ |
| claude | no_rag vs full_system | 0.006 | 0.012 | -0.005 | -277.24 | 9.9 | 0.000 | 0.000 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.026 | 0.012 | +0.014 | 758.47 | 11.2 | 0.000 | 0.000 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.004 | 0.017 | -0.014 | -2962.63 | 17.6 | 0.000 | 0.000 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.004 | 0.007 | -0.004 | -581.69 | 15.6 | 0.000 | 0.000 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.017 | 0.007 | +0.010 | 1635.33 | 14.2 | 0.000 | 0.000 | full_system ✓ |

## mean_cost_total_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.006 | 0.015 | -0.009 | -56.63 | 13.5 | 0.000 | 0.000 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.006 | 0.012 | -0.007 | -32.43 | 18.0 | 0.000 | 0.000 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.015 | 0.012 | +0.003 | 14.80 | 13.2 | 0.000 | 0.000 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.006 | 0.026 | -0.019 | -2626.53 | 15.1 | 0.000 | 0.000 | no_rag ✓ |
| claude | no_rag vs full_system | 0.006 | 0.014 | -0.008 | -477.78 | 10.1 | 0.000 | 0.000 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.026 | 0.014 | +0.012 | 687.28 | 11.8 | 0.000 | 0.000 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.004 | 0.017 | -0.014 | -2962.63 | 17.6 | 0.000 | 0.000 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.004 | 0.010 | -0.006 | -577.06 | 11.0 | 0.000 | 0.000 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.017 | 0.010 | +0.007 | 671.67 | 10.5 | 0.000 | 0.000 | full_system ✓ |

# GEMINI — hybrid (full_system) vs vanilla_vector focus

Does Gemini show a significant full_system > vanilla_vector trend that other models don't?

| metric | Gemini full_system | Gemini vanilla | Δ | perm p | direction |
|---|---|---|---|---|---|
| step_accuracy | 0.912 | 0.817 | +0.096 | 0.020 ✓ sig | full_system ↑ (helps) |
| hallucination_rate | 0.029 | 0.033 | -0.004 | 1.000 | full_system ↑ (helps) |
| loop_rate | 0.000 | 0.000 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| goal_completion_rate | 0.867 | 0.733 | +0.133 | 0.171 | full_system ↑ (helps) |
| mean_latency_sec | 21.158 | 11.367 | +9.791 | 0.000 ✓ sig | vanilla ↑ (hybrid hurts) |
| mean_cost_usd | 0.010 | 0.015 | -0.005 | 0.000 ✓ sig | full_system ↑ (helps) |
| mean_cost_total_usd | 0.012 | 0.015 | -0.003 | 0.000 ✓ sig | full_system ↑ (helps) |

## Same pair, other models — is Gemini's pattern unique?

| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |
|---|---|---|---|---|---|---|
| step_accuracy | gemini | 0.912 | 0.817 | +0.096 | 0.020 ✓ | yes |
| step_accuracy | claude | 1.000 | 0.875 | +0.125 | 0.000 ✓ | yes |
| step_accuracy | gpt | 0.804 | 0.767 | +0.037 | 0.154 | yes |
| hallucination_rate | gemini | 0.029 | 0.033 | -0.004 | 1.000 | yes |
| hallucination_rate | claude | 0.042 | 0.042 | +0.000 | 1.000 | no |
| hallucination_rate | gpt | 0.104 | 0.046 | +0.058 | 0.000 ✓ | no |
| loop_rate | gemini | 0.000 | 0.000 | +0.000 | 1.000 | no |
| loop_rate | claude | 0.000 | 0.013 | -0.013 | 0.204 | yes |
| loop_rate | gpt | 0.025 | 0.029 | -0.004 | 1.000 | yes |
| goal_completion_rate | gemini | 0.867 | 0.733 | +0.133 | 0.171 | yes |
| goal_completion_rate | claude | 0.933 | 1.000 | -0.067 | 0.479 | no |
| goal_completion_rate | gpt | 0.400 | 0.667 | -0.267 | 0.001 ✓ | no |
| mean_latency_sec | gemini | 21.158 | 11.367 | +9.791 | 0.000 ✓ | no |
| mean_latency_sec | claude | 13.393 | 4.302 | +9.091 | 0.000 ✓ | no |
| mean_latency_sec | gpt | 11.370 | 2.871 | +8.499 | 0.000 ✓ | no |
| mean_cost_usd | gemini | 0.010 | 0.015 | -0.005 | 0.000 ✓ | yes |
| mean_cost_usd | claude | 0.012 | 0.026 | -0.014 | 0.000 ✓ | yes |
| mean_cost_usd | gpt | 0.007 | 0.017 | -0.010 | 0.000 ✓ | yes |
| mean_cost_total_usd | gemini | 0.012 | 0.015 | -0.003 | 0.000 ✓ | yes |
| mean_cost_total_usd | claude | 0.014 | 0.026 | -0.012 | 0.000 ✓ | yes |
| mean_cost_total_usd | gpt | 0.010 | 0.017 | -0.007 | 0.000 ✓ | yes |
