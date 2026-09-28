# Study 4 캡처 지시서 (사용자 작업) — 총 24장

작성 2026-09-28. 워크플로우 3개와 시나리오 골격 3개(`scripts/study4_author.py`)는 **매뉴얼 본문만 보고** 캡처 전에 저작했다(스테이징 `data/eval/study4/workflows_draft`, 검증 실행이 끝난 뒤 풀에 편입·커밋). 규칙은 study 2·3과 같다: 각 스크린샷은 표의 "화면 상태"를 보여 주고, "직전 동작"은 그 화면을 만든 동작이며, "보이면 안 되는 것"이 화면에 있으면 다시 찍는다. 창 크기·해상도는 study 3과 같게(전체 화면, 1920×1030 내외), PNG로 저장해 `data/eval/study4/originals_png/<scenario_id>/step_N.png`에 둔다(변환·검증은 세션이 한다). GeoLens 창은 화면에 없어야 한다.

## 준비 (캡처 안 함)
- **QGIS Training Data**: `C:/Users/user/Downloads/QGIS-Training-Data-master/QGIS-Training-Data-master/exercise_data/` 를 쓴다.
- **F 준비**: QGIS 새 프로젝트(저장 안 함), `exercise_data/world/oceans.shp` 로드. 프로젝트 CRS EPSG:4326(기본). Settings ► Custom Projections…에 이전에 만든 사용자 정의 CRS가 있으면 삭제해 표를 비운다.
- **G 준비**: QGIS 새 프로젝트, `C:/GeoLensData/aspect.tif`(study 3에서 만든 aspect 래스터) 로드. Processing Toolbox 열어 둠. 출력 폴더는 `C:/GeoLensData/`를 써도 된다(GT는 폴더 이름을 강제하지 않음).
- **E 준비**: OpendTect F3 Demo 2023, 3D scene 표시, 트리 3D Horizon 아래에 아무것도 없음(있으면 Remove). Attribute Set 창 없음. `4 Dip steered median filter` 볼륨이 Stored 데이터에 있어야 한다(F3 Demo 기본 포함).
- 매뉴얼과 다른 이름이 화면에 보이면(예: horizon 목록 이름) 그대로 진행하고 캡처 노트에 적는다 — GT 정정은 study 3의 H2 절차를 따른다.

## E — `opendtect__spectral_decomp__01` (매뉴얼 §1.5.2a, 9장)
| 파일 | 화면 상태 | 직전 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0 | 3D scene with the tree; 3D Horizon item WITHOUT a color-blended horizon; no dialog; no Attribute Set window. | Nothing yet (initial state). | Select Input Horizon(s) dialog, Attribute Set 3D window |
| step_1 | 'Select Input Horizon(s)' dialog open (Add Color Blended): horizon list incl. Demo 1 --> MFS4, Area subselection row with Select…, OK/Cancel. Nothing selected yet, no Position dialog. | Right-clicked 3D Horizon > Add Color Blended…. | a selected horizon, Position dialog |
| step_2 | 'Position' (Specify Position) dialog open with In-line Range 200 650 and Cross-line Range 500 1000 already typed (Step 1); OK NOT yet clicked. Demo 1 --> MFS4 is selected in the dialog behind. | Selected Demo 1 --> MFS4, clicked Select… and typed the two ranges. | horizon displayed in the scene |
| step_3 | Dialogs closed; tree shows 3D Horizon > Demo 1 --> MFS4 with four attribute layers (three with R/G/B colour flags); horizon visible in the 3D scene; no Attribute Set window. | Clicked OK (ranges) and OK (display). | Attribute Set 3D window, Select Input Horizon(s) dialog |
| step_4 | 'Attribute Set 3D' window open, attribute set <not saved>, EMPTY attribute list, default attribute type; Input Data empty. | Clicked the Attribute Set 3D toolbar icon. | SD_24Hz in the attribute list |
| step_5 | Attribute Set 3D window: list shows ONE attribute SD_24Hz[-8,24ms]; fields still show Spectral Decomposition, Input 4 Dip steered median filter, Time gate -8 24, Output frequency 24, Step 4. | Defined SD_24Hz[-8,24ms] and clicked Add as new. | SD_44Hz in the list |
| step_6 | Attribute Set 3D window: list shows TWO attributes (SD_24Hz[-8,24ms], SD_44Hz[-8,24ms]); Output frequency field shows 44. | Changed frequency to 44, name to SD_44Hz[-8,24ms], clicked Add as new. | SD_64Hz in the list |
| step_7 | Attribute Set 3D window: list shows THREE attributes (SD_24Hz, SD_44Hz, SD_64Hz[-8,24ms]); Output frequency field shows 64. Window still open. | Changed frequency to 64, name to SD_64Hz[-8,24ms], clicked Add as new. | window closed |
| step_8 | GOAL-REACHED: Attribute Set 3D window closed (set saved, e.g. as Spectral Decomposition); 3D scene with the color-blended Demo 1 --> MFS4 horizon and the tree only. | Clicked Close (and named the set on Save on Close). | Attribute Set 3D window |

