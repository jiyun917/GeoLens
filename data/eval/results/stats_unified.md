# Pairwise backend tests — Unified matrix (n=5 per side)

Welch's unequal-variance t + 10,000-resample permutation p.


## step_accuracy (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.525 | 0.600 | -0.075 | -1.13 | 8.0 | 0.291 | 0.479 | vanilla_vector |
| gemini | no_rag vs full_system | 0.525 | 0.550 | -0.025 | -0.37 | 8.0 | 0.725 | 1.000 | full_system |
| gemini | vanilla_vector vs full_system | 0.600 | 0.550 | +0.050 | 0.73 | 8.0 | 0.487 | 0.722 | vanilla_vector |
| claude | no_rag vs vanilla_vector | 0.750 | 0.725 | +0.025 | 0.53 | 6.8 | 0.610 | 1.000 | no_rag |
| claude | no_rag vs full_system | 0.750 | 0.650 | +0.100 | 2.14 | 6.8 | 0.075 | 0.170 | no_rag |
| claude | vanilla_vector vs full_system | 0.725 | 0.650 | +0.075 | 2.12 | 8.0 | 0.069 | 0.208 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.475 | 0.400 | +0.075 | 0.79 | 4.6 | 0.471 | 0.604 | no_rag |
| gpt | no_rag vs full_system | 0.475 | 0.475 | +0.000 | 0.00 | 7.9 | 1.000 | 1.000 | tie |
| gpt | vanilla_vector vs full_system | 0.400 | 0.475 | -0.075 | -0.87 | 4.7 | 0.430 | 0.640 | full_system |
| qwen | no_rag vs vanilla_vector | 0.375 | 0.450 | -0.075 | -1.50 | 7.5 | 0.176 | 0.365 | vanilla_vector |
| qwen | no_rag vs full_system | 0.375 | 0.350 | +0.025 | 0.20 | 4.8 | 0.853 | 1.000 | no_rag |
| qwen | vanilla_vector vs full_system | 0.450 | 0.350 | +0.100 | 0.80 | 4.5 | 0.465 | 0.575 | vanilla_vector |

## hallucination_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.000 | 0.150 | -0.150 | -2.45 | 4.0 | 0.083 | 0.046 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.000 | 0.100 | -0.100 | -2.14 | 4.0 | 0.110 | 0.166 | no_rag |
| gemini | vanilla_vector vs full_system | 0.150 | 0.100 | +0.050 | 0.65 | 7.5 | 0.536 | 0.752 | full_system |
| claude | no_rag vs vanilla_vector | 0.200 | 0.225 | -0.025 | -0.45 | 6.9 | 0.669 | 1.000 | no_rag |
| claude | no_rag vs full_system | 0.200 | 0.350 | -0.150 | -3.79 | 7.7 | 0.008 | 0.032 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.225 | 0.350 | -0.125 | -2.36 | 6.1 | 0.061 | 0.126 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.325 | 0.550 | -0.225 | -2.50 | 7.0 | 0.045 | 0.076 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.325 | 0.400 | -0.075 | -0.85 | 6.7 | 0.426 | 0.570 | no_rag |
| gpt | vanilla_vector vs full_system | 0.550 | 0.400 | +0.150 | 2.19 | 8.0 | 0.063 | 0.123 | full_system |
| qwen | no_rag vs vanilla_vector | 0.500 | 0.675 | -0.175 | -2.06 | 7.9 | 0.076 | 0.133 | no_rag |
| qwen | no_rag vs full_system | 0.500 | 0.475 | +0.025 | 0.34 | 7.8 | 0.741 | 1.000 | full_system |
| qwen | vanilla_vector vs full_system | 0.675 | 0.475 | +0.200 | 2.53 | 7.3 | 0.041 | 0.079 | full_system ✓ |

## loop_rate (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gemini | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 0.050 | 0.100 | -0.050 | -1.26 | 7.7 | 0.244 | 0.519 | no_rag |
| claude | no_rag vs full_system | 0.050 | 0.125 | -0.075 | -2.45 | 4.0 | 0.083 | 0.166 | no_rag |
| claude | vanilla_vector vs full_system | 0.100 | 0.125 | -0.025 | -1.00 | 4.0 | 0.377 | 1.000 | vanilla_vector |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | no_rag vs vanilla_vector | 0.075 | 0.000 | +0.075 | 2.45 | 4.0 | 0.083 | 0.166 | vanilla_vector |
| qwen | no_rag vs full_system | 0.075 | 0.025 | +0.050 | 1.26 | 7.7 | 0.244 | 0.522 | full_system |
| qwen | vanilla_vector vs full_system | 0.000 | 0.025 | -0.025 | -1.00 | 4.0 | 0.377 | 1.000 | vanilla_vector |

