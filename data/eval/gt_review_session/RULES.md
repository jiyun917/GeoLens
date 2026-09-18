# GT 검수 세션 — 고정 규칙 (2026-09-18, 사용자 지시 원문 기준)

이 폴더(`data/eval/gt_review_session/`) 밖의 파일은 열지 않는다. 특히 실행 로그, 모델 응답, 채점 결과(`data/eval/results/`, `*.log`, `run_*.json`, `dev_iter*`)는 열지 않는다. 파이프라인·벤치를 실행하지 않는다. git 명령을 쓰지 않는다. 원본 시나리오 파일(`scenarios/*.json`)은 수정하지 않고, 수정안은 `proposed/` 아래에 같은 파일명으로 저장한다.

입력: `screenshots/<scenario>/step_N.jpg` (24장), `gt_visible_elements_review_v3.md` (vision 열거 결과와 B 25건 목록), `scenarios/*.json` (현재 GT: `steps[i].visual_state_gt.visible_elements`, `expected_action_text_pattern`, `allowed_alternatives`), `manual_excerpts/*.txt` (매뉴얼 해당 절 원문), `survey_s0_add_button_x3.png` / `survey_s0_context.png` (survey step 0 Add 버튼 확대 크롭).

규칙에 없는 경우는 판단하지 말고 **"보류"** 로 남긴다.

## 1. B 25건 (vision이 못 읽은 현 GT 항목)
- 스크린샷에 실제로 보이는 **텍스트 없는 아이콘 버튼** → 유지. 표기는 "매뉴얼의 이름 + 기호"(예: `Add (+)`)로 통일한다.
- **서술형**으로 적힌 항목 → 화면에 라벨이 있으면 그 **라벨 원문**으로 바꾸고, 라벨이 없으면 유지한다.
- 스크린샷에서 **보이지 않는** 항목 → 삭제한다.

## 2. 표본 검수
- 시나리오별로 1장씩 3장(survey_setup step 0, attribute_computation step 3, qgis__vector_buffer step 3)을 골라, 현재 GT `visible_elements`에 들어간 vision 열거 항목을 스크린샷과 대조한다.
- 화면에 없는 문자열(오독)의 **건수와 비율**을 보고한다. 오독이 **5%를 넘으면** 반영을 멈추고 보고한다(그 경우 `proposed/`에 파일을 만들지 않고 보고서만 쓴다).

## 3. survey step 0의 Add 버튼
- 스크린샷에서 텍스트 라벨 없이 "+" 아이콘만 있고, **매뉴얼이 이 버튼을 Add 또는 "+"로 부르면**, `expected_action_text_pattern`은 그대로 두고 `allowed_alternatives`에 `+`, `플러스`, `더하기`만 추가한다. 그 외 표현은 추가하지 않는다. 매뉴얼이 다른 이름으로 부르면 규칙에 없으므로 **보류**로 남긴다(매뉴얼 원문을 인용).

## 4. QGIS step 3
- 스크린샷에서 Input layer 칸이 이미 `roads_33S`로 채워져 있는지 확인한다. 채워져 있으면 그 사실을 `visual_state_gt`에 적고(예: `data_state` 또는 visible_elements의 해당 항목에 값 명시), 기대 동작(`expected_action_text_pattern` / keywords)이 "입력 레이어 선택"을 요구하고 있다면 화면 상태에 맞게 고친다.
- QGIS는 **GT 필드만** 고친다. signature·워크플로우는 건드리지 않고 실행하지 않는다.

## 5. 결과물 (모두 이 폴더에 저장)
- `GT_change_list.md`: 변경 목록 한 장. 항목별로 **근거**(어느 스크린샷의 어느 위치(창/패널/버튼 근처)를 보고 판단했는지)와 적용한 규칙 번호.
- `GT_hold_list.md`: 보류 항목 목록(항목, 스크린샷 경로, 보류 사유 = 어느 규칙에도 해당하지 않음).
- `sample_check.md`: 규칙 2의 표본 검수 결과(스크린샷별 열거 항목 수, 오독 항목 원문, 건수·비율).
- `proposed/<scenario>.json`: GT 필드만 바꾼 시나리오 파일(원본과 diff 가능하도록 키 순서·들여쓰기 유지, `ensure_ascii=False`, indent 2). 바꾸지 않은 시나리오는 그대로 복사한다.
- `SUMMARY.md`: 세션 요약(무엇을 보았고 무엇을 바꿨는지, 보류 건수, 오독률, survey s0·QGIS s3 결론).
