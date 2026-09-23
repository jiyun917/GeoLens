# Apply the reviewed s6-s8 visual_state_gt (recapture review, 2026-09-23) into proposed/.
# Steps 0-5 of proposed/ are left untouched; steps 6-8 take draft_v2's visual_state_gt with the review edits below.
import json, io

PROPOSED = 'proposed/opendtect__horizon_2dviewer__01.json'
DRAFT = 'recapture/opendtect__horizon_2dviewer__01_draft_v2.json'
OVERLAP = '20021203-2-03_00...21203-2-02_0010'   # H7 convention (s3/s4/s5)

before_bytes = open(PROPOSED, 'rb').read()
p = json.loads(before_bytes.decode('utf-8'))
d = json.load(open(DRAFT, encoding='utf-8'))

def edit_list(items, replace=(), remove=(), insert_after=(), insert_before=()):
    out = list(items)
    for old, new in replace:
        assert out.count(old) == 1, (old, out.count(old)); out[out.index(old)] = new
    for r in remove:
        assert out.count(r) == 1, (r, out.count(r)); out.remove(r)
    for anchor, new in insert_after:
        assert anchor in out and new not in out, (anchor, new); out.insert(out.index(anchor) + 1, new)
    for anchor, new in insert_before:
        assert anchor in out and new not in out, (anchor, new); out.insert(out.index(anchor), new)
    assert len(out) == len(set(out)), 'duplicates left'
    return out

# ---- step 6 ----
g6 = json.loads(json.dumps(d['steps'][6]['visual_state_gt'], ensure_ascii=False))
g6['visible_elements'] = edit_list(
    g6['visible_elements'],
    replace=[('20021203-2-03_0000', OVERLAP), ('(s)', 's)')],
    remove=['20021203-2-02_0010'],
    insert_after=[('Close', '?'), ('?', '▷')],
    insert_before=[('400', '200')],
)
g6['data_state'] = ("'Output selection' dialog (Output 2D Horizon field empty with dropdown and Select ..., "
    "'Replace in tree' checked, OK / Cancel / ?) in front of the 2D Viewer window (Line: 19981104-1-04_0037), "
    "whose tree shows 2D Horizon > <New 2D Horizon 1> (checked, selected) and whose section shows the green horizon; "
    "the Horizon Tracking Settings window is also still open (Mode tab) and hides the lower part of the main tree "
    "(rows below 2D Horizon not visible). That the dialog was opened from the viewer tree (right-click <New 2D Horizon 1> > Save as) "
    "is not verifiable on screen — per session history.")

# ---- step 7 ----
g7 = json.loads(json.dumps(d['steps'][7]['visual_state_gt'], ensure_ascii=False))
g7['visible_elements'] = edit_list(
    g7['visible_elements'],
    replace=[('VD (unchecked)', 'VD (checked)'), ('20021203-2-03_0008', OVERLAP)],
    remove=['Scene 1 (checked)', '20021203-2-02_0010',
            'In-line', 'Z-slice', 'Volume', 'Random Line', '2D Line', 'Seismic', '3D Horizon',
            'Fault', 'FaultSet', 'Geobody', 'Well', 'Polygon', 'Prestack Events', 'Wiggle', 'VD'],
    insert_before=[('400', '200')],
)
g7['data_state'] = ("Dialog closed; the horizon now appears under the saved name '2D_Horizon' (checked, selected/highlighted) "
    "in both trees: 2D viewer tree 2D Horizon > 2D_Horizon and main tree 2D Horizon > 2D_Horizon. "
    "The 2D Viewer window is STILL open (section with the green horizon); the Horizon Tracking Settings window is no longer visible "
    "(closed — not verifiable on screen, per session history). Status bar shows coordinates, Value, Line/TrcNr/SP.")

# ---- step 8 ----
g8 = json.loads(json.dumps(d['steps'][8]['visual_state_gt'], ensure_ascii=False))
g8['visible_elements'] = edit_list(g8['visible_elements'], insert_before=[('400', '200')])
g8['data_state'] = ("2D Viewer window no longer visible (closed — not verifiable on screen, per session history); no dialog. "
    "The 3D scene shows the 2D line 19981104-1-04_0037 section with the interpreted horizon (white pick squares along the reflector "
    "near 1500 ms); main tree 2D Horizon > 2D_Horizon (checked, selected/highlighted). Status bar shows only [free mem]. Goal reached.")

for i, g in ((6, g6), (7, g7), (8, g8)):
    assert list(g.keys()) == ['current_dialog', 'visible_elements', 'data_state', 'current_action', '_gt_provenance']
    p['steps'][i]['visual_state_gt'] = g

text = json.dumps(p, ensure_ascii=False, indent=2) + '\n'
with io.open(PROPOSED, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

# ---- verification ----
after = json.loads(open(PROPOSED, encoding='utf-8').read())
old = json.loads(before_bytes.decode('utf-8'))
for k in old:
    if k != 'steps': assert old[k] == after[k], k
for i in range(9):
    for k in old['steps'][i]:
        if k == 'visual_state_gt':
            if i <= 5: assert old['steps'][i][k] == after['steps'][i][k], f'step {i} GT changed!'
        else:
            assert old['steps'][i][k] == after['steps'][i][k], (i, k)
    assert list(old['steps'][i].keys()) == list(after['steps'][i].keys())
assert list(old.keys()) == list(after.keys())
# byte-level: prefix up to step 6's visual_state_gt must be identical
raw_after = open(PROPOSED, 'rb').read()
cut = before_bytes.index(b'"step_index": 6')
assert raw_after[:cut] == before_bytes[:cut], 'bytes before step 6 differ'
assert b'\r\n' not in raw_after and raw_after.endswith(b'\n')
print('OK: steps 0-5 identical (object + bytes up to step 6), top-level and non-GT fields identical, LF, trailing newline')
for i in (6, 7, 8):
    print(f'step {i}: {len(after["steps"][i]["visual_state_gt"]["visible_elements"])} visible_elements')
