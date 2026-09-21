# 보류 목록 — Study 2 외부 검수 (2026-09-21)

규칙 3 필드(`expected_action_text_pattern`, `expected_action_keywords`, `allowed_alternatives`, `expected_workflow_node`, `screenshot_path`, `goal`, `initial_state`, `completion`)는 수정하지 않았다. 아래는 화면과 맞지 않거나 규칙에 없어 판단을 보류한 항목이며, 연구 책임자의 결정이 필요하다.

## A. 규칙 3 필드 관련
| # | 항목 | 스크린샷 | 사유 |
|---|---|---|---|
| H3 | hz step 3 `allowed_alternatives[0].pattern` = `(?i)\b(Steering\|No\|DipSteer)\b` | `screenshots/opendtect__horizon_autotrack__01/step_3.jpg` (다이얼로그 탭 640,388,1000,420) | 화면의 탭은 Mode·Event·Correlation·Properties 4개뿐이고 DipSteer 탭이 없어(딥스티어링 라이선스 없음) 매뉴얼 11번 "Steering = No" 행동은 이 세션에서 일어날 수 없다. 또한 단독 토큰 `No` 는 무관한 문장("Use Correlation = No" 등)에도 매칭되어 허용 대안이 지나치게 느슨하다. 유지/삭제/축소 여부 결정 필요 |
| H4 | fs step 7 `expected_action_text_pattern`·`allowed_alternatives`(비어 있음) | `screenshots/opendtect__fault_sticks__01/step_7.jpg` 왼쪽 메인 툴바 맨 위 아이콘 (0,130,50,175); `crops/opendtect__fault_sticks__01/lefttoolbar_0_3_4_5_7.png` | step 0–6 은 초록 화살표 아이콘인데 step 7 만 손 모양 커서 아이콘으로 바뀌어 있다. 이것이 뷰(회전) 모드를 뜻한다면 매뉴얼 §1.4.3b p.88 의 전제 "1) Position mode is selected" 가 깨진 상태이고, "Position mode 로 전환" 이 정당한 다음 행동이 되지만 step 7 패턴(`Copy Selection\|Create Single New\|Fault_01A\|select\|Select\|선택\|polygon\|폴리곤\|Ctrl\|Go`)은 이를 허용하지 않는다. 아이콘 의미(현재 모드 표시 vs 전환 대상 표시)를 화면만으로 단정할 수 없어 보류 |
| H5 | fs `initial_state.must_be_true[2]` "no FaultStickSet item in the tree"; hz `initial_state.must_be_true[2]` "no 3D Horizon in the tree" | fs step_0.jpg 트리 (48,402,305,690), hz step_0.jpg 트리 | 트리에는 `FaultStickSet`·`3D Horizon` 범주 항목이 항상 표시된다(자식만 없음). 문구 의도("자식 항목 없음")는 맞지만 문자 그대로는 화면과 어긋남. 문구 조정 여부 결정 필요 |
| H6 | fs step 2 `screenshot_path` 가 가리키는 `step_2.jpg` 크기 | `screenshots/opendtect__fault_sticks__01/step_2.jpg` | 1920×1032 로 다른 15장(1922×1041)과 다름(창 크기/캡처 차이). 내용 검수에는 지장 없으나 좌표 기반 처리가 있다면 확인 필요 |
| H7 | hz step 4 `expected_action_keywords` = `["Auto-Track"]` | hz step_4.jpg 다이얼로그 아이콘 열 (1120,150,1160,470) | 화면에 "Auto-Track" 이라는 문자열은 없고 텍스트 없는 아이콘만 있다. 수정안에는 규칙 1 아이콘 조항으로 `Auto-Track (icon)` 을 넣었으므로 grounding 은 통과하지만, 키워드가 화면 문자열이 아니라는 점은 기록해 둔다(변경 요청 아님) |

