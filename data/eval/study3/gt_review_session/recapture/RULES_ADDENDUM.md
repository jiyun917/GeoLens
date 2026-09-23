# 재캡처 검수 규칙 보충 (2026-09-23) — opendtect__horizon_2dviewer__01 step 6·7·8만

- 상위 폴더의 RULES.md가 그대로 적용된다(폴더 밖 파일 금지, 파이프라인·git 금지, 규칙 3 필드 불변, 보류 규칙).
- 입력: `../screenshots/opendtect__horizon_2dviewer__01/step_6.jpg, step_7.jpg, step_8.jpg`(재캡처본), `opendtect__horizon_2dviewer__01_draft_v2.json`(새 초안; s0–s5는 이전 초안과 같고 s6–s8이 새로 채워짐), `gt_visible_elements_review_s6_s8.md`(s6–s8 vision 열거), `../CAPTURE_NOTES.md`(재캡처 절 참조), `../manual_excerpts/1_4_2b_tracking_in_2d_viewer.txt`.
- 할 일: s6·s7·s8의 visible_elements(규칙 1)와 current_dialog/data_state/current_action(규칙 2)을 스크린샷과 전수 대조해 정정한다. 표본 오독률은 세 스텝 전체로 계산한다(5% 초과 시 중단·보고).
- 결과물: `../proposed/opendtect__horizon_2dviewer__01.json`을 **갱신**한다 — 기존 proposed 파일의 s0–s5(이미 검수됨)는 그대로 두고, steps 6·7·8의 `visual_state_gt`만 검수한 값으로 바꾼다(키 순서·indent 2·ensure_ascii=False·LF·끝 개행 유지). 그리고 `GT_change_list_recapture.md`, `GT_hold_list_recapture.md`, `sample_check_recapture.md`, `SUMMARY_recapture.md`를 이 폴더(`recapture/`)에 쓴다.
