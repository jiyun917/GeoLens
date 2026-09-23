# Study 3 GT 변경 목록 — 외부 검수 (2026-09-23)

검수 범위: `opendtect__horizon_2dviewer__01` step 0–5, `qgis__rule_classification__01` step 0–9, `qgis__reclassify_raster__01` step 0–8 (25장). OpendTect step 6·7·8은 재캡처 대기로 제외(초안 그대로 둠).

방법: 원본 JPEG(1920×1032 / 1922×1041)을 PIL로 3–16배 확대 크롭해 `crops/` 아래에 저장하고 Read로 확인. 근거 열의 파일명은 모두 `crops/` 아래 파일이다(`comp_*.png`는 여러 크롭을 한 장에 모은 합성본, 라벨 빨간 글씨). 변경은 `proposed/<scenario>.json`의 `visual_state_gt`(visible_elements, data_state)에만 적용했고, 규칙 3 필드와 `capture_instructions`는 손대지 않았다.

판정 기준(규칙 1):
- 삭제/수정: 화면에 없는 문자열, 철자·숫자·괄호·구두점이 화면과 다른 항목, 화면에 체크박스가 없는데 붙은 `(checked)` 류 상태 표기, 같은 요소를 가리키는 중복.
- 추가: 화면에 있는데 목록에 없는 텍스트 라벨(툴바 라벨, 축 눈금, 툴박스 항목, 버튼 글자).
- 잘린 항목은 잘린 채 둠. 두 라벨이 겹쳐 뒷자리를 읽을 수 없는 축 라벨은 s4 초안이 쓴 겹침 표기 `20021203-2-03_00...21203-2-02_0010`로 통일.
- QGIS 화면의 소수점/천단위 구분 글리프(`0.093473` vs `0,093473`, `0.0 °` vs `0,0 °` 등)는 글꼴 문제로 마침표/쉼표를 화면에서 구분할 수 없어 **초안 표기 그대로 두고 보류 목록(H1)** 으로 넘겼다(오독으로 세지 않음).

---

## opendtect__horizon_2dviewer__01 (변경 38건: 수정 9, 삭제 20, 추가 8, data_state 1)

### step 0 — 변경 없음
47개 항목 전부 화면 확인. 근거: `opendtect__horizon_2dviewer__01__s0__top.png`(제목·메뉴·SEG-Y·Cross-line 0·Step 0·OD Seismic 1), `comp_o_s0.png`(트리 전 항목, Scene 1 체크박스 없음, 2D Line/2D Horizon 자식 없음, `[free mem] 98.9/127.8 GB`), `…s0__axes_top.png`(400·600·Cross-line·800·1000·1200·200·In-line), `…s0__scene_full.png`(Time·500·1000·1500·N·E·Z).

### step 1 — 4건 (표본 스텝)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| Cross-line: (0) | → `Cross-line (0)` | 툴바 원문 `Cross-line 0`(콜론 없음). `…s1__top.png` | 1 |
| Step: (0) | → `Step (0)` | 툴바 원문 `Step 0`. `…s1__top.png` | 1 |
| Scene 1 (checked) | → `Scene 1` | Scene 1 행에는 체크박스가 없음. `comp_o_s1.png` 트리 | 1 |
| SEC | → `SEG-Y` | 화면에 `SEC` 없음. 툴바 라벨 `SEG-Y`(`…s1__top.png`)와 대화상자 왼쪽 SEG-Y 아이콘(`comp_o_s1.png`)을 오독한 것. 초안에 툴바 `SEG-Y`가 빠져 있어 대체 | 1 |

확인 완료: 대화상자 제목 `Select 2D Lines`, `Filter`, 10개 라인명(`19981104-1-04_0037` … `20021203-2-03_0038`, 모두 unchecked), `On OK (Display projection lines only)`, `OK`, `Cancel`(`comp_o_s1.png`); 트리 항목 (checked) 18개; 축 라벨; `[free mem] 98.9/127.8 GB`.

