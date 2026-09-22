# -*- coding: utf-8 -*-
"""Study 3 authoring — three new test-set workflows and scenario skeletons written from the
manual text ONLY (chromadb_v4 chunks), BEFORE any screenshot is captured (2026-09-22).
  C  OpendTect §1.4.2b  Tracking In 2D Viewer          -> horizon_2dviewer_142b (9 nodes / 9 steps)
  B  QGIS §3.3.5        Rule-based Classification      -> qgis_rule_classification_335 (10 / 10)
  D  QGIS §7.3.10       Reclassifying the Raster       -> qgis_reclassify_7310 (9 / 9)
Convention (as study 2): node signature = screen state AFTER the node's action (reached state);
edge instruction = the action leading to the next node; scenario step i shows node i+1's state.
Writes data/workflows/<wf>.json and data/eval/study3/scenarios_draft/<sid>.json (visual_state_gt
left as _FILL_AFTER_CAPTURE for the vision enumeration + external review).
"""
from __future__ import annotations
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OT = "645b7cdf2690408da843b9ce63c52d5b"; QG = "bf2804feea57434bb79b749134ed1df0"
AUTH = {"source": "manual text + figure OCR only (chromadb_v4)", "screenshots_seen": False, "authored_on": "2026-09-22",
        "convention": "signature = screen state AFTER the node's action (reached state); edge instruction = action leading to the next node"}


def node(wf, i, nid, title, desc, stype, dialog, elems, kws, params=(), secs=()):
    return {"id": f"{wf}_{i:02d}_{nid}", "workflow_id": wf, "step_number": i, "title": title, "description": desc, "step_type": stype,
            "visual_signature": {"expected_dialog": dialog, "expected_ui_elements": list(elems), "screenshot_keywords": list(kws)},
            "parameters": [{"name": n, "default": d, "description": x} for n, d, x in params], "manual_sections": list(secs)}


def edges(wf, nodes, instrs):
    return [{"source": nodes[i]["id"], "target": nodes[i + 1]["id"], "edge_type": "sequential", "condition": None, "instruction": ins}
            for i, ins in enumerate(instrs)]


def step(sid, i, nid, pattern, kws, alts, screen, just, must_not):
    return {"step_index": i, "screenshot_path": f"data/eval/screenshots/{sid}/step_{i}.jpg", "expected_workflow_node": nid,
            "expected_action_text_pattern": pattern, "expected_action_keywords": kws, "allowed_alternatives": alts,
            "capture_required": True, "is_error_recovery_test": False,
            "capture_instructions": {"screen_state": screen, "user_should_have_just": just, "must_not_show": must_not},
            "visual_state_gt": {"current_dialog": "_FILL_AFTER_CAPTURE", "visible_elements": [], "data_state": "_FILL_AFTER_CAPTURE", "current_action": "_FILL_AFTER_CAPTURE"}}


DONE = "(?i)^\\s*(완료|Done)\\.?\\s*$"
DONE_ALT = lambda ground: [{"pattern": "(?i)\\b(Done)\\b", "note": "English completion sentinel"}, {"pattern": ground, "note": "Ground-truth element mention for the grounding validator."}]

