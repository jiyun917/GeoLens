# `.archive_unified2/` — Historical Snapshot

**Archived on**: 2026-08-13.

## What lives here

Files in this directory preserve the **unified2-era truth** — the 2-scenario matrix, the Story A/B/C judgment frame, the pre-refinement Goal-Completion footnote ("penultimate state, 3-gate structurally infeasible"), the "4/4 graph_only faith universal" and "3승 1무" narratives, and the $283.45m / 106.6× long-context cost ratio computed against the unified2 full_system baseline.

All of these were true at their point in time and were superseded by later cycles (unified3 → unified4 → qgis_pilot) that expanded the scenario set, refined the 3d_visualization step_3 capture to a goal-reached state, and retagged the cost ratio to 148× against the unified4 full_system baseline.

## Why they are kept

The files are retained because:

1. **Methodology-audit traceability.** Each file is the actual, dated deliverable that a subsequent cycle acted upon. `v2_judgment_report.md` in particular is the "Story A confirmed" decision record that motivated the unified3 scenario expansion.
2. **Pre-registration integrity.** `long_context_prerecord.md` and related v2 pre-registration artifacts must remain readable in their contemporaneous form to defend the pre-registration methodology.
3. **Cost accounting provenance.** The 106.6× (unified2) / 142.9× (unified3) / 148× (unified4) evolution table in `../cost_basis.md § 6b` cites these files as originating documents; deleting them would break that provenance chain.

## What must NOT be cited from here

Do not cite these files as active-paper evidence. Every file in this directory carries a `> **⚠ SUPERSEDED (unified2 snapshot, 2026-08-13 archived)**` banner at the top redirecting to active artifacts:

- `../unified4_judgment_template.md` — active main-matrix judgment
- `../qgis_pilot_result_report.md` — portability pilot result
- `../methodology_audit_trail.md § 저장소 정리 이력` — this cleanup event
- `../../GeoLens_종합결과보고서_final.md` (or `./out/GeoLens_종합결과보고서_final.md`) — single-file synthesis report

## File inventory (11 files)

| File | Origin cycle | Superseded by |
|---|---|---|
| `FINAL_tables_and_prose.md` | unified2 | `paper_portability_section_v2.md` + `paper_discussion_integrated.md` (drafts) or user's own paper prose |
| `v2_judgment_report.md`, `v2_judgment_report_template.md` | unified2 judgment | `../unified4_judgment_template.md` |
| `direction_unified2.md` | unified2 direction consistency | `../direction_unified4.md` |
| `final_unified2_table.md` | unified2 4×6 matrix | `../final_unified4_table.md` |
| `faithfulness_supplement.md` (no tag = unified2) | unified2 faith | `../faithfulness_supplement_unified4.md` |
| `long_context_prerecord.md` | unified2 long-context pre-reg | (long-context runs are now unified4 tag, `run_gemini_longctx_r{1..5}_20260807T18*.json`) |
| `preview_qwen_cost.md` | unified2 Qwen cost preview | `../cost_basis.md § 6b` (148× table) + `../qwen_cost_estimation.md` |
| `table1_full_sd.md` (no tag = unified2) | unified2 25-cell | `../table1_full_sd_unified4.md` |
| `goal_completion_gate_comparison.md` | unified2 Goal-Comp gate redesign history | (Goal-Comp is now unified3-refined, footnote updated in `../final_unified4_table.md`) |
| `NEXT_SESSION_TODO.md` | prior-session TODO | items either completed or superseded by later cycles |

11 files (12 originally proposed for archive; the twelfth was NEXT_SESSION_TODO.md moved from repo root).
