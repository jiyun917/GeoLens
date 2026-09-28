# -*- coding: utf-8 -*-
"""Study 4 (new capture set E/F/G) GT draft builder — same rule as study 2/3: every label the vision model
(gemini-2.5-pro, temperature 0) read is appended to visual_state_gt.visible_elements; current_dialog /
data_state / current_action come from the screen facts recorded by the main session (screenshot inspection,
data/eval/study4/CAPTURE_NOTES.md). Patterns / keywords / alternatives are NOT touched here.
Input : data/eval/study4/scenarios_draft/<sid>.json (after study4_apply_k1.py), data/eval/study4/gt_visible_elements_enum_study2.json
Output: data/eval/study4/scenarios_gt_draft/<sid>.json -> external review session (gt_review_session/scenarios/).
"""
from __future__ import annotations
import glob, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ENUM = ROOT / "data/eval/study4/gt_visible_elements_enum_study2.json"
OT_MAIN = "OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : F3 Demo 2023 - [Scene 1]"
OT_COMMON = ("OpendTect main window title '" + OT_MAIN + "', menu bar (Survey / Analysis / Processing / Scene / View / Utilities / TerraNubis / Help), "
             "toolbars, 'Tree scene 1' panel (Elements / Color; Scene 1 > In-line, Cross-line, Z-slice, Volume, Random Line, 2D Line, 3D Horizon, 2D Horizon, Fault, FaultSet, FaultStickSet, Geobody, Well, PointSet, Polygon, Prestack Events; Annotations), "
             "3D scene with the survey box (Cross-line 400–1200, In-line 200–600, Time 500–1500), colour bar -8.7372 … 8.7372 'OD Seismic 1', status bar '[free mem]'.")
