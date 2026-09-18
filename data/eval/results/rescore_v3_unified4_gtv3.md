# Re-score of archived logs with scorer v2 / v3 — unified4_gtv3

Files: 20. v2 re-implementation vs stored matched/hallucinated: 110 mismatches / 1920 steps.

v3 = ASCII word boundary in step patterns + quote-independent hallucination extractor. v3_think = v3 + unclosed <think> blocks dropped (affects Qwen only). Values are macro means over replicates (%), Δ = variant − v2.

| model | backend | n | StepAcc v2 | v3 | Δ | v3_think | Δ | Hall v2 | v3 | Δ | v3_think | Δ | Loop v2 | v3_think |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini | full_system | 5 | 72.5 | 84.2 | +11.7 | 84.2 | +11.7 | 5.8 | 5.8 | +0.0 | 5.8 | +0.0 | 0.8 | 0.8 |
| gemini | graph_only | 5 | 70.0 | 80.8 | +10.8 | 80.8 | +10.8 | 5.8 | 9.2 | +3.3 | 9.2 | +3.3 | 0.0 | 0.0 |
| gemini | no_rag | 5 | 66.7 | 78.3 | +11.7 | 78.3 | +11.7 | 0.0 | 5.8 | +5.8 | 5.8 | +5.8 | 0.0 | 0.0 |
| gemini | state_path | 5 | 76.7 | 91.7 | +15.0 | 91.7 | +15.0 | 1.7 | 5.8 | +4.2 | 5.8 | +4.2 | 0.0 | 0.0 |
| gemini | vanilla_vector | 5 | 75.0 | 81.7 | +6.7 | 81.7 | +6.7 | 5.0 | 7.5 | +2.5 | 7.5 | +2.5 | 1.7 | 1.7 |
| gemini | vision_only | 5 | 77.5 | 90.8 | +13.3 | 90.8 | +13.3 | 0.8 | 7.5 | +6.7 | 7.5 | +6.7 | 1.7 | 1.7 |
| claude | full_system | 5 | 85.0 | 87.5 | +2.5 | 87.5 | +2.5 | 13.3 | 8.3 | -5.0 | 8.3 | -5.0 | 2.5 | 2.5 |
| claude | graph_only | 5 | 80.0 | 84.2 | +4.2 | 84.2 | +4.2 | 15.0 | 8.3 | -6.7 | 8.3 | -6.7 | 0.8 | 0.8 |
| claude | no_rag | 5 | 85.0 | 87.5 | +2.5 | 87.5 | +2.5 | 19.2 | 12.5 | -6.7 | 12.5 | -6.7 | 2.5 | 2.5 |
| claude | state_path | 5 | 83.3 | 87.5 | +4.2 | 87.5 | +4.2 | 12.5 | 8.3 | -4.2 | 8.3 | -4.2 | 2.5 | 2.5 |
| claude | vanilla_vector | 5 | 84.2 | 87.5 | +3.3 | 87.5 | +3.3 | 15.8 | 10.0 | -5.8 | 10.0 | -5.8 | 0.8 | 0.8 |
| claude | vision_only | 5 | 83.3 | 87.5 | +4.2 | 87.5 | +4.2 | 21.7 | 8.3 | -13.3 | 8.3 | -13.3 | 1.7 | 1.7 |
| gpt | full_system | 5 | 69.2 | 81.7 | +12.5 | 81.7 | +12.5 | 24.2 | 8.3 | -15.8 | 8.3 | -15.8 | 0.0 | 0.0 |
| gpt | graph_only | 5 | 67.5 | 80.0 | +12.5 | 80.0 | +12.5 | 28.3 | 8.3 | -20.0 | 8.3 | -20.0 | 0.0 | 0.0 |
| gpt | no_rag | 5 | 50.8 | 65.0 | +14.2 | 65.0 | +14.2 | 23.3 | 9.2 | -14.2 | 9.2 | -14.2 | 0.0 | 0.0 |
| gpt | state_path | 5 | 72.5 | 79.2 | +6.7 | 79.2 | +6.7 | 20.8 | 9.2 | -11.7 | 9.2 | -11.7 | 0.0 | 0.0 |
| gpt | vanilla_vector | 5 | 60.0 | 70.8 | +10.8 | 70.8 | +10.8 | 26.7 | 11.7 | -15.0 | 11.7 | -15.0 | 1.7 | 1.7 |
| gpt | vision_only | 5 | 54.2 | 67.5 | +13.3 | 67.5 | +13.3 | 27.5 | 13.3 | -14.2 | 13.3 | -14.2 | 0.0 | 0.0 |
| qwen | full_system | 5 | 56.7 | 57.5 | +0.8 | 43.3 | -13.3 | 43.3 | 25.8 | -17.5 | 11.7 | -31.7 | 6.7 | 6.7 |
| qwen | graph_only | 5 | 49.2 | 54.2 | +5.0 | 45.0 | -4.2 | 61.7 | 26.7 | -35.0 | 17.5 | -44.2 | 2.5 | 2.5 |
| qwen | no_rag | 5 | 49.2 | 50.0 | +0.8 | 40.8 | -8.3 | 35.8 | 24.2 | -11.7 | 15.0 | -20.8 | 21.7 | 21.7 |
| qwen | state_path | 5 | 55.0 | 59.2 | +4.2 | 52.5 | -2.5 | 48.3 | 20.0 | -28.3 | 13.3 | -35.0 | 5.8 | 5.8 |
| qwen | vanilla_vector | 5 | 55.0 | 55.0 | +0.0 | 42.5 | -12.5 | 59.2 | 52.5 | -6.7 | 40.0 | -19.2 | 15.0 | 15.0 |
| qwen | vision_only | 5 | 62.5 | 62.5 | +0.0 | 42.5 | -20.0 | 52.5 | 38.3 | -14.2 | 18.3 | -34.2 | 10.0 | 10.0 |

## full_system vs vanilla_vector direction (step_acc / hall)

| model | v2 | v3 | v3_think |
|---|---|---|---|
| gemini | acc 72.5 vs 75.0 (vanilla); hall 5.8 vs 5.0 (vanilla) | acc 84.2 vs 81.7 (full); hall 5.8 vs 7.5 (full) | acc 84.2 vs 81.7 (full); hall 5.8 vs 7.5 (full) |
| claude | acc 85.0 vs 84.2 (full); hall 13.3 vs 15.8 (full) | acc 87.5 vs 87.5 (tie); hall 8.3 vs 10.0 (full) | acc 87.5 vs 87.5 (tie); hall 8.3 vs 10.0 (full) |
| gpt | acc 69.2 vs 60.0 (full); hall 24.2 vs 26.7 (full) | acc 81.7 vs 70.8 (full); hall 8.3 vs 11.7 (full) | acc 81.7 vs 70.8 (full); hall 8.3 vs 11.7 (full) |
