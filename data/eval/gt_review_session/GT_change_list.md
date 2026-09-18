# GT 변경 목록 — gt_review_session (2026-09-18)

- 적용 규칙: RULES.md §1 (1-a 텍스트 없는 아이콘 버튼 / 1-b 서술형 / 1-c 화면에 없음), §4 (QGIS step 3). §3은 보류(GT_hold_list.md H7) — 변경 없음.
- 반영 위치: `proposed/<scenario>.json` (원본 `scenarios/` 불변). 네 파일 모두 원본을 바이트 단위로 왕복(round-trip) 확인한 뒤 GT 필드만 바꿨으므로 diff에는 아래 변경만 나타난다 (CRLF·키 순서·indent 2·ensure_ascii=False 유지).
- 변경 건수 **19**: 규칙 1 = 14 (삭제 2, 라벨 원문 변경 11, 아이콘 표기 변경 1), 규칙 4 = 5.
- 1-b "라벨 원문" 적용 관례: 화면의 라벨 문자열을 그대로 쓰고, 원 항목이 **값을 주장한 경우에만** 화면에 실제 표시된 값을 GT 기존 vision 관례 `라벨 (값)` 형식으로 덧붙였다(예: `Segments field (default 5)` → `Segments (5)`). 값을 주장하지 않은 항목은 라벨만 남겼다(예: `Miter limit field` → `Miter limit`).
- 좌표(x, y)는 스크린샷 픽셀 기준 대략치.

## A. 규칙 1 변경 — B 25건 중 14건

| # | 시나리오 / step | 필드 | 변경 전 | 변경 후 | 규칙 | 근거 (스크린샷 · 위치) |
|---|---|---|---|---|---|---|
| 1 | opendtect__3d_visualization__01 / step 1 | visible_elements | `OR Select Attribute dialog listing seismic cubes` | (삭제) | 1-c | `screenshots/opendtect__3d_visualization__01/step_1.jpg` — 화면의 유일한 팝업은 Tree scene 1의 In-line 노드 우클릭 컨텍스트 메뉴(Add Default Data / Add and Select Data ... / Add at Well Location ... / Add Color Blended; x≈165–355, y≈205–295). 'Select' / 'Select Attribute' 다이얼로그 창은 화면 어디에도 없다. |
| 2 | opendtect__attribute_computation__01 / step 2 | visible_elements | `Input Data = 4 Dip steered median filter` | (삭제) | 1-c | `screenshots/opendtect__attribute_computation__01/step_2.jpg` — Attribute Set 3D 창 Input Data 드롭다운(x≈885–1185, y≈373) 값은 `Seismic_data`. '4 Dip steered median filter' 문자열은 화면에 없다. 필드 자체는 기존 vision 항목 `Input Data (Seismic_data)`로 이미 등재. |
| 3 | 〃 / step 2 | visible_elements | `Time gate populated: -28 to +28` | `Time gate (ms) (-28, 28)` | 1-b | 같은 창 라벨 `Time gate (ms)`(y≈405) 오른쪽 두 입력칸 `-28`, `28` (화면에 '+' 기호 없음). |
| 4 | 〃 / step 4 | visible_elements | `Attribute set Name field = 'my first attribute set'` | `Name (my first attribute set)` | 1-b | `screenshots/opendtect__attribute_computation__01/step_4.jpg` — 'Save Attribute as' 다이얼로그(x≈760–1165, y≈345–680) 라벨 `Name`, 입력칸 `my first attribute set`(y≈595). ※ 동일 문자열이 vision 항목으로 이미 존재 → 중복 정리는 보류(H9). |
| 5 | 〃 / step 4 | visible_elements | `OK button` | `OK` | 1-b | 같은 다이얼로그 하단 버튼 `OK`(녹색 체크 아이콘 + 텍스트, x≈990, y≈637). |
| 6 | 〃 / step 5 | visible_elements | `OpendTect Main Window` | `OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]` | 1-b | `screenshots/opendtect__attribute_computation__01/step_5.jpg` — 메인 창 제목표시줄(최상단, x≈30–440). ※ 중복(H9). |
| 7 | 〃 / step 7 | visible_elements | `'Energy [-28,+28]' layer checkbox is checked (currently rendered on the inline)` | `Energy [-28,+28] (checked)` | 1-b | `screenshots/opendtect__attribute_computation__01/step_7.jpg` — Tree scene 1 › In-line › 250 아래 `Energy [-28,+28]`(굵게 강조, 체크박스 체크; x≈115–235, y≈235). ※ 중복(H9). |
| 8 | opendtect__survey_setup__01 / step 0 | visible_elements | `Survey Data Root tab` | `Survey Data Root ...` | 1-b | `screenshots/opendtect__survey_setup__01/step_0.jpg` — 창 좌상단 버튼 `Survey Data Root ...`(아이콘 + 텍스트, x≈12–152, y≈40)과 오른쪽 경로칸 `C:\Users\user\Downloads\GeoLens_test`. 탭이 아니라 버튼이며 라벨이 있다. |
| 9 | 〃 / step 0 | visible_elements | `Add button` | `New Survey (+)` | 1-a | 같은 스크린샷 좌측 survey 목록 오른편 세로 아이콘열 최상단(x≈939, y≈75): 문서 위 녹색 원 '+' 아이콘, 텍스트 라벨 없음 — `survey_s0_add_button_x3.png`, `survey_s0_context.png`로 확인. 매뉴얼 §1.2.2a p.21 Workflow 원문 "2. Click on the New Survey icon ." → 매뉴얼 이름 `New Survey` + 기호 `+`. (기존 `expected_action_text_pattern`의 `New`, `Survey` 토큰과 충돌 없음.) |
| 10 | 〃 / step 2 | visible_elements | `Survey name field with 'My_F3_Survey' typed` | `Survey name (My_F3_Survey)` | 1-b | `screenshots/opendtect__survey_setup__01/step_2.jpg` — Create New Survey 다이얼로그 라벨 `Survey name`(x≈770, y≈392), 입력칸 `My_F3_Survey`. ※ 중복(H9). |
| 11 | 〃 / step 3 | visible_elements | `OpendTect V7.0.9 application window` | `OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : My_F3_Survey - [Scene 1]` | 1-b | `screenshots/opendtect__survey_setup__01/step_3.jpg` — 제목표시줄(최상단). ※ 중복(H9). |
| 12 | qgis__vector_buffer__01 / step 3 | visible_elements | `Distance field (default 10 or similar)` | `Distance (10,000000)` | 1-b | `screenshots/qgis__vector_buffer__01/step_3.jpg` — Vector Geometry - Buffer 다이얼로그 Parameters 탭 라벨 `Distance`(y≈390), 입력칸 `10,000000`(y≈415; 쉼표 소수점, 3배 확대 확인), 단위 `meters`. |
| 13 | 〃 / step 3 | visible_elements | `Segments field (default 5)` | `Segments (5)` | 1-b | 같은 다이얼로그 라벨 `Segments`(y≈440), 입력칸 `5`(y≈463). ※ 중복(H9). |
| 14 | 〃 / step 3 | visible_elements | `Miter limit field` | `Miter limit` | 1-b | 같은 다이얼로그 라벨 `Miter limit`(y≈582), 입력칸 `2,000000`(y≈605). 원 항목이 값을 주장하지 않아 라벨만. |

