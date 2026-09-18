# Re-score of archived logs with scorer v2 / v3 — longctx

Files: 5. v2 re-implementation vs stored matched/hallucinated: 0 mismatches / 80 steps.

v3 = ASCII word boundary in step patterns + quote-independent hallucination extractor. v3_think = v3 + unclosed <think> blocks dropped (affects Qwen only). Values are macro means over replicates (%), Δ = variant − v2.

| model | backend | n | StepAcc v2 | v3 | Δ | v3_think | Δ | Hall v2 | v3 | Δ | v3_think | Δ | Loop v2 | v3_think |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini | long_context | 5 | 59.2 | 72.5 | +13.3 | 72.5 | +13.3 | 20.8 | 23.3 | +2.5 | 23.3 | +2.5 | 0.0 | 0.0 |

## full_system vs vanilla_vector direction (step_acc / hall)

| model | v2 | v3 | v3_think |
|---|---|---|---|
