# GT 변경 목록 — Study 2 외부 검수 (2026-09-21)

대상: `scenarios/opendtect__fault_sticks__01.json`(9 스텝), `scenarios/opendtect__horizon_autotrack__01.json`(7 스텝). 수정안은 `proposed/` 아래 같은 파일명(키 순서·들여쓰기 2·`ensure_ascii=False` 유지, 원본 대비 `visible_elements`·`data_state` 만 변경, `current_dialog`·`current_action`·`_gt_provenance`·규칙 3 필드는 바이트 단위로 동일함을 스크립트로 확인).

근거 위치 표기: `(x0, y0, x1, y1)` 은 1922×1041 스크린샷 좌표(fs step_2 만 1920×1032). 확대 크롭은 `crops/<scenario>/…` 에 저장.

## 0. 전 스텝 공통으로 적용한 표기 규칙 (규칙 1 "괄호가 다르면 화면 원문")
초안(vision 열거)은 같은 화면 요소를 스텝마다 다르게 표기했다(fs step 0–2·7–8 은 `In-line 110`, step 3–6 은 `In-line (110)`; hz step 3 은 `Compare window (ms) (-40)` + `40`, step 5 는 `Compare window (ms) (-40, 40)`). 화면에는 괄호가 없으므로 다음과 같이 화면 원문으로 통일했다.

| 유형 | 초안 표기 | 화면 원문 → 적용 | 근거 |
|---|---|---|---|
| 위치 툴바 라벨+값 | `In-line (130)`, `Step (10)` | `In-line 130`, `Step 10` (라벨과 스핀박스 값이 나란히 표시됨; 초안 fs step 0–2 와 같은 형식) | `*_sheetA.png` "pos toolbar L" |
| 하단 편집 툴바 콤보 | `Copy Selection to (Fault)` | `Copy Selection to` 와 `Fault` 는 별개의 콤보 박스 → 두 항목 (`Fault` 는 트리 항목과 중복이므로 하나만 남김) | fs `*_sheetA.png` "edit toolbar L" |
| 다이얼로그 필드 라벨(값) | `Event type (Peak)`, `Method (Seed Trace)`, `Nr Traces (5)`, `Compare window (ms) (-40, 40)` 등 | 라벨과 값 위젯을 별개 항목으로: `Event type`, `Peak`, …, `Compare window (ms)`, `-40`, `40` | hz `*_dialog.png`, `*_dialog2.png` |
| 체크 상태 주석 | `In-line [checked]`, `WVA [checked]`, `VD [unchecked]` | 주석 제거(`In-line`, `WVA`, `VD`); 체크 상태는 필요 시 `data_state` 에 문장으로 기록 | fs step_0/5 `sheetB`, hz step_2 `dialog2` |
| 버튼 텍스트 띄어쓰기 | `Select...` | `Select ...` (점 앞에 공백; 하단 툴바·Output selection 다이얼로그 모두) | fs `step_2_dialogsheet.png` 8배 크롭, `*_sheetA.png` "edit toolbar R" |
| 텍스트 없는 아이콘 | `▷` (동영상 도움말 버튼) | 삭제 — 텍스트가 없는 아이콘이고 매뉴얼이 이름을 부르지 않음. `?` 는 글리프가 문자이므로 유지 | hz `step_1_dlg_buttons5x.png` |
| 매뉴얼이 이름을 부르는 아이콘 | (없음) | `Auto-Track (icon)`, `Retrack-All (icon)` 추가 — hz step 4–6 에서만(활성화된 상태). 비활성(회색) 상태인 step 1–3 은 보류 목록 H2 | hz `step_4_dialog.png` 아이콘 열 1번(초록 자동추적)·4번(초록 순환화살표) |

중복 제거(규칙 1): 표기 통일 후 같은 문자열이 된 항목(트리 `In-line`/`Cross-line` 과 장면 축 라벨 `In-line`/`Cross-line`, 툴바 `Fault` 와 트리 `Fault`)은 하나만 남겼다.

## 1. opendtect__fault_sticks__01