## B. 규칙 4 변경 — qgis__vector_buffer__01 / step 3, 5건

화면 사실: `screenshots/qgis__vector_buffer__01/step_3.jpg` — Buffer 다이얼로그가 열리자마자 Input layer 드롭다운(x≈640–885, y≈340)에 `roads_33S [EPSG:32733]`가 **이미 채워져** 있다(프로젝트의 유일한 레이어가 자동 선택됨). 나머지는 기본값: Distance `10,000000` `meters`, Segments `5`, End cap style `Round`, Join style `Round`, Miter limit `2,000000`, ☐ Dissolve result, Buffered `[Create temporary layer]`. 기존 GT의 data_state("No input layer selected yet")와 current_action("about to select roads_33S")은 화면과 불일치 → 규칙 4에 따라 정정.

| # | 필드 | 변경 전 | 변경 후 | 규칙 |
|---|---|---|---|---|
| 15 | visual_state_gt.visible_elements | `Input layer dropdown (default entry or empty)` | `Input layer dropdown (roads_33S [EPSG:32733] already filled)` | 4 (값 명시) |
| 16 | visual_state_gt.data_state | `Buffer dialog just opened. All fields at defaults. No input layer selected yet.` | `Buffer dialog just opened. Input layer already shows roads_33S [EPSG:32733] (auto-filled; no user selection needed). Other fields at defaults: Distance 10,000000 meters, Segments 5, End cap style Round, Join style Round, Miter limit 2,000000, Dissolve result unchecked, Buffered = [Create temporary layer].` | 4 |
| 17 | visual_state_gt.current_action | `user is about to select roads_33S from Input layer dropdown` | `Input layer is already roads_33S [EPSG:32733]; user is about to confirm it and proceed to Distance = 50 (then Dissolve result)` | 4 |
| 18 | expected_action_text_pattern | (아래 코드 블록) | (아래 코드 블록) | 4 |
| 19 | expected_action_keywords | `["Input layer", "roads_33S"]` | `["Input layer", "roads_33S", "Distance", "50"]` | 4 |

