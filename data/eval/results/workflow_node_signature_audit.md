# Workflow-node signature change audit

Tracks knowledge-base changes to hand-authored workflow graphs that
affect routing behavior between benchmark versions. Any signature edit
here is a system-version change and requires a new bench tag.

## 2026-08-05 — `seismic_attribute_01` rename + resignature

**Node**: `seismic_attribute_01_data_load` → **`seismic_attribute_01_ready_to_start`**
(rename + `visual_signature` rewrite + title/description update)

### Why the change

Adding scenario `opendtect__attribute_computation__01` (Phase A of the
matrix expansion tagged for `unified3`) exposed a hand-authoring error
in the original node:

- Original `expected_dialog` was `"Survey Setup"`; original
  `screenshot_keywords` were `["OpendTect", "Survey"]`.
- Manual §1.5's actual opening context is *"F3 Demo already loaded,
  about to open Attribute Set (3D) from the Analysis menu"* — the
  Survey Setup dialog is nowhere in that scene.
- Consequence: the node acted as a routing magnet for any survey-flavored
  query, drawing misroutes from unrelated scenarios.

### Impact on `unified2` routing distribution

Audit of the 5 replicates × 4 models × 2 scenarios full_system +
state_path bench runs (`data/eval/results/run_*_unified2_r*_*.json`):

| Metric | Value |
|---|---|
| Total routed steps (full_system + state_path) | 160 |
| Steps misrouted to wrong workflow            | 36 (22.5%) |
| Misroutes → `seismic_attribute` workflow     | **36 (100%)** |
| Of those, → node `seismic_attribute_01_data_load` | **33 (92%)** |
| Remaining misroutes to `seismic_attribute_06_display` | 3 |

The paper's reported "workflow hit rate 75–80%" (Table 5) is exactly
this pattern: ~22% miss, essentially all going to one hand-authored
node whose signature was too broad.

### Consequence for benchmark comparability

A node whose signature is rewritten is a **knowledge-base version
change**. Re-running the existing `unified2` scenarios against the
corrected node will produce different routing telemetry (fewer misroutes
to this node), which can shift fallback_rate, mean_route_confidence, and
downstream retrieval content in `full_system` / `state_path` cells.

**Handling**: the upcoming full-matrix rerun is tagged **`unified3`** to
mark this as a distinct system version. Methods documentation should
state: *"between unified2 and unified3, one hand-authored workflow node
(`seismic_attribute_01`) was corrected — its original signature described
the wrong dialog and drew misroutes from unrelated scenarios; the
corrected signature reflects manual §1.5's actual opening context."*
Direct numerical comparison of routing telemetry (Table 5) between
unified2 and unified3 is inappropriate; final metric comparisons should
be on the unified3 tag alone.

### What changed, exactly

| Field | Before (unified2) | After (unified3) |
|---|---|---|
| `id` | `seismic_attribute_01_data_load` | `seismic_attribute_01_ready_to_start` |
| `title` | "Survey 및 탄성파 데이터 로드" | "속성 작업 시작 준비 (F3 로드 완료 상태)" |
| `description` | "Survey 선택 후 탄성파 볼륨 로드" | "매뉴얼 1.5 시작 문맥: F3 Demo survey 로드 완료 후 OpendTect Main Window에서 속성 계산을 개시하려는 상태. Analysis / Attributes 메뉴 또는 Tree scene의 Attributes 카테고리 우클릭으로 Create Attribute Set (3D)... 진입 직전." |
| `visual_signature.expected_dialog` | `"Survey Setup"` | `"OpendTect Main Window"` |
| `visual_signature.expected_ui_elements` | `["survey_tree"]` | `["main_menu_bar", "analysis_menu", "attributes_category", "tree_scene"]` |
| `visual_signature.screenshot_keywords` | `["OpendTect", "Survey"]` | `["Analysis", "Attributes", "Create Attribute Set", "Attribute Set 3D"]` |
| `edges[0].source` | `seismic_attribute_01_data_load` | `seismic_attribute_01_ready_to_start` |

`linked_chunks`, `step_number`, `step_type`, and `parameters` unchanged.
An inline `signature_audit` block was added to the node itself so the
change is auditable in-place.

### Verification after change

Routing dry-run (`scripts/routing_dryrun.py`) on all three unified3
scenarios (survey_setup, 3d_visualization, attribute_computation):
**15/15 (100%)** exact-workflow match, including 7/7 on the new
scenario — the pre-change dry-run was 14/15 (93.3%) overall and 6/7
(86%) on the new scenario, with the single miss on the new scenario's
step 0 going to `d3_visualization_01_main_window_ready` (before the
attribute-scenario's step 0 was disambiguated with an Analysis-menu-
opened capture per Phase A option C).

The combined fix (option A + C in the Phase A decision) resolves the
routing ambiguity structurally: the node signature is now correct for
manual §1.5, and the scenario's step 0 depicts a visually distinctive
state (Analysis menu unfolded with Create Attribute Set (3D) visible)
that cannot be confused with the visualization workflow's baseline.

