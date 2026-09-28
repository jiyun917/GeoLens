# GT_change_list.md — 변경 목록 (외부 GT 검수, 2026-09-28)

대상: `scenarios/*.json` → `proposed/*.json`. 변경한 GT 필드는 `visual_state_gt.visible_elements`와 `visual_state_gt.data_state`뿐이다(`current_dialog`·`current_action`은 화면과 일치해 변경 없음). 키 순서·indent 2·ensure_ascii=False 유지, 규칙 3 필드 불변(스크립트로 검증).
규칙 번호는 RULES.md 절 번호. "삭제/수정/추가"는 visible_elements 항목 기준. 근거 크롭은 `crops/<scenario>/s<N>_*.png`.

## 공통 결정
- **QGIS 소수점은 마침표**(`0.0 °`, `-6.8°, 176.6°`). 근거는 sample_check.md 판정 근거 1. RULES.md 예시(`0,0 °`)와 달라 GT_hold_list.md B-1에 확인 요청.
- **텍스트 없는 아이콘 버튼**은 매뉴얼이 이름을 부르는 두 개만 추가(규칙 1): OpendTect 툴바의 Attribute Set 3D 아이콘(매뉴얼 1.5.2a step 3 "click on the A icon", step 20 "open the Attribute set 3D window with the icon") → `Attribute Set 3D (icon)`; QGIS Custom CRS 대화상자의 초록 + 버튼(매뉴얼 §6.1.4 step 4 "Click on the Add new CRS button") → `Add new CRS (icon)`.
- QGIS 대화상자의 `Help` 버튼은 메뉴 `Help`와 같은 문자열이라 중복 규칙상 추가하지 않음(이미 목록에 있음).
- 앱이 `...`로 자른 항목은 그대로(`Van der Gri...`). vision이 붙인 합성 `...`(화면에 없음)은 제거하고 보이는 글자만 남김.

---

## opendtect__spectral_decomp__01 (검수 526항목: 삭제 0 · 수정 9 · 추가 15)

| step | 구분 | 변경 | 근거 | 규칙 |
|---|---|---|---|---|
| 0 | 추가 | `SEG-Y` | 툴바 첫 줄 오른쪽 끝 버튼에 텍스트 라벨 "SEG-Y" 표시(s0_tb1_left.png). s6·s8 초안에는 있음 | 1 |
| 0 | 추가 | `Attribute Set 3D (icon)` | 툴바 두 번째 아이콘(A 모양). 매뉴얼 명명 아이콘 | 1 |
| 1 | 수정 | `...Demo_2023\Surfaces\Demo_0_--_FS4.hor` → `...Demo_2023\Surfaces\Demo_0_--__FS4.hor` | 밑줄 픽셀 런 7·7·14 px → `--` 뒤 밑줄 2개(s1_path10x.png) | 1 |
| 1 | 추가 | `SEG-Y`, `Attribute Set 3D (icon)` | 위와 같음 | 1 |
| 1 | data_state | 경로 힌트 `…Demo_0_--_FS4.hor` → `…Demo_0_--__FS4.hor` | 위와 같음 | 2 |
| 2 | 수정 | `...emo_2023\Surfaces\Demo_1_..._MFS4.hor` → `...emo_2023\Surfaces\Demo_1_--__MFS4.hor` | 화면은 `--` + 밑줄 2개(s2_path10x.png; 런 7·7·15 px) | 1 |
| 2 | 수정 | `Scene 1 (checked)` → `Scene 1` | 트리의 Scene 1에는 체크박스가 없음(s2_tree.png) | 1 |
| 2 | 수정 | `Filt...` → `Filt`, `Area sub...` → `Area sub`, `elect...` → `elect ...` | Positions 대화상자에 가려진 라벨. 화면에 `...`는 없고(합성) 보이는 조각만 남김; `Select ...` 버튼은 원래 점이 있어 `elect ...` | 1(잘린 항목) |
| 2 | 추가 | `SEG-Y`, `Attribute Set 3D (icon)` | | 1 |
| 2 | data_state | 경로 힌트 밑줄 2개로 정정; "Demo 1 --> MFS4 is checked"에 이름이 가려져 `D`만 보인다는 사실과 가려진 라벨 조각(`Filt`, `Area sub`, `elect ...`) 명시 | 화면 사실 | 2 |
| 3 | 추가 | `SEG-Y`, `Attribute Set 3D (icon)` | | 1 |
| 3 | data_state | "'Select RGB Attributes' window … passed with OK" 뒤에 `화면상 확인 불가, 세션 이력 기준` 추가 | 해당 창은 미캡처 | 2 |
| 4 | 수정 | `OpendTect v7.0.9 (Windows) …` → `OpendTect V7.0.9 (Windows) …` | 제목 표시줄은 대문자 V(s4_title.png; 다른 8장과 동일) | 1 |
| 4 | 수정 | `SEC-Y` → `SEG-Y` | 툴바 라벨(s4_segy8x.png) | 1 |
| 4 | 추가 | `Attribute Set 3D (icon)` | | 1 |
| 5 | 추가 | `SEG-Y`, `Attribute Set 3D (icon)` | 창이 y≥240에 있어 툴바 첫 줄은 보임 | 1 |
| 6 | 추가 | `Attribute Set 3D (icon)` | (`SEG-Y`는 초안에 있음) | 1 |
| 7 | 수정 | `Demo 1 -> MFS4` → `Demo 1 --> MFS4` | 트리 항목은 `-->`(s7_tree.png; s3~s6·s8 초안과 동일) | 1 |
| 7 | 추가 | `SEG-Y`, `Attribute Set 3D (icon)` | | 1 |
| 8 | 추가 | `Attribute Set 3D (icon)` | | 1 |
| 8 | data_state | "set saved on close" 뒤에 `화면상 확인 불가, 세션 이력 기준` 추가 | 저장 여부·세트 이름은 화면에 없음 | 2 |

