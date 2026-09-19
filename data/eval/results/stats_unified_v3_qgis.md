
# Pipeline health — routing confidence + fallback rate

Fallback activates when rerank confidence < 0.7. Zero on backends that don't call the router (no_rag, vanilla_vector, graph_only, vision_only if it doesn't hit the reranker).

| model | backend | mean_route_conf | fallback_rate (of routed steps) |
|---|---|---|---|
| gemini | no_rag | — | 0% |
| gemini | vanilla_vector | — | 0% |
| gemini | vanilla_budget | — | 0% |
| gemini | graph_only | — | 0% |
| gemini | vision_only | — | 0% |
| gemini | full_system | 0.80 | 11% |
| gemini | state_path | 0.81 | 0% |
| claude | no_rag | — | 0% |
| claude | vanilla_vector | — | 0% |
| claude | vanilla_budget | — | 0% |
| claude | graph_only | — | 0% |
| claude | vision_only | — | 0% |
| claude | full_system | 0.80 | 11% |
| claude | state_path | 0.81 | 0% |
| gpt | no_rag | — | 0% |
| gpt | vanilla_vector | — | 0% |
| gpt | vanilla_budget | — | 0% |
| gpt | graph_only | — | 0% |
| gpt | vision_only | — | 0% |
| gpt | full_system | 0.80 | 11% |
| gpt | state_path | 0.82 | 0% |
# Pairwise backend tests — Unified matrix (n=5 per side)

Welch's unequal-variance t + 10,000-resample permutation p.


## step_accuracy (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | no_rag vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 1.000 | 0.875 | +0.125 | 0.00 | inf | 0.000 | 0.000 | no_rag ✓ |
| claude | no_rag vs full_system | 1.000 | 0.887 | +0.113 | 9.00 | 9.0 | 0.000 | 0.000 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.875 | 0.887 | -0.012 | -1.00 | 9.0 | 0.344 | 1.000 | full_system |
| gpt | no_rag vs vanilla_vector | 0.988 | 0.912 | +0.075 | 3.29 | 15.5 | 0.005 | 0.019 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.988 | 0.838 | +0.150 | 6.57 | 15.5 | 0.000 | 0.000 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.912 | 0.838 | +0.075 | 2.78 | 18.0 | 0.013 | 0.035 | vanilla_vector ✓ |

## hallucination_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.125 | 0.163 | -0.038 | -1.96 | 9.0 | 0.083 | 0.213 | no_rag |
| gemini | no_rag vs full_system | 0.125 | 0.125 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.163 | 0.125 | +0.038 | 1.96 | 9.0 | 0.083 | 0.208 | full_system |
| claude | no_rag vs vanilla_vector | 0.350 | 0.275 | +0.075 | 1.57 | 14.9 | 0.139 | 0.302 | vanilla_vector |
| claude | no_rag vs full_system | 0.350 | 0.350 | +0.000 | 0.00 | 18.0 | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 0.275 | 0.350 | -0.075 | -1.57 | 14.9 | 0.139 | 0.298 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.125 | 0.125 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 0.125 | 0.125 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | vanilla_vector vs full_system | 0.125 | 0.125 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |

## loop_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 0.000 | 0.075 | -0.075 | -1.96 | 9.0 | 0.083 | 0.208 | no_rag |
| gpt | vanilla_vector vs full_system | 0.000 | 0.075 | -0.075 | -1.96 | 9.0 | 0.083 | 0.208 | vanilla_vector |

## goal_completion_rate (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | no_rag vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs vanilla_vector | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | vanilla_vector vs full_system | 1.000 | 1.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |

## mean_latency_sec (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 8.650 | 10.159 | -1.510 | -4.96 | 17.0 | 0.000 | 0.000 | no_rag ✓ |
| gemini | no_rag vs full_system | 8.650 | 33.056 | -24.406 | -25.32 | 9.7 | 0.000 | 0.000 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 10.159 | 33.056 | -22.896 | -23.47 | 10.2 | 0.000 | 0.000 | vanilla_vector ✓ |
| claude | no_rag vs vanilla_vector | 2.857 | 4.160 | -1.303 | -7.08 | 17.6 | 0.000 | 0.000 | no_rag ✓ |
| claude | no_rag vs full_system | 2.857 | 26.384 | -23.527 | -20.69 | 9.2 | 0.000 | 0.000 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 4.160 | 26.384 | -22.225 | -19.51 | 9.3 | 0.000 | 0.000 | vanilla_vector ✓ |
| gpt | no_rag vs vanilla_vector | 1.876 | 3.136 | -1.260 | -18.49 | 17.2 | 0.000 | 0.000 | no_rag ✓ |
| gpt | no_rag vs full_system | 1.876 | 25.459 | -23.583 | -20.80 | 9.0 | 0.000 | 0.000 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 3.136 | 25.459 | -22.323 | -19.68 | 9.0 | 0.000 | 0.000 | vanilla_vector ✓ |

