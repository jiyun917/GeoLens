# -*- coding: utf-8 -*-
"""Study 4 (new capture set) — K1 signature corrections on the STAGING workflows and the H-type GT corrections on the
scenario drafts, decided from the user's capture notes (data/eval/study4/CAPTURE_NOTES.md) and the signature check
(study4_verify_signatures.py) BEFORE any model run. Strings only: dialog titles as shown by the installed versions,
literal keywords, manual names kept as aliases. Nodes, edges, edge instructions unchanged.
Writes data/eval/study4/K1_signature_log.md.  Run when no benchmark reads the staging dirs (staging only).
"""
from __future__ import annotations
import io, json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
WF = ROOT / "data/eval/study4/workflows_draft"; SC = ROOT / "data/eval/study4/scenarios_draft"
LOG = ["# Study 4 K1 signature corrections (2026-09-28, before any model run; strings only)", ""]


def save(p, d):
    with open(str(p) + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2); fh.write("\n")
    os.replace(str(p) + ".tmp", p)


def fix_node(wf, nid_suffix, dialog=None, kw_add=(), kw_remove=(), note=""):
    n = next(x for x in wf["nodes"] if x["id"].endswith(nid_suffix)); sig = n["visual_signature"]
    before = (sig.get("expected_dialog"), list(sig.get("screenshot_keywords") or []))
    if dialog is not None:
        sig["expected_dialog"] = dialog
    kws = [k for k in (sig.get("screenshot_keywords") or []) if k not in set(kw_remove)]
    for k in kw_add:
        if k not in kws:
            kws.append(k)
    sig["screenshot_keywords"] = kws
    LOG.append(f"- {n['id']}: dialog {before[0]!r} -> {sig['expected_dialog']!r}; keywords {before[1]} -> {kws}" + (f" — {note}" if note else ""))


# ── E: spectral_decomp_152a (OpendTect 7.0.9 / F3 Demo 2023) ──
p = WF / "spectral_decomp_152a.json"; wf = json.load(open(p, encoding="utf-8"))
fix_node(wf, "_02_select_horizon_dialog", dialog="Select Horizons / Select Input Horizon(s)", kw_add=["Select Horizons", "100/300-750/1250"], note="capture note: title 'Select Horizons' in 7.0.9; manual name kept as alias")
fix_node(wf, "_03_position_ranges_entered", dialog="Positions / Position", kw_add=["Positions", "Specify Positions"], note="capture note: title 'Positions', subtitle 'Specify Positions'")
fix_node(wf, "_04_horizon_color_blended", kw_add=["<right-click>", "Z values"], note="capture note: the four layers show as <right-click> x3 + Z values")
fix_node(wf, "_05_attribute_set_open", kw_add=["Similarity"], note="capture note: default attribute type Similarity; Input Data auto-filled with 4 Dip steered median filter")
wf.setdefault("authoring", {})["k1_corrections"] = "2026-09-28 strings only after capture (K1); see data/eval/study4/K1_signature_log.md"
save(p, wf)

# ── G: qgis_aspect_north_736 (QGIS 3.44) ──
p = WF / "qgis_aspect_north_736.json"; wf = json.load(open(p, encoding="utf-8"))
fix_node(wf, "_02_raster_calc_open", kw_add=["Input layers", "0 inputs selected", "Output cell size", "Advanced Parameters"], kw_remove=["Reference layer(s)"], note="capture note: 'Reference layer(s)' is 'Input layers' in 3.44; Layers/Operators live inside the expression builder")
fix_node(wf, "_03_expression_entered", kw_add=['"aspect@1" <= 90 OR "aspect@1" >= 270'], kw_remove=["Expression is valid"], note="capture note: expression shown with quotes; no 'Expression is valid' text")
fix_node(wf, "_04_reference_layer_set", kw_add=["1 input selected", "Input layers"], kw_remove=["1 inputs selected", "Reference layer(s)"], note="capture note: singular '1 input selected'")
wf.setdefault("authoring", {})["k1_corrections"] = "2026-09-28 strings only after capture (K1); see data/eval/study4/K1_signature_log.md"
save(p, wf)

# ── F: qgis_custom_projection_614 — no correction (capture note: none) ──
LOG.append("- qgis_custom_projection_614: no correction (capture note: titles and labels as authored; 'User-defined' group name already in keywords as 'User Defined Coordinate Systems' — alias added)")
p = WF / "qgis_custom_projection_614.json"; wf = json.load(open(p, encoding="utf-8"))
fix_node(wf, "_08_van_der_grinten_selected", kw_add=["User-defined"], note="capture note: group label 'User-defined'")
save(p, wf)

# ── H-type GT corrections on the scenario drafts (version-name aliases only; patterns widened, never narrowed) ──
LOG += ["", "## H-type scenario corrections (version names; GT decisions before any model run)"]
p = SC / "qgis__aspect_north__01.json"; sc = json.load(open(p, encoding="utf-8"))
st = sc["steps"][2]; old = st["expected_action_text_pattern"]
st["expected_action_text_pattern"] = "(?i)\\b(Reference layer|Input layers?|참조 레이어|입력 레이어|reference|aspect)\\b"
LOG.append(f"- qgis__aspect_north__01 s2 pattern: {old!r} -> {st['expected_action_text_pattern']!r} (H4: 3.44 labels the field 'Input layers'; manual 'Reference layer(s)' kept)")
st["capture_instructions"]["screen_state"] = st["capture_instructions"]["screen_state"].replace("Reference layer(s) still empty", "Input layers ('0 inputs selected'; manual: Reference layer(s)) still empty")
sc["steps"][3]["capture_instructions"]["screen_state"] = sc["steps"][3]["capture_instructions"]["screen_state"].replace("'1 inputs selected'", "'1 input selected'")
sc["_study4_note"] += " H4 (2026-09-28, after capture, before any model run): 'Input layers' alias for the manual's 'Reference layer(s)' (QGIS 3.44 label); '1 input selected' wording."
save(p, sc)
p = SC / "opendtect__spectral_decomp__01.json"; sc = json.load(open(p, encoding="utf-8"))
sc["initial_state"]["description"] += " 캡처(7.0.9): 'Select Horizons' 대화상자(매뉴얼 'Select Input Horizon(s)'), 'Positions' 대화상자, 표시 OK 뒤 'Select RGB Attributes' 창은 비운 채 OK로 통과(미캡처), 트리 하위 레이어는 <right-click>×3 + Z values, Attribute Set 3D의 Input Data는 4 Dip steered median filter로 자동 채워짐."
sc["_study4_note"] += " H5 (2026-09-28, after capture, before any model run): version/data facts recorded in initial_state; patterns and keywords unchanged."
LOG.append("- opendtect__spectral_decomp__01: initial_state notes (H5); patterns/keywords unchanged")
save(p, sc)
LOG.append("- qgis__custom_projection__01: no change")
io.open(ROOT / "data/eval/study4/K1_signature_log.md", "w", encoding="utf-8", newline="\n").write("\n".join(LOG) + "\n")
print("\n".join(LOG))