## F — `qgis__custom_projection__01` (매뉴얼 §6.1.4, 9장)
| 파일 | 화면 상태 | 직전 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0 | QGIS main window, oceans layer loaded, world map shown, status-bar CRS EPSG:4326, no dialog. | Nothing yet (initial state). | Custom Projections dialog |
| step_1 | 'Options — User Defined CRS' (Custom Projections) dialog open with an EMPTY CRS table; Name and Parameters empty. | Opened Settings ► Custom Projections…. | a CRS row in the table, text in Parameters |
| step_2 | Same dialog with ONE new row (new CRS) added after +; Name field empty/default, Parameters empty. | Clicked Add new CRS (+). | text in Parameters |
| step_3 | Same dialog: Name = Van der Grinten I, Format = WKT (Recommended); Parameters still EMPTY. | Typed the name and set the format. | text in Parameters |
| step_4 | Same dialog: Parameters contains the PROJCRS WKT (METHOD Van Der Grinten); OK NOT yet clicked. | Pasted/typed the WKT string. | dialog closed |
| step_5 | Dialog closed; main window; status-bar CRS button still shows EPSG:4326; map unchanged. | Clicked OK in the Custom Projections dialog. | Project Properties dialog |
| step_6 | 'Project Properties — CRS' dialog open; Filter empty; nothing new selected. | Clicked the status-bar CRS button. | Van der Grinten selected |
| step_7 | Same dialog: Filter shows Van der Grinten; Van der Grinten I (USER:100000) selected under User Defined Coordinate Systems; OK NOT yet clicked. | Filtered and selected the custom CRS. | reprojected map |
| step_8 | GOAL-REACHED: dialog closed; map shows the world in the circular Van der Grinten projection; status-bar CRS shows USER:100000. | Clicked OK. | Project Properties dialog |

## G — `qgis__aspect_north__01` (매뉴얼 §7.3.6, 6장)
| 파일 | 화면 상태 | 직전 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0 | QGIS main window with the aspect raster loaded (Processing Toolbox may be open); NO Raster Calculator dialog. | Nothing yet (initial state). | Raster Calculator dialog |
| step_1 | 'Raster Calculator' (Processing) dialog open: Layers list (aspect@1 …), Operators, Expression EMPTY, Reference layer(s) empty, output = temporary file. | Double-clicked Raster analysis › Raster calculator in the toolbox. | text in Expression |
| step_2 | Same dialog: Expression = aspect@1 <= 90 OR aspect@1 >= 270 ('Expression is valid'); Reference layer(s) still empty; output temporary. | Typed the expression. | 1 inputs selected |
| step_3 | Same dialog: Reference layer(s) shows '1 inputs selected' (aspect); output still temporary. | Chose aspect via the … button and clicked OK. | aspect_north in the output path |
| step_4 | Same dialog: Calculated = …/raster_analysis/aspect_north.tif; NOT yet run. | Set the output file via … › Save to File. | aspect_north layer in the Layers panel |
| step_5 | GOAL-REACHED: algorithm ran; aspect_north layer (0/1) in the Layers panel; map shows north-facing pixels; dialog closed. | Clicked Run (and closed the dialog). | Raster Calculator dialog |

### E 보충 (OpendTect)
- step_2: Position 대화상자에 In-line 200 650 / Cross-line 500 1000을 **입력한 뒤, OK를 누르기 전에** 찍는다. 그 뒤 OK → (Select Input Horizon(s)로 돌아옴) → OK.
- step_4~7: Attribute Set 3D 창에서 속성 종류 드롭다운을 Spectral Decomposition으로, Input Data는 Select…로 4 Dip steered median filter, Transform type FFT, Time gate -8 24, Output frequency 24 / Step 4, Attribute Name `SD_24Hz[-8,24ms]` → Add as new. 44·64 Hz는 주파수와 이름만 바꿔 Add as new. 매뉴얼의 Amplitude Spectrum 확인(step 5–8)은 생략한다.
- step_8: Close 시 Save on Close가 켜져 있으면 세트 이름을 `Spectral Decomposition`으로 저장.

### F 보충 (QGIS)
- step_4: Parameters에는 매뉴얼 p.191–192의 WKT(PROJCRS["unknown", … METHOD["Van Der Grinten"] …)를 그대로 붙여 넣는다(줄바꿈 포함 가능). Validate는 눌러도 되고 안 눌러도 된다.
- step_6: 상태 표시줄 맨 오른쪽의 `EPSG:4326` 버튼을 클릭하면 Project Properties — CRS 대화상자가 열린다.
- step_8: 지도가 원형(Van der Grinten)으로 바뀌고 상태 표시줄에 `USER:100000`(번호는 다를 수 있음)이 보이면 목표.

### G 보충 (QGIS)
- Raster calculator는 **Processing Toolbox ▸ Raster analysis ▸ Raster calculator**(메뉴 Raster ▸ Raster Calculator… 아님).
- step_3: Reference layer(s)의 … 버튼 → aspect 체크 → OK 후 '1 inputs selected'가 보이는 상태.

## 끝나면
- PNG 24장이 `data/eval/study4/originals_png/<scenario_id>/step_N.png`에 있으면 "캡처 완료"라고 알려 주세요. 그 뒤 세션이 검증(지시서 대조) → 재캡처 요청(필요 시) → GT 열거·외부 검토 → 선정 실행 → 사전등록 4 서명 → 확인 실행 순으로 진행합니다.