### step 2 — 2건
| 항목 | 변경 | 근거 | 규칙 |
|---|---|---|---|
| SEG-Y | 추가 | 툴바 라벨. `…s2__top.png` | 1 |
| 200 | 추가 | In-line 축 눈금 `200`, 2D 라인명 라벨과 겹치지만 판독 가능. `…s2__axes_top.png`, `…s3__scene200.png`(같은 위치) | 1 |

확인 완료: 트리 `2D Line > 19981104-1-04_0037 > Seismic`(`comp_o_s2.png`), `-8.7372`/`8.7372`, 축 라벨, `Time`·500·1000·1500(`comp_o_s2.png`), `[free mem] 98.9/127.8 GB`.

### step 3 — 25건 (수정 3, 삭제 19, 추가 2, data_state 1)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| Line: 19981104-1-04_0037, Inl/Crl: 5750, SP: 551 | → `Line: 19981104-1-04_0037, TrcNr: 3798, SP: 991` | 상태 표시줄 원문은 `TrcNr`이며 `SP: 991`. 2D Viewer 창 아래쪽에 가려 **아랫반쪽만 보임**; TrcNr 끝자리 8/6 판독 불확실 → 보류 H6. `…s3__status_line.png`, `…s3__status_tr.png`, `comp_o_s3_status.png` | 1 |
| [free mem] 50.5/127.6 GB | → `[free mem] 98.9/127.8 GB` | `…s3__status_r.png`, `comp_o_s3_status.png`(윗부분 가려졌으나 숫자 판독 가능) | 1 |
| 20021203-2-03_0008 | → `20021203-2-03_00...21203-2-02_0010` | 2D viewer 상·하 축의 두 라인명 라벨이 겹쳐 `_00` 뒤 두 자리가 판독 불가. `…s3__plot_top.png`, `…s3__plot_bottom.png` | 1 |
| 20021203-2-02_0010 | 삭제 | 위 겹침 표기에 포함(앞 `200`이 겹침 구간) | 1 |
| Scene 1 (checked) | 삭제 | Scene 1 행에 체크박스 없음(`Scene 1`은 유지). `comp_o_s3.png` | 1 |
| FaultStickSet (unchecked) | 삭제 | 2D viewer 트리의 FaultStickSet에는 체크박스가 없음(`FaultStickSet` 유지 = viewer 트리, `FaultStickSet (checked)` 유지 = 메인 트리). `comp_o_s3.png` viewer_tree | 1 |
| PointSet (unchecked) | 삭제 | 위와 같음 | 1 |
| In-line, Z-slice, Volume, Random Line, 2D Line, Seismic, 3D Horizon, Fault, FaultSet, Geobody, Well, Polygon, Prestack Events | 삭제(13건) | 같은 트리 항목의 `(checked)` 표기와 중복 → 하나만 남김(상태 정보가 있는 쪽 유지). 화면에 두 번째 요소가 있는 `Cross-line`(축 라벨), `19981104-1-04_0037`(3D scene 라인 라벨), `2D Horizon`·`FaultStickSet`·`PointSet`(viewer 트리, 체크박스 없음)은 plain도 유지 | 1(중복) |
| Wiggle, VD | 삭제(2건) | `Wiggle (unchecked)`, `VD (checked)`와 중복. `comp_o_s3.png` | 1(중복) |
| SEG-Y | 추가 | 툴바 라벨. `…s3__top.png` | 1 |
| 200 | 추가 | In-line 축 눈금. `comp_o_s3.png` scene200 | 1 |
| data_state | 문장 끝에 "(the Line/TrcNr/SP text is partly hidden behind the viewer window; only its lower half is visible)" 추가 | 화면 사실 보강 | 2 |

확인 완료: `2D Viewer - Line: 19981104-1-04_0037`, `Tree items`, `Line: 19981104-1-04_0037`, `Time (ms)`, `Trace number`, 0/500/1000/1500/2000, `207/1130`, `(626508, 6076813, 1036.6)`, `Value = -0.6270068`(`…s3__viewer_head.png`, `…s3__plot_*.png`, `…s3__status_l.png`).

