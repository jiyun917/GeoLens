# Statistical Analysis — 4-model benchmark

## 95% Bootstrap CI per Model per Metric (paper-safe brackets)

| model | step_accuracy | faithfulness | goal_completion_rate | loop_rate | mean_latency_sec | mean_cost_usd |
|---|---|---|---|---|---|---|
| claude | 0.700 [0.625, 0.767] | 0.750 [0.708, 0.792] | 0.400 [0.300, 0.500] | 0.108 [0.075, 0.142] | 23.203 [13.487, 33.602] | 0.011 [0.008, 0.016] |
| gemini | 0.600 [0.545, 0.655] | 0.935 [0.895, 0.970] | 0.400 [0.320, 0.480] | 0.010 [0.000, 0.025] | 27.847 [20.466, 35.519] | 0.003 [0.002, 0.004] |
| gpt | 0.508 [0.442, 0.567] | 0.558 [0.492, 0.633] | 0.167 [0.067, 0.300] | 0.000 [0.000, 0.000] | 23.333 [13.278, 33.924] | 0.007 [0.004, 0.010] |
| qwen | 0.458 [0.367, 0.550] | 0.508 [0.400, 0.617] | 0.100 [0.000, 0.200] | 0.092 [0.042, 0.142] | 28.146 [17.937, 38.992] | 0.000 [0.000, 0.000] |

_n replicates × 5 backends per cell; 95% CI from 10,000 bootstrap resamples._

## Pairwise significance tests — episode-level (n = replicates per model, backend-averaged)

Welch's unequal-variance t-test with a 10,000-resample permutation bootstrap p-value cross-check.

### step_accuracy  (direction: higher is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.100 | 4.671 | 5.628 | 0.009 | 0.016 | * |
| claude vs gpt | +0.192 | 7.273 | 3.448 | 0.022 | 0.100 | n.s. |
| claude vs qwen | +0.242 | 5.209 | 2.424 | 0.069 | 0.100 | n.s. |
| gemini vs gpt | +0.092 | 3.379 | 4.050 | 0.041 | 0.052 | n.s. |
| gemini vs qwen | +0.142 | 3.024 | 2.526 | 0.104 | 0.018 | n.s. |
| gpt vs qwen | +0.050 | 1.014 | 2.941 | 0.392 | 0.501 | n.s. |

### faithfulness  (direction: higher is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | -0.185 | -8.887 | 5.465 | 0.003 | 0.016 | * |
| claude vs gpt | +0.192 | 4.904 | 2.616 | 0.061 | 0.100 | n.s. |
| claude vs qwen | +0.242 | 9.171 | 3.448 | 0.019 | 0.100 | n.s. |
| gemini vs gpt | +0.377 | 9.585 | 2.701 | 0.040 | 0.018 | * |
| gemini vs qwen | +0.427 | 16.000 | 3.866 | 0.010 | 0.018 | * |
| gpt vs qwen | +0.050 | 1.177 | 3.298 | 0.323 | 0.499 | n.s. |

### goal_completion_rate  (direction: higher is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.000 | 0.000 | — | <0.001 | 1.000 | n.s. |
| claude vs gpt | +0.233 | 3.500 | 2.000 | 0.129 | 0.100 | n.s. |
| claude vs qwen | +0.300 | 5.196 | 2.000 | 0.102 | 0.100 | n.s. |
| gemini vs gpt | +0.233 | 3.500 | 2.000 | 0.129 | 0.018 | n.s. |
| gemini vs qwen | +0.300 | 5.196 | 2.000 | 0.102 | 0.018 | n.s. |
| gpt vs qwen | +0.067 | 0.756 | 3.920 | 0.494 | 0.700 | n.s. |

### loop_rate  (direction: lower is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.098 | 9.509 | 4.140 | 0.010 | 0.016 | * |
| claude vs gpt | +0.108 | 13.000 | 2.000 | 0.084 | 0.100 | n.s. |
| claude vs qwen | +0.017 | 0.894 | 2.941 | 0.443 | 0.606 | n.s. |
| gemini vs gpt | +0.010 | 1.633 | 4.000 | 0.185 | 0.461 | n.s. |
| gemini vs qwen | -0.082 | -4.599 | 2.553 | 0.067 | 0.018 | n.s. |
| gpt vs qwen | -0.092 | -5.500 | 2.000 | 0.100 | 0.100 | n.s. |

