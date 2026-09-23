# Study 3 GT 변경 목록 — 재캡처 검수 (2026-09-23) — opendtect__horizon_2dviewer__01 step 6·7·8

검수 범위: 재캡처된 `screenshots/opendtect__horizon_2dviewer__01/step_6.jpg`(1920×1032), `step_7.jpg`, `step_8.jpg`(1922×1041) 3장. 초안은 `recapture/opendtect__horizon_2dviewer__01_draft_v2.json`의 steps 6–8(`visible_elements`는 `gt_visible_elements_review_s6_s8.md`의 vision 열거 그대로). `proposed/opendtect__horizon_2dviewer__01.json`의 s0–s5는 손대지 않았고 steps 6·7·8의 `visual_state_gt`만 아래대로 바꿨다(적용 스크립트 `recapture/apply_recapture_gt.py`; 실행 후 s0–s5 객체·바이트 동일, 규칙 3 필드·`capture_instructions` 동일, 키 순서·indent 2·ensure_ascii=False·LF·끝 개행 확인).

방법: 원본 JPEG를 PIL로 3–12배 확대한 크롭(`recapture/crops/`, 생성 스크립트 `recapture/crops/crop_recapture.py`)을 Read로 확인. 근거 열의 파일명은 `recapture/crops/opendtect__horizon_2dviewer__01__sN__<name>.png`의 `sN__<name>` 부분이다.

판정 기준은 본 세션 `GT_change_list.md`와 같다. 규칙 1: 화면에 없는 문자열 삭제, 철자·숫자·괄호 정정, 체크박스 없는 항목의 `(checked)` 삭제, 같은 요소의 plain/annotated 중복은 annotated 쪽만 남기되 화면에 두 번째 요소가 있으면 plain도 유지(H10), 겹친 축 라벨은 `20021203-2-03_00...21203-2-02_0010`(H7), 잘린 항목은 잘린 채. 규칙 2: data_state는 화면 사실로 고치고, 화면에서 확인할 수 없는 내용은 지우지 않고 "not verifiable on screen — per session history" 문구를 붙인다.

---

## 변경 건수 합계: 30건 (수정 4, 삭제 18, 추가 5, data_state 3)

| step | 수정 | 삭제 | 추가 | data_state | 계 | 초안 항목 수 → 결과 |
|---|---|---|---|---|---|---|
| 6 | 2 | 1 | 3 | 1 | 7 | 74 → 75 |
| 7 | 2 | 17 (중복 15, 잘못된 상태 표기 1, 겹침 라벨 1) | 1 | 1 | 21 | 93 → 72 |
| 8 | 0 | 0 | 1 | 1 | 2 | 51 → 52 |

---

### step 6 — 7건 (Output selection)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 20021203-2-03_0000 | → `20021203-2-03_00...21203-2-02_0010` | 2D viewer 상·하 축에서 두 교차선 이름이 겹쳐 `_00` 뒤 두 자리 판독 불가(s3·s5와 같은 겹침, H7 표기). `s6__plot_top`, `s6__plot_bottom` | 1 |
| 20021203-2-02_0010 | 삭제 | 위 겹침 표기에 포함(앞 `200`이 겹침 구간) | 1 |
| (s) | → `s)` | 2D viewer 왼쪽 축의 세로 라벨 `Time (ms)`가 Output selection 대화상자에 가려 위쪽 `)`·`s`와 `m`의 획 일부만 보임. 여는 괄호 `(`는 화면에 없음. 잘린 원문대로 `s)`. `s6__plot_ms`, `s6__plot_ms12`(비교: s7의 온전한 라벨 `s7__plot_ms8`) | 1 |
| ? | 추가 | Horizon Tracking Settings 창 Help 버튼 글자(Output selection 대화상자에도 같은 `?` 버튼). s4·s5 proposed와 통일(H11). `s6__settings`, `s6__output_dlg` | 1 |
| ▷ | 추가 | 같은 창의 재생 버튼 글리프, s4·s5와 통일(H11). `s6__settings` | 1 |
| 200 | 추가 | 3D scene In-line 축 눈금 `200`(2D 라인명 라벨과 겹치지만 판독 가능; s0–s5와 같은 처리). `s6__scene200`, `s6__axes_l` | 1 |
| data_state | 재작성 | (a) "opened from the 2D viewer tree"는 화면에서 확인 불가 → "not verifiable on screen — per session history" 문구 추가. (b) Settings 창이 메인 트리의 2D Horizon 아래 행을 가림을 명시. (c) viewer 트리의 `<New 2D Horizon 1>`이 checked·selected임을 명시. (d) `Select...` → 화면 원문 `Select ...`. 나머지 사실(Output 2D Horizon 비어 있음, Replace in tree 체크, OK/Cancel/?, Settings Mode 탭, 녹색 horizon)은 화면과 일치 | 2 |

