# -*- coding: utf-8 -*-
"""Apply the reviewed GT edits (rules 1 and 2 only) to the study-2 drafts and write proposed/<scenario>.json.
Also dumps a machine-readable diff (crops/diff.json) used to write GT_change_list.md."""
import json, os, copy, io
BASE = r"C:\Users\user\Downloads\GeoLens-paper\data\eval\study2\gt_review_session"
FS = "opendtect__fault_sticks__01"; HZ = "opendtect__horizon_autotrack__01"
PH = "화면상 확인 불가, 세션 이력 기준"

def strip_state(items):
    out = []
    for s in items:
        for suf in (" [checked]", " [unchecked]"):
            if s.endswith(suf): s = s[:-len(suf)]
        out.append(s)
    return out

# ops: ("rep", old, [new...]) replace one item by one or more; ("del", old); ("add_after", anchor, [new...]); ("strip_state",)
FS_OPS = {
 0: [("strip_state",), ("add_after", "Time", ["1500"])],
 1: [("add_after", "Help", ["SEG-Y"]), ("add_after", "Time", ["1500"])],
 2: [("add_after", "Time", ["1500"])],
 3: [("rep", "Select...", ["Select ..."]), ("rep", "In-line (110)", ["In-line 110"]), ("rep", "Step (1)", ["Step 1"]),
     ("rep", "Copy Selection to (Fault)", ["Copy Selection to", "Fault"]), ("add_after", "Time", ["1500"])],
 4: [("add_after", "Help", ["SEG-Y"]), ("rep", "Select...", ["Select ..."]), ("rep", "In-line (110)", ["In-line 110"]), ("rep", "Step (1)", ["Step 1"]),
     ("rep", "Copy Selection to (Fault)", ["Copy Selection to", "Fault"]), ("add_after", "Time", ["1500"])],
 5: [("strip_state",), ("rep", "Select...", ["Select ..."]), ("rep", "In-line (110)", ["In-line 110"]), ("rep", "Step (1)", ["Step 1"]),
     ("rep", "Copy Selection to (Fault)", ["Copy Selection to", "Fault"]), ("add_after", "Time", ["1500"])],
 6: [("rep", "Select...", ["Select ..."]), ("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"]),
     ("rep", "Copy Selection to (Fault)", ["Copy Selection to", "Fault"])],
 7: [("rep", "Select...", ["Select ..."])],
 8: [("add_after", "Help", ["SEG-Y"]), ("rep", "Select...", ["Select ..."]), ("rep", "Tr", ["Ti"])],
}
HZ_OPS = {
 0: [("del", "N"), ("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"])],
 1: [("add_after", "Close", ["?"]), ("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"]),
     ("rep", "Method (Seed Trace)", ["Method", "Seed Trace"])],
 2: [("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"]),
     ("rep", "Event type (Peak)", ["Event type", "Peak"]), ("rep", "Threshold type (Relative difference)", ["Threshold type", "Relative difference"]),
     ("rep", "Allowed difference (%) (25)", ["Allowed difference (%)", "25"]), ("rep", "Search window (ms) (-8)", ["Search window (ms)", "-8"]),
     ("rep", "Search window (ms) (8)", ["8"]), ("rep", "Data Display window (ms) (-16)", ["Data Display window (ms)", "-16"]),
     ("rep", "Data Display window (ms) (16)", ["16"]), ("rep", "Nr Traces (5)", ["Nr Traces", "5"]), ("strip_state",)],
 3: [("del", "F"), ("del", "\u25b7"), ("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"]),
     ("rep", "Compare window (ms) (-40)", ["Compare window (ms)", "-40"]), ("rep", "Correlation threshold (%) (60.0)", ["Correlation threshold (%)", "60.0"]),
     ("rep", "Data Display window (ms) (-48)", ["Data Display window (ms)", "-48"]), ("rep", "Nr Traces (5)", ["Nr Traces", "5"])],
 4: [("del", "\u25b7"), ("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"]),
     ("rep", "Compare window (ms) (-40)", ["Compare window (ms)", "-40"]), ("rep", "Correlation threshold (%) (60.0)", ["Correlation threshold (%)", "60.0"]),
     ("rep", "Data Display window (ms) (-48)", ["Data Display window (ms)", "-48"]), ("rep", "Nr Traces (5)", ["Nr Traces", "5"]),
     ("add_after", "Close", ["Auto-Track (icon)", "Retrack-All (icon)"])],
 5: [("del", "N"), ("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"]),
     ("rep", "Compare window (ms) (-40, 40)", ["Compare window (ms)", "-40", "40"]), ("rep", "Correlation threshold (%) (60.0)", ["Correlation threshold (%)", "60.0"]),
     ("rep", "Data Display window (ms) (-48, 48)", ["Data Display window (ms)", "-48", "48"]), ("rep", "Nr Traces (5)", ["Nr Traces", "5"]),
     ("add_after", "Close", ["Auto-Track (icon)", "Retrack-All (icon)"])],
 6: [("rep", "In-line (130)", ["In-line 130"]), ("rep", "Step (10)", ["Step 10"]),
     ("rep", "Compare window (ms) (-40)", ["Compare window (ms)", "-40"]), ("rep", "Correlation threshold (%) (60.0)", ["Correlation threshold (%)", "60.0"]),
     ("rep", "Data Display window (ms) (-48)", ["Data Display window (ms)", "-48"]), ("rep", "Nr Traces (5)", ["Nr Traces", "5"]),
     ("add_after", "Close", ["Auto-Track (icon)", "Retrack-All (icon)"])],
}