# ───────────────────────── C. OpendTect §1.4.2b ─────────────────────────
W = "horizon_2dviewer_142b"; S = ["1.4.2b"]
nC = [
    node(W, 1, "scene_no_2dline", "3D scene, 2D Line 트리 항목 비어 있음 (시작)", "매뉴얼 §1.4.2b 시작 상태: 3D scene에 트리가 보이고 2D Line 항목에 자식이 없음. 2D viewer 창 없음.", "setup", "OpendTect Main Window / 3D scene", ["tree_2d_line_empty", "no_2d_viewer_window"], ["2D Line", "Tree scene 1", "Elements", "no 2D Viewer window"], secs=S),
    node(W, 2, "select_2dlines_dialog", "Select 2D Lines 대화상자 열림 (Well correlation-Line 목록)", "step 1 결과: 2D Line 우클릭 > Add 로 'Select 2D Lines' 대화상자가 열림. 목록에 Well correlation-Line, STG 등이 보이고 'On OK' 동작 선택(Load default data / Display projection lines only / Select attribute)이 있음.", "action", "Select 2D Lines", ["line_list_well_correlation_line", "on_ok_action_dropdown", "load_default_data_option", "ok_button"], ["Select 2D Lines", "Filter", "Well correlation-Line", "STG", "On OK", "Load default data", "Display projection lines only", "Select attribute"], secs=S),
    node(W, 3, "2dline_loaded", "2D line(Well correlation-Line) 로드됨, Seis 속성 표시", "step 2 결과: Well correlation-Line을 선택하고 On OK = Load default data로 OK → 트리 2D Line 아래 Well correlation-Line > Seis가 생기고 3D scene에 2D 라인 단면이 표시됨. 2D viewer는 아직 없음.", "action", "OpendTect Main Window / 3D scene", ["tree_2d_line_well_correlation_line", "tree_attribute_seis", "scene_2d_line_section", "no_2d_viewer_window"], ["2D Line", "Well correlation-Line", "Seis", "no 2D Viewer window"], secs=S),
    node(W, 4, "2dviewer_open", "2D Viewer 창 열림 (Well correlation-Line)", "step 3 결과: 트리의 Seis 우클릭 > Display > 2D Viewer 로 '2D Viewer - Line: Well correlation-Line' 창이 열림. 창 안에 자체 트리(Elements: Seis / 2D Horizon / FaultStickSet …)와 단면이 보임. 2D Horizon은 아직 없음.", "action", "2D Viewer - Line: Well correlation-Line", ["2d_viewer_window", "viewer_tree_2d_horizon_empty", "viewer_section_seis"], ["2D Viewer", "Well correlation-Line", "Seis", "2D Horizon", "Wiggle", "VD", "Distance", "no 2D horizon yet"], secs=S),
    node(W, 5, "track_new_settings", "Track New: Horizon Tracking Settings 열림, <New 2D Horizon> 생성 (기본값)", "step 4–5 결과: 2D viewer 트리의 2D Horizon 우클릭 > Track New → 'Horizon Tracking Settings' 창(Mode: Section Auto-track / Method Adjacent Parent; Event type Max; Correlation Yes 80%, 기본값 그대로)과 트리에 <New 2D Horizon>. 아직 seed 없음.", "setup", "Horizon Tracking Settings", ["tracking_settings_window", "mode_section_auto_track", "method_adjacent_parent", "event_type_max", "correlation_threshold_80", "viewer_tree_new_2d_horizon", "no_seed_yet"], ["Horizon Tracking Settings", "<New 2D Horizon>", "Section Auto-track", "Adjacent Parent", "Event type", "Max", "Allowed difference (%)", "20", "Correlation threshold (%)", "80.0", "Picked on: Seis"], params=[("Method", "Adjacent Parent", "2D 추적 방법(기본값)"), ("Event type", "Max", "기본값"), ("Correlation threshold (%)", "80", "기본값")], secs=S),
    node(W, 6, "seed_picked_tracked", "Max 이벤트에 seed 픽, 라인을 따라 horizon 추적됨", "step 7–8 결과: 2D viewer 단면의 Max 반사면 위에 seed를 찍어 horizon이 라인을 따라 자동 추적됨(선으로 표시). 추가 seed로 라인 전체를 해석한 상태. 아직 저장하지 않음(<New 2D Horizon> 그대로).", "action", "2D Viewer - Line: Well correlation-Line", ["horizon_line_on_section", "viewer_tree_new_2d_horizon", "unsaved"], ["<New 2D Horizon>", "horizon", "seed", "2D Viewer", "Max event"], secs=S),
    node(W, 7, "save_as_dialog", "Output selection 대화상자 (Output 2D Horizon 이름 입력 전)", "step 14: 2D viewer 트리의 <New 2D Horizon> 우클릭 > Save as → 'Output selection' 대화상자, 'Output 2D Horizon' 이름 필드, Replace in tree, OK/Cancel/Help.", "setup", "Output selection", ["output_2d_horizon_name_field", "replace_in_tree_checkbox", "ok_button", "cancel_button"], ["Output selection", "Output 2D Horizon", "Replace in tree", "OK", "Cancel", "Help"], params=[("Output 2D Horizon", "2D_Horizon", "저장 이름")], secs=S),
    node(W, 8, "horizon_saved", "2D horizon 저장됨 (트리에 저장 이름), 2D viewer 아직 열림", "step 14 결과: 이름을 입력하고 OK → 2D viewer 트리 항목이 저장 이름(예: 2D_Horizon)으로 바뀜. 대화상자 닫힘. 2D viewer 창은 아직 열려 있음.", "action", "2D Viewer - Line: Well correlation-Line", ["viewer_tree_saved_horizon_name", "no_dialog_open", "2d_viewer_still_open"], ["2D_Horizon", "2D Viewer", "no Output selection dialog"], secs=S),
    node(W, 9, "viewer_closed_horizon_in_scene", "2D viewer 닫힘, 2D 라인과 해석한 2D horizon이 3D scene에 표시 (목표 도달)", "step 15 결과: 2D viewer를 닫으면 3D scene에 2D line과 새 2D horizon이 표시됨. 메인 트리 2D Horizon 아래에 저장 이름. 목표 도달.", "terminal", "OpendTect Main Window / 3D scene", ["no_2d_viewer_window", "tree_2d_horizon_saved_name", "scene_2d_line_with_horizon"], ["2D Horizon", "2D_Horizon", "Well correlation-Line", "no 2D Viewer window"], secs=S),
]
eC = edges(W, nC, [
    "트리의 2D Line을 우클릭하고 Add를 선택하세요",
    "목록에서 Well correlation-Line을 선택하고 On OK 동작을 Load default data로 바꾼 뒤 OK를 클릭하세요",
    "트리의 Seis(속성 이름)를 우클릭하고 Display > 2D Viewer를 선택하세요",
    "2D viewer 트리의 2D Horizon을 우클릭하고 Track New를 선택하세요",
    "Horizon Tracking Settings는 기본값 그대로 두고, 2D viewer 단면의 Max 반사면 위에 seed를 클릭해 라인을 따라 horizon을 추적하세요",
    "2D viewer 트리의 <New 2D Horizon>을 우클릭하고 Save as를 선택하세요",
    "Output 2D Horizon 이름을 입력하고 OK를 클릭하세요",
    "2D viewer 창을 닫으세요",
])
wfC = {"workflow_id": W, "name": "2D Horizon Tracking in 2D Viewer (§1.4.2b)", "software_id": "opendtect", "manual_reference": "1.4.2b Tracking In 2D Viewer, steps 1–8 and 14–15 (manual-draw steps 9–13 optional, out of scope)",
       "description": "OpendTect 매뉴얼 §1.4.2b: 2D Line 추가(Well correlation-Line, Load default data) → Seis를 2D Viewer로 표시 → 2D Horizon Track New(기본 설정) → Max 이벤트에 seed를 찍어 라인 해석 → Save as → 2D viewer 닫기. 매뉴얼만 보고 저작(study 3, 2026-09-22), 스크린샷 전 커밋.", "authoring": AUTH, "nodes": nC, "edges": eC}
