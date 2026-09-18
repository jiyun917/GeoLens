# rescore_v3 summary — unified4 logs, scorer v2 → v3 (2026-09-18)

## 1. Hallucination rate per cell (v3 scorer; Qwen rows shown but excluded from v3)

| model | backend | Hall v2 (%) | Hall v3 (%) | Δ |
|---|---|---|---|---|
| gemini | full_system | 7.5 | 10.8 | +3.3 |
| gemini | graph_only | 9.2 | 15.0 | +5.8 |
| gemini | no_rag | 0.8 | 7.5 | +6.7 |
| gemini | state_path | 1.7 | 11.7 | +10.0 |
| gemini | vanilla_vector | 7.5 | 11.7 | +4.2 |
| gemini | vision_only | 4.2 | 14.2 | +10.0 |
| claude | full_system | 22.5 | 21.7 | -0.8 |
| claude | graph_only | 23.3 | 17.5 | -5.8 |
| claude | no_rag | 25.0 | 16.7 | -8.3 |
| claude | state_path | 19.2 | 20.0 | +0.8 |
| claude | vanilla_vector | 24.2 | 15.0 | -9.2 |
| claude | vision_only | 26.7 | 20.8 | -5.8 |
| gpt | full_system | 30.8 | 1.7 | -29.2 |
| gpt | graph_only | 35.0 | 0.0 | -35.0 |
| gpt | no_rag | 30.8 | 1.7 | -29.2 |
| gpt | state_path | 20.8 | 5.0 | -15.8 |
| gpt | vanilla_vector | 36.7 | 3.3 | -33.3 |
| gpt | vision_only | 36.7 | 6.7 | -30.0 |
| qwen | full_system | 50.0 | 10.0 | -40.0 |
| qwen | graph_only | 67.5 | 18.3 | -49.2 |
| qwen | no_rag | 40.0 | 18.3 | -21.7 |
| qwen | state_path | 56.7 | 28.3 | -28.3 |
| qwen | vanilla_vector | 61.7 | 36.7 | -25.0 |
| qwen | vision_only | 54.2 | 18.3 | -35.8 |

Distribution of v3 hall over the 18 three-model cells: {'0': 1, '0-5': 3, '5-10': 3, '10-20': 8, '>20': 3} (GT visible_elements not yet completed — S6 pending).

## 2. full_system vs vanilla_vector — step accuracy direction, scorer only changed

| model | v2 full / vanilla → dir | v3 full / vanilla → dir | change |
|---|---|---|---|
| gemini | 72.5 / 75.0 → vanilla | 84.2 / 81.7 → full | vanilla → full |
| claude | 85.0 / 84.2 → full | 87.5 / 87.5 → tie | full → tie |
| gpt | 69.2 / 60.0 → full | 81.7 / 70.8 → full | same |
| qwen | 56.7 / 55.0 → full | 43.3 / 42.5 → full | same |

Qwen shown with v3_think (unclosed <think> dropped). Three-model direction count (full > vanilla): v2 2/3 (Claude, GPT; Gemini vanilla) → v3 2/3 (Gemini, GPT; Claude tie).

