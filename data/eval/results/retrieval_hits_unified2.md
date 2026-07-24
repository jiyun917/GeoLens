# Retrieval hit rate — v2 unified matrix

Only backends that route through guide_pipeline (full_system, state_path) produce non-trivial numbers here. Others show '—'.

Step hit: picked workflow AND picked step within ±1 of expected.

| model | backend | n steps | workflow hit | step hit | fallback rate | mean conf |
|---|---|---|---|---|---|---|
| claude | full_system | 40 | 80% | 50% | 0% | 0.90 |
| gemini | full_system | 40 | 80% | 50% | 0% | 0.91 |
| gpt | full_system | 40 | 75% | 50% | 0% | 0.89 |
| qwen | full_system | 40 | 75% | 50% | 0% | 0.90 |
