# -*- coding: utf-8 -*-
"""Study 3 GT draft builder (same rule as study 2 / v3 Task A): every label the vision model read is
appended to visual_state_gt.visible_elements; current_dialog / data_state / current_action come from
the screen facts recorded in data/eval/study3/CAPTURE_NOTES.md (main session, screenshot inspection).
Steps whose screenshot is missing (C s8) or flagged for recapture (C s6, s7) get provisional facts and
an empty label list; they are rebuilt after the recapture + re-enumeration.
Output: data/eval/study3/scenarios_gt_draft/<sid>.json → external review session.
"""
from __future__ import annotations
import glob, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ENUM = ROOT / "data/eval/study3/gt_visible_elements_enum_study2.json"   # written by gt_enumerate_study2.py --out-prefix data/eval/study3/gt_visible_elements
QGIS_COMMON = "QGIS main window title '*Untitled Project — QGIS', menu bar, toolbars, Layers panel, status bar (Coordinate / Scale / Magnifier / Rotation / Render / EPSG)."
FACTS = {
    "opendtect__horizon_2dviewer__01": {
        0: ("OpendTect Main Window / 3D scene", "Empty 3D scene (survey box only, no data displayed). Tree: In-line … Annotations categories; 2D Line and 2D Horizon have no child items. No dialog, no 2D Viewer window. Toolbar Cross-line 0, Step 0.", "User is about to add a 2D line (right-click 2D Line > Add)."),
        1: ("Select 2D Lines", "'Select 2D Lines' dialog open over the empty scene: Filter box, list of 2D lines (19981104-1-04_0037 … 20021203-2-03_0038 — this F3 Demo 2023 dataset has no 'Well correlation-Line'), 'On OK' dropdown = 'Display projection lines only', OK / Cancel / ?. Nothing selected yet.", "User is about to select a 2D line and set On OK = Load default data."),
        2: ("OpendTect Main Window / 3D scene", "2D line loaded: tree 2D Line > 19981104-1-04_0037 > Seismic (attribute name is 'Seismic'); the line's seismic section is displayed in the 3D scene. No dialog, no 2D Viewer window.", "User is about to right-click the Seismic attribute > Display > 2D Viewer."),
        3: ("2D Viewer - Line: 19981104-1-04_0037", "'2D Viewer - Line: 19981104-1-04_0037' window open in front of the main window: its own Tree items (Wiggle, VD checked, 2D Horizon, FaultStickSet, PointSet), a Time (ms) vs Trace number section, colour range -8.7372 / 8.7372, OD Seismic 1. No 2D horizon, no tracking settings. Status bar shows coordinates, Value, Line/TrcNr/SP.", "User is about to right-click 2D Horizon in the 2D viewer tree > Track New."),
        4: ("Horizon Tracking Settings - <New 2D Horizon 1>", "'Horizon Tracking Settings - <New 2D Horizon 1>' window open (Mode tab: Section Auto-track selected, Manual Draw, Snap to Event; Method Adjacent Parent; If tracking fails: Extrapolate / Stop (Stop selected); tabs Mode, Event, Correlation, Properties; Close / ? / ▷). Main tree shows 2D Horizon > <New 2D Horizon 1>. The 2D viewer is behind. No seed picked, no horizon line.", "User is about to leave the defaults and pick a seed on a Max event in the 2D viewer."),
        5: ("2D Viewer - Line: 19981104-1-04_0037 + Horizon Tracking Settings", "Horizon tracked: a green horizon line runs along the section in the 2D viewer; 2D viewer tree shows 2D Horizon > <New 2D Horizon 1>; Horizon Tracking Settings window still open (Mode tab). Not saved yet.", "User is about to save the horizon (right-click <New 2D Horizon 1> in the 2D viewer tree > Save as)."),
        6: ("Output selection", "PROVISIONAL (recapture requested): 'Output selection' dialog — 'Output 2D Horizon' field empty with dropdown and Select..., 'Replace in tree' checked, OK / Cancel / ?. Expected: 2D Viewer window visible with <New 2D Horizon 1> in its tree. Captured version shows the dialog over the main window with the 2D viewer not visible.", "User is about to type the output name and click OK."),
        7: ("2D Viewer - Line: 19981104-1-04_0037", "PROVISIONAL (recapture requested): dialog closed; the horizon is saved under its new name (tree shows the saved name instead of <New 2D Horizon 1>); expected: 2D Viewer window still open. Captured version shows the main tree 2D Horizon > 2D_Horizon with the 2D viewer not visible.", "User is about to close the 2D viewer."),
        8: ("OpendTect Main Window / 3D scene", "PROVISIONAL (not captured yet): 2D Viewer closed; 3D scene shows the 2D line with the interpreted 2D horizon; main tree 2D Horizon shows the saved name. Goal reached.", "Goal reached."),
    },
    "qgis__reclassify_raster__01": {
        0: ("QGIS main window", QGIS_COMMON + " Layers: aspect (Band 1 (Gray) 360 … 0.093473) on top, srtm_41_19 (Band 1 (Gray) 1,548 … 0). Map shows the grey aspect raster. Processing Toolbox panel open on the right with search text 'aspect' (Recently used, Raster terrain analysis > Aspect, GDAL > Raster analysis > Aspect, GRASS > Raster > r.plane/r.shade/r.slope.aspect). No Reclassify dialog. EPSG:32733.", "User is about to open Raster analysis > Reclassify by table from the Processing Toolbox."),
        1: ("Raster Analysis - Reclassify by Table", "'Raster Analysis - Reclassify by Table' dialog open (Parameters / Log tabs). Raster layer is ALREADY 'aspect [EPSG:32733]' (auto-filled from the active layer — no user selection needed); Band number Band 1 (Gray); Reclassification table 'Fixed table (0x3)' with … button; Advanced Parameters collapsed; Reclassified raster '[Save to temporary file]'; 'Open output file after running algorithm' checked; 0% progress; Advanced / Run as Batch Process… / Run / Close / Help. Right pane: 'Reclassify by table' description. Toolbox search shows 'reclassify'.", "User is about to open the reclassification table (… button); the Raster layer is already set."),
        2: ("Raster Analysis - Reclassify by Table", "Identical to step 1 (Raster layer aspect [EPSG:32733] auto-filled; Fixed table (0x3); output temporary). Only the status-bar coordinate differs. The 'choose aspect' action of the manual required no user input on this screen — state is known from the session history.", "User is about to click the … button of Reclassification table."),
        3: ("Raster Analysis - Reclassify by Table > Reclassification table", "The dialog now shows the 'Reclassification table' panel (back-arrow, columns Minimum / Maximum / Value, buttons Add Row, Remove Row(s), Remove All, OK, Cancel). No rows yet. Right pane description unchanged.", "User is about to add 5 rows with the manual's values and click OK."),
        4: ("Raster Analysis - Reclassify by Table", "Back in the parameters view: Reclassification table = 'Fixed table (5x3)'; Raster layer aspect [EPSG:32733]; Reclassified raster still '[Save to temporary file]'.", "User is about to set the output file (… > Save to File…)."),
        5: ("Raster Analysis - Reclassify by Table", "Reclassified raster = 'C:/GeoLensData/reclassified.tif' (user chose this folder instead of exercise_data/raster_analysis); Fixed table (5x3); not yet run.", "User is about to click Run."),
        6: ("QGIS main window", QGIS_COMMON + " Algorithm ran: Layers now reclassified (Band 1 (Gray) 4 … 1) on top of aspect and srtm_41_19; map shows the grey reclassified raster; dialog closed; Toolbox shows Recently used / Raster analysis > Reclassify by layer, Reclassify by table / Vector table > Add unique value index field.", "User is about to open the Layer Styling panel and switch the renderer to Paletted/Unique values."),
        7: ("Layer Styling", QGIS_COMMON + " Layer Styling panel open on the right for 'reclassified': renderer 'Paletted/Unique values', Band 'Band 1 (Gray)', Color ramp 'Random colors', empty Value / Color / Label table, Classify, +, −, Delete All, …; Layer Rendering (Blending mode Normal, Brightness/Saturation/Contrast 0, Gamma 1,00, Invert colors, Grayscale Off, Colorize, Strength 100%, Reset), Resampling (Zoomed in Nearest Neighbour); Live update checked, Apply. Map still grey. Scale 1:300266.", "User is about to click Classify."),
        8: ("Layer Styling", QGIS_COMMON + " Classify done: Value/Color/Label rows 1 (green), 2 (cyan), 3 (purple), 4 (red); map rendered in the four colours; Layers legend under reclassified shows 1, 2, 3, 4. Goal reached.", "Goal reached."),
    },
    "qgis__rule_classification__01": {
        0: ("QGIS main window", QGIS_COMMON + " Layers: landuse (single layer). Map shows landuse polygons in categorized colours (green, purple, orange, red, …). No dialog. EPSG:4326, Scale 1:117758.", "User is about to open Layer Properties of landuse (Symbology tab)."),
        1: ("Layer Properties - landuse — Symbology", "'Layer Properties - landuse — Symbology' dialog open: renderer 'Categorized', Value 'landuse', Symbol, Color ramp 'Random colors', category table (cemetery, conservation, farmland, forest, grass, industrial, orchard, reservoir, residential, village_green, vineyard, all other values), Classify / + / − / Delete All / Delete Unused, Advanced, Layer Rendering, Style / OK / Cancel / Apply / Help; left tabs Information … Legend. Renderer not yet Rule-based.", "User is about to switch the renderer dropdown to Rule-based."),
        2: ("Layer Properties - landuse — Symbology", "Renderer 'Rule-based': rule table (Label / Rule / Min. Scale / Max. Scale / Count / Duplicate Count) filled with the auto-converted rules cemetery … vineyard (\"landuse\" = '…') and a final ELSE row; buttons +, −, edit, Σ, Refine Selected Rules, Symbol Levels…. Nothing selected.", "User is about to select all rules and remove them."),
        3: ("Layer Properties - landuse — Symbology", "Rule-based renderer with an EMPTY rule table (header only). +, −, edit, Σ buttons; Refine Selected Rules; Symbol Levels….", "User is about to click Add rule (+)."),
        4: ("Edit Rule", "'Edit Rule' dialog open over the Symbology page: Label (empty), Filter (empty) with ε button and Test, Else 'Catch-all for other features', Description, Scale range (Minimum (exclusive) 1:100000, Maximum (inclusive) 1:1000, greyed), Symbol: Fill > Simple Fill (purple), OK / Cancel / Help. Behind it the rule table shows one new row '(no filter)'.", "User is about to enter Label 'Swellendam city' and Filter \"name\" = 'Swellendam', set the colour, and click OK."),
        5: ("Layer Properties - landuse — Symbology", "Rule table shows ONE rule: 'Swellendam …' (label truncated) with Rule \"name\" = 'Swellendam' (blue swatch). Edit Rule closed.", "User is about to add rule 2 (Other residential)."),
        6: ("Layer Properties - landuse — Symbology", "Rule table shows TWO rules: Swellendam … (\"name\" = 'Swellendam'), Other residen… (\"landuse\" = 'residential' …, pale blue-grey swatch).", "User is about to add rule 3 (Big non residential areas)."),
        7: ("Layer Properties - landuse — Symbology", "Rule table shows THREE rules: … plus Big non resid… (\"landuse\" <> 'residential' …, green swatch).", "User is about to add rule 4 (Small non residential areas, Else)."),
        8: ("Layer Properties - landuse — Symbology", "Rule table shows FOUR rules; the last is Small non re… with Rule ELSE (pale green swatch). Symbology not yet applied (OK / Apply not pressed).", "User is about to click Apply / OK."),
        9: ("QGIS main window", QGIS_COMMON + " Dialog closed. Layers panel: landuse expanded with legend Swellendam city (blue), Other residential (pale blue-grey), Big non residential areas (green), Small non residential areas (pale green). Map rendered in these four colours. Scale 1:143205. Goal reached.", "Goal reached."),
    },
}
PROVISIONAL = {("opendtect__horizon_2dviewer__01", 6), ("opendtect__horizon_2dviewer__01", 7), ("opendtect__horizon_2dviewer__01", 8)}


