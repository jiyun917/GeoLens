# Study 4 GT 검수 세션 — 고정 규칙 (2026-09-28)

이 폴더(`data/eval/study4/gt_review_session/`) 밖의 파일은 열지 않는다. 실행 로그, 모델 응답, 채점 결과(`data/eval/results/`, `*.log`, `run_*.json`, `verdict_*`)와 워크플로우 파일(`data/workflows/`, `data/eval/study4/workflows_draft/`)은 열지 않는다. 파이프라인·벤치를 실행하지 않는다. git 명령을 쓰지 않는다. 원본 초안(`scenarios/*.json`)은 수정하지 않고, 수정안은 `proposed/` 아래에 같은 파일명으로 저장한다.

입력: `screenshots/<scenario>/step_N.jpg` (24장: opendtect__spectral_decomp__01 9장, qgis__custom_projection__01 9장, qgis__aspect_north__01 6장), `gt_visible_elements_review_study4.md` (vision 열거 결과), `scenarios/*.json` (GT 초안: `steps[i].visual_state_gt` = current_dialog / visible_elements / data_state / current_action, 그리고 `capture_instructions`, `expected_action_text_pattern`, `expected_action_keywords`, `allowed_alternatives`), `manual_excerpts/*.txt` (매뉴얼 §1.5.2a / QGIS §6.1.4 / §7.3.6 원문), `CAPTURE_NOTES.md` (캡처자의 버전 차이 메모).

작은 글자는 Python(PIL)으로 3배 이상 확대 크롭해 이 폴더의 `crops/` 아래에 저장하고 Read 도구로 본다(트리·패널 항목, 툴바 값, 다이얼로그 필드, 표의 셀, 상태 표시줄, WKT 텍스트 상자). 규칙에 없는 경우는 판단하지 말고 **"보류"** 로 남긴다.

## 1. visible_elements (스텝별 전수 검수)
- 초안의 visible_elements는 vision 모델이 읽은 라벨 전부다. 화면에 없는 문자열(오독·환각)은 삭제하고, 철자·괄호·숫자·쉼표/마침표가 다르면 화면 원문으로 고친다(QGIS는 소수점에 쉼표를 쓸 수 있다: `0,0 °`; OpendTect 값은 `-8.7372`).
- 화면에 있는데 목록에 없는 텍스트 라벨(창 제목, 탭, 버튼, 필드 라벨과 값, 트리·목록·표 항목, 체크박스, 상태 표시줄, 속성 목록 항목, WKT 텍스트의 보이는 줄)은 추가한다. 텍스트 없는 아이콘 버튼은 매뉴얼이 이름을 부르는 경우에만 "매뉴얼 이름 + (icon)" 형식으로 추가한다.
- 잘린 항목은 화면 원문대로(잘린 채) 둔다(예: `Van der Gri...`). 좌표·수치는 화면 원문대로, 스텝 간 복사하지 않는다. 중복은 하나만 남긴다.

## 2. current_dialog / data_state / current_action
- 초안 문장이 스크린샷과 다르면 화면 사실에 맞게 고친다. 화면에서 확인할 수 없는 내용은 삭제하지 말고 "화면상 확인 불가, 세션 이력 기준" 문구를 확인/추가한다.
- `capture_instructions.screen_state`와 실제 화면이 다르면 `GT_change_list.md`에 적되 `capture_instructions`는 고치지 않는다.

## 3. 건드리지 않는 것
- `expected_action_text_pattern`, `expected_action_keywords`, `allowed_alternatives`, `expected_workflow_node`, `screenshot_path`, `goal`, `initial_state`, `completion`, `manual_grounding_sections`. 화면과 맞지 않는 점은 보류 목록에 사유와 함께 적는다(수정하지 않는다).

## 4. 표본 오독률
- 시나리오별 2장씩 6장(spectral_decomp step 1·5, custom_projection step 4·7, aspect_north step 1·3)에 대해 초안 visible_elements 전 항목을 대조해 오독 건수·비율을 보고한다. 5%를 넘으면 반영을 멈추고 보고서만 쓴다(`proposed/`를 만들지 않는다).

## 5. 결과물 (모두 이 폴더에 저장)
- `GT_change_list.md`(항목별 근거·규칙 번호), `GT_hold_list.md`, `sample_check.md`, `proposed/<scenario>.json`(GT 필드만 변경, 키 순서·indent 2·ensure_ascii=False 유지), `SUMMARY.md`. 파일 쓰기 도구가 이름을 거부하면 Python으로 저장한다.
