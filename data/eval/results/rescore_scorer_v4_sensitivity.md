# Scorer v4 sensitivity on the v3 confirmatory results (re-score only; the signed verdict is unchanged)

v4 = v3 + '…'→'...' before step matching + numeric goal values never counted as hallucinated elements. Values = mean over 10 replicates of the replicate-level (scenario-mean) metric.

## QGIS test set (tag v3_qgis)

| model | backend | step_acc v3 | step_acc v4 | Δ | hall v3 | hall v4 | Δ |
|---|---|---|---|---|---|---|---|
| gemini | no_rag | 1.000 | 1.000 | +0.000 | 0.125 | 0.125 | +0.000 |
| gemini | vanilla_vector | 1.000 | 1.000 | +0.000 | 0.163 | 0.125 | -0.038 |
| gemini | vanilla_budget | 0.988 | 0.988 | +0.000 | 0.138 | 0.125 | -0.013 |
| gemini | graph_only | 1.000 | 1.000 | +0.000 | 0.125 | 0.113 | -0.012 |
| gemini | vision_only | 0.988 | 0.988 | +0.000 | 0.138 | 0.125 | -0.013 |
| gemini | state_path | 0.975 | 0.975 | +0.000 | 0.125 | 0.125 | +0.000 |
| gemini | full_system | 1.000 | 1.000 | +0.000 | 0.125 | 0.125 | +0.000 |
| claude | no_rag | 1.000 | 1.000 | +0.000 | 0.350 | 0.125 | -0.225 |
| claude | vanilla_vector | 0.875 | 1.000 | +0.125 | 0.275 | 0.125 | -0.150 |
| claude | vanilla_budget | 0.875 | 1.000 | +0.125 | 0.225 | 0.125 | -0.100 |
| claude | graph_only | 0.887 | 1.000 | +0.113 | 0.125 | 0.125 | +0.000 |
| claude | vision_only | 0.975 | 1.000 | +0.025 | 0.150 | 0.125 | -0.025 |
| claude | state_path | 0.963 | 1.000 | +0.037 | 0.125 | 0.125 | +0.000 |
| claude | full_system | 0.887 | 1.000 | +0.113 | 0.350 | 0.125 | -0.225 |
| gpt | no_rag | 0.988 | 0.988 | +0.000 | 0.125 | 0.125 | +0.000 |
| gpt | vanilla_vector | 0.912 | 0.938 | +0.025 | 0.125 | 0.125 | +0.000 |
| gpt | vanilla_budget | 0.950 | 1.000 | +0.050 | 0.125 | 0.125 | +0.000 |
| gpt | graph_only | 0.963 | 1.000 | +0.037 | 0.125 | 0.125 | +0.000 |
| gpt | vision_only | 1.000 | 1.000 | +0.000 | 0.125 | 0.125 | +0.000 |
| gpt | state_path | 1.000 | 1.000 | +0.000 | 0.125 | 0.125 | +0.000 |
| gpt | full_system | 0.838 | 0.838 | +0.000 | 0.125 | 0.125 | +0.000 |

Primary comparisons under v4 (QGIS test set): gemini: full−vb step +0.012 / hall +0.000, full−vv step +0.000 / hall +0.000; claude: full−vb step +0.000 / hall +0.000, full−vv step +0.000 / hall +0.000; gpt: full−vb step -0.162 / hall +0.000, full−vv step -0.100 / hall +0.000

## OpendTect dev set (tag v3)

| model | backend | step_acc v3 | step_acc v4 | Δ | hall v3 | hall v4 | Δ |
|---|---|---|---|---|---|---|---|
| gemini | no_rag | 0.733 | 0.733 | +0.000 | 0.029 | 0.029 | +0.000 |
| gemini | vanilla_vector | 0.817 | 0.817 | +0.000 | 0.033 | 0.033 | +0.000 |
| gemini | vanilla_budget | 0.821 | 0.821 | +0.000 | 0.021 | 0.021 | +0.000 |
| gemini | graph_only | 0.787 | 0.787 | +0.000 | 0.017 | 0.017 | +0.000 |
| gemini | vision_only | 0.783 | 0.783 | +0.000 | 0.025 | 0.025 | +0.000 |
| gemini | state_path | 0.804 | 0.804 | +0.000 | 0.033 | 0.033 | +0.000 |
| gemini | full_system | 0.912 | 0.912 | +0.000 | 0.029 | 0.029 | +0.000 |
| claude | no_rag | 0.875 | 0.875 | +0.000 | 0.050 | 0.050 | +0.000 |
| claude | vanilla_vector | 0.875 | 0.875 | +0.000 | 0.042 | 0.042 | +0.000 |
| claude | vanilla_budget | 0.875 | 0.875 | +0.000 | 0.042 | 0.042 | +0.000 |
| claude | graph_only | 0.875 | 0.875 | +0.000 | 0.042 | 0.042 | +0.000 |
| claude | vision_only | 0.875 | 0.875 | +0.000 | 0.046 | 0.046 | +0.000 |
| claude | state_path | 0.850 | 0.850 | +0.000 | 0.042 | 0.042 | +0.000 |
| claude | full_system | 1.000 | 1.000 | +0.000 | 0.042 | 0.042 | +0.000 |
| gpt | no_rag | 0.708 | 0.708 | +0.000 | 0.050 | 0.050 | +0.000 |
| gpt | vanilla_vector | 0.767 | 0.767 | +0.000 | 0.046 | 0.046 | +0.000 |
| gpt | vanilla_budget | 0.725 | 0.725 | +0.000 | 0.042 | 0.042 | +0.000 |
| gpt | graph_only | 0.854 | 0.854 | +0.000 | 0.042 | 0.042 | +0.000 |
| gpt | vision_only | 0.783 | 0.783 | +0.000 | 0.046 | 0.046 | +0.000 |
| gpt | state_path | 0.908 | 0.908 | +0.000 | 0.058 | 0.058 | +0.000 |
| gpt | full_system | 0.804 | 0.804 | +0.000 | 0.104 | 0.104 | +0.000 |

Primary comparisons under v4 (OpendTect dev set): gemini: full−vb step +0.092 / hall +0.008, full−vv step +0.096 / hall -0.004; claude: full−vb step +0.125 / hall +0.000, full−vv step +0.125 / hall +0.000; gpt: full−vb step +0.079 / hall +0.062, full−vv step +0.037 / hall +0.058