### step 4 — 3건 (표본 스텝)
| 항목 | 변경 | 근거 | 규칙 |
|---|---|---|---|
| ? | 추가 | Horizon Tracking Settings 창의 Help 버튼 글자(매뉴얼 그림 OCR "Close ? Help"). step 5 초안에는 있음. `…s4__settings.png` | 1 |
| ▷ | 추가 | 같은 창의 버튼 글리프, step 5 초안과 통일. `…s4__settings.png` | 1 |
| 200 | 추가 | In-line 축 눈금. `…s4__scene200.png` | 1 |

확인 완료(오독 0): `Horizon Tracking Settings - <New 2D Horizon 1>`, Mode/Event/Correlation/Properties, `Section Auto-track`(선택), `Manual Draw`, `Snap to Event`, `Method (Adjacent Parent)`, `If tracking fails`, `Extrapolate`, `Stop`(선택), `Close`(`…s4__settings.png`); `4-1-04_0037`(창에 가려 잘린 플롯 제목, 잘린 채 유지, `…s4__plot_title.png`); 메인 트리 `<New 2D Horizon 1>`(`…s4__tree.png`); 축·상태줄(`…s4__plot.png`, `…s4__status.png`).

### step 5 — 4건
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| ltStickSet | → `ultStickSet` | Settings 창 오른쪽 경계 밖으로 `u`까지 보임. `…s5__viewer_tree.png`, `…s5__trunc.png` | 1 |
| 20021203-2-03_0002 | → `20021203-2-03_00...21203-2-02_0010` | step 3과 같은 겹침. `…s5__plot_top.png`, `…s5__plot_bottom.png` | 1 |
| 20021203-2-02_0010 | 삭제 | 겹침 표기에 포함 | 1 |
| SEG-Y | 추가 | 툴바 라벨. `…s5__top.png` | 1 |

확인 완료: `> An`(잘린 Annotations, 유지), `ntSet`(유지), Settings 창 전 항목, viewer 트리 `<New 2D Horizon 1>`, `Time (ms)`, 상태줄. 초안에 없는 `Geobody…Annotations`·메인 scene `Time`은 Settings 창에 가려져 있어 추가하지 않음(맞음).

### step 6·7·8 — 검수 제외, 초안 그대로

---

## qgis__rule_classification__01 (변경 22건: 수정 20, 삭제 1, data_state 1)

공통 확인: 창 제목은 10장 모두 `*Untitled Project — QGIS`(em dash, `comp_qgis_titles.png`); 상태 표시줄 값(`comp_qgis_status.png`): s0 `-34,1685°, 20,7394°` / `1:117758`, s1–s8 `-33,8677°, 19,9954°` / `1:143205`, s9 `-33,8826°, 20,468°` / `1:143205`, 전부 `100%`, `0,0 °`(글리프 보류 H1), `Render` 체크, `EPSG:4326`.

### step 0 — 2건
| 항목 | 변경 | 근거 | 규칙 |
|---|---|---|---|
| EPSG (EPSG:4326) | → `EPSG:4326` | 상태줄 위젯 글자는 `EPSG:4326` 하나뿐(별도 `EPSG` 라벨 없음). 다른 스텝 표기와 통일. `comp_qgis_status.png` | 1 |
| landuse | 삭제 | `landuse [checked]`와 같은 Layers 항목(중복). `qgis__rule_classification__01__s0__layers.png` | 1(중복) |

