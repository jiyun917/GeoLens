# Re-score of archived logs with scorer v2 / v3 — qgis_pilot

Files: 5. v2 re-implementation vs stored matched/hallucinated: 0 mismatches / 120 steps.

v3 = ASCII word boundary in step patterns + quote-independent hallucination extractor. v3_think = v3 + unclosed <think> blocks dropped (affects Qwen only). Values are macro means over replicates (%), Δ = variant − v2.

| model | backend | n | StepAcc v2 | v3 | Δ | v3_think | Δ | Hall v2 | v3 | Δ | v3_think | Δ | Loop v2 | v3_think |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini | full_system | 5 | 57.5 | 87.5 | +30.0 | 87.5 | +30.0 | 12.5 | 0.0 | -12.5 | 0.0 | -12.5 | 0.0 | 0.0 |
| gemini | no_rag | 5 | 62.5 | 82.5 | +20.0 | 82.5 | +20.0 | 10.0 | 0.0 | -10.0 | 0.0 | -10.0 | 0.0 | 0.0 |
| gemini | vanilla_vector | 5 | 62.5 | 82.5 | +20.0 | 82.5 | +20.0 | 17.5 | 5.0 | -12.5 | 5.0 | -12.5 | 0.0 | 0.0 |

## full_system vs vanilla_vector direction (step_acc / hall)

| model | v2 | v3 | v3_think |
|---|---|---|---|
| gemini | acc 57.5 vs 62.5 (vanilla); hall 12.5 vs 17.5 (full) | acc 87.5 vs 82.5 (full); hall 0.0 vs 5.0 (full) | acc 87.5 vs 82.5 (full); hall 0.0 vs 5.0 (full) |