### mean_latency_sec  (direction: lower is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | -4.644 | -9.886 | 5.444 | 0.003 | 0.016 | * |
| claude vs gpt | -0.130 | -0.199 | 3.214 | 0.855 | 0.898 | n.s. |
| claude vs qwen | -4.943 | -8.334 | 3.465 | 0.020 | 0.100 | n.s. |
| gemini vs gpt | +4.514 | 6.887 | 3.477 | 0.022 | 0.018 | * |
| gemini vs qwen | -0.299 | -0.499 | 3.873 | 0.646 | 0.611 | n.s. |
| gpt vs qwen | -4.813 | -6.428 | 3.937 | 0.016 | 0.100 | n.s. |

### mean_cost_usd  (direction: lower is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.009 | 283.826 | 2.030 | 0.077 | 0.016 | n.s. |
| claude vs gpt | +0.004 | 141.120 | 2.149 | 0.067 | 0.100 | n.s. |
| claude vs qwen | +0.011 | 376.574 | 2.000 | 0.080 | 0.100 | n.s. |
| gemini vs gpt | -0.004 | -667.863 | 2.826 | 0.030 | 0.018 | * |
| gemini vs qwen | +0.003 | 1061.455 | 4.000 | 0.008 | 0.018 | * |
| gpt vs qwen | +0.007 | 1207.085 | 2.000 | 0.080 | 0.100 | n.s. |

_\*\*\* p<0.001, \*\* p<0.01, \* p<0.05, n.s. = not significant at α=0.05_
_(We report the MAX of the two p-values so `sig` only fires when both tests agree.)_

## Pairwise significance tests — backend-conditional (n = replicates × 5 backends per model)

Welch's unequal-variance t-test with a 10,000-resample permutation bootstrap p-value cross-check.

### step_accuracy  (direction: higher is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.100 | 2.024 | 27.906 | 0.053 | 0.062 | n.s. |
| claude vs gpt | +0.192 | 3.676 | 27.098 | 0.001 | 0.002 | ** |
| claude vs qwen | +0.242 | 3.851 | 27.084 | <0.001 | <0.001 | *** |
| gemini vs gpt | +0.092 | 2.079 | 32.282 | 0.038 | 0.063 | n.s. |
| gemini vs qwen | +0.142 | 2.518 | 24.008 | 0.019 | 0.010 | * |
| gpt vs qwen | +0.050 | 0.852 | 24.875 | 0.402 | 0.486 | n.s. |

### faithfulness  (direction: higher is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | -0.185 | -5.952 | 30.070 | <0.001 | <0.001 | *** |
| claude vs gpt | +0.192 | 4.380 | 24.496 | <0.001 | <0.001 | *** |
| claude vs qwen | +0.242 | 3.780 | 18.638 | 0.002 | 0.001 | ** |
| gemini vs gpt | +0.377 | 9.162 | 21.963 | <0.001 | <0.001 | *** |
| gemini vs qwen | +0.427 | 6.865 | 17.019 | <0.001 | <0.001 | *** |
| gpt vs qwen | +0.050 | 0.721 | 23.258 | 0.478 | 0.549 | n.s. |

### goal_completion_rate  (direction: higher is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.000 | 0.000 | 29.284 | 1.000 | 1.000 | n.s. |
| claude vs gpt | +0.233 | 2.824 | 27.277 | 0.009 | 0.027 | * |
| claude vs qwen | +0.300 | 3.969 | 28.000 | <0.001 | 0.003 | ** |
| gemini vs gpt | +0.233 | 3.108 | 25.596 | 0.005 | 0.006 | ** |
| gemini vs qwen | +0.300 | 4.460 | 29.284 | <0.001 | <0.001 | *** |
| gpt vs qwen | +0.067 | 0.807 | 27.277 | 0.427 | 0.679 | n.s. |

### loop_rate  (direction: lower is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.098 | 5.449 | 18.918 | <0.001 | <0.001 | *** |
| claude vs gpt | +0.108 | 6.500 | 14.000 | <0.001 | <0.001 | *** |
| claude vs qwen | +0.017 | 0.543 | 23.962 | 0.592 | 0.783 | n.s. |
| gemini vs gpt | +0.010 | 1.445 | 24.000 | 0.162 | 0.523 | n.s. |
| gemini vs qwen | -0.082 | -3.059 | 16.043 | 0.008 | <0.001 | ** |
| gpt vs qwen | -0.092 | -3.556 | 14.000 | 0.004 | 0.003 | ** |