## goal_completion_rate (higher better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.600 | 0.500 | +0.100 | 0.53 | 6.8 | 0.610 | 1.000 | no_rag |
| gemini | no_rag vs full_system | 0.600 | 0.500 | +0.100 | 1.00 | 4.0 | 0.377 | 1.000 | no_rag |
| gemini | vanilla_vector vs full_system | 0.500 | 0.500 | +0.000 | 0.00 | 4.0 | 1.000 | 1.000 | tie |
| claude | no_rag vs vanilla_vector | 0.500 | 0.500 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | no_rag vs full_system | 0.500 | 0.500 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| claude | vanilla_vector vs full_system | 0.500 | 0.500 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| gpt | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | no_rag vs vanilla_vector | 0.100 | 0.000 | +0.100 | 1.00 | 4.0 | 0.377 | 1.000 | no_rag |
| qwen | no_rag vs full_system | 0.100 | 0.200 | -0.100 | -0.63 | 7.7 | 0.546 | 1.000 | full_system |
| qwen | vanilla_vector vs full_system | 0.000 | 0.200 | -0.200 | -1.63 | 4.0 | 0.185 | 0.447 | full_system |

## mean_latency_sec (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 6.679 | 8.080 | -1.401 | -4.48 | 5.2 | 0.013 | 0.009 | no_rag ✓ |
| gemini | no_rag vs full_system | 6.679 | 53.450 | -46.771 | -14.50 | 4.0 | 0.009 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 8.080 | 53.450 | -45.370 | -14.01 | 4.1 | 0.009 | 0.009 | vanilla_vector ✓ |
| claude | no_rag vs vanilla_vector | 2.802 | 4.514 | -1.712 | -1.94 | 4.3 | 0.128 | 0.015 | no_rag ✓ |
| claude | no_rag vs full_system | 2.802 | 73.948 | -71.146 | -17.73 | 4.0 | 0.009 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 4.514 | 73.948 | -69.434 | -16.93 | 4.4 | 0.006 | 0.009 | vanilla_vector ✓ |
| gpt | no_rag vs vanilla_vector | 2.112 | 3.468 | -1.356 | -2.01 | 4.1 | 0.123 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 2.112 | 73.393 | -71.281 | -20.87 | 4.0 | 0.009 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 3.468 | 73.393 | -69.925 | -20.09 | 4.3 | 0.006 | 0.009 | vanilla_vector ✓ |
| qwen | no_rag vs vanilla_vector | 6.344 | 7.421 | -1.077 | -2.42 | 4.8 | 0.071 | 0.039 | no_rag ✓ |
| qwen | no_rag vs full_system | 6.344 | 80.124 | -73.779 | -25.07 | 4.2 | 0.007 | 0.009 | no_rag ✓ |
| qwen | vanilla_vector vs full_system | 7.421 | 80.124 | -72.703 | -24.94 | 4.0 | 0.008 | 0.009 | vanilla_vector ✓ |

## mean_cost_usd (lower better)

| model | pair | mean A | mean B | Δ (A−B) | t | df | Welch p | perm p | winner |
|---|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | 0.001 | 0.009 | -0.009 | -894.70 | 7.1 | 0.000 | 0.009 | no_rag ✓ |
| gemini | no_rag vs full_system | 0.001 | 0.002 | -0.002 | -12.99 | 4.0 | 0.009 | 0.009 | no_rag ✓ |
| gemini | vanilla_vector vs full_system | 0.009 | 0.002 | +0.007 | 55.06 | 4.0 | 0.008 | 0.009 | full_system ✓ |
| claude | no_rag vs vanilla_vector | 0.006 | 0.027 | -0.021 | -320.98 | 7.9 | 0.000 | 0.009 | no_rag ✓ |
| claude | no_rag vs full_system | 0.006 | 0.009 | -0.003 | -7.17 | 4.1 | 0.013 | 0.009 | no_rag ✓ |
| claude | vanilla_vector vs full_system | 0.027 | 0.009 | +0.018 | 43.93 | 4.1 | 0.007 | 0.009 | full_system ✓ |
| gpt | no_rag vs vanilla_vector | 0.003 | 0.018 | -0.015 | -1011.17 | 5.4 | 0.002 | 0.009 | no_rag ✓ |
| gpt | no_rag vs full_system | 0.003 | 0.005 | -0.002 | -7.99 | 4.0 | 0.012 | 0.009 | no_rag ✓ |
| gpt | vanilla_vector vs full_system | 0.018 | 0.005 | +0.013 | 55.04 | 4.0 | 0.008 | 0.009 | full_system ✓ |
| qwen | no_rag vs vanilla_vector | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |
| qwen | vanilla_vector vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |

