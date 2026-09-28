# GT_hold_list.md — 보류 목록 (외부 GT 검수, 2026-09-28)

## A. 규칙 3 필드(수정하지 않음) — 화면과 맞지 않는 점

| # | 시나리오/step | 필드 | 내용 | 영향 |
|---|---|---|---|---|
| A-1 | qgis__custom_projection__01 s6 | expected_action_text_pattern | 대안 `User Defined`(공백)인데 화면 그룹 라벨은 `User-defined`(하이픈, 소문자 d). 모델이 화면 라벨을 그대로 쓰면 `\bUser Defined\b`는 매치되지 않음 | `Van der Grinten`·`Filter`·`USER:100000` 대안으로 여전히 매치 가능 |
| A-2 | qgis__aspect_north__01 s2 | expected_action_keywords `["Reference layer"]` | 화면 라벨은 `Input layers`(3.44). 패턴에는 `Input layers?`가 이미 있음(H4) | 키워드 문자열 자체는 화면에 없음 |
| A-3 | qgis__aspect_north__01 | goal | "Reference layer = aspect" — 화면 라벨은 `Input layers`, 필드 값은 `1 input selected`(레이어 이름 미표시) | 서술상 차이 |
| A-4 | opendtect__spectral_decomp__01 s1 | expected_action_text_pattern | 대안 `Select\.\.\.`/`Select…` — 화면 버튼은 `Select ...`(점 앞 공백). 대안 `Select`로 매치되므로 실질 영향 없음 | 없음 |
| A-5 | opendtect__spectral_decomp__01 s0, s3 | capture_instructions.must_not_show | "Select Input Horizon(s) dialog" — 실제 제목 `Select Horizons` (GT_change_list.md 규칙 2 표 참조) | 없음 |
| A-6 | opendtect__spectral_decomp__01 s3 | expected_action_text_pattern | `A 아이콘`·`Attribute Set` 대안 — 화면의 툴바 아이콘에는 텍스트가 없음(GT에는 `Attribute Set 3D (icon)`로 추가) | 없음 |

## B. 판단 보류 (규칙에 없거나 애매한 경우 — 확인 요청)

| # | 항목 | 상황 | 처리 |
|---|---|---|---|
| B-1 | **QGIS 소수점 문자** | RULES.md 규칙 1 예시는 `0,0 °`이지만, 픽셀 비교 결과 소수점 글리프는 문장 마침표와 동일한 1×2 px 점이고 쉼표는 꼬리가 있는 3행 글리프다(sample_check.md 근거 1, `crops/decimal_mark_composite.png`). 초안이 같은 글꼴의 `0.093473`을 마침표로 읽은 것과도 일치 | 초안의 소수점 쉼표 4건(F s0 ×2, G s5 ×1, 규칙 예시 자체)을 마침표로 정정. 주 세션에서 캡처 원본(PNG)으로 재확인 요망. 만약 쉼표가 맞다면 F s0·G s5의 해당 3항목과 데이터 상태 서술을 되돌리면 됨(다른 step의 초안은 이미 마침표) |
| B-2 | 말줄임 문자 `...` vs `…` | QGIS는 `Search…`, `Run as Batch Process…`, `…` 버튼, Qt 생략 `Van der Gri…`를 U+2026로 그릴 가능성이 높고(점이 가운데 높이), OpendTect `Select ...`는 기준선의 점 3개 | 초안 표기(`...`) 유지. 채점기가 정규화하지 않으면 통일 필요 |
| B-3 | 아이콘 글리프 항목 `?`, `ε`, `+`, `-` | 텍스트가 아닌 아이콘이지만 vision이 일부 step에만 적음(`?` E s1·s2, `ε` G s1·s4, `+`/`-` F s3) | 있는 곳은 유지, 다른 step에는 전파하지 않음(규칙 1의 아이콘 조항은 매뉴얼 명명 아이콘만 허용) |
| B-4 | 공백 2개 가능성 | E s1 `Demo 3 --> Top Foresets`: '3'과 '-->' 사이 10 px(다른 행 5~7 px). E 창 제목 `(Windows)  *UPDATE AVAILABLE*  :` 주변 간격도 넓음 | 초안(공백 1개) 유지 |
| B-5 | 가려지거나 잘린 라벨의 표기 | E s2 `Filt`, `Area sub`, `elect ...`, `D (checked)`, `D (unchecked)`(Positions 대화상자에 가림); E s1 `Demo 6 --> FS8 [unchecked]`(목록 맨 아래 행 절반); F s1~s4 `Coordinate T`(패널 폭에서 잘림, 'r' 일부), `CRS Handling`('g' 일부), `Canvas & Legend`('d' 일부), `Code Editor`(맨 아래 행 절반); F s8 `Scale (:157344704)`; E s4~s6 In-line 축 라벨 `200`은 Attribute Set 3D 창 위쪽 테두리에 절반 가려져 추가하지 않음(s7은 완전히 보여 초안에 있음) | 합성 `...`만 제거하고 보이는 글자 기준으로 유지. 마지막 글자가 일부만 보이는 라벨은 step 간 표기를 통일 |
| B-6 | `Attribute Set 3D (icon)` 이름 | 매뉴얼은 "the A icon"(step 3)과 "Attribute set 3D window with the icon"(step 20) 두 가지로 부름 | 창 이름을 따라 `Attribute Set 3D (icon)`로 추가(9장). `A (icon)`로 바꾸거나 병기하려면 일괄 치환 |
| B-7 | G s5 `aspect_north` | `_` 글리프가 현재-레이어 밑줄(y=187)과 겹쳐 눈으로 구분 불가; 간격 폭(6 px, 밑줄 6~9 / 공백 4~5)과 출력 파일명으로 판정 | `aspect_north`로 정정. 확신도 높음이나 픽셀 근거임을 명시 |
| B-8 | F s4 `Canvas & Legend` | s4 초안 `Canvas & Legen`이 더 축자적일 수 있음('d' 절반) | s1~s3과 통일하여 `Canvas & Legend` |
| B-9 | F s2 `new CRS` 추가 | 표 행 Name 셀 텍스트가 Name 필드 값(`Name (new CRS)`)과 같은 문자열 | 표 항목 규칙에 따라 추가 |
| B-10 | F s0 `oceans (checked)` 삭제 | 체크 상태 정보가 사라짐(다른 step은 `oceans`만) | 중복 규칙 적용; 상태를 남기려면 `oceans`를 `oceans (checked)`로 바꾸는 편이 일관됨 |
| B-11 | QGIS 대화상자 `Help` 버튼 | 메뉴 `Help`와 문자열이 같아 별도 항목으로 추가하지 않음 | 중복 규칙 |
| B-12 | E s2 data_state "Demo 1 --> MFS4 is checked" | 두 번째 행이 체크되어 있고 s3의 결과가 Demo 1 --> MFS4이므로 사실이지만 이름은 가려짐 | 가림 사실을 data_state에 명시(규칙 2) |
| B-13 | 상태 표시줄 `Rotation 0.0 °` 공백 | `°` 앞 공백(5 px)은 화면 원문이나 초안은 step마다 `0.0°`/`0.0 °`가 섞임 | 모두 `0.0 °`로 통일(표본 오독 집계에서는 "공백만 다른" 항목으로 별도 표기) |
