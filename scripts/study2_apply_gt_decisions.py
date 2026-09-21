# -*- coding: utf-8 -*-
"""Study 2 GT finalisation (owner decisions 2026-09-21, delegated to the main session; V3-30).
Input : data/eval/study2/gt_review_session/proposed/<sid>.json (external review output)
Output: data/eval/scenarios/<sid>.json  and  data/eval/scenarios/.study2_test/<sid>.json (identical)
Decisions applied on top of the proposed files (all backends alike, before any system run):
  H3  horizon s3: drop allowed alternative (Steering|No|DipSteer) — no DipSteer tab here; bare 'No' over-matches
  H4  fault_sticks s7: add allowed alternative for switching to Position/Interact mode (screen is in view mode)
  H5  initial_state wording: 'no <category> item' -> 'no child item under <category>'
  H2  horizon s1-s3: greyed Auto-Track / Retrack-All icons are on screen -> add '(icon)' labels
  H1/H8 unnamed icons not added; H6/H7 recorded only; C1-C5 kept as the reviewer applied them.
"""
from __future__ import annotations
import json, os, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
SRC = ROOT / "data/eval/study2/gt_review_session/proposed"
LIVE = ROOT / "data/eval/scenarios"
TEST = LIVE / ".study2_test"
TEST.mkdir(exist_ok=True)
LOG = []


def save(sid, sc):
    txt = json.dumps(sc, ensure_ascii=False, indent=2) + "\n"
    for d in (LIVE, TEST):
        (d / f"{sid}.json").write_text(txt, encoding="utf-8", newline="\n")


# ── horizon_autotrack ──
sid = "opendtect__horizon_autotrack__01"
sc = json.load(open(SRC / f"{sid}.json", encoding="utf-8"))
s3 = sc["steps"][3]
before = list(s3["allowed_alternatives"])
s3["allowed_alternatives"] = [a for a in s3["allowed_alternatives"] if "DipSteer" not in a["pattern"]]
LOG.append(f"{sid} s3 H3: allowed_alternatives {before} -> {s3['allowed_alternatives']}")
for i in (1, 2, 3):
    ve = sc["steps"][i]["visual_state_gt"]["visible_elements"]
    for lab in ("Auto-Track (icon)", "Retrack-All (icon)"):
        if lab not in ve:
            ve.append(lab)
    LOG.append(f"{sid} s{i} H2: + 'Auto-Track (icon)', 'Retrack-All (icon)' (greyed, visible)")
mb = sc["initial_state"]["must_be_true"]
mb[2] = "no child item under 3D Horizon in the tree (the category item itself is always shown)"
LOG.append(f"{sid} H5: initial_state.must_be_true[2] -> {mb[2]!r}")
sc["_study2_note"] += " GT finalised 2026-09-21 after external review (H2/H3/H5 applied; V3-30)."
save(sid, sc)

# ── fault_sticks ──
sid = "opendtect__fault_sticks__01"
sc = json.load(open(SRC / f"{sid}.json", encoding="utf-8"))
s7 = sc["steps"][7]
s7["allowed_alternatives"].append({"pattern": "(?i)\\b(Position mode|Interact mode|Interact|position mode|위치 모드|Position|화살표|arrow)\\b",
                                   "note": "H4 (external review 2026-09-21): the step-7 screen is in view mode (hand cursor icon); switching to Position/Interact mode is a valid next action before selecting sticks (manual p.88 precondition 1)."})
LOG.append(f"{sid} s7 H4: + allowed alternative Position/Interact mode")
mb = sc["initial_state"]["must_be_true"]
mb[2] = "no child item under FaultStickSet in the tree (the category item itself is always shown)"
LOG.append(f"{sid} H5: initial_state.must_be_true[2] -> {mb[2]!r}")
sc["_study2_note"] += " GT finalised 2026-09-21 after external review (H4/H5 applied; V3-30)."
save(sid, sc)

(ROOT / "data/eval/study2/GT_final_applied_log.md").write_text("# Study 2 GT final edits on top of the external review (2026-09-21)\n\n" + "\n".join(f"- {l}" for l in LOG) + "\n", encoding="utf-8")
print("\n".join(LOG))
print("written:", sorted(p.name for p in TEST.glob("*.json")))
