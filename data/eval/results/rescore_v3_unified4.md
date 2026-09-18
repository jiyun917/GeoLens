# Re-score of archived logs with scorer v2 / v3 — unified4

Files: 20. v2 re-implementation vs stored matched/hallucinated: 0 mismatches / 1920 steps.

v3 = ASCII word boundary in step patterns + quote-independent hallucination extractor. v3_think = v3 + unclosed <think> blocks dropped (affects Qwen only). Values are macro means over replicates (%), Δ = variant − v2.

| model | backend | n | StepAcc v2 | v3 | Δ | v3_think | Δ | Hall v2 | v3 | Δ | v3_think | Δ | Loop v2 | v3_think |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini | full_system | 5 | 72.5 | 84.2 | +11.7 | 84.2 | +11.7 | 7.5 | 10.8 | +3.3 | 10.8 | +3.3 | 0.8 | 0.8 |
| gemini | graph_only | 5 | 70.0 | 80.8 | +10.8 | 80.8 | +10.8 | 9.2 | 15.0 | +5.8 | 15.0 | +5.8 | 0.0 | 0.0 |
| gemini | no_rag | 5 | 66.7 | 78.3 | +11.7 | 78.3 | +11.7 | 0.8 | 7.5 | +6.7 | 7.5 | +6.7 | 0.0 | 0.0 |
| gemini | state_path | 5 | 76.7 | 91.7 | +15.0 | 91.7 | +15.0 | 1.7 | 11.7 | +10.0 | 11.7 | +10.0 | 0.0 | 0.0 |
| gemini | vanilla_vector | 5 | 75.0 | 81.7 | +6.7 | 81.7 | +6.7 | 7.5 | 11.7 | +4.2 | 11.7 | +4.2 | 1.7 | 1.7 |
| gemini | vision_only | 5 | 77.5 | 90.8 | +13.3 | 90.8 | +13.3 | 4.2 | 14.2 | +10.0 | 14.2 | +10.0 | 1.7 | 1.7 |
| claude | full_system | 5 | 85.0 | 87.5 | +2.5 | 87.5 | +2.5 | 22.5 | 21.7 | -0.8 | 21.7 | -0.8 | 2.5 | 2.5 |
| claude | graph_only | 5 | 80.0 | 84.2 | +4.2 | 84.2 | +4.2 | 23.3 | 17.5 | -5.8 | 17.5 | -5.8 | 0.8 | 0.8 |
| claude | no_rag | 5 | 85.0 | 87.5 | +2.5 | 87.5 | +2.5 | 25.0 | 16.7 | -8.3 | 16.7 | -8.3 | 2.5 | 2.5 |
| claude | state_path | 5 | 83.3 | 87.5 | +4.2 | 87.5 | +4.2 | 19.2 | 20.0 | +0.8 | 20.0 | +0.8 | 2.5 | 2.5 |
| claude | vanilla_vector | 5 | 84.2 | 87.5 | +3.3 | 87.5 | +3.3 | 24.2 | 15.0 | -9.2 | 15.0 | -9.2 | 0.8 | 0.8 |
| claude | vision_only | 5 | 83.3 | 87.5 | +4.2 | 87.5 | +4.2 | 26.7 | 20.8 | -5.8 | 20.8 | -5.8 | 1.7 | 1.7 |
| gpt | full_system | 5 | 69.2 | 81.7 | +12.5 | 81.7 | +12.5 | 30.8 | 1.7 | -29.2 | 1.7 | -29.2 | 0.0 | 0.0 |
| gpt | graph_only | 5 | 67.5 | 80.0 | +12.5 | 80.0 | +12.5 | 35.0 | 0.0 | -35.0 | 0.0 | -35.0 | 0.0 | 0.0 |
| gpt | no_rag | 5 | 50.8 | 65.0 | +14.2 | 65.0 | +14.2 | 30.8 | 1.7 | -29.2 | 1.7 | -29.2 | 0.0 | 0.0 |
| gpt | state_path | 5 | 72.5 | 79.2 | +6.7 | 79.2 | +6.7 | 20.8 | 5.0 | -15.8 | 5.0 | -15.8 | 0.0 | 0.0 |
| gpt | vanilla_vector | 5 | 60.0 | 70.8 | +10.8 | 70.8 | +10.8 | 36.7 | 3.3 | -33.3 | 3.3 | -33.3 | 1.7 | 1.7 |
| gpt | vision_only | 5 | 54.2 | 67.5 | +13.3 | 67.5 | +13.3 | 36.7 | 6.7 | -30.0 | 6.7 | -30.0 | 0.0 | 0.0 |
| qwen | full_system | 5 | 56.7 | 57.5 | +0.8 | 43.3 | -13.3 | 50.0 | 24.2 | -25.8 | 10.0 | -40.0 | 6.7 | 6.7 |
| qwen | graph_only | 5 | 49.2 | 54.2 | +5.0 | 45.0 | -4.2 | 67.5 | 27.5 | -40.0 | 18.3 | -49.2 | 2.5 | 2.5 |
| qwen | no_rag | 5 | 49.2 | 50.0 | +0.8 | 40.8 | -8.3 | 40.0 | 27.5 | -12.5 | 18.3 | -21.7 | 21.7 | 21.7 |
| qwen | state_path | 5 | 55.0 | 59.2 | +4.2 | 52.5 | -2.5 | 56.7 | 35.0 | -21.7 | 28.3 | -28.3 | 5.8 | 5.8 |
| qwen | vanilla_vector | 5 | 55.0 | 55.0 | +0.0 | 42.5 | -12.5 | 61.7 | 49.2 | -12.5 | 36.7 | -25.0 | 15.0 | 15.0 |
| qwen | vision_only | 5 | 62.5 | 62.5 | +0.0 | 42.5 | -20.0 | 54.2 | 38.3 | -15.8 | 18.3 | -35.8 | 10.0 | 10.0 |

## full_system vs vanilla_vector direction (step_acc / hall)

| model | v2 | v3 | v3_think |
|---|---|---|---|
| gemini | acc 72.5 vs 75.0 (vanilla); hall 7.5 vs 7.5 (tie) | acc 84.2 vs 81.7 (full); hall 10.8 vs 11.7 (full) | acc 84.2 vs 81.7 (full); hall 10.8 vs 11.7 (full) |
| claude | acc 85.0 vs 84.2 (full); hall 22.5 vs 24.2 (full) | acc 87.5 vs 87.5 (tie); hall 21.7 vs 15.0 (vanilla) | acc 87.5 vs 87.5 (tie); hall 21.7 vs 15.0 (vanilla) |
| gpt | acc 69.2 vs 60.0 (full); hall 30.8 vs 36.7 (full) | acc 81.7 vs 70.8 (full); hall 1.7 vs 3.3 (full) | acc 81.7 vs 70.8 (full); hall 1.7 vs 3.3 (full) |
| qwen | acc 56.7 vs 55.0 (full); hall 50.0 vs 61.7 (full) | acc 57.5 vs 55.0 (full); hall 24.2 vs 49.2 (full) | acc 43.3 vs 42.5 (full); hall 10.0 vs 36.7 (full) |