### step 0 — `screenshots/opendtect__fault_sticks__01/step_0.jpg` (52 → 51 항목)
| 항목 | 변경 전 → 후 | 근거 (어디를 봤나) | 규칙 |
|---|---|---|---|
| 트리 항목 19건 | `Scene 1 [checked]`, `In-line [checked]`, `110 [checked]`, `4 Dip steered medi... [checked]`, `Cross-line [checked]`, `Z-slice [checked]`, `Volume [checked]`, `Random Line [checked]`, `2D Line [checked]`, `3D Horizon [checked]`, `2D Horizon [checked]`, `Fault [checked]`, `FaultSet [checked]`, `FaultStickSet [checked]`, `Geobody [checked]`, `Well [checked]`, `PointSet [checked]`, `Polygon [checked]`, `Prestack Events [checked]` → 주석 제거 | 트리 패널 (48,125,305,690) `step_0_sheetB.png`. 참고: `Scene 1` 에는 체크박스가 없음(초안의 `[checked]` 는 잘못된 상태 주석) | 1 |
| 추가 | `1500` | Time 축 눈금, 단면 왼쪽 가장자리에 일부 가려졌으나 판독 가능 (약 (460,780)) `timeaxis_0_5.png` 왼쪽, `step_0_scene1x.jpg` | 1 |
| 중복 제거 | `In-line`, `Cross-line` (트리와 장면 축 라벨) | — | 1 |
| `capture_instructions.screen_state` 차이(수정 안 함) | "In-line view" 라고 했으나 실제는 원근 뷰: 기즈모에 N·E·Z 세 축이 모두 보이고(1780,880,1900,1015) 서베이 박스 전체가 보임. 표시 영역은 단면 일부로 축소되어 있음(`step_0_scene1x.jpg`) | 2 |

### step 1 — `step_1.jpg` (54 → 56)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 추가 | `SEG-Y` | 아이콘 툴바 (0,56,270,90) `step_1_sheetA.png` — 다른 스텝과 동일하게 표시됨, 초안 누락 | 1 |
| 추가 | `1500` | Time 축 눈금 `timeaxis_1_4.png` | 1 |
| `data_state` | `Select...` → `Select ...`; 트리 색상 견본(초록)·툴바 색상 견본(파랑)·undo/redo 활성·상단 툴바 톱니 아이콘 추가를 명시 | `step_1_sheetA.png` edit toolbar R (색상 견본 파랑, undo/redo 초록), pos toolbar R (톱니), `step_1_sheetB.png` (`<New FaultStickSet 1>` 굵게, 초록 견본) | 2 |

### step 2 — `step_2.jpg` (1920×1032; 61 → 62)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 추가 | `1500` | Time 축 눈금 `timeaxis_1_4.png` 두 번째 | 1 |
| 검증만 | `Output selection`, `Output FaultStickSet`, `Replace in tree`, `OK`, `Cancel`, `?`, `Select ...` 모두 다이얼로그 (685,445,1240,585) 에서 확인 `step_2_dialogsheet.png`; `Picking` 상태표시줄 (900,1009,1400,1032) `step_2_bottom_fixed.png` | | 1 |

### step 3 — `step_3.jpg` (55 → 56)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 표기 | `Select...` → `Select ...` | edit toolbar R (450,985,910,1018) `step_3_sheetA.png` | 1 |
| 표기 | `In-line (110)` → `In-line 110`; `Step (1)` → `Step 1` | pos toolbar L (0,88,440,122) | 1 |
| 표기 | `Copy Selection to (Fault)` → `Copy Selection to` (+ `Fault` 는 트리 항목과 중복, 하나 유지) | edit toolbar L | 1 |
| 추가 | `1500` | `timeaxis_1_4.png` | 1 |
| `data_state` | "Only at Sections not yet enabled" 에 "화면상 확인 불가, 세션 이력 기준" 덧붙임; 트리 견본 초록·undo/redo 회색 명시 | `step_3_sheetA.png`, `step_3_sheetB.png` | 2 |