확인만 하고 변경 없음: 모든 step의 메뉴(Survey…Help), `Cross-line (0)`, `Step (0)`, `-8.7372`, `8.7372`, `OD Seismic 1`, 트리 항목, 축 라벨(Cross-line 400~1200, In-line 200~600, Time 500~1500), `[free mem]` 값(92.2/94.2/93.4/93.4/92.3/93.9/92.9/92.1/92.1), Select Horizons 목록 7행과 `Area subselection (100/300-750/1250 (463 samples))`, Positions의 `Range`/`200`/`650`/`500`/`1000`/`Step (1)`, Attribute Set 3D의 `Attribute set (<not saved>)`, `<All>`, `Similarity`/`Spectral Decomposition`, `Input Data (4 Dip steered median filter)`, `Time gate (ms)` -28/28 → -8/24, `Extension (Cross)`, `Stepout (inl:1, crl:1)`, `Steering (None)`, `Output statistic (Average)`, `Transform type` FFT/CWT, `Display Time/Frequency panel`, `Output frequency (Hz)` 24.0/44.0/64.0, `Step (4.0)`, `Attribute Name (SD_…)`, 목록 `SD_24Hz[-8,24ms]`/`SD_44Hz[-8,24ms]`/`SD_64Hz[-8,24ms]`, `Add as new`, `Save on Close`, `Close`.

## qgis__custom_projection__01 (검수 464항목: 삭제 1 · 수정 12 · 추가 18)

