# Study 3 캡처 검증 노트 (2026-09-23)

사용자가 27장(28장 중 `opendtect__horizon_2dviewer__01/step_8` 누락)을 PNG로 캡처(1922×1041 또는 1920×1032). 검증은 메인 세션이 축소본(1100 px)으로 지시서(`CAPTURE_GUIDE.md`)와 대조. PNG 원본은 `originals_png/`에 보존, 벤치용 JPEG(quality 92)는 `data/eval/screenshots/<scenario_id>/step_N.jpg`. 이 노트는 화면 사실만 적고 시나리오·워크플로우 파일은 고치지 않는다(GT 절차의 외부 검토·보류 목록으로 넘긴다).

## C — opendtect__horizon_2dviewer__01 (8/9장; **s6–s8 재캡처 필요**)
- 매뉴얼과 다른 점(데이터): F3 Demo 2023에는 "Well correlation-Line"이 없고 2D 라인 목록이 `19981104-1-04_0037`, `19981104-1-04_0038`, … `20021203-2-03_0038`이다. 사용자는 `19981104-1-04_0037`을 선택했다. 속성 이름은 "Seis"가 아니라 **"Seismic"**. 시나리오 s1 키워드 `Well correlation-Line`·s2 키워드 `Seis`는 이 화면과 어긋난다(보류 목록 대상; 패턴은 `Load default data|OK`, `Display|2D Viewer` 대안으로 통과 가능).
- s0 ✓ 빈 3D scene(데이터 없음), 2D Line 자식 없음, 대화상자 없음.
- s1 ✓ `Select 2D Lines` 대화상자, 목록, On OK = "Display projection lines only"(기본), 아직 선택 없음.
- s2 ✓ 트리 2D Line > 19981104-1-04_0037 > Seismic, scene에 2D 라인 단면 표시, 2D Viewer 없음.
- s3 ✓ `2D Viewer - Line: 19981104-1-04_0037` 창(자체 트리 Wiggle/VD/2D Horizon/FaultStickSet/PointSet, 단면 Time vs Trace number), 2D horizon 없음. 상태 표시줄에 좌표·Value·Line/TrcNr/SP.
- s4 ✓ `Horizon Tracking Settings - <New 2D Horizon 1>`(Mode 탭: Section Auto-track, Method Adjacent Parent, If tracking fails Extrapolate/Stop) + 메인 트리 2D Horizon > <New 2D Horizon 1>; 2D viewer 뒤에 열림; seed 없음.
- s5 ✓ 2D viewer 단면에 녹색 horizon 선(라인 전체), 2D viewer 트리에 <New 2D Horizon 1>, Settings 창 열린 채.
- s6 ✗ `Output selection`(Output 2D Horizon 비어 있음, Replace in tree, OK/Cancel)은 맞으나 **2D Viewer 창이 화면에 없다**(닫혔거나 뒤로 감). 지시서: viewer 트리에서 Save as, viewer 보이는 상태.
- s7 ✗ 대화상자 닫힘, 메인 트리 2D Horizon > `2D_Horizon`, **2D Viewer 없음** — 이는 시나리오의 s8(목표) 상태에 가깝다. 지시서의 s7(viewer 아직 열림)과 다름.
- s8 누락.
- → 재캡처 요청: s6(2D viewer가 보이는 상태에서 viewer 트리의 <New 2D Horizon 1> 우클릭 > Save as로 Output selection 열림), s7(이름 입력 후 OK, viewer 트리에 저장 이름, viewer 여전히 열림), s8(viewer 닫음, 3D scene에 2D 라인+horizon, 메인 트리 2D Horizon에 저장 이름). 창 크기는 다른 장과 같게.

## D — qgis__reclassify_raster__01 (9/9장)
- s0 ✓ Layers: aspect(Band 1 Gray 360…0.093473), srtm_41_19; Processing Toolbox 열림(검색 "aspect"); Reclassify 대화상자 없음. Project CRS EPSG:32733.
- s1 ✓ `Raster Analysis - Reclassify by Table` 대화상자. **Raster layer가 이미 `aspect [EPSG:32733]`로 자동 채워짐**(활성 레이어), Band 1 (Gray), Reclassification table = Fixed table (0x3), Reclassified raster [Save to temporary file], Open output file after running algorithm 체크, Run/Close/Help, Advanced/Run as Batch Process.
- s2 ✓ **s1과 화면 동일**(상태 표시줄 좌표만 다름). Raster layer 선택은 사용자 동작이 필요 없었음(v3 QGIS s3/s4 자동 채움과 같은 상황) — 보류 목록·GT 정정 대상.
- s3 ✓ 대화상자 안의 `Reclassification table` 패널(← 뒤로가기, Minimum/Maximum/Value 열, Add Row, Remove Row(s), Remove All, OK, Cancel), 행 없음. 지시서의 "Fixed table 대화상자"는 이 버전에서 대화상자 내부 패널로 표시됨.
- s4 ✓ Fixed table (5x3), 출력 임시 파일.
- s5 ✓ Reclassified raster = `C:/GeoLensData/reclassified.tif`(사용자가 exercise_data/raster_analysis 대신 다른 폴더 사용; 패턴은 `reclassified`로 통과).
- s6 ✓ 실행 완료: Layers에 reclassified(Band 1 Gray 4…1) 추가, 대화상자 닫힘, Toolbox "Recently used".
- s7 ✓ Layer Styling 패널(reclassified, Paletted/Unique values, Band 1 (Gray), Color ramp Random colors, Value/Color/Label 비어 있음, Classify/Delete All, Layer Rendering …). Scale 1:300266.
- s8 ✓ Classify 후 값 1–4 색 배정(녹/청록/보라/빨강), 지도 4색, Layers 범례 1–4.

## B — qgis__rule_classification__01 (10/10장)
- s0 ✓ landuse 로드(Categorized 색), 대화상자 없음. Project CRS **EPSG:4326**(투영 안 함; AREA는 사용자가 §3.3.3대로 계산했다고 함, 화면에서 확인 불가).
- s1 ✓ `Layer Properties - landuse — Symbology`, Categorized(Value landuse, 11개 범주 + all other values).
- s2 ✓ Rule-based, 변환된 규칙 11행 + ELSE.
- s3 ✓ 규칙 목록 비어 있음.
- s4 ✓ `Edit Rule` 대화상자(Label/Filter/Test/Else "Catch-all for other features"/Description/Scale range/Symbol Fill > Simple Fill), 뒤 목록에 "(no filter)" 행 1개(Add rule이 만든 빈 규칙).
- s5 ✓ 규칙 1행: Swellendam … / "name" = 'Swellendam'.
- s6 ✓ 2행(+ Other residen… / "landuse" = 'residential' …).
- s7 ✓ 3행(+ Big non resid… / "landuse" <> 'residential' …).
- s8 ✓ 4행(마지막 Small non re… / ELSE), 적용 전(뒤 지도 안 보임).
- s9 ✓ 대화상자 닫힘, Layers 범례 landuse > Swellendam city / Other residential / Big non residential areas / Small non residential areas, 지도 4색.

## GT 작성 시 유의
- D s1/s2 화면 동일(자동 채움): data_state에 명시. C s6/s7은 재캡처 후 다시 검증.
- 모든 QGIS 장에 창 제목 `*Untitled Project — QGIS`, 메뉴 바, 상태 표시줄(Coordinate/Scale/Magnifier/Rotation/Render/EPSG)이 공통으로 보임.