확인 완료(초안 74개 중 위 3개 외 71개 화면 일치): 제목·메뉴·`SEG-Y`·`Cross-line (0)`·`Step (0)`·`-8.7372`·`8.7372`·`OD Seismic 1`(`s6__top`); 메인 트리 `Tree scene 1`·`Elements`·`Color`·`Scene 1`(체크박스 없음)·`In-line`…`2D Horizon`(그 아래 행은 Settings 창 제목줄에 가림)(`s6__tree_main`); Settings 창 제목·`Mode`/`Event`/`Correlation`/`Properties`·`Section Auto-track`(선택)·`Manual Draw`·`Snap to Event`·`Method (Adjacent Parent)`·`If tracking fails`·`Extrapolate`·`Stop`(선택)·`Close`(`s6__settings`); `2D Viewer - Line: 19981104-1-04_0037`(`s6__viewer_head`); viewer 트리 `Tree items`·`Wiggle`(unchecked)·`VD`(checked)·`2D Horizon`·`<New 2D Horizon 1>`(checked·선택)·`FaultStickSet`·`PointSet`(`s6__viewer_tree`); `Output selection`·`Output 2D Horizon`·`Select ...`·`Replace in tree`(checked)·`OK`·`Cancel`(`s6__output_dlg`); 플롯 `Line: 19981104-1-04_0037`·`0`·`500`·`1000`·`1500`·`2000`·`Trace number`(왼쪽 축의 1000·1500은 대화상자에 가려 오른쪽 축에서 확인)(`s6__plot_*`); 3D scene `400`·`600`·`Cross-line`·`800`·`1000`·`1200`·`19981104-1-04_0037`·`1500`(`s6__axes_l/r`, `s6__scene_bl`); `N`·`E`·`Z`(`s6__nez`); 상태줄 왼쪽 비어 있음, `[free mem] 99.8/127.8 GB`(`s6__status_l/r`).

### step 7 — 21건 (대화상자 닫힘, 2D Viewer 열림)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| VD (unchecked) | → `VD (checked)` | viewer 트리의 VD 체크박스는 체크됨(Wiggle만 unchecked). `s7__viewer_tree` | 1 |
| 20021203-2-03_0008 | → `20021203-2-03_00...21203-2-02_0010` | s6과 같은 겹침(H7). `s7__plot_top`, `s7__plot_bottom` | 1 |
| 20021203-2-02_0010 | 삭제 | 겹침 표기에 포함 | 1 |
| Scene 1 (checked) | 삭제 | Scene 1 행에 체크박스 없음(`Scene 1` plain은 유지; s1 선례). `s7__tree_main` | 1 |
| In-line, Z-slice, Volume, Random Line, 2D Line, Seismic, 3D Horizon, Fault, FaultSet, Geobody, Well, Polygon, Prestack Events | 삭제(13건) | 같은 메인 트리 항목의 `(checked)` 표기와 중복이고 화면에 두 번째 요소가 없음 → annotated 쪽만 유지(s3 선례·H10). `s7__tree_main` | 1(중복) |
| Wiggle, VD | 삭제(2건) | `Wiggle (unchecked)`, `VD (checked)`와 중복. `s7__viewer_tree` | 1(중복) |
| 200 | 추가 | In-line 축 눈금. `s7__scene200` | 1 |
| data_state | 재작성 | "the horizon is saved as" → 화면 사실은 두 트리에 저장 이름 `2D_Horizon`(checked·선택 강조)이 보이는 것이므로 그렇게 서술. "Horizon Tracking Settings closed" → 화면에서는 보이지 않는 것까지만 확인되므로 "no longer visible (closed — not verifiable on screen, per session history)". 2D Viewer 열림·녹색 horizon·상태줄 내용은 화면과 일치 | 2 |

