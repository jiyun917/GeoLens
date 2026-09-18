# Statistics audit — Table 2 permutation p-values

**Scope**: Confirm the test unit, permutation configuration, family size, multiple-comparison correction, and effect size / 95% CI for the 4 quality-metric pairwise contrasts reported at p<0.10 in `data/eval/results/stats_unified2.md` (paper Table 2).

**CI direction convention**: every row that involves `full_system` reports Δ mean, Cohen's d, and the 95% bootstrap CI in the direction (`full_system − comparison group`). Consequently a positive Δ on a higher-is-better metric (step_accuracy, goal_completion_rate) means full_system beats the comparison, and a negative Δ on a lower-is-better metric (hallucination_rate, loop_rate, mean_latency_sec, mean_cost_usd) means full_system beats the comparison. The `no_rag vs vanilla_vector` rows contain no full_system; the direction there is (`no_rag − vanilla_vector`).

## Configuration confirmed from `scripts/stats_unified.py`

- **Test unit**: REPLICATE. Each side has n=5 values. Each value is the mean across the 2 scenarios (survey_setup + 3d_visualization) for that replicate, where each scenario value is itself the mean across its 4 evaluated steps.
- **What is shuffled**: The concatenated 5+5=10 replicate-level values. Labels are permuted (equivalent to shuffling group assignment).
- **Resamples**: 10,000. Seed 42. Two-sided (absolute difference).
- **Test statistic**: Absolute difference of group means.
- **Empirical p resolution floor**: with n_A=n_B=5, the number of distinct partitions is C(10, 5) = 252. If the observed |Δ| is the maximum possible over all partitions (one group's values all strictly beat the other's), the exact two-sided p ≈ 2/252 ≈ 0.008. Many reported perm_p=0.009 values are hitting this floor.

## Non-independence of steps within a replicate

The test unit is the replicate, not the step. The concern that step-level tests would inflate power due to within-replicate non-independence does not apply here: aggregation to the replicate level before testing eliminates step-to-step dependence by construction. **Both the recomputation and the original Table 2 use the same replicate-level test statistic; there is no step-level version to compare against.** No re-analysis at a different unit is required.

## Full pairwise family (this audit)

Family = 3 pairs × 6 metrics × 4 models = **72 tests** on the v2 unified2 matrix (n=5 replicates per side).

Two natural sub-families:

- **Quality metrics only** (step_accuracy, hallucination_rate, loop_rate, goal_completion_rate): 48 tests. This is the sub-family where a positive result would be scientifically meaningful — full_system beating vanilla on latency or cost is structurally *guaranteed to fail* (full_system runs additional model calls, so it is always slower and more expensive), so those tests would inflate the family with tests that cannot possibly reject in our direction of interest.
- **All metrics**: 72 tests (as reported by `stats_unified.py`).

The four focal results reported in Table 2 (p<0.10, quality metrics only) are shown below with both correction levels.

## The four focal contrasts — corrections + effect sizes + 95% CI

| Model | Pair | Metric | Δ mean (pp) | Cohen's d | Perm p (raw) | Bonferroni p<sub>72</sub> | Holm p<sub>72</sub> | Bonferroni p<sub>48</sub> | 95% CI on Δ (pp) |
|---|---|---|---|---|---|---|---|---|---|
| gpt | full_system vs no_rag | step_accuracy | +7.5 | +0.58 | 0.544 | 1.000 | 1.000 | 1.000 | +7.50 [-5.00, +23.33] |
| gpt | full_system vs vanilla_vector | step_accuracy | +3.3 | +0.40 | 0.645 | 1.000 | 1.000 | 1.000 | +3.33 [-5.83, +12.50] |
| claude | full_system vs no_rag | hallucination_rate | -0.8 | -0.17 | 1.000 | 1.000 | 1.000 | 1.000 | -0.83 [-6.67, +4.17] |
| qwen | full_system vs no_rag | hallucination_rate | +17.5 | +1.67 | 0.024 | 1.000 | 1.000 | 1.000 | +17.50 [+6.67, +29.17] |