### step 4 — `step_4.jpg` (54 → 56)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 추가 | `SEG-Y` | 아이콘 툴바 `step_4_sheetA.png` (초안 누락) | 1 |
| 표기 | `Select...` → `Select ...`; `In-line (110)` → `In-line 110`; `Step (1)` → `Step 1`; `Copy Selection to (Fault)` → `Copy Selection to` | `step_4_sheetA.png` | 1 |
| 추가 | `1500` | `timeaxis_1_4.png`, `step_4_scene1x.jpg` | 1 |
| `data_state` | "Visually identical to step 3" → 실제 차이 기록: 하단 편집 툴바 맨 왼쪽 아이콘 버튼이 강조(토글 on) 상태이고 undo 아이콘이 활성(초록)으로 바뀜; 왼쪽 메인 툴바는 step 0·3 과 동일. Only at Sections 상태에 "화면상 확인 불가, 세션 이력 기준" 문구 | `steps1-8_bottomleft_icons8x.png` (step_3 vs step_4), `step_4_sheetA.png` edit toolbar R, `lefttoolbar_0_3_4_5_7.png` | 2 |
| `capture_instructions.screen_state` 차이(수정 안 함) | "Position mode active, Edit Sticks icon toggled on" — 왼쪽 메인 툴바는 step 0·3 과 픽셀 단위로 동일(맨 위 초록 화살표 아이콘)해서 모드 전환을 화면에서 확인할 수 없음. 토글된 것은 하단 편집 툴바 맨 왼쪽 아이콘뿐이며 그 이름은 확인 불가(보류 H1) | 2 |

### step 5 — `step_5.jpg` (57 → 56)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 트리 항목 19건 | `In-line [checked]` … `Prestack Events [checked]`, `FaultStickSet_01 [checked]` → 주석 제거 | `step_5_sheetB.png` | 1 |
| 표기 | `Select...` → `Select ...`; `In-line (110)` → `In-line 110`; `Step (1)` → `Step 1`; `Copy Selection to (Fault)` → `Copy Selection to` | `step_5_sheetA.png` | 1 |
| 추가 | `1500` | `timeaxis_0_5.png` 오른쪽 | 1 |
| 중복 제거 | `Fault`, `In-line`, `Cross-line` | — | 1 |
| 검증만 | `data_state` "green lines with yellow seed nodes" — 단면 위 초록 스틱·노란 노드 확인 `step_5_scene1x.jpg` | | 2 |

### step 6 — `step_6.jpg` (52 → 52)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 표기 | `Select...` → `Select ...`; `In-line (130)` → `In-line 130`; `Step (10)` → `Step 10`; `Copy Selection to (Fault)` → `Copy Selection to` | `step_6_sheetA.png` | 1 |
| 검증만 | 장면 라벨 `500`, `600`, `Time`, `1000`, `1500` 확인 `step_6_scene.png`, `step_6_scene1x.jpg`; 장면 상단 가장자리에 잘린 라벨 조각이 있으나 판독 불가라 추가하지 않음 `misc_topedge_lefttoolbar.png` | | 1 |
| `data_state` | "sticks exist on several inlines" 은 화면에서 확인 불가(인라인 130 의 스틱만 표시됨) → "화면상 확인 불가, 세션 이력 기준" 덧붙임; 트리 `In-line > 130 > 4 Dip steered medi...` 와 축 라벨 명시 | `step_6_sheetB.png`, `step_6_scene1x.jpg` | 2 |