plain을 함께 남긴 항목(화면에 두 번째 요소가 있음): `Cross-line`(3D scene 축 라벨), `19981104-1-04_0037`(3D scene 라인 라벨), `2D Horizon`·`FaultStickSet`·`PointSet`(viewer 트리, 체크박스 없음), `2D_Horizon`(viewer 트리의 두 번째 요소; 이쪽도 체크됨 — 보류 HR1).

확인 완료(초안 93개 중 위 오독 4개·중복 15개 외 74개 화면 일치): 제목·메뉴·툴바(`s7__top`); 메인 트리 `Scene 1`·`In-line (checked)`…`Prestack Events (checked)`·`2D_Horizon (checked)`(선택 강조·굵게)·`Annotations`(체크박스 없음)(`s7__tree_main`); `2D Viewer - Line: 19981104-1-04_0037`·`-8.7372`·`8.7372`·`OD Seismic 1`(`s7__viewer_head`); viewer 트리 `Tree items`·`Elements`·`Color`·`Wiggle (unchecked)`·`2D Horizon`·`2D_Horizon (checked)`(선택)·`FaultStickSet`·`PointSet`(`s7__viewer_tree`); 플롯 `Line: 19981104-1-04_0037`·`1000`·`2000`·`0`·`500`·`1500`·`Time (ms)`·`Trace number`(`s7__plot_*`); 3D scene `400`·`600`·`Cross-line`·`800`·`1000`·`1200`·`19981104-1-04_0037`·`500`·`Time`·`1500`(`s7__axes_l/r`, `s7__scene_labels`, `s7__scene_bl`); `N`·`E`·`Z`(`s7__nez`); 상태줄 `209/894`·`(620602, 6076696, 191.8)`·`Value = 6.0694513`·`Line: 19981104-1-04_0037, TrcNr: 2852, SP: 754`·`[free mem] 99.8/127.8 GB`(`s7__status_l/m/r`).

### step 8 — 2건 (목표 도달)
| 항목 | 변경 | 근거 | 규칙 |
|---|---|---|---|
| 200 | 추가 | In-line 축 눈금. `s8__scene200` | 1 |
| data_state | 재작성 | "2D Viewer closed" → "no longer visible (closed — not verifiable on screen, per session history)". horizon 표시가 흰 pick 사각형임을 확인(`s8__picks`). `2D_Horizon`이 checked·선택 강조임을 명시. 상태줄에 `[free mem]`만 있음을 추가 | 2 |

확인 완료(초안 51개 전부 화면 일치, 오독 0): 제목·메뉴·툴바(`s8__top`); 메인 트리 전 항목(s7과 동일, `2D_Horizon` 선택 강조)(`s8__tree_main`); 3D scene 축 `400`…`1200`·`Cross-line`·`19981104-1-04_0037`·`500`·`Time`·`1000`·`1500`(`s8__axes_l/r`, `s8__scene_labels`, `s8__scene_bl`); horizon = 약 1500 ms 반사면을 따라 흰 pick 사각형(`s8__picks`); `N`·`E`·`Z`(`s8__nez`); 상태줄 왼쪽 비어 있음, `[free mem] 99.8/127.8 GB`(`s8__status_l/r`). 2D Viewer 창·대화상자 없음.

---

## current_dialog / current_action — 변경 없음
- s6 `Output selection`, s7 `2D Viewer - Line: 19981104-1-04_0037`(s3 관례), s8 `OpendTect Main Window / 3D scene`(s0·s2 관례) 모두 화면과 일치.
- current_action(s6 이름 입력 후 OK, s7 viewer 닫기, s8 Goal reached)은 화면 상태와 모순 없음(그대로 둠).

## `capture_instructions.screen_state` 와 화면의 차이 (기록만, 규칙 2 — `capture_instructions`는 고치지 않음)
| step | 지시서 | 화면 |
|---|---|---|
| 6 | "OK/Cancel/Help", "Right-clicked <New 2D Horizon>" | 버튼은 `OK`·`Cancel`·`?`(Help 글자 없음); 항목명은 `<New 2D Horizon 1>`. 그 외(Output 2D Horizon 비어 있음, Replace in tree) 일치 |
| 7 | "saved name (e.g. 2D_Horizon)", viewer 열림 | 일치(`2D_Horizon`, 2D Viewer 열림, 대화상자 없음) |
| 8 | viewer 닫힘, scene에 horizon, 메인 트리에 저장 이름 | 일치 |
