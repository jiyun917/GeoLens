# Study 3 GT 외부 검수 요약 — 재캡처분 (2026-09-23)

## 범위와 방법
- 대상: `opendtect__horizon_2dviewer__01` step 6·7·8 재캡처본 3장(s6 1920×1032, s7·s8 1922×1041). 초안은 `recapture/opendtect__horizon_2dviewer__01_draft_v2.json`(s0–s5는 이전 초안과 동일함을 스크립트로 확인; s6–s8만 새로 채워짐), vision 열거는 `recapture/gt_visible_elements_review_s6_s8.md`.
- CAPTURE_NOTES.md "C 재캡처" 절의 화면 사실(s6: Output selection + 2D Viewer + Settings 창 동시 표시, s7: 대화상자 닫힘·두 트리에 `2D_Horizon`·viewer 열림·Settings 안 보임, s8: viewer 없음·scene에 라인+horizon·메인 트리 `2D_Horizon`)은 세 장 모두 스크린샷에서 직접 확인했다(일치).
- PIL 3–12배 크롭(`recapture/crops/`)을 Read로 확인. 초안 `visible_elements` 218개 전 항목과 `current_dialog`/`data_state`/`current_action`을 대조. 규칙 3 필드·`capture_instructions`·원본 초안은 건드리지 않았다.

## 표본 오독률 (세 스텝 전체) — 5% 미만, 반영 진행
- **7 / 218 = 3.21%** (s6 3/74, s7 4/93, s8 0/51). 겹친 뒤 라벨 삭제 2건 제외 시 2.29%, 형식성 `(s)`까지 제외 시 1.83%. 환각 0건. 상세는 `sample_check_recapture.md`.

## 변경 (`GT_change_list_recapture.md`) — 30건: 수정 4, 삭제 18, 추가 5, data_state 3
- s6 (7): 겹친 축 라벨 → `20021203-2-03_00...21203-2-02_0010`(뒤 라벨 삭제), `(s)` → `s)`, `?`·`▷`·`200` 추가(s4·s5와 통일), data_state에 "opened from the 2D viewer tree" 화면 확인 불가 문구·Settings 창이 메인 트리를 가림을 명시.
- s7 (21): `VD (unchecked)` → `VD (checked)`, `Scene 1 (checked)` 삭제(체크박스 없음), 겹친 축 라벨 통일, plain/annotated 중복 15건 정리(s3 선례; `Cross-line`·`19981104-1-04_0037`·`2D Horizon`·`FaultStickSet`·`PointSet`·`2D_Horizon`은 두 번째 요소가 있어 plain 유지), `200` 추가, data_state의 "saved"/"Settings closed"를 화면 사실 + 세션 이력 문구로.
- s8 (2): `200` 추가, data_state에 viewer "no longer visible(세션 이력 기준)"·흰 pick 사각형·상태줄 `[free mem]`만 표시 명시.
- current_dialog·current_action은 세 스텝 모두 변경 없음.

## 결과물
- `proposed/opendtect__horizon_2dviewer__01.json` **갱신**: steps 6·7·8의 `visual_state_gt`만 교체(s6 75개, s7 72개, s8 52개 항목). 적용 스크립트 `recapture/apply_recapture_gt.py`가 s0–s5 객체 동일·step 6 이전 바이트 동일·최상위/비GT 필드 동일·키 순서·indent 2·ensure_ascii=False·LF·끝 개행을 검증했다(통과). 이전 proposed의 PROVISIONAL s6·s7과 빈 s8은 사라짐.
- `recapture/GT_change_list_recapture.md`, `GT_hold_list_recapture.md`, `sample_check_recapture.md`, `SUMMARY_recapture.md`(이 파일), 크롭 `recapture/crops/`(+ `crop_recapture.py`).

## 보류 (`GT_hold_list_recapture.md`) — 책임자 결정 필요
- **HR1** s7 `2D_Horizon` plain을 `2D_Horizon (checked)`와 함께 남겼다(두 번째 요소가 viewer 트리에 있으나 그것도 체크됨) — H10 관례와 함께 결정.
- **HR2** s6에 `?`·`▷` 추가(H11 확장) — s4·s5·s6에서 함께 빼는 것도 가능.
- **HR3** s6 잘린 세로 축 라벨 조각 `s)` — 유지 / 삭제 / `Time (ms)` 전체 기록 중 선택.
- HR4 겹친 라벨 집계 기준(정보), HR5 s6 지시서의 "Help"·`<New 2D Horizon>` 표기와 s8 대안 `Well correlation`(H2와 동일, 미수정), HR6 "not verifiable on screen — per session history" 문구의 언어.
- 본 세션 H12(s6–s8 제외)는 해소. H1–H11·H13은 그대로.
