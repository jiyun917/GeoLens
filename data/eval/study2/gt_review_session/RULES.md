# Study 2 GT 검수 세션 — 고정 규칙 (2026-09-21)

이 폴더(`data/eval/study2/gt_review_session/`) 밖의 파일은 열지 않는다. 특히 실행 로그, 모델 응답, 채점 결과(`data/eval/results/`, `*.log`, `run_*.json`, `dev_iter*`, `verdict_*`)와 워크플로우 파일(`data/workflows/`)은 열지 않는다. 파이프라인·벤치를 실행하지 않는다. git 명령을 쓰지 않는다. 원본 초안(`scenarios/*.json`)은 수정하지 않고, 수정안은 `proposed/` 아래에 같은 파일명으로 저장한다.

입력: `screenshots/<scenario>/step_N.jpg` (16장: horizon_autotrack 7장, fault_sticks 9장), `gt_visible_elements_review_study2.md` (vision 열거 결과), `scenarios/*.json` (GT 초안: `steps[i].visual_state_gt` = current_dialog / visible_elements / data_state / current_action, 그리고 `capture_instructions`, `expected_action_text_pattern`, `expected_action_keywords`, `allowed_alternatives`), `manual_excerpts/*.txt` (매뉴얼 §1.4.2a·§1.4.3b 원문).

스크린샷은 1922×1041이다. 작은 글자는 Python(PIL)으로 3배 이상 확대 크롭해 이 폴더의 `crops/` 아래에 저장하고 Read 도구로 본다(트리 항목, 툴바 값, 다이얼로그 필드, 상태 표시줄).

규칙에 없는 경우는 판단하지 말고 **"보류"** 로 남긴다.

## 1. visible_elements (스텝별 전수 검수)
- 초안의 visible_elements는 vision 모델이 읽은 라벨 전부다. 각 항목을 스크린샷과 대조해 **화면에 없는 문자열(오독·환각)은 삭제**하고, 철자·괄호·숫자가 다르면 **화면 원문**으로 고친다.
- 화면에 있는데 목록에 없는 **텍스트 라벨**(창 제목, 탭, 버튼, 필드 라벨과 값, 트리 항목, 체크박스, 상태 표시줄)은 추가한다. 텍스트 없는 아이콘 버튼은 매뉴얼이 이름을 부르는 경우에만 "매뉴얼 이름 + (아이콘)" 형식으로 추가한다(예: `Auto-Track (icon)`).
- 잘린 트리 항목(`4 Dip steered medi...`)은 화면 원문대로 둔다(잘린 채). 매뉴얼 이름 전체(`4 Dip steered median filter`)가 다른 곳(툴바 등)에 보이면 그것도 별도 항목으로 둔다.
- 좌표·수치(`(612287, 6074487, 1066.9)`, `0.61389`)는 화면 원문대로. 스텝마다 다르므로 스텝 간 복사하지 않는다.
- 중복 항목은 하나만 남긴다.

## 2. current_dialog / data_state / current_action
- 초안 문장이 스크린샷과 다르면 화면 사실에 맞게 고친다(예: 탭 이름, 필드 값, 트리 항목 유무). 화면에서 확인할 수 없는 내용(예: "Lock 완료", "Only at Sections 켜짐")은 **삭제하지 말고** "화면상 확인 불가, 세션 이력 기준" 문구가 있는지 확인하고 없으면 덧붙인다.
- `capture_instructions.screen_state`와 실제 화면이 다르면(예: 축소 여부, 카메라 각도) 그 차이를 `GT_change_list.md`에 적되 `capture_instructions`는 고치지 않는다.

## 3. 건드리지 않는 것
- `expected_action_text_pattern`, `expected_action_keywords`, `allowed_alternatives`, `expected_workflow_node`, `screenshot_path`, `goal`, `initial_state`, `completion`. 이들은 캡처 전에 확정된 것이며, 화면과 맞지 않는 점이 보이면 **보류 목록**에 사유와 함께 적는다(수정하지 않는다).

## 4. 표본 오독률
- 시나리오별로 2장씩 4장(horizon_autotrack step 1·4, fault_sticks step 2·7)에 대해 초안 visible_elements 전 항목을 스크린샷과 대조해 **오독(화면에 없는 문자열) 건수와 비율**을 보고한다. 5%를 넘으면 반영을 멈추고 보고서만 쓴다(`proposed/`를 만들지 않는다).

## 5. 결과물 (모두 이 폴더에 저장)
- `GT_change_list.md`: 변경 목록. 항목별 근거(어느 스크린샷의 어느 위치를 보고 판단했는지)와 적용 규칙 번호.
- `GT_hold_list.md`: 보류 항목(항목, 스크린샷 경로, 사유).
- `sample_check.md`: 규칙 4 결과(장별 항목 수, 오독 원문, 건수·비율).
- `proposed/<scenario>.json`: GT 필드만 바꾼 시나리오 파일(키 순서·들여쓰기 유지, `ensure_ascii=False`, indent 2).
- `SUMMARY.md`: 무엇을 보았고 무엇을 바꿨는지, 보류 건수, 오독률.