# GEMINI — hybrid (full_system) vs vanilla_vector focus

Does Gemini show a significant full_system > vanilla_vector trend that other models don't?

| metric | Gemini full_system | Gemini vanilla | Δ | perm p | direction |
|---|---|---|---|---|---|
| step_accuracy | 0.550 | 0.600 | -0.050 | 0.717 | vanilla ↑ (hybrid hurts) |
| hallucination_rate | 0.100 | 0.150 | -0.050 | 0.752 | full_system ↑ (helps) |
| loop_rate | 0.000 | 0.000 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| goal_completion_rate | 0.500 | 0.500 | +0.000 | 1.000 | vanilla ↑ (hybrid hurts) |
| mean_latency_sec | 53.450 | 8.080 | +45.370 | 0.009 ✓ sig | vanilla ↑ (hybrid hurts) |
| mean_cost_usd | 0.002 | 0.009 | -0.007 | 0.009 ✓ sig | full_system ↑ (helps) |

## Same pair, other models — is Gemini's pattern unique?

| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |
|---|---|---|---|---|---|---|
| step_accuracy | gemini | 0.550 | 0.600 | -0.050 | 0.717 | no |
| step_accuracy | claude | 0.650 | 0.725 | -0.075 | 0.206 | no |
| step_accuracy | gpt | 0.475 | 0.400 | +0.075 | 0.638 | yes |
| step_accuracy | qwen | 0.350 | 0.450 | -0.100 | 0.576 | no |
| hallucination_rate | gemini | 0.100 | 0.150 | -0.050 | 0.752 | yes |
| hallucination_rate | claude | 0.350 | 0.225 | +0.125 | 0.129 | no |
| hallucination_rate | gpt | 0.400 | 0.550 | -0.150 | 0.120 | yes |
| hallucination_rate | qwen | 0.475 | 0.675 | -0.200 | 0.080 | yes |
| loop_rate | gemini | 0.000 | 0.000 | +0.000 | 1.000 | no |
| loop_rate | claude | 0.125 | 0.100 | +0.025 | 1.000 | no |
| loop_rate | gpt | 0.000 | 0.000 | +0.000 | 1.000 | no |
| loop_rate | qwen | 0.025 | 0.000 | +0.025 | 1.000 | no |
| goal_completion_rate | gemini | 0.500 | 0.500 | +0.000 | 1.000 | no |
| goal_completion_rate | claude | 0.500 | 0.500 | +0.000 | 1.000 | no |
| goal_completion_rate | gpt | 0.000 | 0.000 | +0.000 | 1.000 | no |
| goal_completion_rate | qwen | 0.200 | 0.000 | +0.200 | 0.443 | yes |
| mean_latency_sec | gemini | 53.450 | 8.080 | +45.370 | 0.009 ✓ | no |
| mean_latency_sec | claude | 73.948 | 4.514 | +69.434 | 0.009 ✓ | no |
| mean_latency_sec | gpt | 73.393 | 3.468 | +69.925 | 0.009 ✓ | no |
| mean_latency_sec | qwen | 80.124 | 7.421 | +72.703 | 0.009 ✓ | no |
| mean_cost_usd | gemini | 0.002 | 0.009 | -0.007 | 0.009 ✓ | yes |
| mean_cost_usd | claude | 0.009 | 0.027 | -0.018 | 0.009 ✓ | yes |
| mean_cost_usd | gpt | 0.005 | 0.018 | -0.013 | 0.009 ✓ | yes |
| mean_cost_usd | qwen | 0.000 | 0.000 | +0.000 | 1.000 | no |