sidC = "opendtect__horizon_2dviewer__01"
scC = {"scenario_id": sidC, "manual_id": OT, "manual_name": "Introduction To OpendTect and OpendTect Pro Training Manual 7.0",
       "manual_reference": "1.4.2b Tracking In 2D Viewer, steps 1–8 and 14–15 (manual-draw mode 9–13 out of scope)", "category": "horizon_tracking", "difficulty": "hard", "language": "ko",
       "goal": "F3 Demo에서 2D Line(Well correlation-Line)을 Load default data로 추가하고, 그 Seis 속성을 2D Viewer로 열어 2D Horizon을 Track New(기본 추적 설정)로 만든 뒤 Max 반사면에 seed를 찍어 라인을 해석하고, Save as로 2D horizon을 저장한 다음 2D viewer를 닫아 3D scene에 표시한다. 매뉴얼 §1.4.2b.",
       "initial_state": {"description": "F3 Demo survey 활성, 3D scene 표시. 2D Line·2D Horizon 트리 항목에 자식 없음. 2D viewer 창 없음.", "must_be_true": ["F3 Demo survey active", "no child item under 2D Line in the tree", "no 2D Viewer window open"]},
       "manual_grounding_sections": ["1.4.2b"],
       "_study3_note": "Authored from the manual only (2026-09-22) before capture; visual_state_gt filled after capture by enumeration + external review; patterns/keywords not changed after screenshots or model output are seen.",
       "steps": [
           step(sidC, 0, nC[0]["id"], "(?i)\\b(2D Line|Add|추가)\\b", ["2D Line", "Add"], [], "3D scene, tree with 2D Line item EMPTY (no child), no dialog, no 2D Viewer window.", "Nothing yet (initial state).", ["Select 2D Lines dialog", "2D Viewer window"]),
           step(sidC, 1, nC[1]["id"], "(?i)\\b(Well correlation|Load default data|OK)\\b", ["Well correlation-Line", "Load default data"], [], "'Select 2D Lines' dialog open: line list (Well correlation-Line, STG ...), 'On OK' action dropdown visible, nothing selected/confirmed yet.", "Right-clicked 2D Line > Add.", ["a 2D line already in the tree", "2D Viewer window"]),
           step(sidC, 2, nC[2]["id"], "(?i)\\b(Seis|Display|2D Viewer|2D viewer)\\b", ["Seis", "2D Viewer"], [], "Dialog closed; tree shows 2D Line > Well correlation-Line > Seis; the 2D line section is displayed in the 3D scene. No 2D Viewer window.", "Selected Well correlation-Line with Load default data and clicked OK.", ["2D Viewer window", "an open right-click menu"]),
           step(sidC, 3, nC[3]["id"], "(?i)\\b(2D Horizon|Track New|Track new)\\b", ["2D Horizon", "Track New"], [], "'2D Viewer - Line: Well correlation-Line' window open with its own tree (Seis, 2D Horizon empty ...) and the section. No 2D horizon, no tracking settings.", "Right-clicked Seis > Display > 2D Viewer.", ["<New 2D Horizon>", "Horizon Tracking Settings window"]),
           step(sidC, 4, nC[4]["id"], "(?i)\\b(seed|Seed|Max|반사면|시드|클릭)\\b", ["seed"], [{"pattern": "(?i)\\b(Close|닫|default|기본값)\\b", "note": "Manual step 5–6: leave defaults / optionally close the settings window."}], "Horizon Tracking Settings window open (defaults: Section Auto-track, Adjacent Parent, Event Max, Correlation 80%) and <New 2D Horizon> in the 2D viewer tree. NO seed yet.", "Right-clicked 2D Horizon (2D viewer tree) > Track New.", ["a seed or tracked horizon line on the section"]),
           step(sidC, 5, nC[5]["id"], "(?i)\\b(Save as|Save As|Save|저장)\\b", ["Save as"], [{"pattern": "(?i)\\b(seed|Seed|interpret|해석|더)\\b", "note": "Manual step 8: continue interpreting the full line with more seeds."}], "Horizon tracked along the 2D line (horizon line visible on the section), <New 2D Horizon> still unsaved in the 2D viewer tree. Settings window may be open or closed.", "Picked seed(s) on a Max event and let the tracker follow the line.", ["Output selection dialog", "a saved horizon name in the tree"]),
           step(sidC, 6, nC[6]["id"], "(?i)\\b(2D_Horizon|OK|이름|name|Output 2D Horizon)\\b", ["OK"], [], "'Output selection' dialog open: 'Output 2D Horizon' field empty/default, Replace in tree, OK/Cancel/Help.", "Right-clicked <New 2D Horizon> (2D viewer tree) > Save as.", ["a name already typed", "dialog already closed"]),
           step(sidC, 7, nC[7]["id"], "(?i)\\b(close|Close|닫|2D viewer|2D Viewer)\\b", ["2D Viewer"], [], "Dialog closed; the 2D viewer tree item now shows the saved name (e.g. 2D_Horizon). 2D Viewer window STILL open.", "Typed the name and clicked OK.", ["Output selection dialog", "2D Viewer closed"]),
           step(sidC, 8, nC[8]["id"], DONE, ["완료"], DONE_ALT("(?i)\\b(2D Horizon|2D_Horizon|horizon|Well correlation)\\b"), "GOAL-REACHED: 2D Viewer closed; 3D scene shows the 2D line with the interpreted 2D horizon; main tree 2D Horizon shows the saved name.", "Closed the 2D viewer.", ["2D Viewer window", "an open dialog"]),
       ],
       "completion": {"final_screenshot_path": f"data/eval/screenshots/{sidC}/step_8.jpg", "expected_done_sentinel": True, "note": "step_8 depicts the goal-achieved terminal state (2D horizon saved and displayed in the 3D scene)."}}

