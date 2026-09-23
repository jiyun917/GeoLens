# -*- coding: utf-8 -*-
"""Study 3 GT finalisation (owner decisions 2026-09-23, delegated to the main session; V3-39).
Input : data/eval/study3/gt_review_session/proposed/<sid>.json (external review output)
Output: data/eval/scenarios/.study3_test_opendtect/<C>.json, data/eval/scenarios/.study3_test_qgis/<B,D>.json,
        and identical copies in data/eval/scenarios/.
Decisions applied on top of the proposed files (all backends alike, before any system run):
  H1  QGIS numerals: period decimal convention (the Korean UI font renders '.' like ','; QGIS source
      strings use '.'); cross-step inconsistencies unified.
  H2  Dataset-name correction (precedent: v3 roads_34S→roads_33S, V3-x): the F3 Demo 2023 dataset has no
      'Well correlation-Line' and names the attribute 'Seismic' — scenario goal / keywords / patterns /
      allowed alternatives refer to the on-screen names; the workflow file is NOT touched.
  H3  reclassify s1: Raster layer auto-filled with the active layer (aspect) — allowed alternative
      accepting the next action (open the Reclassification table) (precedent: v3 QGIS s3).
  C s6–s8 stay PROVISIONAL until the recapture (GT of those steps rebuilt afterwards).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
SRC = ROOT / "data/eval/study3/gt_review_session/proposed"
LIVE = ROOT / "data/eval/scenarios"
OT = LIVE / ".study3_test_opendtect"; QG = LIVE / ".study3_test_qgis"
OT.mkdir(exist_ok=True); QG.mkdir(exist_ok=True)
LOG = []


def save(sid, sc, sub):
    txt = json.dumps(sc, ensure_ascii=False, indent=2) + "\n"
    for d in (LIVE, sub):
        (d / f"{sid}.json").write_text(txt, encoding="utf-8", newline="\n")


def periodise(sc, sid):
    n = 0
    for st in sc["steps"]:
        ve = st["visual_state_gt"]["visible_elements"]
        for i, l in enumerate(ve):
            nl = re.sub(r"(?<=\d),(?=\d)", ".", l)
            if nl != l:
                ve[i] = nl; n += 1
        for k in ("data_state", "current_dialog"):
            v = st["visual_state_gt"].get(k) or ""
            nv = re.sub(r"(?<=\d),(?=\d{2,})", ".", v)
            if nv != v: st["visual_state_gt"][k] = nv
    LOG.append(f"{sid} H1: {n} visible_elements comma-decimals -> period")


# ── B: rule classification ──
sid = "qgis__rule_classification__01"; sc = json.load(open(SRC / f"{sid}.json", encoding="utf-8"))
periodise(sc, sid)
sc["_study3_note"] += " GT finalised 2026-09-23 after external review (H1 applied; V3-39)."
save(sid, sc, QG)

# ── D: reclassify ──
sid = "qgis__reclassify_raster__01"; sc = json.load(open(SRC / f"{sid}.json", encoding="utf-8"))
periodise(sc, sid)
s1 = sc["steps"][1]
s1["allowed_alternatives"].append({"pattern": "(?i)\\b(Reclassification table|Fixed table|\\.\\.\\.|…|테이블|표|already|이미)\\b",
                                   "note": "H3 (external review 2026-09-23): the Raster layer is auto-filled with the active layer (aspect), so the manual's 'choose aspect' needs no user action on this screen; opening the reclassification table is a valid next action (precedent: v3 QGIS s3)."})
LOG.append(f"{sid} s1 H3: + allowed alternative (table action; Raster layer auto-filled)")
sc["_study3_note"] += " GT finalised 2026-09-23 after external review (H1/H3 applied; V3-39)."
save(sid, sc, QG)

# ── C: 2D viewer (provisional for s6–s8) ──
sid = "opendtect__horizon_2dviewer__01"; sc = json.load(open(SRC / f"{sid}.json", encoding="utf-8"))
LINE = "19981104-1-04_0037"
g = sc["goal"]
sc["goal"] = g.replace("2D Line(Well correlation-Line)", f"2D Line({LINE}; 이 F3 Demo 2023 배포판에는 매뉴얼의 'Well correlation-Line'이 없어 첫 번째 2D 라인을 쓴다)").replace("그 Seis 속성을", "그 Seismic 속성을")
LOG.append(f"{sid} H2: goal line/attribute names -> {LINE} / Seismic (dataset-name correction; workflow untouched)")
st = sc["steps"][1]
st["expected_action_keywords"] = ["Load default data"]
st["expected_action_text_pattern"] = st["expected_action_text_pattern"].replace("(?i)\\b(Well correlation|", f"(?i)\\b(Well correlation|{LINE}|19981104|")
LOG.append(f"{sid} s1 H2: keywords -> ['Load default data']; pattern += {LINE}|19981104")
st = sc["steps"][2]
st["expected_action_keywords"] = ["Seismic", "2D Viewer"]
st["expected_action_text_pattern"] = st["expected_action_text_pattern"].replace("(?i)\\b(Seis|", "(?i)\\b(Seismic|Seis|")
LOG.append(f"{sid} s2 H2: keywords Seis -> Seismic; pattern += Seismic")
st = sc["steps"][8]
for a in st["allowed_alternatives"]:
    if "Well correlation" in a["pattern"]:
        a["pattern"] = a["pattern"].replace("Well correlation", f"Well correlation|{LINE}|19981104"); LOG.append(f"{sid} s8 H2: alternative += {LINE}")
sc["initial_state"]["description"] += f" 2D 라인 목록에는 {LINE} 등 F3 Demo 2023의 라인만 있고 'Well correlation-Line'은 없다."
sc["_study3_note"] += " GT partially finalised 2026-09-23 (s0–s5 reviewed; H2 dataset-name correction; s6–s8 PROVISIONAL pending recapture; V3-39)."
save(sid, sc, OT)

(ROOT / "data/eval/study3/GT_final_applied_log.md").write_text("# Study 3 GT final edits on top of the external review (2026-09-23)\n\n" + "\n".join(f"- {l}" for l in LOG) + "\n", encoding="utf-8")
print("\n".join(LOG)); print("written:", sorted(p.name for p in OT.glob("*.json")), sorted(p.name for p in QG.glob("*.json")))
