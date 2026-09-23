# Study 3 표본 오독률 — 규칙 4 (2026-09-23)

표본: horizon_2dviewer step 1·4, rule_classification step 4·8, reclassify_raster step 3·7. 각 스텝의 초안 `visible_elements` 전 항목을 확대 크롭과 대조했다.

## 판정 기준
오독으로 센 것: (a) 화면에 없는 문자열(환각), (b) 철자·숫자·구두점이 화면 원문과 다른 항목, (c) 화면 상태와 다른 `(checked)`류 표기. 
오독으로 세지 않은 것: (d) "라벨 (값)" 묶음처럼 열거 관례에 따른 표기 차이, (e) QGIS 소수점 글리프(마침표/쉼표 구분 불가, 보류 H1), (f) 같은 요소의 중복, (g) 누락(추가는 초안 항목의 오독이 아님). 
초안 `Cross-line: (0)`·`Step: (0)`의 콜론은 (b)로 세되(엄격 기준) 형식성 오독으로 별도 표시했다.

## 결과

| 시나리오 / step | 초안 항목 수 | 오독 수 | 오독 항목 | 스텝 오독률 |
|---|---|---|---|---|
| opendtect__horizon_2dviewer__01 s1 | 64 | 4 | `Cross-line: (0)`(콜론 없음, 형식), `Step: (0)`(형식), `Scene 1 (checked)`(체크박스 없음), `SEC`(화면에 없음; SEG-Y) | 6.25% |
| opendtect__horizon_2dviewer__01 s4 | 70 | 0 | — | 0.00% |
| qgis__rule_classification__01 s4 | 72 | 1 | `Scale range [checked]`(실제 unchecked) | 1.39% |
| qgis__rule_classification__01 s8 | 71 | 2 | `*Untitled Project - QGIS`(em dash), `Swellendam [checked]`(화면은 `Swellendam ...`) | 2.82% |
| qgis__reclassify_raster__01 s3 | 54 | 0 | — | 0.00% |
| qgis__reclassify_raster__01 s7 | 66 | 0 | — | 0.00% |
| **합계(풀링)** | **397** | **7** | | **1.76%** |

- 형식성 오독(콜론 2건) 제외 시: 5 / 397 = **1.26%**.
- 어느 기준으로도 5% 미만 → 규칙 4의 중단 조건에 해당하지 않아 `proposed/`를 작성했다.
- 스텝별로는 O s1이 6.25%로 단독으로는 5%를 넘지만, 규칙 4는 6장 합산 비율을 기준으로 한다. 참고로 O s1의 오독 4건 중 2건은 형식(콜론), 1건은 상태 표기, 1건(SEC)만 환각이다.

## 표본 외 스텝에서 발견된 오독(참고, 비율 계산에 포함하지 않음)
- O s3: 상태줄 `Inl/Crl: 5750, SP: 551`(화면 `TrcNr … SP: 991`), `[free mem] 50.5/127.6 GB`(화면 98.9/127.8), `Scene 1 (checked)`, `FaultStickSet (unchecked)`, `PointSet (unchecked)`, `20021203-2-03_0008`(겹쳐서 판독 불가한 자리). 
- O s5: `ltStickSet`(u까지 보임), `20021203-2-03_0002`.
- Q s2: `'landuse' = '…'` 11건(큰따옴표). Q s6·s8, R s6: 제목 하이픈(em dash). Q s6/s0: `EPSG (4326)`/`EPSG (EPSG:4326)` 표기. Q s7: `Swellendam`, `'residential'...` 공백. Q s9: 좌표 `8626`→`8826`. R s8: `0.0°` 공백.
- 검수한 25장의 초안 항목은 총 1,476개이고, 이 중 화면과 다른 것으로 판정해 고치거나 지운 항목은 36개(2.4%; 수정 31 + 잘못된 상태 표기 삭제 3 + 겹침으로 판독 불가한 라벨 삭제 2)다. 그 밖의 삭제 16건은 같은 요소의 중복 정리, 추가 12건은 누락 보완이며 오독 집계와 무관하다.

## 크롭 근거
`crops/comp_o_s1.png`, `crops/opendtect__horizon_2dviewer__01__s1__top.png`, `…s1__axes.png`, `…s1__status.png`; `crops/opendtect__horizon_2dviewer__01__s4__*.png`; `crops/comp_q_tabs_editrule.png`, `comp_q_s3_s8_tables.png`, `comp_q_bottoms.png`, `comp_q_rows_8x.png`, `comp_qgis_status.png`, `comp_qgis_titles.png`; `crops/comp_r_dialog_s3_s4.png`, `comp_r_bottoms.png`, `comp_r_toolbox.png`, `comp_r_layers.png`; `crops/qgis__reclassify_raster__01__s7__styling.png`, `…s7__layers_tall.png`, `…s7__layers_low.png`.