## B. 규칙에 없어 판단을 보류한 것 (visible_elements 관련)
| # | 항목 | 스크린샷 | 사유 |
|---|---|---|---|
| H1 | fs 하단 편집 툴바의 텍스트 없는 아이콘들에 매뉴얼 이름을 붙여 추가할지: `Edit Sticks (icon)`, `Select sticks (icon)`, `Remove Selected Sticks (icon)`, `Go! (icon)` | fs step_1–8.jpg 하단 툴바 (0,985,910,1018); `crops/opendtect__fault_sticks__01/steps1-8_bottomleft_icons8x.png` | 매뉴얼 §1.4.3b p.88–91 이 이 네 아이콘을 이름으로 부르지만, 화면의 어느 아이콘이 어느 이름인지(맨 왼쪽 큐브 아이콘 = Edit Sticks?, 빨간 올가미 = Select sticks?, 초록 체크 = Go!?, 휴지통 = Remove Selected Sticks?)를 화면만으로 확정할 수 없어 추가하지 않았다. step 4–6 에서 맨 왼쪽 큐브 아이콘이 토글 on 상태인 사실은 `data_state` 에만 적었다. 이름 확정 후 추가 여부 결정 필요 |
| H2 | hz step 1–3 의 `Auto-Track (icon)`, `Retrack-All (icon)` | hz step_1–3.jpg 다이얼로그 아이콘 열 (650,395,692,575) | 아이콘은 보이지만 회색(비활성) 상태. 규칙 1 에 비활성 아이콘 처리 조항이 없어 활성 상태인 step 4–6 에만 추가했다. step 1–3 에도 넣을지 결정 필요 |
| H8 | hz step 4–6 메인 툴바에 새로 나타난 추적 아이콘 6개(톱니, 막대그래프, 톱니+점, 저장, 자물쇠, 빨간 막대) | hz step_4.jpg (640,88,870,122); `crops/opendtect__horizon_autotrack__01/trackicons_4_5_6.png` | 매뉴얼 p.71 은 "the icon in the toolbar in the upper section" 이라고만 하고 이름을 부르지 않아 추가하지 않았다. `data_state` 에 "six additional tracking icons (no text)" 로만 기록 |

## C. 규칙 해석에 대한 확인 요청 (이미 적용했으나 책임자 확인 권고)
| # | 적용한 해석 | 근거 규칙 | 되돌릴 경우 |
|---|---|---|---|
| C1 | 괄호 표기 통일: `In-line (130)` → `In-line 130`, `Event type (Peak)` → `Event type` + `Peak`, `Compare window (ms) (-40, 40)` → `Compare window (ms)` + `-40` + `40` | 규칙 1 "괄호가 다르면 화면 원문" | `crops/build_proposed.py` 의 `FS_OPS`/`HZ_OPS` 에서 해당 `rep` 항목을 제거하고 재실행 |
| C2 | `[checked]`/`[unchecked]` 주석 제거(체크 상태는 `data_state` 문장으로) | 규칙 1 (화면에 없는 문자열) | 같은 스크립트의 `strip_state` 항목 제거 |
| C3 | `?` 는 문자 글리프로 보고 유지·hz step 1 에 추가; `▷` 는 텍스트 없는 아이콘으로 보고 삭제 | 규칙 1 아이콘 조항 | 스크립트에서 `add_after Close ["?"]`, `del ▷` 조정 |
| C4 | fs step 8 의 가려진 Time 라벨: `Tr` → `Ti`(보이는 글자만) | 규칙 1 "화면 원문" | 항목 자체를 삭제하는 쪽이 낫다고 판단되면 `rep Tr → Ti` 를 `del Tr` 로 |
| C5 | 단면에 일부 가려졌지만 판독 가능한 Time 축 눈금 `1500` 을 fs step 0–5 에 추가 | 규칙 1 (화면에 있으나 목록에 없는 라벨) | `add_after Time ["1500"]` 제거 |