## 2026-08-05 (follow-up) — scenario rewrite + expanded node signatures

**Trigger**: on inspecting the actual manual §1.5.1a (image-only pages
118-120), the exercise procedure was found to differ from the batch-
oriented interpretation used in the first draft:

- Attribute type used in exercise: **Energy** (Bright Spot), not Similarity
- Display path used in exercise: **on-the-fly** via Tree scene → In-line
  right-click → Add > Attribute → Attributes category, NOT batch via
  Processing → Create Seismic Output → Attribute
- Tool entry: toolbar **Attribute 3D icon**, not Analysis menu

The first-draft scenario would have measured "manual faithfulness" in
reverse — an on-manual-path response would have scored low because the
scenario expected batch keywords. The scenario was rewritten to follow
the actual §1.5.1a exercise (Energy + on-the-fly path, 8 steps).

### Node signature updates (unified3 vs unified2)

| Node | Field | Before | After |
|---|---|---|---|
| `seismic_attribute_04_configure` | title | "속성 파라미터 설정" | "속성 파라미터 설정 및 attribute set 저장" |
| `seismic_attribute_04_configure` | description | ~"파라미터 설정" | "…Time gate/Compute gradient 등 설정, Attribute Name 입력, Add as new, Save on Close 체크 후 Close로 Save Attribute Set 다이얼로그에서 set 이름 입력 후 OK로 저장" |
| `seismic_attribute_04_configure` | `visual_signature.expected_dialog` | "Attribute Parameters" | "Attribute Set 3D / Save Attribute Set" |
| `seismic_attribute_04_configure` | `visual_signature.screenshot_keywords` | `[Window, Step out, Parameter, Time gate]` | `[Attribute Set 3D, Time gate, Window, Step out, Parameter, Attribute Name, Add as new, Save on Close, Save Attribute Set, attribute set name, Close, my first attribute set]` |
| `seismic_attribute_04_configure` | `expected_ui_elements` | `[parameter_fields, window_size]` | `[parameter_fields, window_size, time_gate_field, attribute_name_field, add_as_new_button, save_on_close_checkbox, save_attribute_set_dialog]` |
| `seismic_attribute_06_display` | title | "속성 볼륨 표시" | "속성 볼륨/슬라이스에 표시 (on-the-fly 또는 stored)" |
| `seismic_attribute_06_display` | description | ~"Scene에 추가하여 시각화" | "…on-the-fly 경로: 우클릭 → Add > Attribute → Select Attribute → Attributes 카테고리에서 정의된 속성 선택. 배치 경로: stored volume을 Scene에 추가" |
| `seismic_attribute_06_display` | `visual_signature.expected_dialog` | "3D Scene" | "Select Attribute / 3D Scene (attribute rendered)" |
| `seismic_attribute_06_display` | `visual_signature.screenshot_keywords` | `[Display, Scene, Color Bar]` | `[Select Attribute, Attributes, Energy, Similarity, on-the-fly, Attribute overlay, Add > Attribute, Display, Scene, Color Bar, 우클릭, inline]` |
| `seismic_attribute_06_display` | `expected_ui_elements` | `[scene_tree, attribute_display]` | `[scene_tree, attribute_display, select_attribute_dialog, attributes_category_tab, attribute_entry_list, color_bar]` |

`linked_chunks`, `step_number`, `step_type`, `parameters`, `edges` unchanged.

### Impact on `unified2` routing distribution — new estimate

The `_04_configure` and `_06_display` signature expansions add
attribute-domain vocabulary that was previously absent. In the
unified2 misroute audit (see previous entry), `seismic_attribute_04`
and `_06` were NOT among the misroute destinations (only `_01_data_load`
was). So the expansions strengthen routing for genuine attribute-domain
queries WITHOUT changing behavior for the survey_setup /
3d_visualization scenarios that were the source of unified2's
misroutes. In other words: the previous misroute magnet effect is
fixed by the `_01` correction; these `_04`/`_06` expansions are pure
coverage additions.

### Routing dry-run script — per-step expected workflow

`scripts/routing_dryrun.py` extended to consult each scenario step's
`expected_workflow_node` field (via a `NODE_TO_WORKFLOW` map built
at script start from all workflow JSONs) rather than only using the
scenario-level `SCENARIO_TO_EXPECTED_WORKFLOW`. This handles
legitimately cross-workflow scenarios like `attribute_computation`
where one step is genuinely a display-primitive action (though after
signature expansion, the router picks the attribute-workflow node
that covers "display-prep for attribute overlay" and the step is not
in fact cross-workflow at the router level).

### Verification after all changes

Dry-run (`scripts/routing_dryrun.py`):

```
opendtect__survey_setup__01:        4/4 (100%)
opendtect__3d_visualization__01:    4/4 (100%)
opendtect__attribute_computation__01: 8/8 (100%)
OVERALL:                            16/16 (100.0%)
STATUS: PASS
```

Ready to emit capture checklist and proceed to capture stage.
