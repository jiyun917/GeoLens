# -*- coding: utf-8 -*-
"""Study 2 GT draft builder (same rule as scripts/gt_apply_visible_elements.py, Task A v3):
every label the vision model read is appended to visual_state_gt.visible_elements (the study-2
drafts start empty, so all labels are additions; duplicates dropped, order = enumeration order).
current_dialog / data_state / current_action are filled from the screen facts recorded in
CAPTURE_NOTES.md and the step's capture_instructions (authored from the manual before capture).
Output: data/eval/study2/scenarios_gt_draft/<scenario_id>.json — to be verified by the external
review session (screenshot comparison) before anything is copied to data/eval/scenarios/.
"""
from __future__ import annotations
import glob, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# screen facts per step (from CAPTURE_NOTES.md, written after looking at the screenshots)
FACTS = {
    "opendtect__horizon_autotrack__01": {
        0: ("OpendTect Main Window / Scene 1", "Random Line 1 shows '4 Dip steered median filter'. 3D Horizon tree item is empty. Horizon Tracking Settings window is not open. Toolbar In-line 130, Step 10.", "User has displayed the random line and is about to start a new 3D horizon tracking."),
        1: ("Horizon Tracking Settings - <New Horizon 1>", "Mode tab active: Section Auto-track selected, Method = Seed Trace. Tabs: Mode, Event, Correlation, Properties (no DipSteer tab; no dip-steering licence). Tree shows <New Horizon 1> with child items Tracking Order, Seed Index, Correlation, Amplitude, Z values (warning icons). No seed picked.", "User has opened the tracking settings via 3D Horizon > New > Auto and Manual Tracking and set the Mode tab; next is the Event tab."),
        2: ("Horizon Tracking Settings - <New Horizon 1>", "Event tab active: Event type = Peak, Threshold type = Relative difference, Allowed difference (%) 25, Search window (ms) -8 8, Data Display window (ms) -16 16, Nr Traces 5, Picked on (empty), WVA checked. Correlation tab not yet edited.", "User has set Event type to Peak; next is the Correlation tab."),
        3: ("Horizon Tracking Settings - <New Horizon 1>", "Correlation tab active: Use Correlation = Yes, Compare window (ms) -40 40, Correlation threshold (%) 60.0, Snap to Event checked, Data Display window (ms) -48 48, Nr Traces 5. No seed on the section.", "User has enabled correlation at 60%; next is picking a seed on the random line."),
        4: ("OpendTect Main Window / Scene 1 + Horizon Tracking Settings - <New Horizon 1>", "One seed picked on a Peak reflector near the bottom of Random Line 1; the section auto-track drew a green horizon line along the section (Section Auto-track behaviour), no 3D patch yet. <New Horizon 1> active in the tree. Settings window moved to the top-right, Correlation tab visible, WVA waveform panel shows the picked trace. Toolbar now shows the tracking icons (Auto-Track, Retrack). Status bar shows coordinates and Value.", "User has picked one seed; next is clicking the Auto-Track icon."),
        5: ("OpendTect Main Window / Scene 1 + Horizon Tracking Settings - <New Horizon 1>", "Auto-Track has run: a green 3D horizon patch spreads out of the random line into the scene. <New Horizon 1> child items now show colour swatches. Settings window still open (Correlation tab). Patch not locked. No context menu open.", "User has auto-tracked a patch; next is QC and locking the patch (right-click > Tracking > Lock)."),
        6: ("OpendTect Main Window / Scene 1 + Horizon Tracking Settings - <New Horizon 1>", "Patch locked via Tracking > Lock. Visually identical to step 5 except the status bar is empty; the lock state is not visible on screen and is known only from the session history. Goal reached.", "User has locked the patch; the workflow goal is achieved."),
    },
    "opendtect__fault_sticks__01": {
        0: ("OpendTect Main Window / Scene 1", "In-line 110 shows '4 Dip steered median filter' (perspective view of the inline). FaultStickSet tree item is empty. No dialog, no context menu. Toolbar In-line 110, Step 1.", "User has loaded inline 110 and is about to create a new FaultStickSet."),
        1: ("OpendTect Main Window / Scene 1", "Tree shows <New FaultStickSet 1> under FaultStickSet (selected). The fault-stick edit toolbar appeared at the bottom: Copy Selection to, Fault, Create Single New, name field, Select..., colour, edit icons; status bar 'Picking'. No dialog open.", "User has created a new FaultStickSet; next is Save as... to name it."),
        2: ("Output selection", "Output selection dialog open from Save as...: 'Output FaultStickSet' field empty with a dropdown and Select... button, 'Replace in tree' checked, OK / Cancel / ? buttons. Tree still shows <New FaultStickSet 1>.", "User is about to type FaultStickSet_01 and click OK."),
        3: ("OpendTect Main Window / Scene 1", "Dialog closed; tree item now reads FaultStickSet_01 (selected). Inline 110 displayed. Only at Sections not yet enabled (no visible change expected). Bottom edit toolbar visible; status bar 'Picking'.", "User has saved the set as FaultStickSet_01; next is Display > Only at Sections."),
        4: ("OpendTect Main Window / Scene 1", "Display > Only at Sections enabled for FaultStickSet_01. Visually identical to step 3 (the toggle has no visible effect while no stick exists); the state is known only from the session history. No stick picked yet.", "User is ready to pick fault sticks on inline 110."),
        5: ("OpendTect Main Window / Scene 1", "Several fault sticks (green lines with yellow seed nodes) picked along the faults on inline 110. Toolbar In-line 110, Step 1. No Z-slice.", "User has picked sticks on inline 110; next is moving to inline 120 (Z/X keys) and continuing."),
        6: ("OpendTect Main Window / Scene 1", "Inline moved to 130 (toolbar In-line 130, Step 10); sticks exist on several inlines and the view is zoomed to the faulted part. Z-slice tree item still empty; no Similarity attribute.", "User has picked sticks on several inlines; next is adding a Z-slice at 1500 ms with the 9-1 Similarity attribute."),
        7: ("OpendTect Main Window / Scene 1", "Z-slice 1500 added with '9-1 Similarity on FEF seismic' displayed (toolbar Z 1500, Step 4); camera tilted towards a top view (north up) with inline 130 visible below. FaultStickSet_01 colour swatch violet; sticks visible as thin violet lines over the slice, none selected. Fault tree item empty.", "User is about to select the sticks of one lineament and use Copy Selection to > Fault > Create Single New."),
        8: ("OpendTect Main Window / Scene 1", "Fault_01A present under Fault in the tree (with a <right-click> child item, blue colour swatch); a blue fault plane is visible in the scene near the inline. FaultStickSet_01 still present. No dialog open. Goal reached.", "User has created the fault plane Fault_01A; the workflow goal is achieved."),
    },
}


