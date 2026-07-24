# seg_y_import — Qualitative Failure Case

## Setup
- **Goal**: F3_Demo Survey를 C:\Survey\F3_Demo 경로에서 SEG-Y import로 불러오기
- **Manual**: OpendTect 7.0 Training Manual (`645b7cdf...`)
- **Attempted**: 2026-07-06

## Failure Mode: RAG Router Mis-routing

The system routed the SEG-Y import task to workflow nodes belonging to
`fault_interpretation` and `seismic_attribute` — semantically related
(both start with "load data on OpendTect main window") but wrong for
the user's actual goal (import wizard).

### Evidence (log excerpts)

```
[STEP] RAG router mode=guide, context=3643chars, node=fault_interpretation_01_data_load
[STEP] RAG router mode=guide, context=3622chars, node=seismic_attribute_01_data_load
[STEP] RAG router mode=guide, context=3116chars, node=fault_interpretation_01_data_load
```

Every /step call for this scenario picked a `_01_data_load` node from
the fault_interpretation or seismic_attribute workflow. There is no
"import" workflow in the auto-generated set — so the localizer picked
the nearest semantic match, which was inappropriate for the wizard flow.

Full log: `seg_y_import_rag_misroute.log`

## Root Cause

`data/workflows/` contains 3 hand-authored workflows:
- fault_interpretation.json
- horizon_tracking.json
- seismic_attribute.json

**Missing**: any SEG-Y or general import workflow.

Auto-generated workflows from manual chunks likewise did not synthesize
an import-wizard workflow.

Consequence: user's goal did not match any real workflow node → RAG
router fell back to closest semantic match (a `data_load` step in an
unrelated workflow) → context injected into Claude was fault/attribute
manual excerpt → Claude guidance drifted from actual SEG-Y wizard.

## Paper Implications

Illustrates a real limitation of RAG-router + auto-workflow approach:
> When user tasks fall outside the auto-generated workflow coverage,
> guidance quality degrades to worse-than-no-workflow baseline.

Good qualitative example for Limitation / Discussion section.
Fix direction: (1) improve auto-workflow generator to detect wizard
patterns, or (2) fall back to plain vector RAG when no confident
workflow match, instead of injecting a wrong workflow's context.

## Screenshots

Deleted (not useful for quantitative bench since flow diverged from
scenario JSON expectations). Scenario JSON moved to `scenarios/excluded/`.