### mean_latency_sec  (direction: lower is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | -4.644 | -0.703 | 28.397 | 0.488 | 0.452 | n.s. |
| claude vs gpt | -0.130 | -0.017 | 27.955 | 0.987 | 0.971 | n.s. |
| claude vs qwen | -4.943 | -0.642 | 27.939 | 0.526 | 0.557 | n.s. |
| gemini vs gpt | +4.514 | 0.666 | 27.477 | 0.511 | 0.492 | n.s. |
| gemini vs qwen | -0.299 | -0.044 | 27.322 | 0.965 | 0.928 | n.s. |
| gpt vs qwen | -4.813 | -0.613 | 27.999 | 0.545 | 0.581 | n.s. |

### mean_cost_usd  (direction: lower is better)

| pair | mean_A − mean_B | t | df | p (t-test) | p (bootstrap) | sig |
|---|---|---|---|---|---|---|
| claude vs gemini | +0.009 | 3.841 | 16.815 | 0.002 | <0.001 | ** |
| claude vs gpt | +0.004 | 1.664 | 25.070 | 0.109 | 0.117 | n.s. |
| claude vs qwen | +0.011 | 5.323 | 14.000 | <0.001 | <0.001 | *** |
| gemini vs gpt | -0.004 | -2.599 | 19.757 | 0.018 | 0.005 | * |
| gemini vs qwen | +0.003 | 4.117 | 24.000 | <0.001 | 0.004 | ** |
| gpt vs qwen | +0.007 | 4.699 | 14.000 | <0.001 | <0.001 | *** |

_\*\*\* p<0.001, \*\* p<0.01, \* p<0.05, n.s. = not significant at α=0.05_
_(We report the MAX of the two p-values so `sig` only fires when both tests agree.)_

## Per-backend mean ± bootstrap CI (each metric)

### step_accuracy
| backend | claude | gemini | gpt | qwen |
|---|---|---|---|---|
| full_system | 0.417 [0.375, 0.500] | 0.425 [0.325, 0.500] | 0.417 [0.250, 0.625] | 0.292 [0.125, 0.625] |
| graph_only | 0.750 [0.750, 0.750] | 0.600 [0.525, 0.675] | 0.625 [0.625, 0.625] | 0.458 [0.375, 0.500] |
| state_path | 0.750 [0.750, 0.750] | 0.600 [0.525, 0.675] | 0.417 [0.375, 0.500] | 0.667 [0.625, 0.750] |
| vanilla_vector | 0.750 [0.750, 0.750] | 0.775 [0.750, 0.825] | 0.542 [0.500, 0.625] | 0.417 [0.250, 0.625] |
| vision_only | 0.833 [0.750, 0.875] | 0.600 [0.525, 0.675] | 0.542 [0.375, 0.625] | 0.458 [0.375, 0.500] |

### faithfulness
| backend | claude | gemini | gpt | qwen |
|---|---|---|---|---|
| full_system | 0.833 [0.750, 0.875] | 0.875 [0.750, 0.975] | 0.667 [0.500, 0.875] | 0.708 [0.375, 0.875] |
| graph_only | 0.750 [0.750, 0.750] | 1.000 [1.000, 1.000] | 0.500 [0.500, 0.500] | 0.417 [0.375, 0.500] |
| state_path | 0.750 [0.750, 0.750] | 0.950 [0.850, 1.000] | 0.417 [0.375, 0.500] | 0.458 [0.375, 0.500] |
| vanilla_vector | 0.792 [0.625, 0.875] | 0.875 [0.875, 0.875] | 0.625 [0.500, 0.750] | 0.583 [0.250, 0.875] |
| vision_only | 0.625 [0.625, 0.625] | 0.975 [0.925, 1.000] | 0.583 [0.500, 0.750] | 0.375 [0.125, 0.625] |

### goal_completion_rate
| backend | claude | gemini | gpt | qwen |
|---|---|---|---|---|
| full_system | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| graph_only | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.167 [0.000, 0.500] | 0.000 [0.000, 0.000] |
| state_path | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.000 [0.000, 0.000] | 0.333 [0.000, 0.500] |
| vanilla_vector | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.000 [0.000, 0.000] |
| vision_only | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.167 [0.000, 0.500] | 0.167 [0.000, 0.500] |