def main():
    enum = json.load(open(ENUM, encoding="utf-8"))
    out_dir = ROOT / "data/eval/study3/scenarios_gt_draft"; out_dir.mkdir(exist_ok=True)
    for f in sorted(glob.glob(str(ROOT / "data/eval/study3/scenarios_draft/*.json"))):
        sc = json.load(open(f, encoding="utf-8")); sid = sc["scenario_id"]
        for st in sc["steps"]:
            i = st["step_index"]; e = enum.get(f"{sid}#{i}") or {}
            labels, seen = [], set()
            for k, v in e.items():
                if isinstance(v, list):
                    for x in v:
                        x = str(x).strip()
                        if x and x.lower() not in seen:
                            seen.add(x.lower()); labels.append(x)
            dlg, ds, ca = FACTS[sid][i]
            st["visual_state_gt"] = {"current_dialog": dlg, "visible_elements": labels, "data_state": ds, "current_action": ca,
                                     "_gt_provenance": {"visible_elements": "gemini-2.5-pro enumeration, temperature 0 (gt_enumerate_study2.py --dir study3, 2026-09-23), all labels appended per the v3 Task-A rule; to be verified by the external review session" + (" — PROVISIONAL, recapture pending" if (sid, i) in PROVISIONAL else ""),
                                                        "dialog_data_state_action": "screen facts from data/eval/study3/CAPTURE_NOTES.md (main session) + capture_instructions authored from the manual before capture"}}
        sc["_study3_note"] += " GT draft built 2026-09-23 (gt_apply_study3.py); patterns/keywords unchanged."
        (out_dir / f"{sid}.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(sid, "labels per step:", [len(s["visual_state_gt"]["visible_elements"]) for s in sc["steps"]])


if __name__ == "__main__":
    main()