# ───────────────────────── B. QGIS §3.3.5 Rule-based Classification ─────────────────────────
W = "qgis_rule_classification_335"; S = ["★★★ Follow Along: Rule-based Classification"]
nB = [
    node(W, 1, "landuse_loaded", "landuse 레이어 로드됨 (AREA 필드 있음), 대화상자 없음", "§3.3.5 시작: Layers 패널에 landuse(AREA 필드 계산 완료, §3.3.3 결과), 지도에 표시. Layer Properties 닫힘.", "setup", "QGIS main window", ["layers_panel_landuse", "map_canvas", "no_dialog"], ["landuse", "Layers", "no Layer Properties dialog"], secs=S),
    node(W, 2, "properties_symbology", "Layer Properties - landuse, Symbology 탭 (Rule-based 전환 전)", "step 1–2 결과: landuse의 Layer Properties가 열리고 Symbology 탭. 렌더러는 아직 이전(Categorized/Graduated 등).", "action", "Layer Properties - landuse | Symbology", ["symbology_tab_active", "renderer_dropdown_not_rule_based", "ok_cancel_apply"], ["Layer Properties", "landuse", "Symbology", "Information", "Source", "Labels", "Apply", "OK", "Cancel"], secs=S),
    node(W, 3, "rule_based_existing_rules", "Rule-based 선택됨, 기존 규칙 목록 표시", "step 3 결과: 렌더러 드롭다운을 Rule-based로 바꾸면 현재 분류가 규칙으로 변환되어 목록(Label / Rule / Min. scale / Max. scale)에 표시됨.", "setup", "Layer Properties - landuse | Symbology", ["renderer_rule_based", "rule_list_populated", "add_rule_button", "remove_selected_rules_button"], ["Rule-based", "Label", "Rule", "Min. scale", "Max. scale", "Refine Selected Rules", "Symbol Levels..."], secs=S),
    node(W, 4, "rules_removed", "규칙 전부 삭제됨 (빈 목록)", "step 4–5 결과: 규칙을 전부 선택해 Remove selected rules → 목록이 비어 있음.", "action", "Layer Properties - landuse | Symbology", ["renderer_rule_based", "rule_list_empty", "add_rule_button"], ["Rule-based", "Label", "Rule", "empty rule list"], secs=S),
    node(W, 5, "edit_rule_dialog_empty", "Edit rule 대화상자 열림 (비어 있음)", "Add rule 클릭 결과: 'Edit Rule' 대화상자 — Label, Filter(+ 식 작성기 버튼), Test, Else, Description, Scale range, Symbol(Fill/Simple fill, Color). 아직 입력 없음.", "setup", "Edit Rule", ["label_field_empty", "filter_field_empty", "expression_builder_button", "else_checkbox", "symbol_color", "ok_cancel"], ["Edit Rule", "Label", "Filter", "Test", "Else", "Catch-all for other features", "Description", "Scale range", "Symbol", "Fill", "Simple fill", "Color", "OK", "Cancel"], secs=S),
    node(W, 6, "rule1_added", "규칙 1 'Swellendam city' 추가됨", "규칙 1 결과: Label = Swellendam city, Filter = \"name\" = 'Swellendam', 진한 회청색 채우기·테두리 없음 → OK 후 Symbology 목록에 규칙 1이 보임.", "action", "Layer Properties - landuse | Symbology", ["rule_list_1", "rule_swellendam_city"], ["Swellendam city", "\"name\" = 'Swellendam'", "Rule-based"], params=[("Label", "Swellendam city", "규칙 1"), ("Filter", "\"name\" = 'Swellendam'", "규칙 1 식")], secs=S),
    node(W, 7, "rule2_added", "규칙 2 'Other residential' 추가됨", "규칙 2 결과: Label = Other residential, Filter = \"landuse\" = 'residential' AND \"name\" <> 'Swellendam', 연한 청회색 → 목록에 규칙 1·2.", "action", "Layer Properties - landuse | Symbology", ["rule_list_2", "rule_other_residential"], ["Other residential", "\"landuse\" = 'residential' AND \"name\" <> 'Swellendam'", "Swellendam city"], params=[("Label", "Other residential", "규칙 2"), ("Filter", "\"landuse\" = 'residential' AND \"name\" <> 'Swellendam'", "규칙 2 식")], secs=S),
    node(W, 8, "rule3_added", "규칙 3 'Big non residential areas' 추가됨", "규칙 3 결과: Label = Big non residential areas, Filter = \"landuse\" <> 'residential' AND \"AREA\" >= 605000, 중간 녹색 → 목록에 규칙 1–3.", "action", "Layer Properties - landuse | Symbology", ["rule_list_3", "rule_big_non_residential"], ["Big non residential areas", "\"landuse\" <> 'residential' AND \"AREA\" >= 605000", "Other residential", "Swellendam city"], params=[("Label", "Big non residential areas", "규칙 3"), ("Filter", "\"landuse\" <> 'residential' AND \"AREA\" >= 605000", "규칙 3 식")], secs=S),
    node(W, 9, "rule4_else_added", "규칙 4 'Small non residential areas' (Else) 추가됨, 적용 전", "규칙 4 결과: Label = Small non residential areas, Filter 대신 Else 체크, 연한 녹색 → 목록에 규칙 1–4(마지막 Rule = ELSE). 아직 Apply/OK 전이라 지도는 이전 상태.", "action", "Layer Properties - landuse | Symbology", ["rule_list_4", "rule_else", "apply_button"], ["Small non residential areas", "ELSE", "Big non residential areas", "Other residential", "Swellendam city", "Apply", "OK"], params=[("Label", "Small non residential areas", "규칙 4"), ("Else", "checked", "규칙 4는 Else")], secs=S),
    node(W, 10, "applied_map", "적용 완료: 지도에 4개 규칙 렌더링 (목표 도달)", "step 9 결과: Apply/OK → 지도에 Swellendam(진회청), 기타 주거(연청회), 큰 비주거(중녹), 작은 비주거(연녹) 4가지로 렌더링. 대화상자 닫힘(OK) 또는 열린 채(Apply). 목표 도달.", "terminal", "QGIS main window", ["map_canvas_four_classes", "layers_panel_landuse_rule_legend"], ["landuse", "Swellendam city", "Other residential", "Big non residential areas", "Small non residential areas"], secs=S),
]
eB = edges(W, nB, [
    "Layers 패널에서 landuse를 우클릭하고 Properties…(레이어 속성)를 열어 Symbology 탭으로 가세요",
    "렌더러 드롭다운을 Rule-based로 바꾸세요",
    "규칙을 모두 선택(클릭·드래그)하고 Remove selected rules 버튼으로 기존 규칙을 전부 삭제하세요",
    "Add rule 버튼을 클릭해 Edit rule 대화상자를 여세요",
    "Label에 Swellendam city, Filter에 \"name\" = 'Swellendam'(Expression String Builder 사용 가능)을 입력하고 진한 회청색·테두리 없음으로 설정한 뒤 OK를 클릭하세요",
    "Add rule로 Label = Other residential, Filter = \"landuse\" = 'residential' AND \"name\" <> 'Swellendam', 연한 청회색 규칙을 추가하세요",
    "Add rule로 Label = Big non residential areas, Filter = \"landuse\" <> 'residential' AND \"AREA\" >= 605000, 중간 녹색 규칙을 추가하세요",
    "Add rule로 Label = Small non residential areas 를 만들고 Filter 대신 Else를 체크한 뒤 연한 녹색으로 설정하세요",
    "Apply(또는 OK)를 클릭해 심볼로지를 적용하세요",
])
wfB = {"workflow_id": W, "name": "Rule-based Classification of landuse (§3.3.5)", "software_id": "qgis", "manual_reference": "QGIS Training Manual 3.44 §3.3.5 Follow Along: Rule-based Classification (pp.117–120)",
       "description": "QGIS 매뉴얼 §3.3.5: landuse 레이어의 Symbology를 Rule-based로 바꾸고 기존 규칙을 지운 뒤 Swellendam city / Other residential / Big non residential areas / Small non residential areas(Else) 네 규칙을 매뉴얼 식대로 추가해 적용한다. 매뉴얼만 보고 저작(study 3, 2026-09-22), 스크린샷 전 커밋.", "authoring": AUTH, "nodes": nB, "edges": eB}