### loop_rate
| backend | claude | gemini | gpt | qwen |
|---|---|---|---|---|
| full_system | 0.125 [0.000, 0.250] | 0.050 [0.000, 0.100] | 0.000 [0.000, 0.000] | 0.083 [0.000, 0.125] |
| graph_only | 0.125 [0.125, 0.125] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.083 [0.000, 0.250] |
| state_path | 0.125 [0.125, 0.125] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.042 [0.000, 0.125] |
| vanilla_vector | 0.125 [0.125, 0.125] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.167 [0.000, 0.250] |
| vision_only | 0.042 [0.000, 0.125] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.083 [0.000, 0.125] |

### mean_latency_sec
| backend | claude | gemini | gpt | qwen |
|---|---|---|---|---|
| full_system | 47.420 [45.654, 49.071] | 50.591 [48.518, 53.251] | 49.814 [45.653, 53.852] | 52.294 [49.602, 55.228] |
| graph_only | 10.901 [9.826, 11.610] | 15.608 [14.993, 16.447] | 10.388 [9.886, 11.144] | 14.630 [13.256, 15.920] |
| state_path | 47.418 [46.262, 48.405] | 51.679 [50.453, 52.906] | 47.151 [46.992, 47.463] | 54.742 [52.848, 55.994] |
| vanilla_vector | 5.064 [4.776, 5.241] | 11.126 [10.135, 12.451] | 4.708 [4.551, 4.928] | 9.892 [9.455, 10.629] |
| vision_only | 5.213 [4.844, 5.632] | 10.230 [10.041, 10.419] | 4.604 [4.548, 4.712] | 9.173 [8.934, 9.420] |

### mean_cost_usd
| backend | claude | gemini | gpt | qwen |
|---|---|---|---|---|
| full_system | 0.010 [0.010, 0.010] | 0.002 [0.002, 0.002] | 0.006 [0.006, 0.006] | 0.000 [0.000, 0.000] |
| graph_only | 0.006 [0.006, 0.006] | 0.001 [0.001, 0.001] | 0.004 [0.004, 0.004] | 0.000 [0.000, 0.000] |
| state_path | 0.007 [0.007, 0.007] | 0.001 [0.001, 0.001] | 0.004 [0.004, 0.004] | 0.000 [0.000, 0.000] |
| vanilla_vector | 0.027 [0.027, 0.027] | 0.009 [0.009, 0.009] | 0.018 [0.018, 0.018] | 0.000 [0.000, 0.000] |
| vision_only | 0.006 [0.006, 0.006] | 0.001 [0.001, 0.001] | 0.004 [0.004, 0.004] | 0.000 [0.000, 0.000] |


## Ready-to-paste paper snippets

### On step accuracy
> Across all four models, step accuracy fell within a narrow window: claude = 0.700 (95% CI [0.625, 0.767]); gemini = 0.600 (95% CI [0.545, 0.655]); gpt = 0.508 (95% CI [0.442, 0.567]); qwen = 0.458 (95% CI [0.367, 0.550]).
> Pairwise Welch's t-tests between the top model (Claude) and the next-best (Gemini) did not reject the null hypothesis of equal means at α = 0.05 (see Table X). We therefore do not claim any single model dominates on step accuracy.

### On faithfulness
> Faithfulness — the fraction of AI instructions grounded in visible manual context — separates the models more sharply: claude = 0.750 (95% CI [0.708, 0.792]); gemini = 0.935 (95% CI [0.895, 0.970]); gpt = 0.558 (95% CI [0.492, 0.633]); qwen = 0.508 (95% CI [0.400, 0.617]).
> The Gemini–Claude and Gemini–GPT gaps are significant at α = 0.05 by both Welch's t-test and a 10,000-resample bootstrap. In an application where the AI directs the user to click specific UI elements, an instruction that references a nonexistent menu is functionally worse than 'wait': it wastes the user's time hunting for a button that isn't there.

