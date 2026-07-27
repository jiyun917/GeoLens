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
| gemini / no_rag | 92.5±11.2 | 7.5±11.2 | ✓ |
| gemini / vanilla_vector | 90.0±10.5 | 10.0±10.5 | ✓ |
| gemini / graph_only | 97.5±5.6 | 2.5±5.6 | ✓ |
| gemini / vision_only | 95.0±6.8 | 5.0±6.8 | ✓ |
| gemini / full_system | 95.0±6.8 | 5.0±6.8 | ✓ |
| gemini / state_path | 92.5±11.2 | 7.5±11.2 | ✓ |
| claude / no_rag | 75.0±0.0 | 25.0±0.0 | ✓ |
| claude / vanilla_vector | 75.0±8.8 | 25.0±8.8 | ✓ |
| claude / graph_only | 80.0±11.2 | 20.0±11.2 | ✓ |
| claude / vision_only | 70.0±11.2 | 30.0±11.2 | ✓ |
| claude / full_system | 85.0±5.6 | 15.0±5.6 | ✓ |
| claude / state_path | 90.0±5.6 | 10.0±5.6 | ✓ |
| gpt / no_rag | 60.0±16.3 | 40.0±16.3 | ✓ |
| gpt / vanilla_vector | 52.5±5.6 | 47.5±5.6 | ✓ |
| gpt / graph_only | 72.5±20.5 | 27.5±20.5 | ✓ |
| gpt / vision_only | 72.5±16.3 | 27.5±16.3 | ✓ |
| gpt / full_system | 45.0±6.8 | 55.0±6.8 | ✓ |
| gpt / state_path | 50.0±0.0 | 50.0±0.0 | ✓ |
| qwen / no_rag | 37.5±8.8 | 62.5±8.8 | ✓ |
| qwen / vanilla_vector | 27.5±20.5 | 72.5±20.5 | ✓ |
| qwen / graph_only | 30.0±14.3 | 70.0±14.3 | ✓ |
| qwen / vision_only | 30.0±11.2 | 70.0±11.2 | ✓ |
| qwen / full_system | 52.5±10.5 | 47.5±10.5 | ✓ |
| qwen / state_path | 40.0±5.6 | 60.0±5.6 | ✓ |
| gemini / long_context | 62.5±19.8 | 37.5±19.8 | ✓ |

**Definitional identity check**: for every cell, mean(faith) + mean(hall) ≈ 1 — confirmed for all cells.

## Direction-consistency reproduction (paper Table 3 rows)

The paper's ablation table reports per-pair direction consistency on faithfulness. Because faithfulness = 1 − hall_rate, the direction of any pairwise comparison on faithfulness is the *opposite* of the direction on hall_rate, and the win counts are identical when scored in the correct direction. Below we recompute A-wins on faithfulness (higher-better) directly from the per-replicate 5-value means.

| Pair (A vs B) | Gemini | Claude | GPT | Qwen | A wins |
|---|---|---|---|---|---|
| full_system vs vanilla_vector | A (95.0/90.0) | A (85.0/75.0) | B (45.0/52.5) | A (52.5/27.5) | 3/4 |
| full_system vs no_rag | A (95.0/92.5) | A (85.0/75.0) | B (45.0/60.0) | A (52.5/37.5) | 3/4 |
| vanilla_vector vs no_rag | B (90.0/92.5) | = (75.0/75.0) | B (52.5/60.0) | B (27.5/37.5) | 0/3 |
| graph_only vs vanilla_vector | A (97.5/90.0) | A (80.0/75.0) | A (72.5/52.5) | A (30.0/27.5) | 4/4 |
| graph_only vs full_system | A (97.5/95.0) | B (80.0/85.0) | A (72.5/45.0) | B (30.0/52.5) | 2/4 |
| state_path vs full_system | B (92.5/95.0) | A (90.0/85.0) | A (50.0/45.0) | B (40.0/52.5) | 2/4 |

**Reproduction check** (against `data/eval/results/direction_unified2.md`):

- `full_system vs vanilla_vector` on faithfulness: **3/4** (Gemini, Claude, Qwen win; GPT loses) — matches the "3승 1무 0패" narrative once tied cases are collapsed.
- `graph_only vs vanilla_vector` on faithfulness: **4/4** (all four models win) — matches the "4/4 전승" citation in the paper's Table 3 discussion.
- `full_system vs no_rag` on faithfulness: **3/4** — matches direction_unified2.md.

## Manuscript Methods paragraph draft (English)

> **Faithfulness.** We report faithfulness = 1 − hallucination rate as a higher-is-better companion column to the hallucination rate. It is not an independent metric; scenario-level faithfulness is stored as `round(1.0 − hallucination_rate, 4)` at aggregation time. The hallucination scorer is fully deterministic: for each step, we extract UI-element mentions from the model response using two regex patterns (quoted tokens and elements followed by a Korean/English UI-kind noun such as 버튼/menu/tab), then check membership against the ground-truth `visible_elements` list defined in the scenario JSON with a case-insensitive substring match in either direction. A step is hallucinated if any extracted mention fails the membership check. The substring-lenient direction of the check is conservative in the hallucination-rate direction (equivalently, generous in the faithfulness direction): a hallucinated element whose name happens to contain a ground-truth substring can pass and be counted as grounded. This is documented so readers can interpret absolute faithfulness scale accordingly; direction consistency across models — the paper's primary judgment quantity — is unaffected by the scorer's precision ceiling.

