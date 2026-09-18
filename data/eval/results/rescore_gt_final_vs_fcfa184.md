# Re-score with old vs new GT (v3 scorer) — old = fcfa184, new = working tree

Files: 27. Metrics per (group, model, backend): step matches and hallucination flags summed over scenarios × steps × replicates.

| group | model | backend | n steps | step_acc old → new | Δpp | hall rate old → new | Δpp |
|---|---|---|---|---|---|---|---|
| dev_iter0 | gemini | full_system | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter0 | gemini | no_rag | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter0 | gemini | vanilla_budget | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter0 | gemini | vanilla_vector | 16 | 0.688 → 0.688 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter1 | gemini | full_system | 16 | 0.938 → 0.938 | +0.0 | 0.000 → 0.000 | +0.0 |
| dev_iter1 | gemini | no_rag | 16 | 0.750 → 0.750 | +0.0 | 0.000 → 0.000 | +0.0 |
| dev_iter1 | gemini | vanilla_budget | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter1 | gemini | vanilla_vector | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | full_system | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | no_rag | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | vanilla_budget | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | vanilla_vector | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gemini | full_system | 32 | 0.781 → 0.781 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gemini | no_rag | 32 | 0.656 → 0.656 | +0.0 | 0.031 → 0.031 | +0.0 |
| dev_iter4 | gemini | vanilla_budget | 32 | 0.719 → 0.719 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gemini | vanilla_vector | 32 | 0.719 → 0.719 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | full_system | 16 | 0.875 → 0.875 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | no_rag | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | vanilla_budget | 16 | 0.688 → 0.688 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | vanilla_vector | 16 | 0.875 → 0.875 | +0.0 | 0.062 → 0.062 | +0.0 |
| latency_baseline | ? | full_system | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| latency_baseline | ? | vanilla_budget | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| latency_baseline | ? | vanilla_vector | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| unified4 | claude | full_system | 80 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | claude | graph_only | 80 | 0.787 → 0.787 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | claude | no_rag | 80 | 0.812 → 0.812 | +0.0 | 0.087 → 0.087 | +0.0 |
| unified4 | claude | state_path | 80 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | claude | vanilla_vector | 80 | 0.812 → 0.812 | +0.0 | 0.075 → 0.075 | +0.0 |
| unified4 | claude | vision_only | 80 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | gemini | full_system | 80 | 0.838 → 0.838 | +0.0 | 0.025 → 0.025 | +0.0 |
| unified4 | gemini | graph_only | 80 | 0.800 → 0.800 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | gemini | no_rag | 80 | 0.738 → 0.738 | +0.0 | 0.025 → 0.025 | +0.0 |
| unified4 | gemini | state_path | 80 | 0.887 → 0.887 | +0.0 | 0.025 → 0.025 | +0.0 |
| unified4 | gemini | vanilla_vector | 80 | 0.750 → 0.750 | +0.0 | 0.050 → 0.050 | +0.0 |
| unified4 | gemini | vision_only | 80 | 0.875 → 0.875 | +0.0 | 0.037 → 0.037 | +0.0 |
| unified4 | gpt | full_system | 80 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | gpt | graph_only | 80 | 0.787 → 0.787 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | gpt | no_rag | 80 | 0.688 → 0.688 | +0.0 | 0.075 → 0.075 | +0.0 |
| unified4 | gpt | state_path | 80 | 0.800 → 0.800 | +0.0 | 0.075 → 0.075 | +0.0 |
| unified4 | gpt | vanilla_vector | 80 | 0.775 → 0.775 | +0.0 | 0.087 → 0.087 | +0.0 |
| unified4 | gpt | vision_only | 80 | 0.662 → 0.662 | +0.0 | 0.125 → 0.125 | +0.0 |
| unified4 | qwen | full_system | 80 | 0.487 → 0.487 | +0.0 | 0.237 → 0.237 | +0.0 |
| unified4 | qwen | graph_only | 80 | 0.487 → 0.487 | +0.0 | 0.300 → 0.300 | +0.0 |
| unified4 | qwen | no_rag | 80 | 0.475 → 0.475 | +0.0 | 0.212 → 0.212 | +0.0 |
| unified4 | qwen | state_path | 80 | 0.588 → 0.588 | +0.0 | 0.263 → 0.263 | +0.0 |
| unified4 | qwen | vanilla_vector | 80 | 0.487 → 0.487 | +0.0 | 0.438 → 0.438 | +0.0 |
| unified4 | qwen | vision_only | 80 | 0.575 → 0.575 | +0.0 | 0.388 → 0.388 | +0.0 |

## Flipped step results (0)

| group | model | backend | file | scenario | step | match old→new | hall old→new | response |
|---|---|---|---|---|---|---|---|---|