sidB = "qgis__rule_classification__01"
scB = {"scenario_id": sidB, "manual_id": QG, "manual_name": "QGIS Training Manual 3.44", "manual_reference": "§3.3.5 Follow Along: Rule-based Classification, steps 1–9 (pp.117–120). Prerequisite §3.3.3 (AREA field on landuse) is part of the initial state.",
       "category": "symbology", "difficulty": "hard", "language": "ko",
       "goal": "QGIS Training Data의 landuse 레이어를 Rule-based 심볼로지로 분류한다: 기존 규칙을 모두 지우고, Swellendam city(\"name\" = 'Swellendam', 진한 회청색), Other residential(\"landuse\" = 'residential' AND \"name\" <> 'Swellendam', 연한 청회색), Big non residential areas(\"landuse\" <> 'residential' AND \"AREA\" >= 605000, 중간 녹색), Small non residential areas(Else, 연한 녹색) 네 규칙을 추가해 적용한다. 매뉴얼 §3.3.5.",
       "initial_state": {"description": "QGIS Desktop 3.44. Layers 패널에 landuse 레이어(QGIS-Training-Data exercise_data/landuse.sqlite; §3.3.3에 따라 Field Calculator로 AREA 필드($area) 계산 완료)가 로드되어 지도에 표시됨. Layer Properties 대화상자 닫힘.", "must_be_true": ["QGIS main window visible", "landuse layer loaded and visible", "landuse has an AREA field", "Layer Properties dialog closed"]},
       "manual_grounding_sections": ["★★★ Follow Along: Rule-based Classification"],
       "_study3_note": "Authored from the manual only (2026-09-22) before capture; visual_state_gt filled after capture; patterns/keywords not changed after screenshots or model output are seen.",
       "steps": [
           step(sidB, 0, nB[0]["id"], "(?i)\\b(Properties|속성|Layer Properties|Symbology|더블\\s?클릭|double-?click)\\b", ["Properties"], [], "QGIS main window, landuse in Layers panel (with AREA field), map shown, NO dialog open.", "Nothing yet (initial state).", ["Layer Properties dialog"]),
           step(sidB, 1, nB[1]["id"], "(?i)\\b(Rule-?based|규칙 기반|규칙)\\b", ["Rule-based"], [], "Layer Properties - landuse open on the Symbology tab; renderer dropdown still NOT Rule-based (previous renderer).", "Opened landuse properties and clicked the Symbology tab.", ["Rule-based already selected"]),
           step(sidB, 2, nB[2]["id"], "(?i)\\b(Remove|삭제|제거|select all|모두 선택|전체 선택|drag|드래그)\\b", ["Remove"], [], "Renderer = Rule-based; the auto-converted rules are listed (several rows). Nothing selected yet.", "Switched the renderer to Rule-based.", ["empty rule list", "Edit Rule dialog"]),
           step(sidB, 3, nB[3]["id"], "(?i)\\b(Add rule|Add Rule|규칙 추가|추가|\\+)\\b", ["Add rule"], [], "Rule-based renderer with an EMPTY rule list.", "Selected all rules and clicked Remove selected rules.", ["any rule row", "Edit Rule dialog"]),
           step(sidB, 4, nB[4]["id"], "(?i)\\b(Swellendam city|Swellendam|Label|Filter|\"name\")\\b", ["Swellendam"], [], "'Edit Rule' dialog open, Label and Filter EMPTY, default symbol.", "Clicked Add rule.", ["a label already typed"]),
           step(sidB, 5, nB[5]["id"], "(?i)\\b(Other residential|residential|Add rule|규칙 추가)\\b", ["Other residential"], [], "Back in Symbology: rule list shows ONE rule (Swellendam city, \"name\" = 'Swellendam'). Edit Rule closed.", "Filled rule 1 and clicked OK.", ["Edit Rule dialog", "a second rule"]),
           step(sidB, 6, nB[6]["id"], "(?i)\\b(Big non residential|non residential|605000|AREA|Add rule|규칙 추가)\\b", ["Big non residential"], [], "Rule list shows TWO rules (Swellendam city; Other residential).", "Added rule 2 and clicked OK.", ["Edit Rule dialog", "a third rule"]),
           step(sidB, 7, nB[7]["id"], "(?i)\\b(Small non residential|Else|ELSE|Add rule|규칙 추가)\\b", ["Else"], [], "Rule list shows THREE rules (…; Big non residential areas).", "Added rule 3 and clicked OK.", ["Edit Rule dialog", "an ELSE rule"]),
           step(sidB, 8, nB[8]["id"], "(?i)\\b(Apply|OK|적용)\\b", ["Apply"], [], "Rule list shows FOUR rules, the last with Rule = ELSE (Small non residential areas). Symbology NOT yet applied (map behind still shows the old rendering).", "Added the Else rule and clicked OK in Edit Rule.", ["Edit Rule dialog", "map already rendered with the 4 new colours"]),
           step(sidB, 9, nB[9]["id"], DONE, ["완료"], DONE_ALT("(?i)\\b(landuse|Swellendam|residential|rule|규칙)\\b"), "GOAL-REACHED: map rendered with the four rule colours; Layers panel legend lists the four labels; Layer Properties closed (OK) or still open after Apply.", "Clicked Apply / OK.", ["an unrelated dialog"]),
       ],
       "completion": {"final_screenshot_path": f"data/eval/screenshots/{sidB}/step_9.jpg", "expected_done_sentinel": True, "note": "step_9 depicts the goal-achieved terminal state (four rule classes rendered)."}}

