# Route-confidence distribution — v2 unified matrix

Fallback threshold = **0.7**. Any routed step with confidence < 0.7 triggers vector-only fallback.

| model | backend | n | min | Q25 | median | Q75 | max | mean | n below 0.7 |
|---|---|---|---|---|---|---|---|---|---|
| claude | full_system | 40 | 0.70 | 0.90 | 0.90 | 0.95 | 0.95 | 0.90 | 0 |
| gemini | full_system | 40 | 0.70 | 0.90 | 0.90 | 0.95 | 0.98 | 0.91 | 0 |
| gpt | full_system | 40 | 0.70 | 0.85 | 0.90 | 0.95 | 0.98 | 0.89 | 0 |
| qwen | full_system | 40 | 0.75 | 0.90 | 0.90 | 0.95 | 0.95 | 0.90 | 0 |

**Total routed steps**: 160
**Steps below threshold 0.7**: 0 (0.0%)

## Interpretation for the paper

The confidence gate at threshold 0.7 did not activate on any of the 160 routed steps across the entire v2 matrix. The observed minimum confidence across all (model, backend) cells was above 0.7, so the fallback branch of the pipeline was dead code on this dataset. This does not mean the branch is gratuitous — the ground-truth dry-run (with hand-authored visual_state) produced confidences as low as 0.60, so the safety net exists for cases where Gemini's real-time vision extraction is less certain than the authored ground truth. On the two scenarios in this benchmark, no such uncertainty occurred.