### step 1 — 변경 없음
84개 항목 확인: `Layer Properties - landuse — Symbology`, `Categorized`, `Value (landuse)`, `Symbol`, `Color ramp (Random colors)`, 표 헤더 Symbol/Value/Legend, 11개 범주 + `all other values`(체크), `Classify`/`Delete All`/`Delete Unused`/`Advanced`, 왼쪽 탭 20개, `Layer Rendering`, `Style`/OK/Cancel/Apply/Help (`comp_q_s1_table.png`, `comp_q_tabs_editrule.png`, `comp_q_bottoms.png`). 탭 목록 맨 아래 반쯤 잘린 행(`QGIS Server`로 보임)은 추가하지 않음 → 보류 H8.

### step 2 — 11건
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| 'landuse' = 'cemetery' 외 10건 (conservation, farmland, forest, grass, industrial, orchard, reservoir, residential, village_green, vineyard) | → `"landuse" = '…'` | Rule 열의 필드명은 큰따옴표. `comp_q_s2_table.png`, `comp_q_misc_8x.png`(8배) | 1 |

확인 완료: `Rule-based`, 헤더 `Label/Rule/Min. Scale/Max. Scale/Count/Duplicate Count`(마지막 t가 오른쪽 경계에 걸쳐 잘림, 유지 → H9), `ELSE`(이탤릭), `Refine Selected Rules`, `Symbol Levels...`(화면은 `Symbol Levels···`).

### step 3 — 변경 없음
빈 규칙 표(헤더만), 버튼·탭·상태줄 전부 확인(`comp_q_s3_s8_tables.png`, `comp_q_bottoms.png`).

### step 4 — 2건 (표본 스텝)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| Scale range [checked] | → `Scale range [unchecked]` | Edit Rule의 Scale range 체크박스는 비어 있음(Symbol만 체크). `comp_q_tabs_editrule.png` | 1 |
| data_state | "Scale range (Minimum…" → "Scale range (unchecked; Minimum…" | 위와 같음 | 2 |

확인 완료: `Edit Rule`, `Label`, `Filter [selected]`, `Else [unselected]`, `Catch-all for other features`, `Description`, `Minimum (exclusive) (1:100000)`, `Maximum (inclusive) (1:1000)`, `Test`, `Fill`, `Simple Fill`, `Symbol [checked]`, 뒤 표의 `(no filter)` 행, OK/Cancel/Help.

### step 5 — 변경 없음
`Swellendam ...`, `"name" = 'Swellendam'` 확인(`comp_q_rows_8x.png`).

### step 6 — 2건
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| *Untitled Project - QGIS | → `*Untitled Project — QGIS` | 제목은 em dash. `comp_qgis_titles.png` | 1 |
| EPSG (4326) | → `EPSG:4326` | 상태줄 원문. `comp_qgis_status.png` | 1 |

확인 완료: `Other residen...`, `"landuse" = 'residential' ...`(줄임표 앞 공백 있음).

### step 7 — 2건
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| Swellendam | → `Swellendam ...` | Label 열은 잘려서 ` ...`가 붙어 표시됨. `comp_q_rows_8x.png` | 1 |
| "landuse" = 'residential'... | → `"landuse" = 'residential' ...` | 줄임표 앞에 공백(다른 스텝과 동일). `comp_q_rows_8x.png` | 1 |

확인 완료: `Big non resid...`, `"landuse" <> 'residential...`(이쪽은 공백 없이 단어 중간에서 잘림).

### step 8 — 2건 (표본 스텝)
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| *Untitled Project - QGIS | → `*Untitled Project — QGIS` | `comp_qgis_titles.png` | 1 |
| Swellendam [checked] | → `Swellendam ... [checked]` | 잘린 라벨 원문. `comp_q_rows_8x.png` | 1 |

확인 완료: `Small non re...`, `ELSE`, 나머지 3행, `landuse [checked]`(Layers 패널), 상태줄.

### step 9 — 1건
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| Coordinate (-33,8626°, 20,468°) | → `Coordinate (-33,8826°, 20,468°)` | 16배 확대에서 `8826`. 소수점 글리프는 초안 표기(쉼표) 유지(H1). `comp_q_misc_8x.png`, `comp_qgis_status.png` | 1 |