| step | 구분 | 변경 | 근거 | 규칙 |
|---|---|---|---|---|
| 0 | 수정 | `Coordinate (-6,8°, 176,6°)` → `Coordinate (-6.8°, 176.6°)` | 소수점 글리프 = 마침표(공통 결정; s0_nn_coord.png, crops/decimal_mark_composite.png) | 1 |
| 0 | 수정 | `Rotation (0,0 °)` → `Rotation (0.0 °)` | 같음 | 1 |
| 0 | 삭제 | `oceans (checked)` | `oceans`와 같은 레이어 항목의 중복(다른 step은 `oceans`만 있음) | 1(중복) |
| 1 | 수정 | `You can define … for specifying a` → `… for specifying a CRS.` | 안내문 둘째 줄 `CRS.`도 화면에 보임(s1_dlg_head.png) | 1 |
| 1 | 추가 | `Add new CRS (icon)` | 표 오른쪽 초록 + 버튼(s1_plusminus.png); 매뉴얼 명명 | 1 |
| 2 | 수정 | `Coordinate T...` → `Coordinate T` | 왼쪽 트리 라벨이 패널 폭에서 잘림; 화면에 `...` 없음. s1·s4 표기와 통일 | 1(잘린 항목) |
| 2 | 추가 | `new CRS` | 표 첫 행의 Name 셀(s2_dlg_table.png) — 표 항목 | 1 |
| 2 | 추가 | `Add new CRS (icon)` | | 1 |
| 3 | 수정 | `Coordinate T...` → `Coordinate T` | 위와 같음 | 1 |
| 3 | 추가 | `Add new CRS (icon)` | (`+`, `-`는 그대로 둠 — GT_hold_list.md B-3) | 1 |
| 4 | 수정 | `Van der Gri... PROJCRS["unknown",BASEGEOGCRS["unknown","DATUM"["unknown","ELLIPSOID"["unknown",…` → 두 항목 `Van der Gri...` / `PROJCRS["unknown",BASEGEOGCRS["unknown",DATUM["unknown",ELLIPSOID["unknown",6371000,0,LENGTHUNIT["metre",1,ID["...` | 표의 두 셀은 별개 항목; `DATUM`·`ELLIPSOID` 둘레 따옴표는 화면에 없음(s4_table_cell6x*.png) | 1 |
| 4 | 수정 | `Parameters (PARAMETER["False easting",0, … ID["EPSG",8807]], … )` 한 항목 → 보이는 WKT 13줄(중복 2줄 제거): `PARAMETER["False easting",0,` `LENGTHUNIT["metre",1],` `ID["EPSG",8806]],` `PARAMETER["False northing",0,` `ID["EPSG",8807]]],` `CS[Cartesian,2],` `AXIS["(E)",east,` `ORDER[1],` `LENGTHUNIT["metre",1,` `ID["EPSG",9001]]],` `AXIS["(N)",north,` `ORDER[2],` `ID["EPSG",9001]]]]` | 규칙 1 "WKT 텍스트의 보이는 줄"; 초안의 `ID["EPSG",8807]],`는 화면 `]]],`(괄호 하나 누락)(s4_params_top8x.png); `Parameters` 라벨 항목은 별도로 이미 있음 | 1 |
| 4 | 수정 | 안내문 첫 줄 → 두 줄 전체 | s1과 같음 | 1 |
| 4 | 수정 | `Canvas & Legen` → `Canvas & Legend` | 같은 픽셀을 s1~s3은 `Legend`로 읽음; 'd'가 반쯤 보여 통일(B-5) | 1 |
| 4 | 추가 | `Add new CRS (icon)` | | 1 |
| 5 | 수정 | `Rotation 0.0°` → `Rotation 0.0 °` | ° 앞 공백 5 px(s5_status_r8x.png) | 1 |
| 6 | — | 변경 없음 | Predefined 목록 12행·Authority ID·속성 글머리표 5줄·`Hide deprecated CRSs`·`OK/Cancel/Apply` 모두 일치 | |
| 7 | — | 변경 없음 | `Filter (Van der Grinten)`, `Projected`/`van der Grinten (I)`/`Sphere_Van_der_Grinten_I`/`ESRI:53029`/`World_Van_der_Grinten_I`/`ESRI:54029`/`User-defined`/`Van der Grinten I`/`USER:100000`, WKT 2줄 모두 일치 | |
| 8 | 수정 | `Coordinate (82014073, -11191302)` → `Coordinate (32014073, -11191302)` | 첫 자리는 3(s8_coord_nn.png) | 1 |
| 8 | 수정 | `Scale (1:57344704)` → `Scale (:157344704)` | Scale 필드에 보이는 문자열은 `:157344704`(앞의 `1`은 필드에서 잘림, s8_scale_nn.png). 잘린 채 기록 | 1(잘린 항목) |
| 8 | data_state | "Scale 1:157344704" → 좌표 `32014073, -11191302` 명시, Scale 필드 표시 `:157344704`(선행 `1` 잘림) 설명 | 화면 사실 | 2 |

## qgis__aspect_north__01 (검수 508항목: 삭제 0 · 수정 11 · 추가 3)

| step | 구분 | 변경 | 근거 | 규칙 |
|---|---|---|---|---|
| 0 | — | 변경 없음 | 툴박스 그룹 31개(`Database`·`Mesh`는 메뉴 항목과 같은 문자열로 이미 포함), 레이어 `aspect`/`Band 1 (Gray)`/`360`/`0.093473`, 상태 표시줄 값 일치 | |
| 1 | 수정 | `0.0°` → `0.0 °` | Rotation 필드 `0.0 °`(공백 5 px; s1_status_r.png) | 1 |
| 1 | 추가 | `Cancel` | 진행 막대 오른쪽의 비활성 `Cancel` 버튼(s1_dlg_bottom.png; s4 초안에는 있음) | 1 |
| 2 | 수정 | `*Untitled Project - QGIS` → `*Untitled Project — QGIS` | 제목 대시 13 px = em dash(s0·s1 초안·current_dialog와 동일) | 1 |
| 2 | 수정 | `Rotation 0.0°` → `Rotation 0.0 °` | | 1 |
| 2 | 추가 | `Cancel` | | 1 |
| 3 | 수정 | `*Untitled Project - QGIS` → `*Untitled Project — QGIS`; `0.0°` → `0.0 °` | | 1 |
| 3 | 추가 | `Cancel` | | 1 |
| 3 | data_state | "'1 input selected' (aspect)" → `(aspect — 화면상 확인 불가, 세션 이력 기준)` | 선택된 레이어 이름은 필드에 표시되지 않음 | 2 |
| 4 | 수정 | `*Untitled Project - QGIS` → `— QGIS`; `Rotation 0.0°` → `Rotation 0.0 °` | | 1 |
| 5 | 수정 | `*Untitled Project - QGIS` → `— QGIS` | | 1 |
| 5 | 수정 | `aspect north` → `aspect_north` | 간격 6 px = 밑줄 폭(6~9 px), 공백은 4~5 px; `_` 글리프가 현재-레이어 밑줄과 겹침(sample_check.md 근거 4). 출력 파일 `aspect_north.tif`에서 만들어진 레이어 이름 | 1 |
| 5 | 수정 | `Rotation (0,0°)` → `Rotation (0.0 °)` | 마침표 + 공백 | 1 |
| 5 | 수정 | `Coordinate (1051441, 6206391)` → `Coordinate (1051440, 6206391)` | 첫 수 끝자리 `1440`(픽셀 맵; s5_status_r8x.png) | 1 |