## mean_cost_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.005 | 0.010 | -0.005 | -16.83 | 17.2 | 0.000 | 0.000 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.005 | 0.009 | -0.003 | -13.57 | 17.9 | 0.000 | 0.000 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.010 | 0.009 | +0.001 | 5.31 | 16.7 | 0.000 | 0.000 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.007 | 0.018 | -0.011 | -538.16 | 13.0 | 0.000 | 0.000 | no_rag ✓ |
| claude | no_rag vs full_system | 0.007 | 0.011 | -0.004 | -248.18 | 14.4 | 0.000 | 0.000 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.018 | 0.011 | +0.006 | 272.83 | 17.5 | 0.000 | 0.000 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.004 | 0.012 | -0.008 | -3420.97 | 14.3 | 0.000 | 0.000 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.004 | 0.007 | -0.003 | -374.32 | 9.3 | 0.000 | 0.000 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.012 | 0.007 | +0.005 | 504.59 | 9.9 | 0.000 | 0.000 | full_system ✓ |

## mean_cost_total_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.005 | 0.010 | -0.005 | -16.83 | 17.2 | 0.000 | 0.000 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.005 | 0.011 | -0.006 | -15.83 | 13.6 | 0.000 | 0.000 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.010 | 0.011 | -0.001 | -3.18 | 15.5 | 0.007 | 0.001 | vanilla_vector ✓ |
| claude | no_rag vs vanilla_vector | 0.007 | 0.018 | -0.011 | -538.16 | 13.0 | 0.000 | 0.000 | no_rag ✓ |
| claude | no_rag vs full_system | 0.007 | 0.014 | -0.007 | -35.96 | 9.0 | 0.000 | 0.000 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.018 | 0.014 | +0.004 | 18.22 | 9.1 | 0.000 | 0.000 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.004 | 0.012 | -0.008 | -3420.97 | 14.3 | 0.000 | 0.000 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.004 | 0.010 | -0.006 | -30.37 | 9.0 | 0.000 | 0.000 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.012 | 0.010 | +0.002 | 8.61 | 9.0 | 0.000 | 0.000 | full_system ✓ |

# GEMINI — hybrid (full_system) vs vanilla_vector focus

Does Gemini show a significant full_system > vanilla_vector trend that other models don't?

| metric | Gemini full_system | Gemini vanilla | Δ | perm p | direction |
|---|---|---|---|---|---|
| step_accuracy | 1.000 | 1.000 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| hallucination_rate | 0.125 | 0.163 | -0.038 | 0.213 | full_system ↑ (helps) |
| loop_rate | 0.000 | 0.000 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| goal_completion_rate | 1.000 | 1.000 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| mean_latency_sec | 33.056 | 10.159 | +22.896 | 0.000 ✓ sig | vanilla ↑ (hybrid hurts) |
| mean_cost_usd | 0.009 | 0.010 | -0.001 | 0.000 ✓ sig | full_system ↑ (helps) |
| mean_cost_total_usd | 0.011 | 0.010 | +0.001 | 0.001 ✓ sig | vanilla ↑ (hybrid hurts) |

## Same pair, other models — is Gemini's pattern unique?

| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |
|---|---|---|---|---|---|---|
| step_accuracy | gemini | 1.000 | 1.000 | +0.000 | 1.000 | no |
| step_accuracy | claude | 0.887 | 0.875 | +0.012 | 1.000 | yes |
| step_accuracy | gpt | 0.838 | 0.912 | -0.075 | 0.035 ✓ | no |
| hallucination_rate | gemini | 0.125 | 0.163 | -0.038 | 0.213 | yes |
| hallucination_rate | claude | 0.350 | 0.275 | +0.075 | 0.306 | no |
| hallucination_rate | gpt | 0.125 | 0.125 | +0.000 | 1.000 | no |
| loop_rate | gemini | 0.000 | 0.000 | +0.000 | 1.000 | no |
| loop_rate | claude | 0.000 | 0.000 | +0.000 | 1.000 | no |
| loop_rate | gpt | 0.075 | 0.000 | +0.075 | 0.212 | no |
| goal_completion_rate | gemini | 1.000 | 1.000 | +0.000 | 1.000 | no |
| goal_completion_rate | claude | 1.000 | 1.000 | +0.000 | 1.000 | no |
| goal_completion_rate | gpt | 1.000 | 1.000 | +0.000 | 1.000 | no |
| mean_latency_sec | gemini | 33.056 | 10.159 | +22.896 | 0.000 ✓ | no |
| mean_latency_sec | claude | 26.384 | 4.160 | +22.225 | 0.000 ✓ | no |
| mean_latency_sec | gpt | 25.459 | 3.136 | +22.323 | 0.000 ✓ | no |
| mean_cost_usd | gemini | 0.009 | 0.010 | -0.001 | 0.000 ✓ | yes |
| mean_cost_usd | claude | 0.011 | 0.018 | -0.006 | 0.000 ✓ | yes |
| mean_cost_usd | gpt | 0.007 | 0.012 | -0.005 | 0.000 ✓ | yes |
| mean_cost_total_usd | gemini | 0.011 | 0.010 | +0.001 | 0.001 ✓ | no |
| mean_cost_total_usd | claude | 0.014 | 0.018 | -0.004 | 0.000 ✓ | yes |
| mean_cost_total_usd | gpt | 0.010 | 0.012 | -0.002 | 0.000 ✓ | yes |