확인 완료: Layers 범례 `Swellendam city / Other residential / Big non residential areas / Small non residential areas`(`…s9__layers.png`).

---

## qgis__reclassify_raster__01 (변경 7건: 수정 2, 추가 4, data_state 1)

공통 확인: 제목 9장 모두 `*Untitled Project — QGIS`; 상태줄 좌표 s0 `1052474, 6201432`, s1 `1052400, 6225383`, s2 `1051135, 6217871`, s3 `1052028, 6213259`, s4 `1052846, 6225458`, s5 `1051730, 6198011`, s6 `1052176, 6208127`, s7 `1051400, 6212151`, s8 `1050765, 6197613`; Scale s0–s6 `1:281131`, s7–s8 `1:300266`; `EPSG:32733` (`comp_qgis_status.png`). Layers 패널 s0–s5 동일: `aspect / Band 1 (Gray) / 360 / 0,093473 / srtm_41_19 / Band 1 (Gray) / 1,548 / 0`(`comp_r_layers.png`; 구분 글리프는 H1).

### step 0 — 1건
| 항목 | 변경 | 근거 | 규칙 |
|---|---|---|---|
| Aspect | 추가 | 툴박스 검색 결과 `Raster terrain analysis > Aspect`, `GDAL > Raster analysis > Aspect`. vision은 읽었으나 초안 적용 시 레이어명 `aspect`와 대소문자 무시 중복 처리된 것으로 보임. `comp_r_toolbox.png` | 1 |

### step 1 — 변경 없음
대화상자 전 항목 확인(`comp_r_dialog_s1_s2.png`, `comp_r_bottoms.png`): `Raster layer (aspect [EPSG:32733])`, `Band number (Band 1 (Gray))`, `Reclassification table (Fixed table (0x3))`, `Advanced Parameters`, `Reclassified raster ([Save to temporary file])`, `Open output file after running algorithm (checked)`, `...`, `0%`, `Cancel`(비활성), `Advanced`, `Run as Batch Process...`, `Run`, `Close`, `Help`, 오른쪽 설명문.

### step 2 — 2건
| 항목 | 변경 | 근거 | 규칙 |
|---|---|---|---|
| ... | 추가 | `…` 버튼 3개(Raster layer / Reclassification table / Reclassified raster). step 1 초안에는 있고 2·4·5에는 없음. `comp_r_dialog_s1_s2.png` | 1 |
| data_state | 끝에 "(화면상 확인 불가, 세션 이력 기준)" 추가 | 화면이 step 1과 동일해 사용자 동작을 확인할 수 없음 | 2 |

### step 3 — 변경 없음 (표본 스텝, 오독 0)
`Reclassification table` 패널, `Minimum/Maximum/Value`, `Add Row`, `Remove Row(s)`, `Remove All`, `OK`, `Cancel`, 행 없음(`comp_r_dialog_s3_s4.png`).

### step 4 — 1건
| ... | 추가 | `comp_r_dialog_s3_s4.png` | 1 |

확인 완료: `Fixed table (5x3)`, `[Save to temporary file]`, `Open output file after running algorithm [checked]`.

### step 5 — 1건
| ... | 추가 | `comp_r_dialog_s5.png` | 1 |

확인 완료: `C:/GeoLensData/reclassified.tif`(화면 글리프는 `reclassified,tif`로 보임 → H1), 나머지 필드·버튼.

### step 6 — 1건
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| *Untitled Project - QGIS | → `*Untitled Project — QGIS` | `comp_qgis_titles.png` | 1 |

확인 완료: Layers `reclassified (checked)` `Band 1 (Gray)` `4`/`1`, `aspect`, `srtm_41_19`, `1,548`, `0`(`…s6__layers_tall.png`, `…s6__layers_low.png`); 툴박스 `Recently used` 등.

