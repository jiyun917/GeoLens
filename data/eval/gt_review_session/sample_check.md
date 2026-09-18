# 규칙 2 표본 검수 결과 — gt_review_session (2026-09-18)

검수 대상: 시나리오별 1장씩 3장 (survey_setup step 0, attribute_computation step 3, qgis__vector_buffer step 3). 각 스크린샷의 현재 GT `visible_elements` 중 **vision 열거 항목**(review_v3 A 목록에서 GT에 추가된 항목; `_gt_provenance`의 "vision-enumerated" 수와 일치)을 스크린샷 원본 해상도(Read)로 대조하고, 판독이 애매한 부분은 PIL로 3–8배 확대 크롭을 스크래치패드(폴더 밖 임시 디렉터리)에 만들어 재확인했다.

판정 기준
- **오독**: 문자열이 가리키는 요소가 화면에 없거나, 글자·숫자가 화면과 다름.
- **표기 차이**: 요소는 화면에 있으나 공백·소수점 구분자 등 표기만 다름. 규칙 2의 "화면에 없는 문자열"을 가장 보수적으로 읽으면 이것도 포함되므로 별도 집계하고 합산치도 제시한다.
- vision 항목의 `라벨 (값)` 괄호 표기(예: `Input Data (Seismic_data)`, `Z (924)`)는 GT 전반의 관례이므로 표기 차이로 세지 않았다.

## 요약

| 스크린샷 | vision 열거 항목 수 | 오독 | 표기 차이 | 오독률 | 보수 합산(오독+표기) |
|---|---|---|---|---|---|
| `screenshots/opendtect__survey_setup__01/step_0.jpg` | 4 | 0 | 0 | 0.00% | 0.00% |
| `screenshots/opendtect__attribute_computation__01/step_3.jpg` | 51 | 0 | 1 | 0.00% | 1.96% |
| `screenshots/qgis__vector_buffer__01/step_3.jpg` | 49 | 1 | 3 | 2.04% | 8.16% |
| **합계** | **104** | **1** | **4** | **0.96%** | **4.81%** |

**결론: 전체 오독률 0.96% (표기 차이까지 합산해도 4.81%) < 5% → 반영 진행.**
단, qgis step 3 한 장만 보면 보수 합산치가 8.16%로 5%를 넘는다(오독만은 2.04%). 스크린샷 단위 기준을 적용하려면 재판단이 필요하다. 규칙 2가 반영 중단 조건으로 든 것은 오독("화면에 없는 문자열")이며, 지시에 따라 전체 비율로 판단했다.

## 상세

### 1. survey_setup step 0 — `screenshots/opendtect__survey_setup__01/step_0.jpg`
vision 열거 항목 (4): Survey Setup and Selection | Notes | Log | Survey Data Root (C:\Users\user\Downloads\GeoLens_test)

- 전부 확인: 제목표시줄 `Survey Setup and Selection`(최상단 좌측); 하단 좌측 탭 `Information / Notes / Log`(y≈617); 좌상단 버튼 `Survey Data Root ...`(x≈12–152, y≈40) + 오른쪽 경로칸 `C:\Users\user\Downloads\GeoLens_test`.
- 오독 0, 표기 차이 0.

### 2. attribute_computation step 3 — `screenshots/opendtect__attribute_computation__01/step_3.jpg`
vision 열거 항목 (51): OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1] | Survey | Analysis | Processing | View | Utilities | TerraNubis | Help | File | Step 4 | SEG-Y | Select ... | Add as new | Z (924) | -9968 | OD Seismic 1 | Attribute set (<not saved>) | <All> | Input Data (Seismic_data) | Time gate (ms) (-28, 28) | Output (Energy) | Attribute Name (Energy [-28, +28]) | Elements | In-line | 425 | Cross-line | 775 | Z-slice | Volume | 343-506 / 656-893 / 69... | <right-click> | Random Line | 2D Line | 3D Horizon | 2D Horizon | Fault | Geobody | Well | PointSet | Polygon | Prestack Events | Annotations | Save on Close (checked) | Compute gradient | Yes (unchecked) | No (checked) | Tree scene 1 | Color | 1200 | Inl: 343-506, Crl: 656-893, Time: 696-1156 | [free mem] 101.6/127.8 GB