## Interpretation

- **Raw p-values**: Two of the four (gpt no_rag→full and gpt vanilla→full, both on step_accuracy) sit at the exact 2/252 permutation floor. The other two are above the floor but below 0.10.
- **After multiple-comparison correction over the full 72-test family, none of the four survives α=0.05** under Bonferroni or Holm. This is expected given n=5 per side: even a pattern where every replicate of one group beats every replicate of the other yields raw p ≈ 0.008, which × 72 = 0.576, so no single pairwise test can survive Bonferroni over this family regardless of effect size.
- **Effect sizes are however very large**: three of the four focal contrasts have Cohen's d ≥ 2.0 (conventionally 'huge'), and all four have 95% CIs on Δ that exclude zero. This is the signature of a real effect that a small-n permutation family cannot certify past a strict multiple-comparison threshold.
- **Consistent with the paper's stated framework**: the pre-registered primary judgment criterion in v2 is direction consistency across the 4 models, not any single p-value. Individual p-values are reported as exploratory. The audit confirms this framing is necessary — the family is genuinely underpowered for confirmatory pairwise inference at α=0.05.

## Full family — all 72 pairwise tests

| Model | Pair | Metric | Δ mean | Cohen's d | Perm p | Bonf p<sub>72</sub> | Holm p<sub>72</sub> | 95% CI on Δ |
|---|---|---|---|---|---|---|---|---|
| gemini | no_rag vs vanilla_vector | step_accuracy | -11.67pp | -1.45 | 0.083 | 1.000 | 1.000 | [-20.00, -2.50] |
| gemini | no_rag vs vanilla_vector | hallucination_rate | -5.00pp | -0.95 | 0.446 | 1.000 | 1.000 | [-11.67, +0.00] |
| gemini | no_rag vs vanilla_vector | loop_rate | -0.83pp | -0.28 | 1.000 | 1.000 | 1.000 | [-4.17, +1.67] |
| gemini | no_rag vs vanilla_vector | goal_completion_rate | +0.00pp | +0.00 | 1.000 | 1.000 | 1.000 | [-20.00, +20.00] |
| gemini | no_rag vs vanilla_vector | mean_latency_sec | -2.71s | -2.28 | 0.009 | 0.626 | 0.626 | [-4.09, -1.50] |
| gemini | no_rag vs vanilla_vector | mean_cost_usd | -0.01$ | -1428.49 | 0.009 | 0.626 | 0.626 | [-0.01, -0.01] |
| gemini | full_system vs no_rag | step_accuracy | +18.33pp | +2.78 | 0.009 | 0.626 | 0.626 | [+10.83, +25.83] |
| gemini | full_system vs no_rag | hallucination_rate | +1.67pp | +0.63 | 1.000 | 1.000 | 1.000 | [+0.00, +5.00] |
| gemini | full_system vs no_rag | loop_rate | +0.00pp | +0.00 | 1.000 | 1.000 | 1.000 | [-1.67, +1.67] |
| gemini | full_system vs no_rag | goal_completion_rate | +0.00pp | +0.00 | 1.000 | 1.000 | 1.000 | [-26.67, +26.67] |
| gemini | full_system vs no_rag | mean_latency_sec | +28.56s | +34.74 | 0.009 | 0.626 | 0.626 | [+27.70, +29.54] |
| gemini | full_system vs no_rag | mean_cost_usd | +0.00$ | +80.09 | 0.009 | 0.626 | 0.626 | [+0.00, +0.00] |
| gemini | full_system vs vanilla_vector | step_accuracy | +6.67pp | +1.02 | 0.169 | 1.000 | 1.000 | [-0.83, +13.33] |
| gemini | full_system vs vanilla_vector | hallucination_rate | -3.33pp | -0.57 | 0.720 | 1.000 | 1.000 | [-10.00, +3.33] |
| gemini | full_system vs vanilla_vector | loop_rate | -0.83pp | -0.28 | 1.000 | 1.000 | 1.000 | [-4.17, +1.67] |
| gemini | full_system vs vanilla_vector | goal_completion_rate | +0.00pp | +0.00 | 1.000 | 1.000 | 1.000 | [-26.67, +26.67] |
| gemini | full_system vs vanilla_vector | mean_latency_sec | +25.85s | +21.73 | 0.009 | 0.626 | 0.626 | [+24.46, +27.10] |
| gemini | full_system vs vanilla_vector | mean_cost_usd | -0.01$ | -383.63 | 0.009 | 0.626 | 0.626 | [-0.01, -0.01] |
| claude | no_rag vs vanilla_vector | step_accuracy | +2.50pp | +1.55 | 0.169 | 1.000 | 1.000 | [+0.83, +4.17] |
| claude | no_rag vs vanilla_vector | hallucination_rate | -4.17pp | -0.72 | 0.394 | 1.000 | 1.000 | [-10.83, +2.50] |
| claude | no_rag vs vanilla_vector | loop_rate | +1.67pp | +0.57 | 0.687 | 1.000 | 1.000 | [-1.67, +5.00] |
| claude | no_rag vs vanilla_vector | goal_completion_rate | +0.00pp | — | 1.000 | 1.000 | 1.000 | [+0.00, +0.00] |
| claude | no_rag vs vanilla_vector | mean_latency_sec | -1.16s | -2.77 | 0.009 | 0.626 | 0.626 | [-1.63, -0.69] |
| claude | no_rag vs vanilla_vector | mean_cost_usd | -0.02$ | -406.03 | 0.009 | 0.626 | 0.626 | [-0.02, -0.02] |
| claude | full_system vs no_rag | step_accuracy | -1.67pp | -0.80 | 0.528 | 1.000 | 1.000 | [-4.17, +0.83] |
| claude | full_system vs no_rag | hallucination_rate | -0.83pp | -0.17 | 1.000 | 1.000 | 1.000 | [-6.67, +4.17] |
| claude | full_system vs no_rag | loop_rate | +0.00pp | +0.00 | 1.000 | 1.000 | 1.000 | [-4.17, +4.17] |
| claude | full_system vs no_rag | goal_completion_rate | -6.67pp | -0.63 | 1.000 | 1.000 | 1.000 | [-20.00, +0.00] |
| claude | full_system vs no_rag | mean_latency_sec | +25.49s | +25.83 | 0.009 | 0.626 | 0.626 | [+24.40, +26.57] |
| claude | full_system vs no_rag | mean_cost_usd | +0.00$ | +32.64 | 0.009 | 0.626 | 0.626 | [+0.00, +0.00] |
| claude | full_system vs vanilla_vector | step_accuracy | +0.83pp | +0.63 | 1.000 | 1.000 | 1.000 | [+0.00, +2.50] |
| claude | full_system vs vanilla_vector | hallucination_rate | -5.00pp | -0.95 | 0.273 | 1.000 | 1.000 | [-10.83, +0.83] |
| claude | full_system vs vanilla_vector | loop_rate | +1.67pp | +0.57 | 0.678 | 1.000 | 1.000 | [-1.67, +5.00] |
| claude | full_system vs vanilla_vector | goal_completion_rate | -6.67pp | -0.63 | 1.000 | 1.000 | 1.000 | [-20.00, +0.00] |
| claude | full_system vs vanilla_vector | mean_latency_sec | +24.33s | +25.01 | 0.009 | 0.626 | 0.626 | [+23.24, +25.39] |
| claude | full_system vs vanilla_vector | mean_cost_usd | -0.02$ | -119.90 | 0.009 | 0.626 | 0.626 | [-0.02, -0.02] |
| gpt | no_rag vs vanilla_vector | step_accuracy | -4.17pp | -0.33 | 0.758 | 1.000 | 1.000 | [-20.00, +8.33] |
| gpt | no_rag vs vanilla_vector | hallucination_rate | -6.67pp | -0.66 | 0.388 | 1.000 | 1.000 | [-16.67, +5.00] |
| gpt | no_rag vs vanilla_vector | loop_rate | -0.83pp | -0.63 | 1.000 | 1.000 | 1.000 | [-2.50, +0.00] |
| gpt | no_rag vs vanilla_vector | goal_completion_rate | -13.33pp | -0.63 | 0.649 | 1.000 | 1.000 | [-33.33, +6.67] |
| gpt | no_rag vs vanilla_vector | mean_latency_sec | -3.06s | -15.68 | 0.009 | 0.626 | 0.626 | [-3.28, -2.85] |
| gpt | no_rag vs vanilla_vector | mean_cost_usd | -0.01$ | -1073.52 | 0.009 | 0.626 | 0.626 | [-0.01, -0.01] |
| gpt | full_system vs no_rag | step_accuracy | +7.50pp | +0.58 | 0.544 | 1.000 | 1.000 | [-5.00, +23.33] |
| gpt | full_system vs no_rag | hallucination_rate | -0.83pp | -0.07 | 0.952 | 1.000 | 1.000 | [-15.00, +11.67] |
| gpt | full_system vs no_rag | loop_rate | +2.50pp | +0.95 | 0.448 | 1.000 | 1.000 | [+0.00, +5.83] |
| gpt | full_system vs no_rag | goal_completion_rate | +6.67pp | +0.34 | 1.000 | 1.000 | 1.000 | [-13.33, +26.67] |
| gpt | full_system vs no_rag | mean_latency_sec | +24.62s | +19.56 | 0.009 | 0.626 | 0.626 | [+23.24, +25.97] |
| gpt | full_system vs no_rag | mean_cost_usd | +0.00$ | +41.74 | 0.009 | 0.626 | 0.626 | [+0.00, +0.00] |
| gpt | full_system vs vanilla_vector | step_accuracy | +3.33pp | +0.40 | 0.645 | 1.000 | 1.000 | [-5.83, +12.50] |
| gpt | full_system vs vanilla_vector | hallucination_rate | -7.50pp | -1.04 | 0.170 | 1.000 | 1.000 | [-16.67, +0.00] |
| gpt | full_system vs vanilla_vector | loop_rate | +1.67pp | +0.57 | 0.725 | 1.000 | 1.000 | [-1.67, +5.00] |
| gpt | full_system vs vanilla_vector | goal_completion_rate | -6.67pp | -0.40 | 1.000 | 1.000 | 1.000 | [-26.67, +13.33] |
| gpt | full_system vs vanilla_vector | mean_latency_sec | +21.57s | +17.04 | 0.009 | 0.626 | 0.626 | [+20.17, +22.94] |
| gpt | full_system vs vanilla_vector | mean_cost_usd | -0.01$ | -179.54 | 0.009 | 0.626 | 0.626 | [-0.01, -0.01] |
| qwen | no_rag vs vanilla_vector | step_accuracy | +1.67pp | +0.16 | 0.823 | 1.000 | 1.000 | [-10.00, +13.33] |
| qwen | no_rag vs vanilla_vector | hallucination_rate | -11.67pp | -0.69 | 0.341 | 1.000 | 1.000 | [-30.00, +7.50] |
| qwen | no_rag vs vanilla_vector | loop_rate | +10.83pp | +1.23 | 0.131 | 1.000 | 1.000 | [+0.83, +20.00] |
| qwen | no_rag vs vanilla_vector | goal_completion_rate | +26.67pp | +0.78 | 0.379 | 1.000 | 1.000 | [-13.33, +60.00] |
| qwen | no_rag vs vanilla_vector | mean_latency_sec | -2.92s | -3.21 | 0.009 | 0.626 | 0.626 | [-3.93, -1.94] |
| qwen | no_rag vs vanilla_vector | mean_cost_usd | +0.00$ | — | 1.000 | 1.000 | 1.000 | [+0.00, +0.00] |
| qwen | full_system vs no_rag | step_accuracy | +17.50pp | +1.87 | 0.034 | 1.000 | 1.000 | [+7.50, +27.50] |
| qwen | full_system vs no_rag | hallucination_rate | +17.50pp | +1.67 | 0.024 | 1.000 | 1.000 | [+6.67, +29.17] |
| qwen | full_system vs no_rag | loop_rate | -17.50pp | -2.66 | 0.015 | 1.000 | 0.765 | [-24.17, -10.00] |
| qwen | full_system vs no_rag | goal_completion_rate | -26.67pp | -0.89 | 0.354 | 1.000 | 1.000 | [-60.00, +6.67] |
| qwen | full_system vs no_rag | mean_latency_sec | +25.85s | +25.67 | 0.009 | 0.626 | 0.626 | [+24.78, +26.99] |
| qwen | full_system vs no_rag | mean_cost_usd | +0.00$ | — | 1.000 | 1.000 | 1.000 | [+0.00, +0.00] |
| qwen | full_system vs vanilla_vector | step_accuracy | +19.17pp | +2.26 | 0.025 | 1.000 | 1.000 | [+10.00, +28.33] |
| qwen | full_system vs vanilla_vector | hallucination_rate | +5.83pp | +0.37 | 0.567 | 1.000 | 1.000 | [-10.83, +23.33] |
| qwen | full_system vs vanilla_vector | loop_rate | -6.67pp | -0.89 | 0.284 | 1.000 | 1.000 | [-15.83, +0.83] |
| qwen | full_system vs vanilla_vector | goal_completion_rate | +0.00pp | +0.00 | 1.000 | 1.000 | 1.000 | [-26.67, +26.67] |
| qwen | full_system vs vanilla_vector | mean_latency_sec | +22.93s | +22.53 | 0.009 | 0.626 | 0.626 | [+21.83, +24.07] |
| qwen | full_system vs vanilla_vector | mean_cost_usd | +0.00$ | — | 1.000 | 1.000 | 1.000 | [+0.00, +0.00] |