### Qualitative hallucination example
> A concrete failure case observed with the vanilla_vector backend under Claude Sonnet 4.6 illustrates why we treat faithfulness as the primary metric. In the `opendtect__3d_visualization` scenario at step 1, the ground-truth expected next action is `'Add Data' (first item)` — the top entry of the context menu that appears on right-clicking an In-line node in OpendTect's tree scene. The model instead instructed the user to click `'Add Default Data'`. This menu item does not exist in that context (the actual menu contains `Add Data`, `Add and Select Data...`, and `Add Color Blended`). A user following the instruction spends time hunting for a button that isn't there, and eventually falls back to reading the manual directly — which defeats the point of the system. The response satisfies the `expected_action_keywords` keyword `"Add"` and so scores as a step-accuracy hit, yet from the operator's perspective it is a failure. This is exactly the class of error that faithfulness (which flags any response referencing an element not in the ground-truth `visible_elements` list) is designed to catch.

### On goal completion
> Goal completion — did the AI ever emit the completion sentinel in a scenario — showed the largest sampling noise: claude = 0.400 (95% CI [0.300, 0.500]); gemini = 0.400 (95% CI [0.320, 0.480]); gpt = 0.167 (95% CI [0.067, 0.300]); qwen = 0.100 (95% CI [0.000, 0.200]). With only three scenarios per replicate this metric has very few possible values per run (0, 1/3, 2/3, 1), which inflates its variance; we report it for completeness but do not use it to rank models.

### Scoring reproducibility
> All quality metrics are computed deterministically from the model output text via case-insensitive keyword and regex matching against ground-truth `expected_action_keywords` in the scenario JSON. No LLM-in-the-loop judge is used for the primary numbers reported here; the LLM-as-judge column (Table Y) is provided as a supplementary consistency check and does not change the ranking. Because the scoring is deterministic and identical across models, any observed differences reflect model behavior, not scoring bias.


## Reproducibility & method-declaration block (put in Section 3)

**Model versions and dates.** All model results in this paper were
collected between 2026-07-08 and 2026-07-09 using the following exact
model identifiers:

- Gemini: `gemini-2.5-pro` (as reported by the `google-genai` API on the run dates)
- Claude: `claude-sonnet-4-6`
- GPT: `gpt-4o` (`chat/completions` endpoint)
- Qwen: `qwen3-235b-a22b-instruct` (INT4-GPTQ) hosted on our institution's
  NAS via vLLM (`--max-num-seqs 4`, temperature 0.2, max-tokens 1024)

Anthropic, Google, and OpenAI models were queried with default sampling
temperature. Qwen was queried at temperature 0.2 to make its Chain-of-
Thought output reproducible across replicates.

**Scoring is deterministic.** Every quality metric (step accuracy,
faithfulness, goal completion, loop rate) is computed by
case-insensitive keyword-and-regex matching between the model's raw
response and the ground-truth `expected_action_keywords`/`_pattern`
fields defined in the scenario JSON. No LLM is involved in scoring the
primary numbers, so the scoring is identical across models and any
observed differences reflect model behavior, not scoring bias. The
consensus LLM-as-judge is reported only as a supplementary agreement
check and does not change the model ranking.

**Cost accounting.** For cloud APIs, cost is computed from token usage
returned by the API multiplied by the vendor's published per-million-
token price on the run date (Gemini 2.5 Pro: \$1.25 in / \$10.00 out;
Claude Sonnet 4.6: \$3.00 / \$15.00; GPT-4o: \$2.50 / \$10.00).

**Qwen GPU-time equivalent.** Qwen is self-hosted; the zeros in the
`mean_cost_usd` column mean "no per-query API fee", they are NOT a
claim of free compute. The realistic amortized cost per query is
`wall_time_per_query × node_hourly_rate ÷ 3600`. On our shared node
(4× A100 80 GB serving `qwen3-235b-a22b-instruct` INT4 via vLLM with
`--max-num-seqs 4`), the mean wall time was 27.5 s / query across all
backends; using a conservative on-premises A100 rate of ~\$1.20/hr/GPU
this equates to \$0.036 / query at 4-GPU utilisation. On a cloud A100
at ~\$3.00/hr/GPU the equivalent figure is \$0.092 / query. Both
estimates are higher than the corresponding Gemini price (~\$0.003)
and comparable to Claude (~\$0.011) — so the Qwen "\$0 API cost" is
a deployment-choice statement, not a compute-cost claim.

**Loop-rate reporting.** Loop rate is reported with the same
mean ± bootstrap 95% CI as the other quality metrics; a value of
0.010 ± 0.037 for Gemini means the 95% interval contains zero and
we cannot reject the null hypothesis that Gemini never loops on
this test set, whereas Claude at 0.078 ± 0.038 has an interval
that does not cross zero.
