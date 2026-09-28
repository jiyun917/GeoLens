# -*- coding: utf-8 -*-
"""Repair of the H6 pattern of qgis__custom_projection__01 s6: the first write went through a shell heredoc that
turned the regex word boundary \\b into a backspace character (0x08). Rewrites the pattern from this file (no
shell involved) in both copies of the final GT and checks every final pattern for control characters."""
import glob, json, re
PAT = r"(?i)\b(Van der Grinten|Filter|필터|USER:100000|User[- ]?Defined)\b"
for p in ("data/eval/scenarios/.study5_test_qgis/qgis__custom_projection__01.json", "data/eval/scenarios/qgis__custom_projection__01.json"):
    sc = json.load(open(p, encoding="utf-8"))
    st = sc["steps"][6]
    st["expected_action_text_pattern"] = PAT
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sc, fh, ensure_ascii=False, indent=2); fh.write("\n")
    print(p, "->", st["expected_action_text_pattern"])
bad = 0
for p in glob.glob("data/eval/scenarios/.study5_test_*/*.json"):
    sc = json.load(open(p, encoding="utf-8"))
    for st in sc["steps"]:
        for s in [st.get("expected_action_text_pattern") or ""] + [a.get("pattern") or "" for a in st.get("allowed_alternatives") or []]:
            if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", s):
                bad += 1; print("CONTROL CHAR in", p, st["step_index"], repr(s)[:80])
            re.compile(s)
print("control-char patterns:", bad)
assert re.search(PAT, "User-defined 아래의 Van der Grinten I 을 선택하세요") and re.search(PAT, "User Defined Coordinate Systems")
print("H6 pattern matches both spellings")