def main():
    enum = json.load(open(ROOT / "data/eval/study2/gt_visible_elements_enum_study2.json", encoding="utf-8"))
    out_dir = ROOT / "data/eval/study2/scenarios_gt_draft"; out_dir.mkdir(exist_ok=True)
    for f in sorted(glob.glob(str(ROOT / "data/eval/study2/scenarios_draft/*.json"))):
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
            st["visual_state_gt"] = {
                "current_dialog": dlg,
                "visible_elements": labels,
                "data_state": ds,
                "current_action": ca,
                "_gt_provenance": {"visible_elements": "gemini-2.5-pro enumeration, temperature 0 (gt_enumerate_study2.py, 2026-09-21), all labels appended per the v3 Task-A rule; to be verified by the external review session", "dialog_data_state_action": "screen facts from CAPTURE_NOTES.md (main session, screenshot inspection) + capture_instructions authored from the manual before capture"},
            }
        sc["_study2_note"] += " GT draft built 2026-09-21 (gt_apply_study2.py); patterns/keywords unchanged."
        (out_dir / f"{sid}.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(sid, "steps", len(sc["steps"]), "visible_elements per step:", [len(s["visual_state_gt"]["visible_elements"]) for s in sc["steps"]])


if __name__ == "__main__":
    main()
