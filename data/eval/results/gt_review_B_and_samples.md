# GT review — B items (current GT not read by vision) + 3 applied samples

Category A (vision-read labels not covered by the old GT) has been applied to every step. B entries are kept in the GT unless you strike them; decide per line.

## SAMPLE opendtect__attribute_computation__01 step 3 — data/eval/screenshots/opendtect__attribute_computation__01/step_3.jpg
applied visible_elements (56): Attribute Set 3D window | Attribute list panel (left) showing 'Energy [-28,+28]' entry (just added) | Save on Close checkbox = CHECKED | Close button | OK / Save button | OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1] | Survey | Analysis | Processing | View | Utilities | TerraNubis | Help | File | Step 4 | SEG-Y | Select ... | Add as new | Z (924) | -9968 | OD Seismic 1 | Attribute set (<not saved>) | <All> | Input Data (Seismic_data) | Time gate (ms) (-28, 28) | Output (Energy) | Attribute Name (Energy [-28, +28]) | Elements | In-line | 425 | Cross-line | 775 | Z-slice | Volume | 343-506 / 656-893 / 69... | <right-click> | Random Line | 2D Line | 3D Horizon | 2D Horizon | Fault | Geobody | Well | PointSet | Polygon | Prestack Events | Annotations | Save on Close (checked) | Compute gradient | Yes (unchecked) | No (checked) | Tree scene 1 | Color | 1200 | Inl: 343-506, Crl: 656-893, Time: 696-1156 | [free mem] 101.6/127.8 GB

## SAMPLE opendtect__survey_setup__01 step 0 — data/eval/screenshots/opendtect__survey_setup__01/step_0.jpg
applied visible_elements (10): Survey Data Root tab | Add button | Edit button | Select button | Cancel button | Information tab | Survey Setup and Selection | Notes | Log | Survey Data Root (C:\Users\user\Downloads\GeoLens_test)

## SAMPLE qgis__vector_buffer__01 step 3 — data/eval/screenshots/qgis__vector_buffer__01/step_3.jpg
applied visible_elements (60): Buffer algorithm dialog opened (modal on top of main window) | Input layer dropdown (default entry or empty) | Selected features only checkbox (unchecked) | Distance field (default 10 or similar) | Distance unit dropdown showing meters | Segments field (default 5) | End cap style, Join style dropdowns | Miter limit field | Dissolve results checkbox (unchecked) | Buffered output field with '[Create temporary layer]' default + '…' button | Run / Close / Help buttons at bottom | *Untitled Project — QGIS | Vector Geometry - Buffer | Edit | View | Settings | Plugins | Raster | Database | Web | Mesh | Processing | Advanced | Run as Batch Process... | Cancel | Parameters | Input layer (roads_33S [EPSG:32733]) | Distance (10.000000) | Segments (5) | End cap style (Round) | Join style (Round) | Miter limit (2.000000) | Buffered ([Create temporary layer]) | Type to locate (Ctrl+K) | Create wedge buffers | Multi-ring buffer (constant distance) | Rectangles, ovals, diamonds | Single sided buffer | Tapered buffers | Variable width buffer (by M value) | Vector selection | Extract within distance | Select within distance | GDAL | Buffer vectors | One side buffer | GRASS | r.buffer | Vector (v.*) | v.buffer | Render | Layers | This algorithm computes a buffer area for all the features in an input layer, using a fixed or dynamic distance. | The segments parameter controls the number of line segments to use to approximate a quarter circle when creating rounded offsets. | The end cap style parameter controls how line endings are handled in the buffer. | The miter limit parameter is only applicable for miter join styles, and controls the maximum distance from the offset curve to use when creating a mitered join. | Coordinate 1026658, 6236015 | Scale 1:240882 | Magnifier 100% | Rotation 0.0°