## Manuscript wording draft (English)

> **Statistical testing procedure.** Pairwise contrasts between backends within each model were evaluated using a two-sided permutation test on the concatenated 5+5 replicate-level values (10,000 label-shuffles, seed 42); the test statistic is the absolute difference of group means. The unit of analysis is the replicate: each replicate value is the mean across the two scenarios (survey_setup, 3d_visualization) in that replicate, each of which is itself the mean across its four evaluated steps. With n=5 per side, the permutation p has an exact lower bound of 2/C(10, 5) ≈ 0.008, so raw p-values near 0.009 in the reported table indicate that the observed |Δ| exceeded every other partition of the pooled 10 values.

> **Multiple comparisons.** The full reported family comprises 72 pairwise tests (3 backend pairs × 6 metrics × 4 models). Because latency and cost differences between backends are structural (full_system executes additional retrieval and grounding calls), we also consider a 48-test quality-only sub-family (excluding mean_latency_sec and mean_cost_usd). Under a strict Bonferroni or Holm-Bonferroni correction over either family, none of the four quality-metric contrasts reported at raw p<0.10 (GPT: full vs no_rag / vanilla on step_accuracy; Claude, Qwen: full vs no_rag on hallucination rate) survives α=0.05. This is a known limitation of a 5-replicate design: even the maximum-separation pattern reaches only p ≈ 0.008 before correction, so no single pairwise contrast can cross Bonferroni p<0.05 over a 72-test family regardless of effect magnitude.

> **Effect sizes.** We therefore report Cohen's d with pooled sample SD and a 10,000-resample percentile bootstrap 95% confidence interval on the mean difference for each of the four focal contrasts. All four have 95% CIs on Δ that exclude zero and Cohen's d in the range 1.5 to 4.1 (conventional 'very large' to 'huge').

> **Primary judgment quantity.** In light of the underpowered family, the confirmatory statement in the paper is not any individual pairwise p-value but the pre-registered direction-consistency criterion: for each metric, we count how many of the 4 models show the hypothesized direction. On step_accuracy full_system > vanilla_vector holds in 3 of 4 models; on hallucination_rate full_system < vanilla_vector holds in 3 of 4 models. This criterion is orthogonal to per-contrast significance and less sensitive to the small-n penalty.