### step 7 — `step_7.jpg` (51 → 51)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 표기 | `Select...` → `Select ...` | `step_7_sheetA.png` edit toolbar R | 1 |
| 검증만 | `Z 1500`, `Step 4`, `0.61389`, `0.96727`, `130/559`, `(612287, 6074487, 1066.9)`, `Value = -1109`, `In-line: 130` (상태표시줄 L1·L2), 트리 `1500`, `9-1 Similarity on F...`, 기즈모 `N`·`E`(Z 는 화면 안쪽 방향으로 글자가 보이지 않음 `step_7_gizmo6x.png`), 장면에 문자 라벨 없음 `step_7_scene.png` | | 1 |
| `data_state` | 트리 라벨이 `9-1 Similarity on F...` 로 잘려 있음을 명시(전체 이름은 "화면상 확인 불가, 세션 이력 기준"); 기즈모 N·E; 상태표시줄 값; 왼쪽 메인 툴바 맨 위 아이콘이 손 모양 커서(step 0–6 은 화살표) 임을 기록 | `step_7_sheetA.png`, `step_7_sheetB.png`, `lefttoolbar_0_3_4_5_7.png` | 2 |
| `capture_instructions.screen_state` 차이(수정 안 함) | "view from the top (View North)" — 정확히는 북쪽이 위인 기울어진 상면 뷰로, 인라인 130 단면이 아래쪽에 원근으로 보임 `step_7_scene1x.jpg`. 스틱은 슬라이스·인라인 교선을 따라 짧은 보라색 표시로 보임(모두 비선택) | 2 |

### step 8 — `step_8.jpg` (51 → 52)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 추가 | `SEG-Y` | 아이콘 툴바 `step_8_sheetA.png` (초안 누락) | 1 |
| 표기 | `Select...` → `Select ...` | `step_8_sheetA.png` | 1 |
| 오독 수정 | `Tr` → `Ti` | 단면에 가려진 Time 축 라벨 (595,740,665,795): 보이는 글자는 `T`, `i` 와 세 번째 글자의 왼쪽 획뿐 `step_8_misc.png` 10배 크롭. 화면 원문(보이는 부분)으로 고침 | 1 |
| 검증만 | 트리 `Fault_01A`(파랑 견본), `<right-click>`(컬러바 견본), `FaultStickSet_01`(보라 견본) `step_8_sheetB.png`; 기즈모 `Z`·`N`·`E`; 장면 `500` `step_8_misc.png`; 상태표시줄은 `[free mem]` 외 비어 있음 | | 1 |
| `capture_instructions` 차이(수정 안 함) | "Copy Selection toolbar closed/idle" — 툴바는 여전히 표시됨(유휴 상태, 이름 필드 비어 있음) | 2 |

## 2. opendtect__horizon_autotrack__01

### step 0 — `screenshots/opendtect__horizon_autotrack__01/step_0.jpg` (47 → 46)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 삭제(오독) | `N` | 오리엔테이션 기즈모 (1700,860,1922,1041) 에 `E`(왼쪽 초록 화살표)·`Z`(아래 파랑 화살표) 만 있음; N 축은 화면 안쪽 방향이라 글자 없음 `gizmos_wide.png` 1번째, `step_0_sheetB.png`. 화면 다른 곳에도 단독 `N` 없음 | 1 |
| 표기 | `In-line (130)` → `In-line 130`; `Step (10)` → `Step 10` | `step_0_sheetA.png` | 1 |
| 검증만 | `4 Dip steered me...`(굵은 글꼴·선택 상태라 step 1–6 의 `medi...` 보다 짧게 잘림) `step_0_treeitem6x.png`; 상태표시줄 `425/825`, `(618734, 6082045, 404.1)`, `Value = 435`, `Random Line 1`; 장면 `600`, `In-line 400`(겹쳐 표시) `all_scene_labels.png` | | 1 |

### step 1 — `step_1.jpg` (58 → 60)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 추가 | `?` | 다이얼로그 하단 도움말 버튼 (1100,690,1290,720) `step_1_dlg_buttons5x.png` — 같은 창의 step 2–6 초안에는 열거되어 있어 일관성 위해 추가 | 1 |
| 표기 | `In-line (130)` → `In-line 130`; `Step (10)` → `Step 10`; `Method (Seed Trace)` → `Method`, `Seed Trace` | `step_1_dialog.png` | 1 |
| `data_state` | "(no dip-steering licence)" 는 화면에서 확인 불가 → 문구 덧붙임; `Snap to Event` 체크박스가 비활성(회색)임을 명시 | `step_1_dialog.png` | 2 |

