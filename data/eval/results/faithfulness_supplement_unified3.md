# Faithfulness — supplementary table + reproduction check

## Definition (traced from code)

From `api/services/evaluation.py:790`:

```python
"faithfulness": round(1.0 - hall_rate, 4),  # higher = better
```

Faithfulness is **defined as** `1 − hallucination_rate` at the scenario-level aggregation step. It is not an independently measured quantity — it is a monotonic-decreasing view of the hallucination scoring, provided as a higher-is-better column for convenience.

## Scoring procedure (deterministic)

The underlying hallucination detector is `hallucinated_elements()` at `api/services/evaluation.py:532-553`. For each step, given the model response and the ground-truth `visible_elements`:

1. Extract UI-element mentions from the response using two regexes:
   - Quoted tokens: `'X'`, `"X"`, `` `X` `` (length 1–40).
   - Elements followed by a UI-kind noun: `X (버튼|메뉴|탭|button|menu|tab)`.
2. For each extracted mention `r`, compute a lenient membership check against the ground-truth list: `r` is considered grounded if any ground-truth element string contains it as a substring, or vice versa (case-insensitive).
3. Any extracted mention that fails the membership check is a hallucination.
4. A step is `hallucinated` if the returned list is non-empty. `hallucination_rate` at the scenario level = `n_hallucinated_steps / n_steps`.

The scorer is **fully deterministic**: no LLM-in-the-loop, no thresholds tuned on model output, no randomness. Given the same response text and scenario JSON, the score is bit-identical across runs and models.

**Consequences of the substring-lenient check** (worth stating in the manuscript):

- False negatives: a response that misspells a UI element and does not embed a ground-truth substring will be flagged as hallucinated even if the intent was correct. Rare in practice.
- False positives (missed hallucinations): a hallucinated element whose name happens to contain any ground-truth substring will be let through. Example: if `Add Data` is a ground-truth element, the hallucinated `Add Default Data` might pass the check (the substring `Add` is common). Manual review of Table 6 confirmed at least one such case in the Claude v1 vanilla_vector output.

This is the ceiling on the scorer's precision, not a scoring bug — it is why the paper's positioning of hallucination-rate differences uses direction consistency rather than absolute-scale claims.

## Supplementary Table — 25-cell mean ± sample SD

Statistical unit = replicate (n=5 per cell). Per-replicate value = mean across the 2 scenarios (each already a mean over 4 steps). SD is sample SD.

| Cell (Model / Backend) | Faithfulness (%, ↑) | Hall Rate (%, ↓) | 1 − Hall matches Faith? |
|---|---|---|---|
| gemini / no_rag | 100.0±0.0 | 0.0±0.0 | ✓ |
| gemini / vanilla_vector | 95.0±7.5 | 5.0±7.5 | ✓ |
| gemini / graph_only | 97.5±5.6 | 2.5±5.6 | ✓ |
| gemini / vision_only | 95.8±5.9 | 4.2±5.9 | ✓ |
| gemini / full_system | 98.3±3.7 | 1.7±3.7 | ✓ |
| gemini / state_path | 96.7±3.5 | 3.3±3.5 | ✓ |
| claude / no_rag | 74.2±5.4 | 25.8±5.4 | ✓ |
| claude / vanilla_vector | 70.0±6.2 | 30.0±6.2 | ✓ |
| claude / graph_only | 79.2±5.9 | 20.8±5.9 | ✓ |
| claude / vision_only | 75.0±4.2 | 25.0±4.2 | ✓ |
| claude / full_system | 75.0±4.2 | 25.0±4.2 | ✓ |
| claude / state_path | 74.2±4.6 | 25.8±4.6 | ✓ |
| gpt / no_rag | 66.7±13.8 | 33.3±13.8 | ✓ |
| gpt / vanilla_vector | 60.0±3.7 | 40.0±3.7 | ✓ |
| gpt / graph_only | 64.2±8.6 | 35.8±8.6 | ✓ |
| gpt / vision_only | 69.2±10.9 | 30.8±10.9 | ✓ |
| gpt / full_system | 67.5±9.5 | 32.5±9.5 | ✓ |
| gpt / state_path | 83.3±7.2 | 16.7±7.2 | ✓ |
| qwen / no_rag | 56.7±12.4 | 43.3±12.4 | ✓ |
| qwen / vanilla_vector | 45.0±20.5 | 55.0±20.5 | ✓ |
| qwen / graph_only | 40.0±5.6 | 60.0±5.6 | ✓ |
| qwen / vision_only | 39.2±8.6 | 60.8±8.6 | ✓ |
| qwen / full_system | 39.2±8.1 | 60.8±8.1 | ✓ |
| qwen / state_path | 40.0±14.9 | 60.0±14.9 | ✓ |
| gemini / long_context | 90.0±7.0 | 10.0±7.0 | ✓ |

