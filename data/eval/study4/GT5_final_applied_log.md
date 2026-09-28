# Study 5 GT final edits on top of the external review (2026-09-28; owner decisions delegated to the main session)

External review: sample misread 1.34% (6/449) < 5%; 1,498 items checked, 1 deleted, 32 corrected, 36 added; data_state corrected in 6 steps; current_dialog/current_action unchanged.

- B-1 (hold): QGIS status-bar decimal mark is a period per the reviewer's glyph comparison; the proposed files already use periods -> ACCEPTED (consistent with study 3 H1).
- opendtect__spectral_decomp__01: proposed accepted as final (visible_elements/data_state edits per GT_change_list.md); rule-3 fields unchanged.
- qgis__custom_projection__01 s6 H6: pattern '(?i)\\b(Van der Grinten|Filter|필터|USER:100000|User Defined)\\b' -> '(?i)\x08(Van der Grinten|Filter|필터|USER:100000|User[- ]?Defined)\x08' (QGIS 3.44 group label 'User-defined'; manual/authored 'User Defined' kept; reviewer hold on a rule-3 field, decided by the owner before any model run)
- qgis__aspect_north__01: proposed accepted as final; the 'Reference layer' vs 'Input layers' hold is covered by H4 (pattern alias), keywords unchanged.
- Other holds (icon glyph items ?, ε, +, -; ellipsis characters; double spaces; truncated labels; 'Attribute Set 3D (icon)' naming): left as the reviewer wrote them; no further edits.

- Repair (same session, before any model run on the set): the H6 pattern was first written through a shell heredoc that turned '\b' into a backspace character; rewritten from scripts/study5_fix_h6_pattern.py and verified (no control characters in any final pattern; both spellings match). The selection run's OpendTect pass had started before the repair; the QGIS pass (which uses this file) had not.