## B items (25) — current GT entries the vision model did not read
| scenario | step | screenshot | GT entry | keep? |
|---|---|---|---|---|
| opendtect__3d_visualization__01 | 1 | data/eval/screenshots/opendtect__3d_visualization__01/step_1.jpg | OR Select Attribute dialog listing seismic cubes | |
| opendtect__3d_visualization__01 | 3 | data/eval/screenshots/opendtect__3d_visualization__01/step_3.jpg | No context menu, no dialog | |
| opendtect__attribute_computation__01 | 0 | data/eval/screenshots/opendtect__attribute_computation__01/step_0.jpg | Parameter panel (empty / disabled until type chosen) | |
| opendtect__attribute_computation__01 | 2 | data/eval/screenshots/opendtect__attribute_computation__01/step_2.jpg | Input Data = 4 Dip steered median filter | |
| opendtect__attribute_computation__01 | 2 | data/eval/screenshots/opendtect__attribute_computation__01/step_2.jpg | Time gate populated: -28 to +28 | |
| opendtect__attribute_computation__01 | 3 | data/eval/screenshots/opendtect__attribute_computation__01/step_3.jpg | OK / Save button | |
| opendtect__attribute_computation__01 | 4 | data/eval/screenshots/opendtect__attribute_computation__01/step_4.jpg | Attribute set Name field = 'my first attribute set' | |
| opendtect__attribute_computation__01 | 4 | data/eval/screenshots/opendtect__attribute_computation__01/step_4.jpg | OK button | |
| opendtect__attribute_computation__01 | 5 | data/eval/screenshots/opendtect__attribute_computation__01/step_5.jpg | OpendTect Main Window | |
| opendtect__attribute_computation__01 | 5 | data/eval/screenshots/opendtect__attribute_computation__01/step_5.jpg | Attribute Set 3D closed | |
| opendtect__attribute_computation__01 | 7 | data/eval/screenshots/opendtect__attribute_computation__01/step_7.jpg | 'Energy [-28,+28]' layer checkbox is checked (currently rendered on the inline) | |
| opendtect__survey_setup__01 | 0 | data/eval/screenshots/opendtect__survey_setup__01/step_0.jpg | Survey Data Root tab | |
| opendtect__survey_setup__01 | 0 | data/eval/screenshots/opendtect__survey_setup__01/step_0.jpg | Add button | |
| opendtect__survey_setup__01 | 0 | data/eval/screenshots/opendtect__survey_setup__01/step_0.jpg | Edit button | |
| opendtect__survey_setup__01 | 2 | data/eval/screenshots/opendtect__survey_setup__01/step_2.jpg | Survey name field with 'My_F3_Survey' typed | |
| opendtect__survey_setup__01 | 3 | data/eval/screenshots/opendtect__survey_setup__01/step_3.jpg | OpendTect V7.0.9 application window | |
| opendtect__survey_setup__01 | 3 | data/eval/screenshots/opendtect__survey_setup__01/step_3.jpg | Toolbar | |
| qgis__vector_buffer__01 | 0 | data/eval/screenshots/qgis__vector_buffer__01/step_0.jpg | Map Canvas (center) rendering road network | |
| qgis__vector_buffer__01 | 1 | data/eval/screenshots/qgis__vector_buffer__01/step_1.jpg | Map Canvas unchanged from step_0 | |
| qgis__vector_buffer__01 | 3 | data/eval/screenshots/qgis__vector_buffer__01/step_3.jpg | Distance field (default 10 or similar) | |
| qgis__vector_buffer__01 | 3 | data/eval/screenshots/qgis__vector_buffer__01/step_3.jpg | Segments field (default 5) | |
| qgis__vector_buffer__01 | 3 | data/eval/screenshots/qgis__vector_buffer__01/step_3.jpg | End cap style, Join style dropdowns | |
| qgis__vector_buffer__01 | 3 | data/eval/screenshots/qgis__vector_buffer__01/step_3.jpg | Miter limit field | |
| qgis__vector_buffer__01 | 7 | data/eval/screenshots/qgis__vector_buffer__01/step_7.jpg | QGIS main window with Buffer dialog and Save-to-GeoPackage dialog both CLOSED | |
| qgis__vector_buffer__01 | 7 | data/eval/screenshots/qgis__vector_buffer__01/step_7.jpg | Map Canvas rendering the dissolved buffer as a single polygon covering 50 m around the road network (semi-transparent overlay over the roads) | |

Also for decision (patterns, not GT): survey_setup step 0 has no text label on the Add button (models write '+ 아이콘'); QGIS step 3 expects 'Input layer' selection but the captured dialog may already show roads_33S. Patterns were NOT changed.


## S6 검수 자료 — survey_setup step 0: Add 버튼 표기 (2026-09-18 추가, 패턴 미변경)

- 스크린샷: `data/eval/screenshots/opendtect__survey_setup__01/step_0.jpg` (1920×1032). 버튼 확대 크롭(×3): `gt_review/survey_s0_add_button_x3.png` (원본 px (872,31)–(980,117), Gemini Flash가 준 bbox 기준), 주변 문맥 크롭: `gt_review/survey_s0_context.png`, 좌표 기록: `gt_review/survey_s0_crops.json`.
- 화면의 버튼: 텍스트 라벨 없음. 흰 문서 아이콘 위에 초록색 원형 '+' (바로 아래 연필=Edit 아이콘). 현재 GT visible_elements 표기: 'Add button'.
- 매뉴얼 표기(v4 인덱스, §1.2.2a p.21): "1. … or click on the Survey Setup icon ." / "**2. Click on the New Survey icon .**" — 매뉴얼은 이 버튼을 **New Survey icon**이라 부르며 아이콘 그림을 본문에 인라인으로 넣음(텍스트 없음).
- 채점 패턴(불변): `(?i)(Survey|Create|New|Add)`, 키워드 ['Survey','Create','New'], 허용 대안 `(?i)(Add)` ("The Add / '+' button opens Create New Survey dialog").
- 관측된 모델 응답: full_system(iteration 0) "초록색 더하기 아이콘을 클릭하세요" → 불일치; vanilla_vector "새 survey 아이콘을 클릭합니다" → 일치('survey'); 이전 실행들 "+ 아이콘을 클릭" → 불일치.
- iteration 2부터 생성기 프롬프트(모든 백엔드 공통)에 "컨트롤 이름은 Reference Manual Context 표기 그대로, 텍스트 없는 아이콘 버튼은 매뉴얼 이름 + 모양 설명"을 추가한다(V3-12 예정). 패턴은 사용자 결정 전까지 그대로 둔다.
- 결정 요청: (1) 패턴 유지 / (2) '+'·'더하기'·'plus' 추가 / (3) 'New Survey icon' 표기만 정답 인정. 어느 쪽이든 결정 후 unified4·v3 dev 로그를 구·신 패턴으로 재채점해 차이를 기록한다.