**Definitional identity check**: for every cell, mean(faith) + mean(hall) ≈ 1 — confirmed for all cells.

## Direction-consistency reproduction (paper Table 3 rows)

The paper's ablation table reports per-pair direction consistency on faithfulness. Because faithfulness = 1 − hall_rate, the direction of any pairwise comparison on faithfulness is the *opposite* of the direction on hall_rate, and the win counts are identical when scored in the correct direction. Below we recompute A-wins on faithfulness (higher-better) directly from the per-replicate 5-value means.

| Pair (A vs B) | Gemini | Claude | GPT | Qwen | A wins |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (98.3/95.0) | A (75.0/70.0) | A (67.5/60.0) | B (39.2/45.0) | 3/4 |
| full_system vs no_rag | B (98.3/100.0) | A (75.0/74.2) | A (67.5/66.7) | B (39.2/56.7) | 2/4 |
| vanilla_vector vs no_rag | B (95.0/100.0) | B (70.0/74.2) | B (60.0/66.7) | B (45.0/56.7) | 0/4 |
| graph_only vs vanilla_vector | A (97.5/95.0) | A (79.2/70.0) | A (64.2/60.0) | B (40.0/45.0) | 3/4 |
| graph_only vs full_system | B (97.5/98.3) | A (79.2/75.0) | B (64.2/67.5) | A (40.0/39.2) | 2/4 |
| state_path vs full_system | B (96.7/98.3) | B (74.2/75.0) | A (83.3/67.5) | A (40.0/39.2) | 2/4 |

**Reproduction check** (against `data/eval/results/direction_unified3.md`): the win counts in the table above are recomputed here from raw per-replicate faithfulness (n=5 per cell). Compare them column-by-column with the faithfulness section of direction_unified3.md — if they match, the deterministic identity `faithfulness = 1 − hall` holds all the way through aggregation. Any narrative citations such as "3승" or "4/4 전승" in downstream reports should be regenerated from these numbers, not carried over between tags.

## Manuscript Methods paragraph draft (English)

> **Faithfulness.** We report faithfulness = 1 − hallucination rate as a higher-is-better companion column to the hallucination rate. It is not an independent metric; scenario-level faithfulness is stored as `round(1.0 − hallucination_rate, 4)` at aggregation time. The hallucination scorer is fully deterministic: for each step, we extract UI-element mentions from the model response using two regex patterns (quoted tokens and elements followed by a Korean/English UI-kind noun such as 버튼/menu/tab), then check membership against the ground-truth `visible_elements` list defined in the scenario JSON with a case-insensitive substring match in either direction. A step is hallucinated if any extracted mention fails the membership check. The substring-lenient direction of the check is conservative in the hallucination-rate direction (equivalently, generous in the faithfulness direction): a hallucinated element whose name happens to contain a ground-truth substring can pass and be counted as grounded. This is documented so readers can interpret absolute faithfulness scale accordingly; direction consistency across models — the paper's primary judgment quantity — is unaffected by the scorer's precision ceiling.

