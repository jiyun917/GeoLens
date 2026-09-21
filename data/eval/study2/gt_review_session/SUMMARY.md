# Study 2 GT 검수 요약 (외부 검수, 2026-09-21)

## 무엇을 보았나
- 입력: RULES.md, gt_visible_elements_review_study2.md, scenarios/*.json 2개(16 스텝), manual_excerpts/*.txt 2개, screenshots/ 16장. 이 폴더 밖의 파일은 열지 않았고 파이프라인과 git은 실행하지 않았다.
- 16장 전부에 대해 PIL로 3배(일부 4-10배) 확대 크롭을 만들어 crops/<scenario>/ 에 저장하고 Read로 대조했다: 제목표시줄/메뉴/아이콘 툴바/위치 툴바/하단 편집 툴바/상태표시줄(*_sheetA.png), 트리 패널과 기즈모(*_sheetB.png), 다이얼로그(*_dialog*.png), 3D 장면 축 라벨(*_scene*.png|jpg, timeaxis_*.png), 스텝 간 비교 시트(steps1-8_bottomleft_icons8x.png, lefttoolbar_0_3_4_5_7.png, seedmarkers_4_5_6.png, trackicons_4_5_6.png, gizmos_wide.png).
- 초안 visible_elements 927개 항목(fault_sticks 487, horizon_autotrack 443)을 전수 대조했다.

## 표본 오독률 (규칙 4)
- hz step 1(58), hz step 4(67), fs step 2(61), fs step 7(51) = 237 항목 중 화면에 없는 문자열 0건 -> 0.0 % (텍스트 없는 아이콘을 기호로 옮긴 ▷ 1건을 엄격히 포함해도 0.42 %). 5 % 미만이므로 proposed/ 를 작성했다. 상세: sample_check.md.

## 무엇을 바꿨나 (proposed/<scenario>.json, 상세: GT_change_list.md)
- 바꾼 필드는 visible_elements 와 data_state 뿐이다. current_dialog, current_action, _gt_provenance 와 규칙 3 필드는 원본과 동일하며 키 순서, 들여쓰기 2, ensure_ascii=False, 끝 개행을 유지했다(crops/build_proposed.py 로 생성, 원본 왕복 직렬화 동일성 확인).
- 오독 삭제/수정 4건: hz step 0, 5 의 N (기즈모에 E, Z 만 표시), hz step 3 의 F (E 를 두 번 읽음), fs step 8 의 Tr -> Ti (단면에 가려진 Time 라벨).
- 텍스트 없는 아이콘 기호 ▷ 2건 삭제(hz step 3, 4).
- 표기 통일 58건(괄호 형식 "In-line (130)", 다이얼로그 "라벨 (값)", "Select..." 띄어쓰기), [checked]/[unchecked] 주석 제거 41건, 중복 제거 8건.
- 누락 라벨 추가 16건: SEG-Y (fs step 1, 4, 8), Time 축 눈금 1500 (fs step 0-5), ? (hz step 1), 매뉴얼이 이름을 부르는 Auto-Track (icon), Retrack-All (icon) (hz step 4-6).
- data_state 10 스텝 수정: 화면과 다른 문장 3건을 고쳤고(hz step 4 "Status bar shows coordinates and Value" -> 비어 있음; fs step 4 "Visually identical to step 3" -> 하단 툴바 아이콘 토글, undo 활성; hz step 6 "Visually identical to step 5" -> 시드 표시 색 변화), 화면에서 확인 불가한 내용 7곳(Only at Sections, Lock, 딥스티어링 라이선스, 다른 인라인의 스틱, Correlation 미편집, Peak 이벤트, 잘린 속성 이름)에 "화면상 확인 불가, 세션 이력 기준" 문구를 덧붙였다.
- capture_instructions 와 화면의 차이 6건은 기록만 했다(fs step 0 "In-line view" vs 원근 뷰, fs step 4 "Position mode/Edit Sticks 토글" 확인 불가, fs step 7 "View North" vs 기울어진 상면 뷰, fs step 8 툴바 "closed", hz step 2 "Picked on: 4 Dip steered median filter" vs 빈 필드, hz step 4 "cross cursor" 미캡처).

## 보류 (GT_hold_list.md)
- 규칙 3 관련 5건: H3 hz step 3 허용 대안 Steering|No|DipSteer (DipSteer 탭 없음, No 과다 매칭); H4 fs step 7 왼쪽 툴바 손 모양 커서 -> Position mode 전환이 정당한 다음 행동일 수 있으나 패턴이 허용 안 함; H5 initial_state "no FaultStickSet/3D Horizon item" 문구; H6 fs step_2.jpg 크기 1920x1032; H7 hz step 4 키워드 Auto-Track 은 화면 문자열이 아님.
- 아이콘 처리 3건: H1 fs 하단 툴바 Edit Sticks/Select sticks/Remove Selected Sticks/Go! 아이콘 식별 불가; H2 hz step 1-3 의 비활성 Auto-Track/Retrack-All 아이콘; H8 hz 메인 툴바 추적 아이콘 6개는 매뉴얼에 이름 없음.
- 규칙 해석 확인 요청 5건(C1-C5: 괄호 통일, 주석 제거, ?/▷ 취급, Tr->Ti, 가려진 1500 추가) - 되돌리는 방법을 각 항목에 적었다.

## 결과물
GT_change_list.md, GT_hold_list.md, sample_check.md, proposed/opendtect__fault_sticks__01.json, proposed/opendtect__horizon_autotrack__01.json, SUMMARY.md(이 문서). 작업용 크롭과 생성 스크립트는 crops/ 에 있다(build_proposed.py 는 초안을 읽고 proposed/ 만 쓴다; diff.json 은 항목별 변경 로그).