### step 2 — `step_2.jpg` (67 → 73)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 표기 | `In-line (130)` → `In-line 130`; `Step (10)` → `Step 10` | `step_2_sheetA.png` | 1 |
| 표기 | `Event type (Peak)` → `Event type`, `Peak`; `Threshold type (Relative difference)` → `Threshold type`, `Relative difference`; `Allowed difference (%) (25)` → `Allowed difference (%)`, `25`; `Search window (ms) (-8)` → `Search window (ms)`, `-8`; `Search window (ms) (8)` → `8`; `Data Display window (ms) (-16)` → `Data Display window (ms)`, `-16`; `Data Display window (ms) (16)` → `16`; `Nr Traces (5)` → `Nr Traces`, `5` | Event 탭 (685,415,1100,660) `step_2_dialog2.png` | 1 |
| 표기 | `WVA [checked]` → `WVA`; `VD [unchecked]` → `VD`; `Symmetric [unchecked]` → `Symmetric` | `step_2_dialog.png` 오른쪽 | 1 |
| `data_state` | VD 미체크·Symmetric 두 개 미체크 명시; "Correlation tab not yet edited" 에 확인 불가 문구 | `step_2_dialog2.png` | 2 |
| `capture_instructions.screen_state` 차이(수정 안 함) | "'Picked on: 4 Dip steered median filter' visible" — 실제 `Picked on` 필드는 비어 있는 회색 필드(아직 시드 없음) `step_2_dialog2.png` | 2 |

### step 3 — `step_3.jpg` (70 → 72)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 삭제(오독) | `F` | 화면에 단독 `F` 없음. 기즈모의 `E` 한 글자를 vision 이 `E` 와 `F` 로 두 번 읽은 것으로 판단 `gizmos_wide.png` 2번째; 다이얼로그·트리·상태표시줄에도 없음 `step_3_scene1x.jpg` | 1 |
| 삭제(아이콘) | `▷` | 텍스트 없는 동영상 버튼 아이콘 (1100,690,1290,720); 매뉴얼에 이름 없음 | 1 |
| 표기 | `In-line (130)` → `In-line 130`; `Step (10)` → `Step 10`; `Compare window (ms) (-40)` → `Compare window (ms)`, `-40`; `Correlation threshold (%) (60.0)` → `Correlation threshold (%)`, `60.0`; `Data Display window (ms) (-48)` → `Data Display window (ms)`, `-48`; `Nr Traces (5)` → `Nr Traces`, `5` | Correlation 탭 `step_3_dialog2.png` | 1 |
| 검증만 | `Use Correlation`, `Yes`(선택), `No`, `Snap to Event`(체크), `WVA`(체크), `VD`, `Symmetric`, `40`, `48`; 장면 `600`, `In-line 400` 는 다이얼로그에 가리지 않음 `step_3_scene1x.jpg` | | 1 |

### step 4 — `step_4.jpg` (67 → 72)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 삭제(아이콘) | `▷` | 위와 같음 (1115,100,1760,465 창 하단) | 1 |
| 표기 | `In-line (130)` → `In-line 130`; `Step (10)` → `Step 10`; `Compare window (ms) (-40)`, `Correlation threshold (%) (60.0)`, `Data Display window (ms) (-48)`, `Nr Traces (5)` → 라벨/값 분리 | `step_4_dialog.png` | 1 |
| 추가 | `Auto-Track (icon)`, `Retrack-All (icon)` | 다이얼로그 왼쪽 아이콘 열 1번(초록 자동추적)·4번(초록 순환화살표)이 step 3 의 회색에서 활성으로 바뀜 `step_4_dialog.png` vs `step_3_dialog.png`; 매뉴얼 §1.4.2a 14·17 이 "Auto-Track icon / Retrack-All icon in the Horizon Tracking Setup window" 로 이름을 부름 | 1 |
| `data_state` | "Status bar shows coordinates and Value" → 상태표시줄은 `[free mem]` 외 비어 있음 (0,1017,1400,1041) `step_4_sheetA.png`; "on a Peak reflector" 는 Event 탭 설정에 근거한 것이라 확인 불가 문구; 트리 자식 항목의 경고 아이콘 유지, 창 제목이 비활성(회색), 파형 패널의 초록 시드 표시, 메인 툴바의 추적 아이콘 6개(텍스트 없음) 명시 | `step_4_sheetA.png`, `step_4_sheetB.png`, `step_4_dlgtitle4x.png`, `trackicons_4_5_6.png` | 2 |
| `capture_instructions` 차이(수정 안 함) | "cross cursor" — 스크린샷에 마우스 커서가 찍히지 않아 확인 불가. 시드 표시는 흰 사각형 `seedmarkers_4_5_6.png` | 2 |