확인만 하고 변경 없음: 대화상자 제목 `Raster Analysis - Raster Calculator`(하이픈), `Input layers (0 inputs selected)`/`1 input selected`, `Expression ("aspect@1" <= 90 OR "aspect@1" >= 270)`(따옴표 포함), `Output extent [optional] (Not set)`, `Output cell size (leave empty to set automatically) [optional] (Not set)`, `Output CRS [optional]`, `Advanced Parameters`, `Calculated ([Save to temporary file])` → `(C:/GeoLensData/raster_analysis/aspect_north.tif)`, `Open output file after running algorithm`, `This algorithm performs algebraic operations using raster layers.`, `0%`, `Advanced`, `Run as Batch Process...`, `Run`, `Close`, Raster analysis 알고리즘 33개, 상태 표시줄 좌표(1051678/1049851/1051837/1050805), `EPSG:32733`.

---

## capture_instructions.screen_state와 실제 화면의 차이 (규칙 2 — 기록만, 수정하지 않음)

| 시나리오/step | capture_instructions | 실제 화면 |
|---|---|---|
| E s0, s3 (must_not_show) | "Select Input Horizon(s) dialog" | 해당 대화상자의 7.0.9 제목은 `Select Horizons` (의미는 동일) |
| E s1 | "'Select Input Horizon(s)' dialog open" | 제목 `Select Horizons`; 나머지(목록·Area subselection·Select…·OK/Cancel·미선택) 일치 |
| E s2 | "'Position' (Specify Position) dialog" | 제목 `Positions`, 부제 `Specify Positions`; 범위 값·OK 미클릭 일치 |
| E s3 | "four attribute layers (three with R/G/B colour flags)" | 하위 4행: `<right-click>`×3(색 플래그 회백·파랑·초록) + `Z values`(빨강). 개수는 일치 |
| E s4 | "EMPTY attribute list, default attribute type; Input Data empty" | 목록 비어 있음·기본 종류 Similarity는 일치하나 Input Data는 `4 Dip steered median filter`로 자동 채워짐 |
| E s8 | "set saved, e.g. as Spectral Decomposition" | 저장/이름은 화면에서 확인 불가 |
| F s4 | "Parameters contains the PROJCRS WKT (METHOD Van Der Grinten)" | Parameters 상자는 끝부분으로 스크롤되어 `PARAMETER["False easting"…` 이후만 보이고 METHOD 줄은 안 보임; PROJCRS는 표 행에만 보임 |
| F s7 | "under User Defined Coordinate Systems" | 그룹 라벨은 `User-defined` |
| G s1 | "Layers list (aspect@1 …), Operators, Expression EMPTY, Reference layer(s) empty, output = temporary file" | 3.44 대화상자에는 Layers/Operators 패널이 없음(ε 빌더 안); 라벨은 `Input layers` `0 inputs selected`; Expression 비어 있음·임시 파일 출력은 일치 |
| G s2 | "Expression = … ('Expression is valid'); Input layers ('0 inputs selected'; manual: Reference layer(s))" | `Expression is valid` 문구 없음; 식은 따옴표 포함 `"aspect@1" <= 90 OR "aspect@1" >= 270` |
| G s3 | "Reference layer(s) shows '1 input selected'" | 라벨은 `Input layers` |
| G s4, s5 | 일치 | Calculated 경로·레이어 `aspect_north`(0/1)·대화상자 닫힘 |
| F s0~s3, s5, s6, s8; E s5~s7; G s0 | 일치 | |