# sentence edits (rule 2)
SENT = {
 (FS, 1): {"data_state": "Tree shows <New FaultStickSet 1> under FaultStickSet (selected, green colour swatch). The fault-stick edit toolbar appeared at the bottom: Copy Selection to, Fault, Create Single New, name field, Select ..., blue colour swatch, edit icons (undo/redo enabled); the top toolbar gained a gear icon; status bar 'Picking'. No dialog open."},
 (FS, 3): {"data_state": "Dialog closed; tree item now reads FaultStickSet_01 (selected, green colour swatch). Inline 110 displayed. Only at Sections not yet enabled (no visible change expected; " + PH + "). Bottom edit toolbar visible (undo/redo greyed); status bar 'Picking'."},
 (FS, 4): {"data_state": "Display > Only at Sections enabled for FaultStickSet_01 (" + PH + "). Compared with step 3 the only visible differences are in the bottom edit toolbar: its leftmost icon button is now highlighted (toggled on) and the undo icon is enabled (green); the left main toolbar is unchanged. The section itself is unchanged and no stick is picked yet. Status bar 'Picking'."},
 (FS, 6): {"data_state": "Inline moved to 130 (toolbar In-line 130, Step 10; tree In-line > 130 > 4 Dip steered medi...); the section shows several sticks on inline 130 and the view is zoomed in on the faulted part (axis labels 500, 600, Time, 1000, 1500). Sticks on the other inlines exist but are not displayed on screen (" + PH + "). Z-slice tree item still empty; no Similarity attribute."},
 (FS, 7): {"data_state": "Z-slice 1500 added with '9-1 Similarity on F...' (tree label truncated; full name '9-1 Similarity on FEF seismic' " + PH + ") displayed (toolbar Z 1500, Step 4); camera tilted towards a top view (north up; gizmo shows N and E) with inline 130 visible below. FaultStickSet_01 colour swatch violet; sticks visible as short violet marks along the slice/inline intersection, none selected. Fault tree item empty. Status bar shows 130/559, (612287, 6074487, 1066.9), Value = -1109, In-line: 130. The top icon of the left main toolbar shows a hand cursor (arrow cursor in steps 0-6)."},
 (HZ, 1): {"data_state": "Mode tab active: Section Auto-track selected, Method = Seed Trace; Snap to Event checkbox greyed out. Tabs: Mode, Event, Correlation, Properties (no DipSteer tab; no dip-steering licence: " + PH + "). Tree shows <New Horizon 1> with child items Tracking Order, Seed Index, Correlation, Amplitude, Z values (warning icons). No seed picked."},
 (HZ, 2): {"data_state": "Event tab active: Event type = Peak, Threshold type = Relative difference, Allowed difference (%) 25, Search window (ms) -8 8, Data Display window (ms) -16 16, Nr Traces 5, Picked on (empty), WVA checked, VD unchecked, both Symmetric boxes unchecked. Correlation tab not yet edited (" + PH + ")."},
 (HZ, 4): {"data_state": "One seed picked near the bottom of Random Line 1 (white square marker); the section auto-track drew a green horizon line along the section (Section Auto-track behaviour), no 3D patch yet. The seed is on a Peak event per the Event-tab setting (" + PH + "). <New Horizon 1> active in the tree (child items still show warning icons). Settings window moved to the top-right (inactive title bar), Correlation tab visible, WVA waveform panel shows the picked trace with a green seed marker. The dialog's Auto-Track and Retrack-All icons are now enabled (green); the main toolbar shows six additional tracking icons (no text). Status bar is empty except [free mem]."},
 (HZ, 5): {"data_state": "Auto-Track has run: a green 3D horizon patch spreads out of the random line into the scene. <New Horizon 1> child items now show colour swatches. Settings window still open (Correlation tab); the main toolbar's save icon is now enabled. Patch not locked (" + PH + "). No context menu open. Status bar shows 425/429, (608829, 6081768, 1817.8), Value = -3612, Random Line 1."},
 (HZ, 6): {"data_state": "Patch locked via Tracking > Lock (" + PH + "). Visually identical to step 5 except: the status bar is empty (only [free mem]) and the seed marker on the section is blue (white in step 5); whether the blue marker reflects the lock cannot be confirmed from the screen. Goal reached."},
}