- 오독 0.
- 표기 차이 1: `Attribute Name (Energy [-28, +28])` — 화면의 Attribute Name 입력칸(Attribute Set 3D 창 하단, x≈885–1185, y≈742)은 `Energy [-28,+28]`(쉼표 뒤 공백 없음; 3배 확대 확인). 좌측 attribute 목록 항목도 `Energy [-28,+28]`.
- 확인 위치: 제목표시줄·메뉴바(Survey … Help, y≈42); 툴바(SEG-Y y≈70; Z 924 / Step 4 / -9968 / 9968 / OD Seismic 1 y≈104); Attribute Set 3D 창(File y≈282; Attribute set `<not saved>`, `<All>`, `Energy` y≈341; Input Data `Seismic_data` + `Select ...` y≈373; Time gate (ms) `-28` `28` y≈405; Compute gradient ○Yes ●No y≈439; Output `Energy` y≈473; Attribute Name + `Add as new` y≈742; ☑ Save on Close, `Close`, `?` y≈781); Tree scene 1 패널(Elements/Color 헤더 y≈158; In-line 425, Cross-line 775, Z-slice 924, Volume `343-506 / 656-893 / 69...`, `<right-click>`, Random Line … Prestack Events, Annotations y≈198–662); 3D 뷰 볼륨 박스 라벨 `1200`(x≈1675, y≈512); 상태바 `Inl: 343-506, Crl: 656-893, Time: 696-1156`(y≈1030), `[free mem] 101.6/127.8 GB`(우하단).

### 3. qgis__vector_buffer step 3 — `screenshots/qgis__vector_buffer__01/step_3.jpg`
vision 열거 항목 (49): *Untitled Project — QGIS | Vector Geometry - Buffer | Edit | View | Settings | Plugins | Raster | Database | Web | Mesh | Processing | Advanced | Run as Batch Process... | Cancel | Parameters | Input layer (roads_33S [EPSG:32733]) | Distance (10.000000) | Segments (5) | End cap style (Round) | Join style (Round) | Miter limit (2.000000) | Buffered ([Create temporary layer]) | Type to locate (Ctrl+K) | Create wedge buffers | Multi-ring buffer (constant distance) | Rectangles, ovals, diamonds | Single sided buffer | Tapered buffers | Variable width buffer (by M value) | Vector selection | Extract within distance | Select within distance | GDAL | Buffer vectors | One side buffer | GRASS | r.buffer | Vector (v.*) | v.buffer | Render | Layers | This algorithm computes a buffer area … | The segments parameter controls … | The end cap style parameter controls … | The miter limit parameter is only applicable … | Coordinate 1026658, 6236015 | Scale 1:240882 | Magnifier 100% | Rotation 0.0°

- **오독 1**: `Coordinate 1026658, 6236015` — 상태바 Coordinate 칸(x≈1135–1230, y≈1017)은 `1028658, 6236015` (8배 확대 확인; 세 번째 자리 6→8 오독).
- **표기 차이 3** (소수점 구분자; 화면은 쉼표): `Distance (10.000000)` → 화면 `10,000000`(Parameters 탭 y≈415); `Miter limit (2.000000)` → 화면 `2,000000`(y≈605); `Rotation 0.0°` → 화면 `0,0 °`(상태바 x≈1630, y≈1017). 3배 확대 확인.
- 나머지 45건 확인 위치: 제목표시줄 `*Untitled Project — QGIS`; 다이얼로그 제목 `Vector Geometry - Buffer`(x≈645, y≈250); 메뉴바(Edit … Processing y≈32); 다이얼로그 하단 `Advanced` `Run as Batch Process...`(y≈768), `Cancel`(y≈741); 탭 `Parameters`(y≈289); 필드 Input layer `roads_33S [EPSG:32733]`(y≈340), Segments `5`(y≈463), End cap style `Round`(y≈510), Join style `Round`(y≈558), Buffered `[Create temporary layer]`(y≈699); 우측 도움말 패널 4문장(x≈1040–1290, y≈315–585); Processing Toolbox 트리(Create wedge buffers … v.buffer, x≈1690, y≈239–554), `GDAL`, `GRASS`, `Vector selection`, `Vector (v.*)`; 상태바 `Type to locate (Ctrl+K)`(좌하단), `Scale 1:240882`, `Magnifier 100%`, ☑`Render`; 좌측 패널 제목 `Layers`.

## 비고
- 위 오독·표기 차이는 규칙 2에 따라 **보고만** 한다. A 항목 수정은 어느 규칙에도 없어 `proposed/`에 반영하지 않았다 (GT_hold_list.md H10).
- 표본 밖 스텝의 A 항목은 검수하지 않았다. QGIS의 쉼표 소수점은 이 세션의 로케일 설정이므로, 다른 QGIS 스텝의 `50.000000`, `2.000000`, `0.0 °` 류 항목도 같은 표기 차이를 가질 가능성이 있다(미확인).
