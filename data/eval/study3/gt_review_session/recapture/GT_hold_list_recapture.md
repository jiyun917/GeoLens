# Study 3 GT 보류 목록 — 재캡처 검수 (2026-09-23) — opendtect__horizon_2dviewer__01 step 6·7·8

본 세션 `GT_hold_list.md`의 H1–H13은 그대로 유효하다. 그중 **H12(s6·s7·s8 검수 제외)는 이번 검수로 해소**됐다(구 초안의 `Cross-line 0`/`Step 0` 표기와 `(212/493 (…` 이중 괄호는 새 초안 v2에 없음). 아래는 이번 3장에서 새로 생긴, 규칙에 없어 책임자 결정이 필요한 항목이다. 임의로 정하지 않았고, 이미 적용한 쪽은 "적용값"에 적었다.

## HR1. s7 `2D_Horizon` plain 항목 유지 여부 (H10 확장)
- 현상: s7 초안에 `2D_Horizon`(plain)과 `2D_Horizon (checked)`가 모두 있다. 화면에는 같은 이름의 요소가 둘(메인 트리·viewer 트리) 있고 **둘 다 체크박스가 체크**돼 있다. s3 선례(H10)는 "두 번째 요소가 있으면 plain도 유지"였지만 그때의 두 번째 요소는 체크박스가 없는 viewer 트리 항목이었다.
- 적용값: plain `2D_Horizon`도 유지(두 번째 요소가 있고, 이 문자열이 s6·s8 규칙 3 패턴이 참조하는 저장 이름이기도 함). 결과 s7에는 `2D_Horizon`·`2D_Horizon (checked)` 둘 다 있고, s8에는 초안대로 `2D_Horizon`(annotated 없음)만 있다.
- 결정할 것: (a) 적용값 유지, (b) annotated 하나로 통합(plain 삭제), (c) s6·s8처럼 이 시나리오의 상태 표기를 아예 통일. (c)는 H10과 함께 정해야 한다.

## HR2. s6에 추가한 `?`·`▷` (H11 확장)
- s4·s5 proposed와 통일하려고 s6에도 Settings 창의 `?`(Help)·`▷` 버튼 글리프를 추가했다. Output selection 대화상자에도 `?` 버튼이 있어 `?` 한 항목이 둘을 대표한다. H11에서 셋(s4·s5·s6)을 함께 빼는 결정도 가능.

## HR3. s6 잘린 축 라벨 `s)`
- 화면 사실: 2D viewer 왼쪽 축의 세로 라벨 `Time (ms)`가 Output selection 대화상자에 가려 `)`·`s`·(`m`의 획 일부)만 보인다. vision은 `(s)`로 읽었고 여는 괄호는 화면에 없다(`recapture/crops/…__s6__plot_ms12.png`).
- 적용값: 규칙 1 "잘린 항목은 잘린 채" + 괄호 정정 → `s)`. 오독률 집계에는 구두점 오독(형식성)으로 넣고 제외 시 비율도 병기했다.
- 결정할 것: `s)` 유지 / 판독 불가 조각으로 보고 삭제 / 가려진 라벨 전체 `Time (ms)`로 기록(이 경우 "잘린 채" 규칙의 예외가 됨).

## HR4. 겹친 축 라벨을 오독으로 세는 방식 (H7 관련, 집계만)
- `20021203-2-03_00xx`(s6 `_0000`, s7 `_0008`)는 판독 불가 자리를 vision이 임의로 채운 것이라 오독으로 셌고, 뒤 라벨 `20021203-2-02_0010`(앞 `200`이 겹침 구간)의 삭제도 본 세션 집계("겹침으로 판독 불가한 라벨 삭제")와 같이 오독으로 셌다. 뒤 라벨을 세지 않는 기준의 비율도 `sample_check_recapture.md`에 병기. 어느 기준으로도 5% 미만.

## HR5. 규칙 3 필드·지시서와 화면 (기록만, 미수정)
- s6 `capture_instructions.screen_state`의 "OK/Cancel/Help"·"<New 2D Horizon>"은 화면의 `?` 버튼·`<New 2D Horizon 1>`과 다르다(변경 목록 끝 표). 채점 패턴 `(2D_Horizon|OK|이름|name|Output 2D Horizon)`은 화면과 어긋나지 않음.
- s8 `allowed_alternatives`의 `Well correlation`은 H2와 같은 문제(화면 라인명은 `19981104-1-04_0037`); `2D Horizon|2D_Horizon|horizon` 대안으로 통과 가능. H2에서 함께 결정.
- s6·s7·s8의 `expected_workflow_node`·`expected_action_keywords`(`OK`, `2D Viewer`, `완료`)는 화면 상태와 모순 없음.

## HR6. data_state에 넣은 "not verifiable on screen — per session history" 문구
- s6 "대화상자가 viewer 트리의 Save as로 열렸다", s7 "Settings 창이 닫혔다", s8 "2D Viewer가 닫혔다"는 화면에서는 각각 '대화상자가 떠 있다', '창이 보이지 않는다'까지만 확인된다. 규칙 2대로 삭제하지 않고 문구를 붙였다. 영어로 쓴 것은 s0–s5 data_state가 영어라서다. 한국어 원문("화면상 확인 불가, 세션 이력 기준")으로 바꾸길 원하면 세 문장을 함께 고치면 된다.