def apply_ops(items, ops):
    items = list(items); log = []
    for op in ops:
        if op[0] == "strip_state":
            new = strip_state(items)
            for a, b in zip(items, new):
                if a != b: log.append(("fmt", a, b))
            items = new
        elif op[0] == "rep":
            _, old, news = op
            assert old in items, (old, items)
            i = items.index(old); items[i:i+1] = news
            log.append(("rep", old, " | ".join(news)))
        elif op[0] == "del":
            _, old = op; assert old in items, old
            items.remove(old); log.append(("del", old, ""))
        elif op[0] == "add_after":
            _, anchor, news = op; assert anchor in items, anchor
            i = items.index(anchor); items[i+1:i+1] = news
            log.append(("add", "", " | ".join(news)))
    seen = set(); out = []
    for s in items:
        if s in seen: log.append(("dedup", s, "")); continue
        seen.add(s); out.append(s)
    return out, log

diff = {}
for scen, ops_tbl in ((FS, FS_OPS), (HZ, HZ_OPS)):
    src = os.path.join(BASE, "scenarios", scen + ".json")
    with io.open(src, encoding="utf-8") as f: raw = f.read()
    data = json.loads(raw)
    rt = json.dumps(data, ensure_ascii=False, indent=2)
    print(scen, "round-trip identical:", rt == raw.rstrip("\n"), "| trailing newline in source:", raw.endswith("\n"))
    new = copy.deepcopy(data)
    for step in new["steps"]:
        idx = step["step_index"]; vs = step["visual_state_gt"]
        before = list(vs["visible_elements"])
        after, log = apply_ops(before, ops_tbl.get(idx, []))
        vs["visible_elements"] = after
        sent = {}
        for k, v in SENT.get((scen, idx), {}).items():
            sent[k] = (vs[k], v); vs[k] = v
        diff[scen + "/step_" + str(idx)] = {"n_before": len(before), "n_after": len(after), "items": log, "sentences": sent}
    dst = os.path.join(BASE, "proposed", scen + ".json")
    with io.open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(new, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else ""))
    print("wrote", os.path.relpath(dst, BASE))
with io.open(os.path.join(BASE, "crops", "diff.json"), "w", encoding="utf-8") as f:
    json.dump(diff, f, ensure_ascii=False, indent=1)
for k, v in diff.items():
    print(k, v["n_before"], "->", v["n_after"], "| ops:", len(v["items"]), "| sentences:", list(v["sentences"].keys()))
