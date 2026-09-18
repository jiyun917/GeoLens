# 수치 표기 재확인 결과 (외부 검토 결정 H10, 2026-09-18)

확인 방법: `screenshots/qgis__vector_buffer__01/step_N.jpg`(8장)와 `screenshots/opendtect__attribute_computation__01/step_3.jpg`에서 해당 칸을 PIL로 4~10배 확대 크롭해 `numeric_crops/`에 저장하고 Read 도구로 읽었다. 화면 문자열은 QGIS 표기(소수점 쉼표, `0,0 °`의 공백)를 그대로 옮겼다. 파일(시나리오 JSON)은 수정하지 않았다.

- 상태 표시줄: `stepN_statusbar_x4.png`(Coordinate~Rotation 전체, 4배) + `stepN_coord_scale_rot_x6x8.png`(Coordinate·Scale 6배, Rotation 8배 합본)
- Buffer 다이얼로그: `stepN_distance_x4.png`, `stepN_segments_x4.png`, `stepN_miter_x4.png` + 소수점 확인용 `step3_distance_sep_x8.png`, `step5_distance_sep_x8.png`, `step6_distance_sep_x8.png`, `step3_miter_sep_x8.png`
- attribute step 3: `attr_step3_attribute_name_x4.png` + `attr_step3_attribute_name_bracket_x8.png`(쉼표 뒤 공백 확인), `attr_step3_list_entry_x8.png`(좌측 목록의 동일 항목 참고)

## 결과 표

| 스텝 | 현재 GT 문자열 | 화면 문자열(확정) | 같음/다름/화면에 없음 | 근거 크롭 파일 |
|---|---|---|---|---|
| qgis step 0 | `Coordinate (1054725, 6221612)` | `1054725, 6221612` | 같음 | step0_statusbar_x4.png, step0_coord_scale_rot_x6x8.png |
| qgis step 0 | `Scale (1:240882)` | `1:240882` | 같음 | step0_coord_scale_rot_x6x8.png |
| qgis step 0 | `Rotation (0.0 °)` | `0,0 °` | 다름 (소수점 `.`→`,`) | step0_coord_scale_rot_x6x8.png |
| qgis step 1 | `Coordinate (1043954, 6244110)` | `1043954, 6244110` | 같음 | step1_statusbar_x4.png, step1_coord_scale_rot_x6x8.png |
| qgis step 1 | `Scale (1:240882)` | `1:240882` | 같음 | step1_coord_scale_rot_x6x8.png |
| qgis step 1 | `Rotation (0.0 °)` | `0,0 °` | 다름 (소수점 `.`→`,`) | step1_coord_scale_rot_x6x8.png |
| qgis step 2 | `Coordinate (1045420, 6224416)` | `1045420, 6224416` | 같음 | step2_statusbar_x4.png, step2_coord_scale_rot_x6x8.png |
| qgis step 2 | `Scale (1:240882)` | `1:240882` | 같음 | step2_coord_scale_rot_x6x8.png |
| qgis step 2 | `Rotation (0.0°)` | `0,0 °` | 다름 (소수점 `.`→`,`, `°` 앞 공백 있음) | step2_coord_scale_rot_x6x8.png |
| qgis step 3 | `Distance (10,000000)` | `10,000000` | 같음 | step3_distance_x4.png, step3_distance_sep_x8.png |
| qgis step 3 | `Distance (10.000000)` | `10,000000` | 다름 (소수점 `.`→`,`) | step3_distance_x4.png, step3_distance_sep_x8.png |
| qgis step 3 | `Miter limit (2.000000)` | `2,000000` | 다름 (소수점 `.`→`,`) | step3_miter_x4.png, step3_miter_sep_x8.png |
| qgis step 3 | `Coordinate 1026658, 6236015` | `1028658, 6236015` | 다름 (네 번째 자리 `6`→`8`) | step3_statusbar_x4.png, step3_coord_scale_rot_x6x8.png, step3_coordinate_x10.png |
| qgis step 3 | `Scale 1:240882` | `1:240882` | 같음 | step3_coord_scale_rot_x6x8.png |
| qgis step 3 | `Rotation 0.0°` | `0,0 °` | 다름 (소수점 `.`→`,`, `°` 앞 공백 있음) | step3_coord_scale_rot_x6x8.png |
| qgis step 3 | `Segments (5)` | `5` | 같음 | step3_segments_x4.png |
| qgis step 4 | `10,000000` | `10,000000` | 같음 | step4_distance_x4.png |
| qgis step 4 | `2,000000` | `2,000000` | 같음 | step4_miter_x4.png |
| qgis step 4 | `1044336, 6233594` | `1044336, 6233594` | 같음 | step4_statusbar_x4.png, step4_coord_scale_rot_x6x8.png |
| qgis step 4 | `1:240882` | `1:240882` | 같음 | step4_coord_scale_rot_x6x8.png |
| qgis step 5 | `50.000000` | `50,000000` | 다름 (소수점 `.`→`,`) | step5_distance_x4.png, step5_distance_sep_x8.png |
| qgis step 5 | `2.000000` | `2,000000` | 다름 (소수점 `.`→`,`) | step5_miter_x4.png |
| qgis step 5 | `1044846, 6212179` | `1044846, 6212179` | 같음 | step5_statusbar_x4.png, step5_coord_scale_rot_x6x8.png |
| qgis step 5 | `1:240882` | `1:240882` | 같음 | step5_coord_scale_rot_x6x8.png |
| qgis step 6 | `Distance (50.000000)` | `50,000000` | 다름 (소수점 `.`→`,`) | step6_distance_x4.png, step6_distance_sep_x8.png |
| qgis step 6 | `Miter limit (2.000000)` | `2,000000` | 다름 (소수점 `.`→`,`) | step6_miter_x4.png |
| qgis step 6 | `Coordinate (1028212, 6215621)` | `1028212, 6215621` | 같음 | step6_statusbar_x4.png, step6_coord_scale_rot_x6x8.png |
| qgis step 6 | `Scale (1:240882)` | `1:240882` | 같음 | step6_coord_scale_rot_x6x8.png |
| qgis step 6 | `Rotation (0.0 °)` | `0,0 °` | 다름 (소수점 `.`→`,`) | step6_coord_scale_rot_x6x8.png |
| qgis step 7 | `Coordinate (1055235, 6207527)` | `1055235, 6207527` | 같음 | step7_statusbar_x4.png, step7_coord_scale_rot_x6x8.png |
| qgis step 7 | `Scale (1:240882)` | `1:240882` | 같음 | step7_coord_scale_rot_x6x8.png |
| qgis step 7 | `Rotation (0.0 °)` | `0,0 °` | 다름 (소수점 `.`→`,`) | step7_coord_scale_rot_x6x8.png |
| attribute step 3 | `Attribute Name (Energy [-28, +28])` | `Energy [-28,+28]` | 다름 (쉼표 뒤 공백 없음) | attr_step3_attribute_name_x4.png, attr_step3_attribute_name_bracket_x8.png, attr_step3_list_entry_x8.png |

