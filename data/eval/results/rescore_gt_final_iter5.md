# Re-score with old vs new GT (v3 scorer) — old = fcfa184, new = working tree

Files: 2. Metrics per (group, model, backend): step matches and hallucination flags summed over scenarios × steps × replicates.

| group | model | backend | n steps | step_acc old → new | Δpp | hall rate old → new | Δpp |
|---|---|---|---|---|---|---|---|
| dev | gemini | full_system | 32 | 0.875 → 0.875 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev | gemini | no_rag | 32 | 0.719 → 0.719 | +0.0 | 0.031 → 0.031 | +0.0 |
| dev | gemini | vanilla_budget | 32 | 0.719 → 0.719 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev | gemini | vanilla_vector | 32 | 0.781 → 0.781 | +0.0 | 0.062 → 0.062 | +0.0 |

## Flipped step results (0)

| group | model | backend | file | scenario | step | match old→new | hall old→new | response |
|---|---|---|---|---|---|---|---|---|