변경 전 패턴:
```
(?i)\b(Input layer|roads_33S|select|선택|드롭다운|dropdown)\b
```
변경 후 패턴:
```
(?i)\b(Input layer|roads_33S|Distance|50|Dissolve|select|선택|드롭다운|dropdown)\b
```

근거: 기존 패턴/키워드는 "입력 레이어 선택"만 기대했으나 화면상 이미 선택되어 있다. 매뉴얼 §6.2.6 step 5 (p.214) "Select roads_34S as Input layer, set Distance to 50 and use the default values for the rest of the parameters."에서 이 화면에 남은 동작은 Distance = 50이고, 시나리오 goal이 Dissolve results 체크를 요구하므로 `Distance|50|Dissolve`를 추가했다. 기존 토큰(Input layer, roads_33S, select 등)은 "이미 roads_33S가 선택돼 있음을 확인"하는 응답도 화면과 부합하므로 유지했다. `allowed_alternatives`는 규칙 4가 언급하지 않아 손대지 않았다(기존 항목 "select roads_33S"는 확인 응답과도 부합). keywords의 채점 의미(any-of / all-of)는 파이프라인을 열지 않아 확인하지 못했으므로 keywords 추가분(`Distance`, `50`)은 사용자 확인을 권장한다(H11). signature·workflow·capture_instructions는 규칙대로 미변경.

## C. 규칙 1 판정 — 변경 없음(유지) 5건

| B 항목 | 시나리오 / step | 판정 | 규칙 | 근거 |
|---|---|---|---|---|
| `Edit button` | opendtect__survey_setup__01 / step 0 | 유지(원문 그대로) | 1-a | `screenshots/opendtect__survey_setup__01/step_0.jpg` 아이콘열 두 번째(x≈939, y≈105) 연필 아이콘, 텍스트 없음(`survey_s0_context.png`). '매뉴얼 이름 + 기호' 표기는 매뉴얼 발췌에 이 아이콘의 이름이 없어 적용 불가 → 표기만 보류(H5). |
| `Toolbar` | opendtect__survey_setup__01 / step 3 | 유지 | 1-b | `.../survey_setup__01/step_3.jpg` 메뉴바 아래 아이콘 툴바(y≈60–80). 서술형이며 화면에 'Toolbar' 라벨 없음. |
| `Map Canvas (center) rendering road network` | qgis__vector_buffer__01 / step 0 | 유지 | 1-b | `.../qgis__vector_buffer__01/step_0.jpg` 중앙 지도 영역(x≈300–1920, y≈120–1000)에 녹색 도로망 표시. 'Map Canvas' 라벨 없음. |
| `Map Canvas unchanged from step_0` | qgis__vector_buffer__01 / step 1 | 유지 | 1-b | `.../step_1.jpg` 중앙 지도(Processing Toolbox가 우측에 도킹되어 폭만 줄고 동일 도로망·동일 축척 1:240882). 라벨 없음. |
| `Map Canvas rendering the dissolved buffer as a single polygon covering 50 m around the road network (semi-transparent overlay over the roads)` | qgis__vector_buffer__01 / step 7 | 유지 | 1-b | `.../step_7.jpg` 중앙 지도에 도로망을 따라 연속된 노란 버퍼 폴리곤(갈색 외곽선) 렌더링; Layers 패널 최상단 `roads_buffer_50m_dissolved`. 라벨 없음. (50 m·반투명 여부는 화면에서 검증 불가하나 화면과 모순되지 않음.) |

규칙 1 판정 **보류 6건**(3d s3 `No context menu, no dialog`, attr s0 `Parameter panel (...)`, attr s3 `OK / Save button`, attr s5 `Attribute Set 3D closed`, qgis s3 `End cap style, Join style dropdowns`, qgis s7 `QGIS main window ... both CLOSED`)은 GT_hold_list.md H1–H4, H6, H8 참조.

B 25건 판정 분포: 삭제 2 / 변경 12 / 유지 5 / 보류 6.
