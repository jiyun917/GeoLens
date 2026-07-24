# Discarded Replicates — Audit Trail

This folder contains benchmark replicates that were **discarded and rerun**
under the pre-registered analysis rule: "environmental failures contaminating
a replicate are discarded; partial data is not mixed into the reported
matrix." Each discard is preserved here for reviewer audit.

The methodology audit section of the paper (`methodology_audit_trail.md`)
references these files as evidence that the discard-and-rerun protocol was
actually applied when triggered, not just declared.

## Discarded replicates in this repo

### 1. `run_qwen_unified2_r2_20260716T084817.json`

- **Model / tag**: Qwen3-235B / unified2 (v2 matrix, first attempt)
- **Failed at**: 2026-07-16 during Phase 2 matrix execution
- **Detected at**: 2026-07-20 during Qwen mini-checkpoint
- **Failure type**: Gemini Flash `503 UNAVAILABLE` (auxiliary vision call)
- **Failure count**: 2 hard failures after 3 retries each
- **Blast radius**: 1 of 40 steps affected (`survey_setup` / `graph_only` /
  step 3, probably). Response was generated (Empty=0/240) but pipeline
  degraded during that step, with `<think>` tag leak in output.
- **Why discarded despite response being generated**: `graph_only` was a
  key ablation backend (v2 preview showed graph_only as faithfulness winner
  at 4/4 universal), so any contamination of its scores would need footnote
  treatment. `<think>` leak indicates the response came through a degraded
  path even though it happened to match ground truth. Rather than
  attaching a caveat to that one cell, we discarded the entire replicate
  and reran cleanly.
- **Rerun file**: `../run_qwen_unified2_r2_20260720T024532.json`
  (all 48 steps clean, 0 aux failures)

### 2. `run_gemini_longctx_r5_20260723T035334.json`

- **Model / tag**: Gemini 2.5 Pro / longctx (long_context upper-bound reference)
- **Failed at**: 2026-07-23 during long_context 5-replicate run
- **Failure type**: Gemini API `429 RESOURCE_EXHAUSTED` — monthly project
  spending cap reached (long_context injects ~226k tokens per step at
  $0.28/step, exhausting cap after ~40 steps of prior work + partial r5)
- **Failure count**: Multiple 429s across retries; final step of
  `survey_setup` scenario returned empty
- **Blast radius**: 1 of 8 steps empty (survey_setup step 3)
- **Why discarded despite 7/8 steps being clean**: Same pre-registered
  rule — a replicate with any empty step is not mixed into aggregates.
  This is the exact category (429 / quota exhaustion) the user pre-listed
  as automatic discard trigger.
- **Resolution**: User raised the spending cap; rerun executed cleanly.
- **Rerun file**: `../run_gemini_longctx_r5_20260723T041637.json`
  (all 8 steps clean)

## Summary counts

| Category | Discards |
|---|---|
| Aux service `503 UNAVAILABLE` (transient) | 1 (Qwen r2 → rerun) |
| API quota `429 RESOURCE_EXHAUSTED` | 1 (Gemini longctx r5 → rerun after cap raise) |
| Empty response from generator (no upstream cause) | 0 |
| **Total discards** | **2** |
| Total rerun outcomes | 2 clean |

## Aggregate compute cost of the audit-trail discipline

- Qwen r2 rerun: ~30 minutes on NAS
- Gemini longctx r5 rerun: ~10 minutes wall time, ~$2.3 API cost

Both reruns produced clean data on first retry.

## Verification hooks

Reviewers can verify no discarded replicate leaks into the final results by:

```bash
# All final result files (excluded from discards folder):
ls data/eval/results/run_*_r*_*.json | wc -l   # expected: 25 (5 models × 5 reps)
                                                 # = 4 unified2 (20) + 1 longctx (5)

# All discards (this folder):
ls data/eval/results/discarded/*.json | wc -l   # expected: 2
```

The aggregation scripts (`scripts/build_final_table.py`,
`scripts/stats_unified.py`) glob only the top-level `data/eval/results/`
directory and do not recurse into `discarded/`, so files here cannot
accidentally be scored into the reported matrix.