# ───────────────────────── D. QGIS §7.3.10 Reclassifying the Raster ─────────────────────────
W = "qgis_reclassify_7310"; S = ["★★☆ Follow Along: Reclassifying the Raster"]
nD = [
    node(W, 1, "aspect_loaded", "aspect 래스터 로드됨, Reclassify 도구 닫힘", "§7.3.10 시작: Layers에 aspect(0–360°) 래스터가 있고 지도에 표시. Processing Toolbox는 열려 있을 수 있음. Reclassify by table 대화상자 없음.", "setup", "QGIS main window", ["layers_panel_aspect", "map_canvas", "no_reclassify_dialog"], ["aspect", "Layers", "Processing Toolbox", "no Reclassify by table dialog"], secs=S),
    node(W, 2, "reclassify_dialog_open", "Reclassify by table 대화상자 열림 (Raster layer 미선택/기본값)", "step 1 결과: Processing Toolbox › Raster analysis › Reclassify by table(또는 검색)을 열어 대화상자가 표시됨: Raster layer, Band number, Reclassification table(Fixed table … 버튼), Advanced parameters, Reclassified raster, Run/Close.", "action", "Reclassify by Table", ["raster_layer_dropdown", "band_number", "reclassification_table_button", "reclassified_raster_output", "run_button"], ["Reclassify by Table", "Parameters", "Log", "Raster layer", "Band number", "Band 1 (Gray)", "Reclassification table", "Fixed table", "Advanced parameters", "Reclassified raster", "Run", "Close"], secs=S),
    node(W, 3, "raster_layer_aspect", "Raster layer = aspect 선택됨", "step 2 결과: Raster layer 드롭다운에서 aspect 선택. 테이블은 아직 비어 있음(Fixed table (0x3)).", "setup", "Reclassify by Table", ["raster_layer_aspect", "reclassification_table_empty"], ["Raster layer", "aspect", "Fixed table (0x3)", "Reclassification table"], params=[("Raster layer", "aspect", "입력 래스터")], secs=S),
    node(W, 4, "fixed_table_dialog", "Fixed table 대화상자 열림 (행 없음)", "step 3 결과: Reclassification table의 … 버튼 → 'Fixed table' 대화상자(Minimum / Maximum / Value 열, Add Row / Remove Row(s) / Remove All, OK/Cancel). 아직 행 없음.", "setup", "Fixed table", ["columns_minimum_maximum_value", "add_row_button", "remove_row_button", "ok_cancel", "no_rows"], ["Fixed table", "Minimum", "Maximum", "Value", "Add Row", "Remove Row(s)", "Remove All", "OK", "Cancel"], secs=S),
    node(W, 5, "table_filled", "5행 입력 완료 후 OK → Fixed table (5x3)", "step 4 결과: Add Row 5회, (0,45,1) (315,360,1) (45,135,2) (135,225,3) (225,315,4) 입력 후 OK → 대화상자에 'Fixed table (5x3)' 표시. 출력 경로는 아직 기본(임시).", "action", "Reclassify by Table", ["reclassification_table_5x3", "reclassified_raster_output_default"], ["Fixed table (5x3)", "Reclassification table", "Reclassified raster", "[Save to temporary file]"], params=[("rows", "0-45→1, 315-360→1, 45-135→2, 135-225→3, 225-315→4", "aspect 재분류 표")], secs=S),
    node(W, 6, "output_path_set", "Reclassified raster 출력 = exercise_data/raster_analysis/reclassified.tif", "step 5 결과: Reclassified raster의 … › Save to File… 로 raster_analysis 폴더에 reclassified.tif 지정. 아직 Run 전.", "setup", "Reclassify by Table", ["reclassified_raster_path_set", "run_button"], ["reclassified.tif", "raster_analysis", "Reclassified raster", "Run"], params=[("Reclassified raster", "exercise_data/raster_analysis/reclassified.tif", "출력 파일")], secs=S),
    node(W, 7, "ran_layer_added", "Run 실행 완료: reclassified 레이어 추가됨", "step 6 결과: Run → 알고리즘 실행, Layers 패널에 reclassified 레이어(값 1–4, Singleband gray)가 추가되고 지도에 표시. 대화상자는 닫혔거나 Log 탭 완료 상태.", "action", "QGIS main window", ["layers_panel_reclassified", "map_canvas_reclassified_gray"], ["reclassified", "Layers", "Singleband gray", "1", "4"], secs=S),
    node(W, 8, "styling_paletted", "Layer Styling 패널: Paletted/Unique values 선택 (Classify 전)", "스타일 step 1–2 결과: Layer Styling 패널을 열고 렌더러를 Singleband gray → Paletted/Unique values로 바꿈. 값 목록은 아직 비어 있음(Classify 전).", "setup", "Layer Styling", ["layer_styling_panel", "renderer_paletted_unique_values", "classify_button", "value_list_empty"], ["Layer Styling", "reclassified", "Paletted/Unique values", "Band", "Band 1 (Gray)", "Color ramp", "Random colors", "Classify", "Delete All"], secs=S),
    node(W, 9, "classified_map", "Classify 완료: 값 1–4에 색 배정, 지도 렌더링 (목표 도달)", "스타일 step 3 결과: Classify 클릭 → Value/Color/Label 목록에 1,2,3,4와 임의 색, 지도가 4색으로 렌더링. 목표 도달.", "terminal", "Layer Styling", ["value_list_1_to_4", "map_canvas_four_colours"], ["Classify", "Value", "Color", "Label", "1", "2", "3", "4", "reclassified"], secs=S),
]
eD = edges(W, nD, [
    "Processing Toolbox에서 Raster analysis › Reclassify by table 도구를 여세요(검색창에 reclassify 입력 가능)",
    "Raster layer 드롭다운에서 aspect를 선택하세요",
    "Reclassification table 옆의 … 버튼을 클릭해 Fixed table 대화상자를 여세요",
    "Add Row를 5번 눌러 행을 만들고 Minimum/Maximum/Value를 0-45→1, 315-360→1, 45-135→2, 135-225→3, 225-315→4 로 입력한 뒤 OK를 클릭하세요",
    "Reclassified raster의 … 버튼 › Save to File… 로 exercise_data/raster_analysis 폴더에 reclassified.tif 로 저장 경로를 지정하세요",
    "Run을 클릭하세요",
    "Layer Styling 패널을 열고(reclassified 선택) 렌더러를 Singleband gray에서 Paletted/Unique values로 바꾸세요",
    "Classify 버튼을 클릭해 값 1–4에 색을 배정하세요",
])
wfD = {"workflow_id": W, "name": "Reclassify the aspect raster by table (§7.3.10)", "software_id": "qgis", "manual_reference": "QGIS Training Manual 3.44 §7.3.10 Follow Along: Reclassifying the Raster (pp.286–289)",
       "description": "QGIS 매뉴얼 §7.3.10: Processing Toolbox의 Reclassify by table로 aspect 래스터(0–360°)를 1(N)/2(E)/3(S)/4(W)로 재분류(Fixed table 5행), reclassified.tif로 저장·실행한 뒤 Layer Styling에서 Paletted/Unique values + Classify로 표시한다. 매뉴얼만 보고 저작(study 3, 2026-09-22), 스크린샷 전 커밋.", "authoring": AUTH, "nodes": nD, "edges": eD}