QGIS_COMMON = "QGIS main window title '*Untitled Project — QGIS', menu bar, toolbars, Layers panel, status bar (Type to locate / Coordinate / Scale / Magnifier / Rotation / Render / CRS button)."
FACTS = {
    "opendtect__spectral_decomp__01": {
        0: (OT_MAIN, OT_COMMON + " Empty survey box (no data displayed); 3D Horizon has NO child item. No dialog, no Attribute Set window. A leftover tracking toolbar (icons) from an earlier session is visible at the top right (irrelevant).",
            "User is about to right-click 3D Horizon in the tree and choose Add Color Blended…."),
        1: ("Select Horizons", "'Select Horizons' dialog (7.0.9 title; the manual calls it Select Input Horizon(s)) open over the empty scene: Filter field, checkbox list Demo 0 --> FS4 (bold, current), Demo 1 --> MFS4, Demo 2 --> FS6, Demo 3 --> Top Foresets, Demo 4 --> Truncation, Demo 5 --> FS7, Demo 6 …; 'Area subselection' = '100/300-750/1250 (463 samples)' with 'Select ...' button; OK / Cancel / ?; path hint '…Demo_2023\\Surfaces\\Demo_0_--_FS4.hor'. Nothing checked yet; no Positions dialog.",
            "User is about to tick Demo 1 --> MFS4 and click Select … to set the area subselection."),
        2: ("Positions", "'Positions' dialog ('Specify Positions') open in front of the Select Horizons dialog: Area subselection = Range; In-line range 200 – 650 Step 1; Cross-line range 500 – 1000 Step 1 (typed); OK / Cancel / ?. Behind it Demo 1 --> MFS4 is checked and the path hint reads '…emo_2023\\Surfaces\\Demo_1_--_MFS4.hor'. OK not yet clicked.",
            "User is about to click OK (Positions) and then OK (Select Horizons) to display the horizon."),
        3: (OT_MAIN, OT_COMMON + " Dialogs closed (the 'Select RGB Attributes' window that appeared after OK was passed with OK, empty). Tree: 3D Horizon > Demo 1 --> MFS4 (checked, colour flag) with four child layers <right-click> (three, R/G/B colour flags) and Z values; the horizon surface (red/black Z-values display) is drawn in the 3D scene around Time 1000. No Attribute Set window.",
            "User is about to click the Attribute Set 3D toolbar icon."),
        4: ("Attribute Set 3D", "'Attribute Set 3D' window open in front of the scene: File menu, toolbar icons, Attribute set '<not saved>', EMPTY attribute list on the left (up/down/sort/remove buttons), attribute type '<All>' / 'Similarity' (default), Input Data '4 Dip steered median filter' (auto-filled) with 'Select ...', Time gate (ms) -28 28, Extension Cross, Stepout inl:1 crl:1, Steering None, Output statistic Average, Attribute Name (empty), 'Add as new', 'Save on Close' checked, Close, ?. Tree behind shows Demo 1 --> MFS4 with the four layers.",
            "User is about to choose Spectral Decomposition, set Time gate -8 24, Output frequency 24 Step 4, name SD_24Hz[-8,24ms] and click Add as new."),
        5: ("Attribute Set 3D", "'Attribute Set 3D' window: attribute list shows ONE entry SD_24Hz[-8,24ms]; attribute type Spectral Decomposition; Input Data 4 Dip steered median filter; Transform type FFT (selected) / CWT; Time gate (ms) -8 24; 'Display Time/Frequency panel' button; Output frequency (Hz) 24.0 Step 4.0; Attribute Name SD_24Hz[-8,24ms]; Add as new; Save on Close checked; Close.",
            "User is about to change Output frequency to 44 and the name to SD_44Hz[-8,24ms] and click Add as new."),
        6: ("Attribute Set 3D", "'Attribute Set 3D' window: attribute list shows TWO entries SD_24Hz[-8,24ms], SD_44Hz[-8,24ms] (second selected); Output frequency (Hz) 44.0 Step 4.0; Attribute Name SD_44Hz[-8,24ms]; other fields as in step 5.",
            "User is about to change Output frequency to 64 and the name to SD_64Hz[-8,24ms] and click Add as new."),
        7: ("Attribute Set 3D", "'Attribute Set 3D' window: attribute list shows THREE entries SD_24Hz[-8,24ms], SD_44Hz[-8,24ms], SD_64Hz[-8,24ms] (third selected); Output frequency (Hz) 64.0 Step 4.0; Attribute Name SD_64Hz[-8,24ms]; window still open; Save on Close checked.",
            "User is about to click Close (and save the set as Spectral Decomposition)."),
        8: (OT_MAIN, OT_COMMON + " Attribute Set 3D window closed (set saved on close; name not visible on screen). Tree: 3D Horizon > Demo 1 --> MFS4 with the four layers; horizon surface displayed in the scene. No dialog. Goal reached.",
            "Goal reached — nothing further; a completion sentinel is expected."),
    },
    "qgis__custom_projection__01": {
        0: ("*Untitled Project — QGIS", QGIS_COMMON + " Layers: oceans (single layer, green polygons); map canvas shows the world oceans in EPSG:4326 (rectangular). Status bar CRS button 'EPSG:4326'. No dialog.",
            "User is about to open Settings ► Custom Projections…."),
        1: ("Options — User Defined CRS", "'Options — User Defined CRS' dialog open (left tree: General, System, User Profiles, CRS and Transforms > CRS Handling / Coordinate Transforms / User Defined (selected), Data Sources, GDAL, Rendering …): explanatory text; EMPTY Name / Parameters table with + (green) and − (red) buttons; Name field empty; Definition: Format 'WKT (Recommended)', Parameters box empty, copy icon, Validate; Test (collapsed); OK / Cancel / Help.",
            "User is about to click the + (Add new CRS) button."),
        2: ("Options — User Defined CRS", "Same dialog: the table now has ONE row 'new CRS' (Parameters column empty); Name field shows 'new CRS' (selected/editable); Format WKT (Recommended); Parameters empty.",
            "User is about to type the name Van der Grinten I (format stays WKT)."),
        3: ("Options — User Defined CRS", "Same dialog: table row 'Van der Gri…' (truncated), Name field 'Van der Grinten I', Format 'WKT (Recommended)', Parameters box still EMPTY.",
            "User is about to paste the WKT string into Parameters."),
        4: ("Options — User Defined CRS", "Same dialog: table row 'Van der Gri…' with Parameters 'PROJCRS[\"unknown\",BASEGEOGCRS[\"unknown\",DATUM[\"unknown\",ELLIPSOID[\"unknown\",6371000,0,LENGTHUNIT[\"metre\",1,ID[…' (truncated); Parameters box shows the END of the WKT (PARAMETER[\"False easting\",0 …, PARAMETER[\"False northing\",0 …, CS[Cartesian,2], AXIS[\"(E)\",east, ORDER[1] …, AXIS[\"(N)\",north, ORDER[2] …) because it is scrolled down — the METHOD line is not visible; Validate button; OK not yet clicked.",
            "User is about to click OK."),
        5: ("*Untitled Project — QGIS", QGIS_COMMON + " Dialog closed; map unchanged (rectangular EPSG:4326 world); status bar CRS button still 'EPSG:4326'; Layers: oceans.",
            "User is about to click the status-bar CRS button (EPSG:4326) to open the project CRS dialog."),
        6: ("Project Properties — CRS", "'Project Properties — CRS' dialog open (left: General, Metadata, View Settings, CRS (selected), Transformations, Styles, Colors, Data Sources, Relations, Variables, Macros, QGIS Server, Temporal, Elevation, Sensors): 'Project Coordinate Reference System (CRS)', 'No CRS' checkbox, Filter (empty), 'Recently Used Coordinate Reference Systems' (empty list), 'Predefined Coordinate Reference Systems' list with WGS 84 EPSG:4326 highlighted and WGS 84 variants (OGC:CRS84, EPSG:9055 …), 'Hide deprecated CRSs', properties text 'WGS 84', preview map, OK / Cancel / Apply / Help.",
            "User is about to type Van der Grinten in Filter and select the user-defined CRS."),
        7: ("Project Properties — CRS", "Same dialog: Filter = 'Van der Grinten'; Predefined list shows Projected > van der Grinten (I) > Sphere_Van_der_Grinten_I (ESRI:53029), World_Van_der_Grinten_I (ESRI:54029) and User-defined > Van der Grinten I (USER:100000) highlighted/selected; properties text 'Van der Grinten I' (Units meters, Method van der Grinten (I)) with the WKT; preview map; OK not yet clicked.",
            "User is about to click OK."),
        8: ("*Untitled Project — QGIS", QGIS_COMMON + " Dialog closed; the map canvas shows the world in the circular Van der Grinten projection; status bar CRS button 'USER:100000', Scale 1:157344704. Goal reached.",
            "Goal reached — nothing further; a completion sentinel is expected."),
    },
    "qgis__aspect_north__01": {
        0: ("*Untitled Project — QGIS", QGIS_COMMON + " Layers: aspect (Band 1 (Gray) 360 … 0.093473); map shows the grey aspect raster; Processing Toolbox panel open on the right (groups Recently used … Vector tiles, GDAL, GRASS; search empty). No Raster Calculator dialog. EPSG:32733.",
            "User is about to open Raster analysis ► Raster calculator in the Processing Toolbox."),
        1: ("Raster Analysis - Raster Calculator", "'Raster Analysis - Raster Calculator' dialog open (Parameters / Log tabs): Input layers '0 inputs selected' with … button; Expression (EMPTY) with ε (expression builder) button; Output extent [optional] 'Not set'; Output cell size (leave empty to set it automatically) [optional] 'Not set'; Output CRS [optional]; Advanced Parameters (collapsed); Calculated '[Save to temporary file]' with …; 'Open output file after running algorithm' checked; right pane 'Raster calculator — This algorithm performs algebraic operations using raster layers.'; progress 0%; Advanced / Run as Batch Process… / Run / Close / Help. Toolbox behind shows Raster analysis expanded with 'Raster calculator' highlighted.",
            "User is about to type the expression \"aspect@1\" <= 90 OR \"aspect@1\" >= 270."),
        2: ("Raster Analysis - Raster Calculator", "Same dialog: Expression = '\"aspect@1\" <= 90 OR \"aspect@1\" >= 270' (with quotes; no 'Expression is valid' text in this version); Input layers still '0 inputs selected'; Calculated still '[Save to temporary file]'.",
            "User is about to click the … button next to Input layers and tick aspect."),
        3: ("Raster Analysis - Raster Calculator", "Same dialog: Input layers = '1 input selected' (aspect); Expression as in step 2; Calculated still '[Save to temporary file]'.",
            "User is about to set the output file via … › Save to File (aspect_north.tif)."),
        4: ("Raster Analysis - Raster Calculator", "Same dialog: Calculated = 'C:/GeoLensData/raster_analysis/aspect_north.tif'; Input layers '1 input selected'; Expression as before; Run not yet clicked.",
            "User is about to click Run."),
        5: ("*Untitled Project — QGIS", QGIS_COMMON + " Algorithm ran and the dialog closed: Layers now aspect_north (Band 1 (Gray) 1 … 0) on top of aspect; map shows the binary black/white north-facing raster; Processing Toolbox still open (Raster calculator highlighted). Goal reached.",
            "Goal reached — nothing further; a completion sentinel is expected."),
    },
}


def main():
    enum = json.load(open(ENUM, encoding="utf-8"))
    out_dir = ROOT / "data/eval/study4/scenarios_gt_draft"; out_dir.mkdir(exist_ok=True)
    for f in sorted(glob.glob(str(ROOT / "data/eval/study4/scenarios_draft/*.json"))):
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
                                     "_gt_provenance": {"visible_elements": "gemini-2.5-pro enumeration, temperature 0 (gt_enumerate_study2.py --dir study4, 2026-09-28), all labels appended per the v3 rule; external review edits follow",
                                                        "dialog_data_state_action": "screen facts from main-session screenshot inspection + data/eval/study4/CAPTURE_NOTES.md; capture_instructions authored from the manual before capture"}}
        sc["_study4_note"] += " GT draft built 2026-09-28 (gt_apply_study4.py); patterns/keywords unchanged."
        (out_dir / f"{sid}.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(sid, "labels per step:", [len(s["visual_state_gt"]["visible_elements"]) for s in sc["steps"]])


if __name__ == "__main__":
    main()
