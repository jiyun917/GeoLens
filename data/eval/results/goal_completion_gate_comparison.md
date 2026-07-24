# Goal-completion metric — old (sentinel-only) vs new (three-gate)

Generated from `scripts/rescore_results.py` after applying the tightened
goal-completion gate. The new gate requires:

1. **Sentinel present** — response ends with "완료" or "Done"
2. **Grounded** — every UI element the response names is confirmed by the
   final step's `visual_state_gt` (no phantom claims)
3. **Visual confirms goal** — the final step's `visual_state_gt` /
   `capture_instructions.screen_state` actively indicates goal-reached

The old scoring required only (1), which is why zero-shot baselines with a
habitual "완료" utterance scored perfect goal_completion.

## Per-(model, backend) mean, n = replicates × scenarios

| model | backend | n | old_goal | new_goal | Δ |
|---|---|---|---|---|---|
| claude | full_system | 9 | 0.111 | 0.000 | -0.111 |
| claude | graph_only | 9 | 0.444 | 0.444 | +0.000 |
| claude | state_path | 9 | 0.667 | 0.444 | -0.222 |
| claude | vanilla_vector | 9 | 0.667 | 0.444 | -0.222 |
| claude | vision_only | 9 | 0.667 | 0.333 | -0.333 |
| claude_unified | full_system | 10 | 1.000 | 0.500 | **-0.500** |
| claude_unified | no_rag | 10 | 1.000 | 0.500 | **-0.500** |
| claude_unified | vanilla_vector | 10 | 1.000 | 0.500 | **-0.500** |
| gemini | full_system | 15 | 0.067 | 0.067 | +0.000 |
| gemini | graph_only | 15 | 0.400 | 0.400 | +0.000 |
| gemini | state_path | 15 | 0.400 | 0.400 | +0.000 |
| gemini | vanilla_vector | 15 | 0.600 | 0.600 | +0.000 |
| gemini | vision_only | 15 | 0.467 | 0.467 | +0.000 |
| gemini_flash | full_system | 4 | 0.000 | 0.000 | +0.000 |
| gemini_flash | graph_only | 4 | 0.000 | 0.250 | +0.250 |
| gemini_flash | no_rag | 4 | 0.250 | 0.250 | +0.000 |
| gemini_flash | state_path | 4 | 0.250 | 0.000 | -0.250 |
| gemini_flash | vanilla_vector | 4 | 0.250 | 0.000 | -0.250 |
| gemini_flash | vision_only | 4 | 0.250 | 0.000 | -0.250 |
| gemini_unified | full_system | 6 | 1.000 | 0.500 | **-0.500** |
| gemini_unified | no_rag | 6 | 1.000 | 0.500 | **-0.500** |
| gemini_unified | vanilla_vector | 6 | 1.000 | 0.500 | **-0.500** |
| gpt | full_system | 9 | 0.000 | 0.000 | +0.000 |
| gpt | graph_only | 9 | 0.222 | 0.222 | +0.000 |
| gpt | state_path | 9 | 0.222 | 0.222 | +0.000 |
| gpt | vanilla_vector | 9 | 0.333 | 0.333 | +0.000 |
| gpt | vision_only | 9 | 0.222 | 0.222 | +0.000 |
| gpt_unified | full_system | 10 | 0.400 | 0.000 | **-0.400** |
| gpt_unified | no_rag | 10 | 0.200 | 0.000 | -0.200 |
| gpt_unified | vanilla_vector | 10 | 0.600 | 0.000 | **-0.600** |
| qwen | full_system | 9 | 0.000 | 0.000 | +0.000 |
| qwen | graph_only | 9 | 0.111 | 0.111 | +0.000 |
| qwen | state_path | 9 | 0.111 | 0.111 | +0.000 |
| qwen | vanilla_vector | 9 | 0.333 | 0.333 | +0.000 |
| qwen | vision_only | 9 | 0.444 | 0.444 | +0.000 |
| qwen_unified | full_system | 10 | 0.300 | 0.200 | -0.100 |
| qwen_unified | no_rag | 10 | 0.300 | 0.100 | -0.200 |
| qwen_unified | vanilla_vector | 10 | 0.400 | 0.000 | **-0.400** |

## Headline

The unified matrix (5-replicate paper data) shows that Claude and Gemini's
perfect 1.000 goal_completion under the old metric drops uniformly to 0.500
under the honest gate — **half of previously-scored completions were
utterance habits, not screen observation.** GPT and Qwen show larger
proportional drops because their sentinel emission was less consistent to
begin with.

The scenario-level pattern: under the new gate, `survey_setup__01` still
credits bare sentinels because its final step's `visual_state_gt.data_state`
explicitly says "Goal achieved." `3d_visualization__01` credits nothing
because that scenario's final step captures the *penultimate* state (only
2 of 3 slices displayed), so no completion declaration can be visually
grounded. This is an accurate signal that the 3d_visualization scenario's
completion capture should be either (a) recaptured at the true terminal
state, or (b) marked `expected_done_sentinel: false`.

## Methodology note for the paper (Methods section, draft text)

> During analysis we discovered that the goal_completion metric under
> sentinel-only scoring credited responses that emit a completion token
> without any grounding in the final visual state — e.g. no_rag models
> emitting "In-line, Cross-line, Z-slice 모두 표시되어 있음. 완료." when
> the screen actually shows two of the three slices (n = 3/5 replicates
> for Claude on the 3d_visualization scenario). To measure screen
> observation rather than utterance habit, we adopted a three-gate
> completion check: (i) sentinel present, (ii) every UI element the
> response names must be confirmed by the final step's visual_state, and
> (iii) the visual_state must actively indicate goal-reached. All existing
> runs were re-scored under this rule; the table above compares the two.