sidD = "qgis__reclassify_raster__01"
scD = {"scenario_id": sidD, "manual_id": QG, "manual_name": "QGIS Training Manual 3.44", "manual_reference": "§7.3.10 Follow Along: Reclassifying the Raster, tool steps 1–6 and styling steps 1–3 (pp.286–289). Prerequisite: aspect raster from §7.3.x Aspect tool is part of the initial state.",
       "category": "raster_analysis", "difficulty": "hard", "language": "ko",
       "goal": "QGIS에서 aspect 래스터(0–360°)를 Processing Toolbox의 Reclassify by table로 방위 4구간 — 1 = North(0–45, 315–360), 2 = East(45–135), 3 = South(135–225), 4 = West(225–315) — 로 재분류해 exercise_data/raster_analysis/reclassified.tif 로 저장·실행하고, Layer Styling에서 Paletted/Unique values 렌더러로 바꿔 Classify로 값 1–4에 색을 배정한다. 매뉴얼 §7.3.10.",
       "initial_state": {"description": "QGIS Desktop 3.44. Layers 패널에 aspect 래스터(QGIS-Training-Data exercise_data/raster/SRTM/srtm_41_19.tif 에서 Raster › Raster terrain analysis › Aspect로 계산, exercise_data/raster_analysis/aspect.tif)가 로드되어 표시됨. Reclassify by table 대화상자 닫힘.", "must_be_true": ["QGIS main window visible", "aspect raster layer loaded and visible", "Reclassify by table dialog closed", "exercise_data/raster_analysis folder exists"]},
       "manual_grounding_sections": ["★★☆ Follow Along: Reclassifying the Raster"],
       "_study3_note": "Authored from the manual only (2026-09-22) before capture; visual_state_gt filled after capture; patterns/keywords not changed after screenshots or model output are seen.",
       "steps": [
           step(sidD, 0, nD[0]["id"], "(?i)\\b(Reclassify by table|Reclassify|재분류|Raster analysis|Toolbox|reclassify)\\b", ["Reclassify"], [], "QGIS main window with the aspect raster loaded (Processing Toolbox may be open). NO Reclassify by table dialog.", "Nothing yet (initial state).", ["Reclassify by table dialog"]),
           step(sidD, 1, nD[1]["id"], "(?i)\\b(aspect|Raster layer|래스터 레이어)\\b", ["aspect"], [], "'Reclassify by Table' dialog open; Raster layer NOT yet set to aspect (default/first layer), table empty.", "Opened the Reclassify by table tool.", ["Fixed table dialog", "Raster layer = aspect"]),
           step(sidD, 2, nD[2]["id"], "(?i)\\b(Reclassification table|Fixed table|\\.\\.\\.|…|테이블|표)\\b", ["Reclassification table"], [], "Raster layer = aspect selected; Reclassification table still 'Fixed table (0x3)'.", "Chose aspect as the Raster layer.", ["Fixed table dialog open"]),
           step(sidD, 3, nD[3]["id"], "(?i)\\b(Add Row|Add row|행 추가|45|315|Minimum|Maximum|Value)\\b", ["Add Row"], [], "'Fixed table' dialog open with columns Minimum / Maximum / Value and NO rows.", "Clicked the … button of Reclassification table.", ["rows already filled"]),
           step(sidD, 4, nD[4]["id"], "(?i)\\b(reclassified\\.tif|reclassified|Save to File|raster_analysis|Reclassified raster|저장)\\b", ["reclassified"], [], "Back in Reclassify by Table: Reclassification table shows 'Fixed table (5x3)'; Reclassified raster still '[Save to temporary file]'.", "Added 5 rows with the manual values and clicked OK.", ["Fixed table dialog", "reclassified.tif already set"]),
           step(sidD, 5, nD[5]["id"], "(?i)\\b(Run|실행)\\b", ["Run"], [], "Reclassified raster path set to …/raster_analysis/reclassified.tif; NOT yet run.", "Set the output file via … › Save to File.", ["reclassified layer in the Layers panel"]),
           step(sidD, 6, nD[6]["id"], "(?i)\\b(Layer Styling|Styling|Paletted|Unique values|스타일)\\b", ["Layer Styling"], [], "Algorithm ran: 'reclassified' layer in the Layers panel (Singleband gray, values 1–4), dialog closed or on Log tab. Layer Styling panel NOT showing Paletted yet.", "Clicked Run.", ["Paletted/Unique values already selected"]),
           step(sidD, 7, nD[7]["id"], "(?i)\\b(Classify|분류)\\b", ["Classify"], [], "Layer Styling panel for reclassified with renderer = Paletted/Unique values and an EMPTY value list (before Classify).", "Opened Layer Styling and switched the renderer to Paletted/Unique values.", ["values 1–4 already listed"]),
           step(sidD, 8, nD[8]["id"], DONE, ["완료"], DONE_ALT("(?i)\\b(reclassified|Classify|Paletted|1|2|3|4)\\b"), "GOAL-REACHED: value list shows 1,2,3,4 with colours; map rendered in four colours.", "Clicked Classify.", ["an unrelated dialog"]),
       ],
       "completion": {"final_screenshot_path": f"data/eval/screenshots/{sidD}/step_8.jpg", "expected_done_sentinel": True, "note": "step_8 depicts the goal-achieved terminal state (four aspect classes coloured)."}}


def main():
    out_wf = ROOT / "data/workflows"; out_sc = ROOT / "data/eval/study3/scenarios_draft"; out_sc.mkdir(parents=True, exist_ok=True)
    for wf in (wfC, wfB, wfD):
        (out_wf / f"{wf['workflow_id']}.json").write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("workflow", wf["workflow_id"], len(wf["nodes"]), "nodes", len(wf["edges"]), "edges")
    for sc in (scC, scB, scD):
        (out_sc / f"{sc['scenario_id']}.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("scenario", sc["scenario_id"], len(sc["steps"]), "steps")


if __name__ == "__main__":
    main()