### step 7 — 변경 없음 (표본 스텝, 오독 0)
Layer Styling 패널 전 항목 확인(`…s7__styling.png`): `reclassified`, `Paletted/Unique values`, `Band`/`Band 1 (Gray)`, `Color ramp`/`Random colors`, `Value/Color/Label`(빈 표), `Classify`, `Delete All`, `...`, `Layer Rendering`, `Blending mode`/`Normal`, `Brightness`/`Saturation`/`Contrast` 0, `Gamma` `1,00`(H1), `Invert colors`, `Grayscale`/`Off`, `Colorize`, `Hue`, `Strength`/`100%`, `Reset`, `Resampling`, `Zoomed in`/`Nearest Neighbour`, `Live update`, `Apply`, 탭 `Layer Styling`/`Processing Toolbox`.

### step 8 — 1건
| 항목 | 변경 전 → 후 | 근거 | 규칙 |
|---|---|---|---|
| Rotation 0.0° | → `Rotation 0.0 °` | 값과 ° 사이에 공백(`0,0 °`). `comp_qgis_status.png` | 1 |

확인 완료: Value/Color/Label 1–4, Layers 범례 1–4(`…s8__styling.png`, `…s8__layers_tall.png`).

---

## capture_instructions.screen_state 와 실제 화면의 차이 (규칙 2 — 기록만, 수정 안 함)

| 시나리오 / step | capture_instructions | 실제 화면 |
|---|---|---|
| O s1 | 목록 `Well correlation-Line, STG ...` | 목록은 `19981104-1-04_0037` … `20021203-2-03_0038`(F3 Demo 2023에 Well correlation-Line 없음) |
| O s2 | `2D Line > Well correlation-Line > Seis`; "Selected Well correlation-Line" | `2D Line > 19981104-1-04_0037 > Seismic` |
| O s3 | `'2D Viewer - Line: Well correlation-Line'`, 트리 `(Seis, 2D Horizon empty ...)`; "Right-clicked Seis" | `2D Viewer - Line: 19981104-1-04_0037`; viewer 트리 `Wiggle / VD / 2D Horizon / FaultStickSet / PointSet`; 속성명 `Seismic` |
| O s4 | "defaults: … Event Max, Correlation 80%"; "`<New 2D Horizon>` in the 2D viewer tree" | Mode 탭만 보여 Event/Correlation 값은 화면상 확인 불가; viewer 트리는 Settings 창에 가려짐(`<New 2D Horizon 1>`은 메인 트리에 보임) |
| O s5 | `<New 2D Horizon>` | 화면 표기는 `<New 2D Horizon 1>` |
| Q s8 | "map behind still shows the old rendering" | 대화상자 뒤 지도 캔버스에 폴리곤이 보이지 않아 화면상 확인 불가 |
| R s1 | "Raster layer NOT yet set to aspect"; must_not_show `Raster layer = aspect` | 이미 `aspect [EPSG:32733]`로 자동 채워짐 |
| R s2 | "Chose aspect as the Raster layer" | 사용자 동작 없음; step 1과 동일 화면(상태줄 좌표만 다름) |
| R s3 | "'Fixed table' dialog open" | 별도 대화상자가 아니라 같은 대화상자 안의 `Reclassification table` 패널(뒤로가기 화살표 있음) |
| R s5 | `…/raster_analysis/reclassified.tif` | `C:/GeoLensData/reclassified.tif` |

## 검토했으나 바꾸지 않은 항목
- O s4 `4-1-04_0037`, O s5 `> An`·`ntSet`, Q s5–s8 `Other residen...`·`Big non resid...`·`Small non re...`, Q s2 `Duplicate Count`: 잘린 채 화면 원문과 일치.
- O s3/s5 `20021203-2-03_00...21203-2-02_0010` 표기 자체(s4 초안 방식)는 유지; 관례는 H7.
- `(checked)` / `[checked]` 표기 혼용, `Coordinate (…)` 식의 "라벨 (값)" 묶음 표기: 화면 사실이 아니라 열거 관례이므로 손대지 않음(H13).
- QGIS 소수점 글리프 전부(H1).
