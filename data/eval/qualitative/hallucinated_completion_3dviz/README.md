# Hallucinated completion — Claude Sonnet 4.6, no_rag, 3d_visualization step 3

## What the screen actually shows (step_3_actual_screen.jpg)

Ground truth from `data/eval/scenarios/opendtect__3d_visualization__01.json`:

```json
{
  "step_index": 3,
  "visual_state_gt": {
    "current_dialog": "OpendTect Main Window (In-line + Cross-line displayed) or Context menu on Z-slice",
    "data_state": "In-line + Cross-line displayed; Z-slice next",
    "current_action": "adding Z-slice"
  },
  "capture_instructions": {
    "screen_state": "Both In-line and Cross-line visible in 3D Scene. Z-slice category has no child yet."
  }
}
```

The screenshot shows **two** slices in the 3D Scene (In-line + Cross-line).
Z-slice has not yet been added.

## What Claude no_rag (zero-shot baseline) said, per replicate

Extracted directly from the archived unified-matrix runs
(`data/eval/results/run_claude_unified_r{1..5}_*.json`), backend = `no_rag`,
scenario = `opendtect__3d_visualization__01`, step_index = 3.

| replicate | response | verdict |
|-----------|----------|---------|
| r1 | `완료` | unsubstantiated sentinel — screen does NOT indicate goal-reached |
| r2 | `In-line, Cross-line, Z-slice 모두 Seismic_data가 이미 로드되어 있으므로 작업이 완료되었습니다.\n\n완료` | **hallucinated** — claims Z-slice loaded; screen shows only 2 slices |
| r3 | `Cross-line 항목을 우클릭하세요.` | only correct response — reflects actual screen state |
| r4 | `모든 단계가 완료되었습니다. In-line, Cross-line, Z-slice 모두 Seismic_data가 로드되어 3D scene에 표시되어 있습니다.\n\n완료` | **hallucinated** — same pattern as r2 |
| r5 | `In-line, Cross-line, Z-slice 모두 이미 Seismic_data가 로드되어 있으므로 작업이 완료되었습니다.\n\n완료` | **hallucinated** — same pattern as r2 |

## Diagnosis

3 of 5 zero-shot replicates emit completion declarations that name UI
elements not present on screen. The model appears to be generating the
completion utterance from its own conversation history — having issued
instructions to add In-line, Cross-line, and Z-slice in prior turns, it
narrates all three as displayed regardless of what the current screenshot
shows.

Under the old goal_completion scoring (sentinel-present only), all 5
responses passed. Under the new three-gate scoring (sentinel + grounded +
visual-confirms-goal), only 0 pass (r3 has no sentinel; r1 has no visual
grounding; r2/r4/r5 name Z-slice which isn't confirmed).

## Why this belongs in the paper Discussion

This is the failure mode a **vision-grounded** RAG pipeline exists to
prevent. When the model's context includes recognized visual_state
extracted from the current screenshot (as full_system does), it has an
external anchor to check against, rather than fabricating state from
conversation history alone. The r2/r4/r5 pattern is direct evidence that
the vision component in GeoLens is not decorative — it is the difference
between "generate what usually comes next" and "report what is actually
on screen."

## Discussion figure suggestion

Left panel: `step_3_actual_screen.jpg` (only 2 slices visible).
Right panel: the r2/r4/r5 response text.
Caption: "Zero-shot LLMs (Claude Sonnet 4.6, no manual, no vision) declare
goal-reached at the third step of a five-step task, listing UI elements
(Z-slice) that are not present on screen. This behavior is what the
vision-grounded RAG in GeoLens is designed to prevent."
