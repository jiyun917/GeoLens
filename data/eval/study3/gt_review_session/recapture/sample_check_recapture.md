# Study 3 표본 오독률 — 재캡처 검수 (2026-09-23) — opendtect__horizon_2dviewer__01 step 6·7·8

RULES_ADDENDUM.md대로 표본은 재캡처 3장 전체이고, 각 스텝의 초안(`recapture/opendtect__horizon_2dviewer__01_draft_v2.json`) `visible_elements` 전 항목을 확대 크롭(`recapture/crops/`)과 대조했다. 판정 기준은 본 세션 `sample_check.md`와 같다: 오독 = (a) 화면에 없는 문자열, (b) 철자·숫자·구두점이 화면 원문과 다른 항목, (c) 화면 상태와 다른 `(checked)`류 표기. 오독으로 세지 않은 것 = 같은 요소의 중복(15건), 누락(추가 5건), `라벨 (값)` 묶음 표기.

## 결과

| step | 초안 항목 수 | 오독 수 | 오독 항목 | 스텝 오독률 |
|---|---|---|---|---|
| 6 | 74 | 3 | `20021203-2-03_0000`(겹쳐서 판독 불가한 자리, H7), `20021203-2-02_0010`(앞 `200`이 겹침 구간; 삭제·겹침 표기에 포함), `(s)`(여는 괄호 없음 → `s)`, 형식성) | 4.05% |
| 7 | 93 | 4 | `Scene 1 (checked)`(체크박스 없음), `VD (unchecked)`(실제 checked), `20021203-2-03_0008`(겹침), `20021203-2-02_0010`(겹침) | 4.30% |
| 8 | 51 | 0 | — | 0.00% |
| **합계(풀링)** | **218** | **7** | | **3.21%** |

- 겹친 뒤 라벨 `20021203-2-02_0010` 삭제 2건을 세지 않으면 5 / 218 = **2.29%**; 거기서 형식성 `(s)`까지 빼면 4 / 218 = **1.83%**.
- 어느 기준으로도 5% 미만 → 보충 규칙의 중단 조건에 해당하지 않아 `proposed/opendtect__horizon_2dviewer__01.json`의 steps 6–8을 갱신했다.
- 환각(화면에 전혀 없는 문자열)은 0건. 의미 있는 상태 오독은 s7의 `VD (unchecked)`·`Scene 1 (checked)` 2건이고, 나머지는 겹침 자리의 추정 숫자와 잘린 조각의 괄호다.
- 참고: 본 세션 6장 표본(7/397, 1.76%)과 합치면 14 / 615 = 2.28%.

## 크롭 근거
`recapture/crops/opendtect__horizon_2dviewer__01__s6__{top, tree_main, settings, viewer_head, viewer_tree, output_dlg, plot_top, plot_left, plot_ms, plot_ms12, plot_right, plot_bottom, axes_l, axes_r, scene200, scene_bl, nez, status_l, status_r}.png`,
`…__s7__{top, tree_main, viewer_head, viewer_tree, plot_top, plot_left, plot_ms8, plot_right, plot_bottom, axes_l, axes_r, scene200, scene_labels, scene_bl, nez, status_l, status_m, status_r}.png`,
`…__s8__{top, tree_main, axes_l, axes_r, scene200, scene_labels, scene_bl, picks, nez, status_l, status_r}.png` (생성 스크립트 `recapture/crops/crop_recapture.py`).