### step 5 — `step_5.jpg` (68 → 75)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 삭제(오독) | `N` | 기즈모 `E`·`Z` 만 표시 `step_5_gizmo6x.png`; 상태표시줄 문자열에도 단독 `N` 없음 `step_5_sheetA.png` | 1 |
| 표기 | `In-line (130)` → `In-line 130`; `Step (10)` → `Step 10`; `Compare window (ms) (-40, 40)` → `Compare window (ms)`, `-40`, `40`; `Correlation threshold (%) (60.0)` → 분리; `Data Display window (ms) (-48, 48)` → `Data Display window (ms)`, `-48`, `48`; `Nr Traces (5)` → 분리 | `step_5_dialog.png` | 1 |
| 추가 | `Auto-Track (icon)`, `Retrack-All (icon)` | step 4 와 동일(활성 상태) `step_5_dialog.png` | 1 |
| `data_state` | "Patch not locked" 에 확인 불가 문구; 상태표시줄 값(`425/429`, `(608829, 6081768, 1817.8)`, `Value = -3612`, `Random Line 1`)과 메인 툴바 저장 아이콘 활성 명시 | `step_5_sheetA.png`, `trackicons_4_5_6.png` | 2 |

### step 6 — `step_6.jpg` (66 → 72)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 표기 | step 3·4 와 같은 라벨/값 분리 6건 | `step_6_dialog.png` | 1 |
| 추가 | `Auto-Track (icon)`, `Retrack-All (icon)` | `step_6_dialog.png` | 1 |
| `data_state` | "Visually identical to step 5 except the status bar is empty" → 단면 위 시드 표시가 흰색(step 5)에서 파란색으로 바뀐 점을 추가 기록(잠금과의 관계는 화면에서 확인 불가); 잠금 상태에 "화면상 확인 불가, 세션 이력 기준" | `seedmarkers_4_5_6.png`, `step_6_sheetA.png` | 2 |

## 3. 변경하지 않고 검증만 한 것
- `current_dialog`·`current_action` 16 스텝 전부: 화면 사실과 어긋나는 문장이 없어 그대로 둠.
- 제목표시줄 `OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : F3 Demo 2023 - [Scene 1]`, 메뉴 8개, `Tree scene 1`/`Elements`/`Color`, `[free mem] …` 값(101.5/101.6/101.6/101.6/101.3/100.1/100.8/100.8/100.8; 100.6×5/100.5×2)은 16장 모두 초안과 일치.
- 좌표·수치는 스텝별 화면 원문 그대로 유지(복사 없음).

## 4. 집계
| | fault_sticks | horizon_autotrack |
|---|---|---|
| 오독 삭제/수정 | 1 (`Tr`→`Ti`) | 3 (`N`×2, `F`) |
| 아이콘 기호 삭제 | 0 | 2 (`▷`×2) |
| 괄호·띄어쓰기 표기 수정 | 19 | 39 |
| `[checked]` 주석 제거 | 38 | 3 |
| 항목 추가 | 9 (`SEG-Y`×3, `1500`×6) | 7 (`?`, 아이콘 2×3) |
| 중복 제거 | 8 | 0 |
| `data_state` 수정 | 5 (step 1·3·4·6·7) | 5 (step 1·2·4·5·6) |
| `capture_instructions` 차이 기록(수정 안 함) | 4 (step 0·4·7·8) | 2 (step 2·4) |