참고: 좌표·축척·회전 값은 8개 스텝 모두 상태 표시줄에 보이며, Segments 칸은 step 3~6 모두 `5`로 표시된다(GT에 Segments 문자열이 있는 스텝은 step 3뿐). "화면에 없음"에 해당하는 항목은 없었다.

## 다른 항목 정리 (GT 형식 기준 수정안)

총 **14건** 다름 (33건 중), 같음 19건, 화면에 없음 0건.

| # | 스텝 | 현재 GT | 화면 기준 수정안 | 유형 |
|---|---|---|---|---|
| 1 | qgis step 0 | `Rotation (0.0 °)` | `Rotation (0,0 °)` | 소수점 표기 |
| 2 | qgis step 1 | `Rotation (0.0 °)` | `Rotation (0,0 °)` | 소수점 표기 |
| 3 | qgis step 2 | `Rotation (0.0°)` | `Rotation (0,0 °)` | 소수점 표기 + 공백 |
| 4 | qgis step 3 | `Distance (10.000000)` | `Distance (10,000000)` (이미 있는 `Distance (10,000000)`과 중복됨) | 소수점 표기 |
| 5 | qgis step 3 | `Miter limit (2.000000)` | `Miter limit (2,000000)` | 소수점 표기 |
| 6 | qgis step 3 | `Coordinate 1026658, 6236015` | `Coordinate 1028658, 6236015` | **숫자 자체 오기** (6→8) |
| 7 | qgis step 3 | `Rotation 0.0°` | `Rotation 0,0 °` | 소수점 표기 + 공백 |
| 8 | qgis step 5 | `50.000000` | `50,000000` | 소수점 표기 |
| 9 | qgis step 5 | `2.000000` | `2,000000` | 소수점 표기 |
| 10 | qgis step 6 | `Distance (50.000000)` | `Distance (50,000000)` | 소수점 표기 |
| 11 | qgis step 6 | `Miter limit (2.000000)` | `Miter limit (2,000000)` | 소수점 표기 |
| 12 | qgis step 6 | `Rotation (0.0 °)` | `Rotation (0,0 °)` | 소수점 표기 |
| 13 | qgis step 7 | `Rotation (0.0 °)` | `Rotation (0,0 °)` | 소수점 표기 |
| 14 | attribute step 3 | `Attribute Name (Energy [-28, +28])` | `Attribute Name (Energy [-28,+28])` | 쉼표 뒤 공백 |

유형별: 소수점 `.`→`,` 12건(그중 2건은 `°` 앞 공백 누락 동반), 숫자 오기 1건(step 3 좌표), 공백 1건(attribute name). 삭제·중복 처리 여부는 이 문서에서 판단하지 않는다.
