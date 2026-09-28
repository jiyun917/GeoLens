# -*- coding: utf-8 -*-
"""Study 4 authoring — three new test-set workflows and scenario skeletons written from the manual text
ONLY (chromadb_v4 chunks), BEFORE any screenshot is captured (2026-09-28). Same conventions as study 3
(scripts/study3_author.py): node signature = screen state AFTER the node's action (reached state); edge
instruction = the action leading to the next node; scenario step i shows node i+1's state.
  E  OpendTect §1.5.2a  Spectral Decomposition (attribute definition part, manual steps 1-4, 9-13)
                         -> spectral_decomp_152a (9 nodes / 9 steps)
  F  QGIS §6.1.4        Creating Your Own Projection -> qgis_custom_projection_614 (9 / 9)
  G  QGIS §7.3.6        Finding the north-facing aspect -> qgis_aspect_north_736 (6 / 6)
Outputs go to STAGING directories (data/eval/study4/workflows_draft, data/eval/study4/scenarios_draft) so a
running benchmark never sees them; they are moved into data/workflows/ and relinked after the study-4
development verification has finished.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OT = "645b7cdf2690408da843b9ce63c52d5b"; QG = "bf2804feea57434bb79b749134ed1df0"
AUTH = {"source": "manual text + figure OCR only (chromadb_v4); main-window / Processing dialog titles follow the study-2/3 screens of the same application versions", "screenshots_seen": False, "authored_on": "2026-09-28",
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
NOTE = "Authored from the manual only (2026-09-28) before capture; visual_state_gt filled after capture by enumeration + external review; patterns/keywords not changed after screenshots or model output are seen."

# ───────────────────────── E. OpendTect §1.5.2a Spectral Decomposition ─────────────────────────
W = "spectral_decomp_152a"; S = ["1.5.2a"]
nE = [
    node(W, 1, "scene_start", "3D scene, 3D Horizon 트리 항목에 color-blended horizon 없음 (시작)", "§1.5.2a 시작 상태: F3 Demo 3D scene, 트리에 3D Horizon 항목이 있으나 Demo 1 --> MFS4 color-blended 표시 없음. Attribute Set 창 없음.", "start",
         "F3 Demo 2023 - [Scene 1]", ["tree_3d_horizon_item", "no_color_blended_horizon", "no_attribute_set_window"], ["3D Horizon", "Tree scene 1", "F3 Demo 2023"], secs=S),
    node(W, 2, "select_horizon_dialog", "Select Input Horizon(s) 대화상자 열림 (Add Color Blended)", "step 1 결과: 트리 3D Horizon 우클릭 > Add Color Blended… → 'Select Input Horizon(s)' 대화상자: Filter, 목록(Demo 0 --> FS4, Demo 1 --> MFS4, …), Area subselection + Select…, OK/Cancel/Help. 아직 선택·범위 없음.", "dialog",
         "Select Input Horizon(s)", ["horizon_list", "area_subselection_row", "select_button", "ok_cancel"], ["Select Input Horizon", "Demo 1 --> MFS4", "Demo 0 --> FS4", "Area subselection", "Select...", "Filter"], secs=S),
    node(W, 3, "position_ranges_entered", "Demo 1 --> MFS4 선택, Position 대화상자에 In-line 200–650 / Cross-line 500–1000 입력 (OK 전)", "step 2 결과: 목록에서 Demo 1 --> MFS4를 선택하고 Area subselection의 Select…를 클릭 → 'Position'(Specify Position) 대화상자에서 In-line Range 200 650, Cross-line Range 500 1000 을 입력한 상태(OK 누르기 전).", "dialog",
         "Position", ["inline_range_200_650", "crossline_range_500_1000", "ok_cancel"], ["Position", "Specify Position", "In-line Range", "Cross-line Range", "200", "650", "500", "1000", "Step"],
         params=[("In-line Range", "200-650", "manual §1.5.2a step 2"), ("Cross-line Range", "500-1000", "manual §1.5.2a step 2")], secs=S),
    node(W, 4, "horizon_color_blended", "Demo 1 --> MFS4 가 color-blended 로 표시됨 (트리에 4개 속성 레이어)", "step 2 결과(OK, OK): 트리 3D Horizon 아래 Demo 1 --> MFS4 가 4개의 속성 레이어(아래 3개는 R/G/B 채널 색 플래그)와 함께 표시되고 scene에 horizon이 보임. 대화상자 없음.", "action",
         "F3 Demo 2023 - [Scene 1]", ["tree_demo1_mfs4", "four_attribute_layers", "rgb_channel_flags", "horizon_in_scene"], ["Demo 1 --> MFS4", "3D Horizon", "Tree scene 1", "F3 Demo 2023"], secs=S),
    node(W, 5, "attribute_set_open", "Attribute Set 3D 창 열림 (빈 세트, <not saved>)", "step 3 결과: 툴바의 Attribute Set 3D 아이콘(A) 클릭 → 'Attribute Set 3D' 창: File 메뉴, Attribute set <not saved>, 속성 목록 비어 있음, 속성 종류 드롭다운, Input Data, Attribute Name, Add as new, Close.", "dialog",
         "Attribute Set 3D", ["attribute_type_dropdown", "input_data_field", "attribute_name_field", "add_as_new_button", "empty_attribute_list"], ["Attribute Set 3D", "Attribute set <not saved>", "Input Data", "Attribute Name", "Add as new", "Close", "Save on Close"], secs=S),
    node(W, 6, "sd_24hz_added", "SD_24Hz[-8,24ms] 정의 후 Add as new (목록에 1개)", "step 4, 9–11 결과: 속성 = Spectral Decomposition, Input Data = 4 Dip steered median filter, Transform type FFT, Time gate (ms) -8 24, Output frequency (Hz) 24, Step 4, Attribute Name SD_24Hz[-8,24ms] → Add as new → 목록에 SD_24Hz[-8,24ms] 1개.", "action",
         "Attribute Set 3D", ["attribute_list_sd_24", "spectral_decomposition_selected", "time_gate_minus8_24", "output_frequency_24_step_4"], ["Spectral Decomposition", "SD_24Hz[-8,24ms]", "4 Dip steered median filter", "Time gate (ms)", "-8", "24", "Output frequency (Hz)", "24.0", "Step", "4.0", "FFT"],
         params=[("Time gate (ms)", "[-8, 24]", "manual §1.5.2a step 4"), ("Output frequency (Hz)", "24", "step 10"), ("Step (Hz)", "4", "step 10"), ("Input Data", "4 Dip steered median filter", "step 9")], secs=S),
    node(W, 7, "sd_44hz_added", "SD_44Hz[-8,24ms] 추가됨 (목록에 2개)", "step 12 결과(중간 주파수): Output frequency 44, Attribute Name SD_44Hz[-8,24ms] → Add as new → 목록에 SD_24Hz, SD_44Hz.", "action",
         "Attribute Set 3D", ["attribute_list_sd_24_44", "output_frequency_44"], ["SD_44Hz[-8,24ms]", "SD_24Hz[-8,24ms]", "44.0", "Spectral Decomposition"], params=[("Output frequency (Hz)", "44", "step 12")], secs=S),
    node(W, 8, "sd_64hz_added", "SD_64Hz[-8,24ms] 추가됨 (목록에 3개)", "step 12 결과(높은 주파수): Output frequency 64, Attribute Name SD_64Hz[-8,24ms] → Add as new → 목록에 SD_24Hz, SD_44Hz, SD_64Hz.", "action",
         "Attribute Set 3D", ["attribute_list_sd_24_44_64", "output_frequency_64"], ["SD_64Hz[-8,24ms]", "SD_44Hz[-8,24ms]", "SD_24Hz[-8,24ms]", "64.0", "Spectral Decomposition"], params=[("Output frequency (Hz)", "64", "step 12")], secs=S),
    node(W, 9, "attribute_set_closed", "Attribute Set 창 닫힘 (세트 이름 Spectral Decomposition 저장), 3D scene 만 표시 (목표 도달)", "step 13 결과: Close(Save on Close 켜짐, 이름 예: Spectral Decomposition) → Attribute Set 3D 창이 사라지고 3D scene과 트리(Demo 1 --> MFS4 color-blended)만 보임.", "verification",
         "F3 Demo 2023 - [Scene 1]", ["no_attribute_set_window", "tree_demo1_mfs4", "four_attribute_layers"], ["Demo 1 --> MFS4", "3D Horizon", "Tree scene 1", "F3 Demo 2023"], secs=S),
]
eE = edges(W, nE, [
    "트리의 3D Horizon을 우클릭하고 Add Color Blended…를 선택하세요",
    "목록에서 Demo 1 --> MFS4를 선택하고, Area subselection의 Select…를 클릭해 In-line Range 200–650, Cross-line Range 500–1000을 입력하세요",
    "OK를 클릭해 범위를 적용하고, 다시 OK를 클릭해 horizon을 표시하세요",
    "툴바의 Attribute Set 3D 아이콘(A)을 클릭해 Attribute Set 3D 창을 여세요",
    "속성 종류로 Spectral Decomposition을 선택하고 Input Data = 4 Dip steered median filter, Time gate [-8, 24] ms, Output frequency 24 Hz, Step 4 Hz, Attribute Name SD_24Hz[-8,24ms]를 입력한 뒤 Add as new를 클릭하세요",
    "Output frequency를 44 Hz로 바꾸고 Attribute Name을 SD_44Hz[-8,24ms]로 바꾼 뒤 Add as new를 클릭하세요",
    "Output frequency를 64 Hz로 바꾸고 Attribute Name을 SD_64Hz[-8,24ms]로 바꾼 뒤 Add as new를 클릭하세요",
    "Close를 클릭해 Attribute Set 창을 닫으세요(Save on Close가 켜져 있으면 세트 이름 Spectral Decomposition을 입력)",
])
wfE = {"workflow_id": W, "name": "Spectral Decomposition attributes on a color-blended horizon (§1.5.2a)", "software_id": "opendtect",
       "manual_reference": "1.5.2a Spectral Decomposition, steps 1–4 and 9–13 (amplitude-spectrum inspection 5–8 and horizon-output 14–25 out of scope; frequencies 24/44/64 Hz taken from the manual)",
       "description": "OpendTect 매뉴얼 §1.5.2a: 3D Horizon > Add Color Blended…로 Demo 1 --> MFS4를 In-line 200–650 / Cross-line 500–1000 범위로 표시 → Attribute Set 3D에서 Spectral Decomposition 속성(Input 4 Dip steered median filter, Time gate [-8,24] ms, Step 4 Hz)을 24/44/64 Hz로 세 개 정의(SD_24Hz[-8,24ms] 등, Add as new) → Close.",
       "authoring": AUTH, "nodes": nE, "edges": eE}
sidE = "opendtect__spectral_decomp__01"
scE = {"scenario_id": sidE, "manual_id": OT, "manual_name": "Introduction To OpendTect and OpendTect Pro Training Manual 7.0",
       "manual_reference": "1.5.2a Spectral Decomposition, steps 1–4 and 9–13 (pp.130–133)", "category": "attribute_analysis", "difficulty": "hard", "language": "ko",
       "goal": "F3 Demo에서 3D Horizon Demo 1 --> MFS4를 Add Color Blended…로 In-line 200–650, Cross-line 500–1000 범위만 표시한 뒤, Attribute Set 3D에서 Spectral Decomposition 속성 세 개(Input Data 4 Dip steered median filter, Time gate [-8, 24] ms, Output frequency 24 / 44 / 64 Hz, Step 4 Hz, 이름 SD_24Hz[-8,24ms] / SD_44Hz[-8,24ms] / SD_64Hz[-8,24ms])를 Add as new로 정의하고 창을 닫는다.",
       "initial_state": {"description": "F3 Demo 2023 survey 활성, 3D scene 표시, 트리에 3D Horizon 항목이 있으나 color-blended horizon 없음. Attribute Set 창 없음. (4 Dip steered median filter 볼륨은 stored data로 존재.)", "must_be_true": ["F3 Demo survey active", "no color-blended horizon in the tree", "no Attribute Set 3D window"]},
       "manual_grounding_sections": ["1.5.2a"], "_study4_note": NOTE,
       "steps": [
           step(sidE, 0, nE[0]["id"], "(?i)\\b(3D Horizon|Add Color Blended|Color Blended|color blended|컬러 블렌드|블렌드)\\b", ["Add Color Blended"], [],
                "3D scene with the tree; 3D Horizon item WITHOUT a color-blended horizon; no dialog; no Attribute Set window.", "Nothing yet (initial state).", ["Select Input Horizon(s) dialog", "Attribute Set 3D window"]),
           step(sidE, 1, nE[1]["id"], "(?i)\\b(MFS4|Demo 1|Area subselection|Select\\.\\.\\.|Select…|Select|영역|범위|부분 선택)\\b", ["MFS4"], [],
                "'Select Input Horizon(s)' dialog open (Add Color Blended): horizon list incl. Demo 1 --> MFS4, Area subselection row with Select…, OK/Cancel. Nothing selected yet, no Position dialog.", "Right-clicked 3D Horizon > Add Color Blended….", ["a selected horizon", "Position dialog"]),
           step(sidE, 2, nE[2]["id"], "(?i)\\b(OK|확인|적용)\\b", ["OK"], [{"pattern": "(?i)\\b(200|650|500|1000|In-line|Cross-line|Inline|Crossline)\\b", "note": "Restating the ranges to be applied is accepted (manual step 2 values)."}],
                "'Position' (Specify Position) dialog open with In-line Range 200 650 and Cross-line Range 500 1000 already typed (Step 1); OK NOT yet clicked. Demo 1 --> MFS4 is selected in the dialog behind.", "Selected Demo 1 --> MFS4, clicked Select… and typed the two ranges.", ["horizon displayed in the scene"]),
           step(sidE, 3, nE[3]["id"], "(?i)\\b(Attribute Set|Attribute set|attribute set|속성 세트|속성 집합|속성 셋|A 아이콘|Attributes 3D)\\b", ["Attribute Set"], [],
                "Dialogs closed; tree shows 3D Horizon > Demo 1 --> MFS4 with four attribute layers (three with R/G/B colour flags); horizon visible in the 3D scene; no Attribute Set window.", "Clicked OK (ranges) and OK (display).", ["Attribute Set 3D window", "Select Input Horizon(s) dialog"]),
           step(sidE, 4, nE[4]["id"], "(?i)\\b(Spectral Decomposition|Spectral|스펙트럼|Dip steered median|-8|24)\\b", ["Spectral Decomposition"], [],
                "'Attribute Set 3D' window open, attribute set <not saved>, EMPTY attribute list, default attribute type; Input Data empty.", "Clicked the Attribute Set 3D toolbar icon.", ["SD_24Hz in the attribute list"]),
           step(sidE, 5, nE[5]["id"], "(?i)\\b(44|SD_44Hz|Add as new|Output frequency)\\b", ["44"], [],
                "Attribute Set 3D window: list shows ONE attribute SD_24Hz[-8,24ms]; fields still show Spectral Decomposition, Input 4 Dip steered median filter, Time gate -8 24, Output frequency 24, Step 4.", "Defined SD_24Hz[-8,24ms] and clicked Add as new.", ["SD_44Hz in the list"]),
           step(sidE, 6, nE[6]["id"], "(?i)\\b(64|SD_64Hz|Add as new|Output frequency)\\b", ["64"], [],
                "Attribute Set 3D window: list shows TWO attributes (SD_24Hz[-8,24ms], SD_44Hz[-8,24ms]); Output frequency field shows 44.", "Changed frequency to 44, name to SD_44Hz[-8,24ms], clicked Add as new.", ["SD_64Hz in the list"]),
           step(sidE, 7, nE[7]["id"], "(?i)\\b(Close|닫|Save on Close|저장|Spectral Decomposition)\\b", ["Close"], [{"pattern": "(?i)\\b(Done|완료)\\b", "note": "Declaring the three attributes done is accepted only with the closing action; bare sentinel handled by the scorer."}],
                "Attribute Set 3D window: list shows THREE attributes (SD_24Hz, SD_44Hz, SD_64Hz[-8,24ms]); Output frequency field shows 64. Window still open.", "Changed frequency to 64, name to SD_64Hz[-8,24ms], clicked Add as new.", ["window closed"]),
           step(sidE, 8, nE[8]["id"], DONE, ["완료"], DONE_ALT("(?i)\\b(Spectral|SD_|attribute|속성|MFS4)\\b"),
                "GOAL-REACHED: Attribute Set 3D window closed (set saved, e.g. as Spectral Decomposition); 3D scene with the color-blended Demo 1 --> MFS4 horizon and the tree only.", "Clicked Close (and named the set on Save on Close).", ["Attribute Set 3D window"]),
       ],
       "completion": {"final_screenshot_path": f"data/eval/screenshots/{sidE}/step_8.jpg", "expected_done_sentinel": True, "note": "step_8 depicts the goal-achieved terminal state (three SD attributes defined, window closed)."}}

# ───────────────────────── F. QGIS §6.1.4 Creating Your Own Projection ─────────────────────────
W = "qgis_custom_projection_614"; S = ["★★★ Follow Along: Creating Your Own Projection"]
WKT_SHORT = 'PROJCRS["unknown", BASEGEOGCRS["unknown", DATUM["unknown", ELLIPSOID["unknown",6371000,0, LENGTHUNIT["metre",1, ID["EPSG",9001]]]], PRIMEM["Greenwich",0, ANGLEUNIT["degree",0.0174532925199433], ID["EPSG",8901]]], CONVERSION["unknown", METHOD["Van Der Grinten"], PARAMETER["Longitude of natural origin",0, ANGLEUNIT["degree",0.0174532925199433], ID["EPSG",8802]], PARAMETER["False easting",0, LENGTHUNIT["metre",1], ID["EPSG",8806]], PARAMETER["False northing",0, LENGTHUNIT["metre",1], ID["EPSG",8807]]], CS[Cartesian,2], AXIS["(E)",east, ORDER[1], LENGTHUNIT["metre",1, ID["EPSG",9001]]], AXIS["(N)",north, ORDER[2], LENGTHUNIT["metre",1, ID["EPSG",9001]]]]'
nF = [
    node(W, 1, "oceans_loaded", "새 프로젝트에 world/oceans.shp 로드됨 (EPSG:4326), 대화상자 없음", "§6.1.4 step 1–2: 새 맵에 oceans 레이어가 로드되어 지도에 세계 해양이 보임. 상태 표시줄 CRS = EPSG:4326. 대화상자 없음.", "start",
         "Untitled Project - QGIS", ["layers_panel_oceans", "map_canvas_world", "statusbar_crs_epsg4326"], ["oceans", "EPSG:4326", "Untitled Project"], secs=S),
    node(W, 2, "custom_crs_dialog", "Custom Projections 대화상자 열림 (Options — User Defined CRS, 항목 없음)", "step 3 결과: Settings ► Custom Projections… → 'Options — User Defined CRS' 대화상자: 상단 Name/Parameters 표(비어 있음), + / - 버튼, Name, Definition(Format, Parameters), Validate, Test, OK/Cancel/Help.", "dialog",
         "Options — User Defined CRS", ["crs_table_empty", "add_new_crs_button", "name_field", "format_dropdown", "parameters_field", "validate_button"], ["User Defined CRS", "Custom Projections", "Name", "Parameters", "Format", "Validate", "Test", "Definition"], secs=S),
    node(W, 3, "new_crs_row_added", "Add new CRS(+) 클릭: 표에 새 CRS 행 추가됨 (이름 미입력)", "step 4 결과: + (Add new CRS) 클릭 → 표에 새 행(new CRS)이 생기고 Name 필드가 편집 가능. Parameters 비어 있음.", "action",
         "Options — User Defined CRS", ["crs_table_one_row", "new_crs_row", "name_field_empty"], ["new CRS", "Name", "Parameters", "WKT (Recommended)", "Proj String"], secs=S),
    node(W, 4, "name_and_format_set", "Name = Van der Grinten I, Format = WKT (Recommended)", "step 5–6 결과: Name 필드에 Van der Grinten I 입력, Format 드롭다운 WKT (Recommended). Parameters 아직 비어 있음.", "setup",
         "Options — User Defined CRS", ["name_van_der_grinten", "format_wkt", "parameters_empty"], ["Van der Grinten I", "WKT (Recommended)", "Parameters"], params=[("Name", "Van der Grinten I", "manual step 5"), ("Format", "WKT (Recommended)", "manual step 6")], secs=S),
    node(W, 5, "wkt_entered", "Parameters에 Van Der Grinten WKT 문자열 입력됨 (OK 전)", "step 7 결과: Parameters 필드에 PROJCRS[\"unknown\", … METHOD[\"Van Der Grinten\"] … ] WKT 문자열이 들어 있음(Validate 가능). OK 아직 안 누름.", "setup",
         "Options — User Defined CRS", ["parameters_wkt_projcrs", "method_van_der_grinten", "ellipsoid_6371000"], ["PROJCRS", "Van Der Grinten", "6371000", "BASEGEOGCRS", "Van der Grinten I"], params=[("Parameters (WKT)", WKT_SHORT, "manual step 7")], secs=S),
    node(W, 6, "crs_saved_dialog_closed", "OK: 사용자 정의 CRS 저장, 대화상자 닫힘 (프로젝트 CRS 아직 EPSG:4326)", "step 8 결과: OK → 대화상자 닫힘, 메인 창. 상태 표시줄 CRS 버튼은 아직 EPSG:4326.", "action",
         "Untitled Project - QGIS", ["no_dialog", "statusbar_crs_epsg4326", "map_canvas_world"], ["EPSG:4326", "oceans", "Untitled Project"], secs=S),
    node(W, 7, "project_crs_dialog", "프로젝트 CRS 대화상자 열림 (Project Properties — CRS)", "step 9 결과: 상태 표시줄 오른쪽의 현재 CRS 버튼 클릭 → 'Project Properties — CRS' 대화상자: Filter, Recently Used / Predefined CRS 목록, 미리보기. 아직 필터·선택 없음.", "dialog",
         "Project Properties — CRS", ["filter_field", "crs_list", "recently_used", "predefined_crs", "ok_cancel_apply"], ["Project Properties", "Coordinate Reference System", "Filter", "Recently Used", "Predefined Coordinate Reference Systems", "No CRS"], secs=S),
    node(W, 8, "van_der_grinten_selected", "Filter 'Van der Grinten' → 사용자 정의 CRS Van der Grinten I 선택됨 (OK 전)", "step 10 결과: Filter에 Van der Grinten 입력 → User Defined Coordinate Systems 아래 Van der Grinten I (USER:100000) 선택. OK 아직 안 누름.", "setup",
         "Project Properties — CRS", ["filter_van_der_grinten", "user_defined_crs_selected", "usercrs_100000"], ["Van der Grinten I", "USER:100000", "User Defined Coordinate Systems", "Filter"], secs=S),
    node(W, 9, "map_reprojected", "OK: 지도가 Van der Grinten I 로 재투영됨 (원형 세계지도, 목표 도달)", "step 11 결과: OK → 지도가 원형(Van der Grinten)으로 재투영되고 상태 표시줄 CRS 버튼에 USER:100000 표시.", "verification",
         "Untitled Project - QGIS", ["map_canvas_circular_world", "statusbar_crs_user100000", "no_dialog"], ["USER:100000", "oceans", "Untitled Project"], secs=S),
]
eF = edges(W, nF, [
    "Settings 메뉴에서 Custom Projections…를 여세요",
    "Add new CRS 버튼(+)을 클릭해 새 CRS 항목을 만드세요",
    "Name에 Van der Grinten I 를 입력하고 Format을 WKT (Recommended)로 선택하세요",
    "Parameters에 매뉴얼의 WKT 문자열을 입력하세요: " + WKT_SHORT,
    "OK를 클릭해 사용자 정의 CRS를 저장하고 대화상자를 닫으세요",
    "상태 표시줄 오른쪽의 현재 CRS 버튼(EPSG:4326)을 클릭해 프로젝트 CRS 대화상자를 여세요",
    "Filter에 Van der Grinten 을 입력하고 User Defined Coordinate Systems 아래의 Van der Grinten I 을 선택하세요",
    "OK를 클릭해 프로젝트 CRS를 적용하세요",
])
wfF = {"workflow_id": W, "name": "Create a custom Van der Grinten I projection and apply it (§6.1.4)", "software_id": "qgis",
       "manual_reference": "QGIS Training Manual 3.44 §6.1.4 Follow Along: Creating Your Own Projection, steps 1–11 (pp.190–192)",
       "description": "QGIS 매뉴얼 §6.1.4: Settings ► Custom Projections…에서 + 로 새 CRS를 만들고 Name = Van der Grinten I, Format = WKT, Parameters = 매뉴얼의 PROJCRS WKT(METHOD Van Der Grinten, 반경 6371000) 입력 → OK → 상태 표시줄 CRS 버튼으로 프로젝트 CRS를 Van der Grinten I 로 바꿔 지도를 재투영.",
       "authoring": AUTH, "nodes": nF, "edges": eF}
sidF = "qgis__custom_projection__01"
scF = {"scenario_id": sidF, "manual_id": QG, "manual_name": "QGIS Training Manual 3.44", "manual_reference": "§6.1.4 Follow Along: Creating Your Own Projection, steps 1–11 (pp.190–192)",
       "category": "projections", "difficulty": "hard", "language": "ko",
       "goal": "QGIS에서 world/oceans.shp 를 로드한 새 프로젝트에 사용자 정의 투영 'Van der Grinten I'(Settings ► Custom Projections…, Format WKT, 매뉴얼 §6.1.4의 PROJCRS WKT 문자열: METHOD Van Der Grinten, 반경 6371000 m)을 만들고, 상태 표시줄의 CRS 버튼으로 프로젝트 CRS를 그 투영으로 바꿔 지도를 원형으로 재투영한다.",
       "initial_state": {"description": "QGIS Desktop 3.44, 새 프로젝트, Layers 패널에 oceans(QGIS-Training-Data exercise_data/world/oceans.shp) 로드, 프로젝트 CRS EPSG:4326. 대화상자 없음.", "must_be_true": ["oceans layer loaded", "project CRS EPSG:4326", "no dialog open"]},
       "manual_grounding_sections": ["★★★ Follow Along: Creating Your Own Projection"], "_study4_note": NOTE,
       "steps": [
           step(sidF, 0, nF[0]["id"], "(?i)\\b(Custom Projections|Custom Projection|사용자 정의 투영|사용자 정의 좌표|Settings|설정)\\b", ["Custom Projections"], [],
                "QGIS main window, oceans layer loaded, world map shown, status-bar CRS EPSG:4326, no dialog.", "Nothing yet (initial state).", ["Custom Projections dialog"]),
           step(sidF, 1, nF[1]["id"], "(?i)\\b(Add new CRS|\\+|추가|new CRS|새 CRS|새 좌표)\\b", ["Add new CRS"], [{"pattern": "(?i)\\b(Van der Grinten|Name|이름)\\b", "note": "Typing the name first is accepted (the + is implied in some versions)."}],
                "'Options — User Defined CRS' (Custom Projections) dialog open with an EMPTY CRS table; Name and Parameters empty.", "Opened Settings ► Custom Projections….", ["a CRS row in the table", "text in Parameters"]),
           step(sidF, 2, nF[2]["id"], "(?i)\\b(Van der Grinten|WKT)\\b", ["Van der Grinten"], [],
                "Same dialog with ONE new row (new CRS) added after +; Name field empty/default, Parameters empty.", "Clicked Add new CRS (+).", ["text in Parameters"]),
           step(sidF, 3, nF[3]["id"], "(?i)\\b(PROJCRS|Van Der Grinten|6371000|BASEGEOGCRS)\\b", ["PROJCRS"], [],
                "Same dialog: Name = Van der Grinten I, Format = WKT (Recommended); Parameters still EMPTY.", "Typed the name and set the format.", ["text in Parameters"]),
           step(sidF, 4, nF[4]["id"], "(?i)\\b(OK|확인|Validate|검증)\\b", ["OK"], [],
                "Same dialog: Parameters contains the PROJCRS WKT (METHOD Van Der Grinten); OK NOT yet clicked.", "Pasted/typed the WKT string.", ["dialog closed"]),
           step(sidF, 5, nF[5]["id"], "(?i)\\b(CRS|EPSG:4326|status bar|상태 표시줄|상태바|Project Properties|프로젝트 속성|Current CRS|좌표계)\\b", ["CRS"], [],
                "Dialog closed; main window; status-bar CRS button still shows EPSG:4326; map unchanged.", "Clicked OK in the Custom Projections dialog.", ["Project Properties dialog"]),
           step(sidF, 6, nF[6]["id"], "(?i)\\b(Van der Grinten|Filter|필터|USER:100000|User Defined)\\b", ["Van der Grinten"], [],
                "'Project Properties — CRS' dialog open; Filter empty; nothing new selected.", "Clicked the status-bar CRS button.", ["Van der Grinten selected"]),
           step(sidF, 7, nF[7]["id"], "(?i)\\b(OK|확인|Apply|적용)\\b", ["OK"], [],
                "Same dialog: Filter shows Van der Grinten; Van der Grinten I (USER:100000) selected under User Defined Coordinate Systems; OK NOT yet clicked.", "Filtered and selected the custom CRS.", ["reprojected map"]),
           step(sidF, 8, nF[8]["id"], DONE, ["완료"], DONE_ALT("(?i)\\b(Van der Grinten|USER:100000|재투영|projection|투영)\\b"),
                "GOAL-REACHED: dialog closed; map shows the world in the circular Van der Grinten projection; status-bar CRS shows USER:100000.", "Clicked OK.", ["Project Properties dialog"]),
       ],
       "completion": {"final_screenshot_path": f"data/eval/screenshots/{sidF}/step_8.jpg", "expected_done_sentinel": True, "note": "step_8 depicts the goal-achieved terminal state (map reprojected to the custom CRS)."}}

# ───────────────────────── G. QGIS §7.3.6 Finding the north-facing aspect ─────────────────────────
W = "qgis_aspect_north_736"; S = ["★★☆ Follow Along: Finding the north-facing aspect"]
nG = [
    node(W, 1, "aspect_loaded", "aspect 래스터 로드됨, Raster calculator 닫힘", "§7.3.6 시작: Layers에 aspect(0–360°) 래스터(§7.3.5 결과)가 있고 지도에 표시. Processing Toolbox 열려 있을 수 있음. Raster calculator 대화상자 없음.", "start",
         "Untitled Project - QGIS", ["layers_panel_aspect", "map_canvas_aspect", "processing_toolbox"], ["aspect", "Processing Toolbox", "Untitled Project"], secs=S),
    node(W, 2, "raster_calc_open", "Raster calculator(Processing) 대화상자 열림 (식 비어 있음)", "step 1 결과: Processing Toolbox › Raster analysis › Raster calculator 더블클릭 → 'Raster Calculator' 대화상자: Layers 목록(aspect@1 …), Operators, Expression(비어 있음), Reference layer(s) [optional], Cell size, Output extent, Output CRS, Calculated 출력(임시 파일), Run.", "dialog",
         "Raster Analysis - Raster Calculator", ["layers_list_aspect_at_1", "operators_panel", "expression_empty", "reference_layers_row", "output_row", "run_button"], ["Raster Calculator", "Expression", "Layers", "Operators", "aspect@1", "Reference layer(s)", "Cell size", "Output extent", "Output CRS", "Calculated"], secs=S),
    node(W, 3, "expression_entered", "Expression = aspect@1 <= 90 OR aspect@1 >= 270 (Expression is valid)", "step 2 결과: Expression 필드에 aspect@1 <= 90 OR aspect@1 >= 270 입력 → 'Expression is valid'. Reference layer 아직 없음.", "setup",
         "Raster Analysis - Raster Calculator", ["expression_aspect_north", "expression_is_valid"], ["aspect@1 <= 90 OR aspect@1 >= 270", "Expression is valid", "aspect@1"], params=[("Expression", "aspect@1 <= 90 OR aspect@1 >= 270", "manual step 2")], secs=S),
    node(W, 4, "reference_layer_set", "Reference layer(s) = aspect (1 inputs selected)", "step 3–4 결과: Reference layer(s)의 … 버튼 → 다중 선택 대화상자에서 aspect 체크 → OK → '1 inputs selected'.", "setup",
         "Raster Analysis - Raster Calculator", ["reference_layers_1_selected"], ["1 inputs selected", "Reference layer(s)", "aspect"], params=[("Reference layer(s)", "aspect", "manual step 4")], secs=S),
    node(W, 5, "output_set", "Calculated 출력 = exercise_data/raster_analysis/aspect_north.tif (Run 전)", "step 5 결과: Calculated(출력)의 … › Save to File… 로 raster_analysis 폴더에 aspect_north.tif 지정. 아직 Run 안 함.", "setup",
         "Raster Analysis - Raster Calculator", ["output_aspect_north_tif"], ["aspect_north.tif", "raster_analysis", "Calculated", "Run"], params=[("Output", "aspect_north.tif", "manual step 5")], secs=S),
    node(W, 6, "ran_layer_added", "Run 완료: aspect_north 레이어(0/1) 추가됨 (목표 도달)", "step 6 결과: Run → 알고리즘 실행, Layers 패널에 aspect_north 레이어(값 0/1, 흑백)가 추가되고 지도에 북향 픽셀이 흰색으로 표시. 대화상자 닫힘(또는 Close).", "verification",
         "Untitled Project - QGIS", ["layers_panel_aspect_north", "map_canvas_binary"], ["aspect_north", "Untitled Project"], secs=S),
]
eG = edges(W, nG, [
    "Processing Toolbox에서 Raster analysis › Raster calculator를 더블클릭해 여세요(검색창에 raster calculator 입력 가능)",
    "Expression에 aspect@1 <= 90 OR aspect@1 >= 270 을 입력하세요",
    "Reference layer(s) 옆의 … 버튼을 클릭해 aspect 레이어를 선택하고 OK를 클릭하세요",
    "Calculated(출력)의 … 버튼 › Save to File… 로 exercise_data/raster_analysis 폴더에 aspect_north.tif 로 저장 경로를 지정하세요",
    "Run을 클릭하세요",
])
wfG = {"workflow_id": W, "name": "North-facing aspect with the Raster calculator (§7.3.6)", "software_id": "qgis",
       "manual_reference": "QGIS Training Manual 3.44 §7.3.6 Follow Along: Finding the north-facing aspect, steps 1–6 (pp.263–264)",
       "description": "QGIS 매뉴얼 §7.3.6: Processing Toolbox의 Raster analysis › Raster calculator에서 식 aspect@1 <= 90 OR aspect@1 >= 270 을 입력하고 Reference layer = aspect, 출력 aspect_north.tif 로 저장한 뒤 Run → 북향 픽셀이 1인 래스터 생성.",
       "authoring": AUTH, "nodes": nG, "edges": eG}
sidG = "qgis__aspect_north__01"
scG = {"scenario_id": sidG, "manual_id": QG, "manual_name": "QGIS Training Manual 3.44", "manual_reference": "§7.3.6 Follow Along: Finding the north-facing aspect, steps 1–6 (pp.263–264). Prerequisite §7.3.5 (aspect raster).",
       "category": "raster_analysis", "difficulty": "medium", "language": "ko",
       "goal": "QGIS에서 aspect 래스터로부터 북향(aspect ≤ 90° 또는 ≥ 270°) 픽셀만 1인 래스터를 만든다: Processing Toolbox의 Raster analysis › Raster calculator에서 식 aspect@1 <= 90 OR aspect@1 >= 270, Reference layer = aspect, 출력 raster_analysis/aspect_north.tif 로 저장하고 Run.",
       "initial_state": {"description": "QGIS Desktop 3.44. Layers 패널에 aspect 래스터(§7.3.5 결과, C:/GeoLensData/aspect.tif 등)가 로드되어 지도에 표시. Raster calculator 대화상자 없음.", "must_be_true": ["aspect raster loaded", "no Raster Calculator dialog"]},
       "manual_grounding_sections": ["★★☆ Follow Along: Finding the north-facing aspect"], "_study4_note": NOTE,
       "steps": [
           step(sidG, 0, nG[0]["id"], "(?i)\\b(Raster calculator|Raster Calculator|래스터 계산기|Raster analysis|Toolbox|calculator)\\b", ["Raster calculator"], [],
                "QGIS main window with the aspect raster loaded (Processing Toolbox may be open); NO Raster Calculator dialog.", "Nothing yet (initial state).", ["Raster Calculator dialog"]),
           step(sidG, 1, nG[1]["id"], "(?i)\\b(aspect@1|<= 90|>= 270|Expression|식|수식)\\b", ["aspect@1"], [],
                "'Raster Calculator' (Processing) dialog open: Layers list (aspect@1 …), Operators, Expression EMPTY, Reference layer(s) empty, output = temporary file.", "Double-clicked Raster analysis › Raster calculator in the toolbox.", ["text in Expression"]),
           step(sidG, 2, nG[2]["id"], "(?i)\\b(Reference layer|참조 레이어|reference|aspect)\\b", ["Reference layer"], [{"pattern": "(?i)\\b(aspect_north|Output|출력|Save to File|Calculated|저장)\\b", "note": "Setting the output first is accepted (manual steps 3–5 are order-free in the dialog)."}],
                "Same dialog: Expression = aspect@1 <= 90 OR aspect@1 >= 270 ('Expression is valid'); Reference layer(s) still empty; output temporary.", "Typed the expression.", ["1 inputs selected"]),
           step(sidG, 3, nG[3]["id"], "(?i)\\b(aspect_north|Output|출력|Save to File|Calculated|저장)\\b", ["aspect_north"], [{"pattern": "(?i)\\b(Run|실행)\\b", "note": "Running with a temporary output is accepted (the manual names the file but the analysis is identical)."}],
                "Same dialog: Reference layer(s) shows '1 inputs selected' (aspect); output still temporary.", "Chose aspect via the … button and clicked OK.", ["aspect_north in the output path"]),
           step(sidG, 4, nG[4]["id"], "(?i)\\b(Run|실행)\\b", ["Run"], [],
                "Same dialog: Calculated = …/raster_analysis/aspect_north.tif; NOT yet run.", "Set the output file via … › Save to File.", ["aspect_north layer in the Layers panel"]),
           step(sidG, 5, nG[5]["id"], DONE, ["완료"], DONE_ALT("(?i)\\b(aspect_north|aspect|north|북향)\\b"),
                "GOAL-REACHED: algorithm ran; aspect_north layer (0/1) in the Layers panel; map shows north-facing pixels; dialog closed.", "Clicked Run (and closed the dialog).", ["Raster Calculator dialog"]),
       ],
       "completion": {"final_screenshot_path": f"data/eval/screenshots/{sidG}/step_5.jpg", "expected_done_sentinel": True, "note": "step_5 depicts the goal-achieved terminal state (aspect_north raster created)."}}


def main():
    out_wf = ROOT / "data/eval/study4/workflows_draft"; out_sc = ROOT / "data/eval/study4/scenarios_draft"
    out_wf.mkdir(parents=True, exist_ok=True); out_sc.mkdir(parents=True, exist_ok=True)
    for wf in (wfE, wfF, wfG):
        (out_wf / f"{wf['workflow_id']}.json").write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("workflow", wf["workflow_id"], len(wf["nodes"]), "nodes", len(wf["edges"]), "edges")
    for sc in (scE, scF, scG):
        (out_sc / f"{sc['scenario_id']}.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("scenario", sc["scenario_id"], len(sc["steps"]), "steps")


if __name__ == "__main__":
    main()
