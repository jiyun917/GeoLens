# 수치 표기 재확인 과제 (외부 검토 결정 H10, 2026-09-18)

목적: QGIS 8개 스텝(및 attribute step 3)의 GT `visible_elements`에 들어간 **수치가 포함된 문자열**을 스크린샷에서 3배 확대로 다시 읽어, 화면 문자열과 다르면 정확한 문자열을 적는다. 화면을 읽기만 하고 파일은 수정하지 않는다. 이 폴더 밖 파일은 열지 않는다.

확인 방법: `screenshots/qgis__vector_buffer__01/step_N.jpg`에서 해당 값이 있는 위치(상태 표시줄 좌표·축척·회전 칸, Buffer 다이얼로그의 Distance·Segments·Miter limit 칸)를 Python(PIL)으로 3배 이상 확대 크롭해 이 폴더의 `numeric_crops/` 아래에 저장하고 Read 도구로 본다. 좌표는 상태 표시줄 왼쪽 "Coordinate" 칸, 축척은 "Scale" 칸, 회전은 "Rotation" 칸.

QGIS는 소수점에 쉼표를 쓴다(예: `10,000000`, `2,000000`, `0,0 °`). GT의 마침표 표기는 표기 오류일 가능성이 높으니 화면 그대로 적는다. 공백(예: `0,0 °`의 공백)도 화면대로.

## 확인할 항목 (현재 GT 문자열)

| 스텝 | 현재 GT 문자열 |
|---|---|
| qgis step 0 | `Coordinate (1054725, 6221612)`, `Scale (1:240882)`, `Rotation (0.0 °)` |
| qgis step 1 | `Coordinate (1043954, 6244110)`, `Scale (1:240882)`, `Rotation (0.0 °)` |
| qgis step 2 | `Coordinate (1045420, 6224416)`, `Scale (1:240882)`, `Rotation (0.0°)` |
| qgis step 3 | `Distance (10,000000)`, `Distance (10.000000)`, `Miter limit (2.000000)`, `Coordinate 1026658, 6236015`, `Scale 1:240882`, `Rotation 0.0°`, `Segments (5)` |
| qgis step 4 | `10,000000`, `2,000000`, `1044336, 6233594`, `1:240882` |
| qgis step 5 | `50.000000`, `2.000000`, `1044846, 6212179`, `1:240882` |
| qgis step 6 | `Distance (50.000000)`, `Miter limit (2.000000)`, `Coordinate (1028212, 6215621)`, `Scale (1:240882)`, `Rotation (0.0 °)` |
| qgis step 7 | `Coordinate (1055235, 6207527)`, `Scale (1:240882)`, `Rotation (0.0 °)` |
| attribute step 3 | `Attribute Name (Energy [-28, +28])` — 화면의 Attribute Name 칸 원문(공백 유무) |

## 결과물

`NUMERIC_CHECK_RESULT.md` — 표: 스텝 | 현재 GT 문자열 | 화면 문자열(확정) | 같음/다름 | 근거 크롭 파일. 화면에서 그 값 자체가 보이지 않으면 "화면에 없음"으로 적는다(삭제 여부는 판단하지 않는다). 마지막에 다른 항목 수를 요약한다.
