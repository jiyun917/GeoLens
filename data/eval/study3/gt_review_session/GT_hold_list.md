# Study 3 GT 보류 목록 — 외부 검수 (2026-09-23)

규칙에 없는 판단이 필요하거나(RULES.md 7행), 규칙 3 필드(패턴·키워드·대안·goal·initial_state 등)가 화면과 어긋나는 항목. 아무것도 수정하지 않았다. 각 항목에 스터디 책임자가 정할 것을 적었다.

## H1. QGIS 소수점/천단위 구분 글리프 — 마침표인지 쉼표인지 화면에서 구분 불가 (결정 필요)
- 현상: QGIS 패널·상태줄 글꼴(굴림 계열)에서 ASCII 마침표가 쉼표처럼 렌더링된다. 근거: QGIS 소스 문자열이 마침표인 표 헤더 `Min. Scale`/`Max. Scale`이 화면에서는 `Min, Scale`처럼 보이고(`crops/comp_q_misc_8x.png`, `crops/glyph_composite.png`), 좌표 필드의 x·y 구분 쉼표(진짜 쉼표)와 소수점 글리프가 같은 모양이다. 반면 다른 글꼴을 쓰는 툴박스 항목 `r.slope.aspect`의 마침표는 점으로 보인다. 즉 화면 픽셀만으로는 `0.093473`/`0,093473`, `1,548`/`1.548`(천단위 쉼표일 가능성 큼), `0.0 °`/`0,0 °`, `1.00`/`1,00`, `-33.8677°`/`-33,8677°`, `reclassified.tif`를 구분할 수 없다.
- 영향 항목(초안 표기 그대로 둠, 오독으로 세지 않음): Q s0–s9 Coordinate 값·Rotation 값(`0.0 °` 8장, `0,0 °` s9), R s0–s8 `0.093473`, `1,548`(s0–s6) vs `1.548`(s7–s8), R s6 `Rotation (0,0 °)` vs 나머지 `0.0 °`, R s7–s8 `Gamma 1.00`, R s5 `C:/GeoLensData/reclassified.tif`, Q s2 이후 `Min. Scale`/`Max. Scale`.
- 결정할 것: (a) 자료의 실제 문자열 기준(마침표; 한국어 로캘도 소수점은 마침표)으로 통일할지, (b) RULES 1의 "QGIS는 소수점에 쉼표를 쓸 수 있다: `10,000000`" 주석대로 쉼표로 통일할지, (c) 초안 그대로 둘지. 어느 쪽이든 `1,548`/`1.548`과 `0.0 °`/`0,0 °`의 스텝 간 불일치는 정리하는 편이 좋다. 검수자는 (a)를 권한다(`Min. Scale` 근거).

## H2. 규칙 3 필드가 화면에 없는 이름을 참조 — opendtect__horizon_2dviewer__01
- s1 `expected_action_keywords` `Well correlation-Line`, 패턴 `(Well correlation|Load default data|OK)`: 화면 목록에 Well correlation-Line 없음(선택한 라인은 `19981104-1-04_0037`). 패턴은 `Load default data`/`OK` 대안으로 통과 가능.
- s2 `expected_action_keywords` `Seis`, 패턴 `\b(Seis|Display|2D Viewer|2D viewer)\b`: 화면 속성명은 `Seismic`. `\bSeis\b`는 `Seismic`에 매치되지 않으므로 키워드 `Seis`는 실제 화면 기준 응답을 놓칠 수 있음(`Display`/`2D Viewer` 대안으로는 통과).
- s8 `allowed_alternatives` 패턴에 `Well correlation`; `goal`에 "2D Line(Well correlation-Line)", "그 Seis 속성"; s1–s3 `capture_instructions`도 같은 이름 사용(변경 목록에 기록).
- 결정할 것: 키워드/goal을 화면 데이터명으로 바꿀지(사전등록 원칙과 충돌), 채점 시 대안 패턴으로 흡수할지.

## H3. qgis__reclassify_raster__01 s1→s2 전이가 화면상 무변화
- s1 `expected_action_text_pattern` `(aspect|Raster layer|래스터 레이어)`, 키워드 `aspect`, s2 `expected_workflow_node` `…_03_raster_layer_aspect`: Raster layer는 대화상자가 열리며 활성 레이어로 자동 채워졌고(s1 화면), s2는 s1과 동일 화면(상태줄 좌표만 다름). "aspect를 고르라"는 지시는 화면 기준으로는 이미 끝난 동작이다.
- 결정할 것: s1의 기대 행동을 "이미 aspect가 선택돼 있음을 확인하고 표(…)를 연다"로 볼지, s1/s2를 합칠지, 그대로 둘지(v3 QGIS s3/s4와 같은 상황).

## H4. qgis__reclassify_raster__01 s4·s5 경로
- s4 패턴에 `raster_analysis`, `goal`/`initial_state`/`must_be_true`에 `exercise_data/raster_analysis`: 실제 저장 경로는 `C:/GeoLensData/reclassified.tif`. 패턴은 `reclassified`로 통과. 기록만.

## H5. qgis__rule_classification__01 initial_state — AREA 필드
- `initial_state.description`/`must_be_true`의 "landuse has an AREA field(§3.3.3 계산 완료)"는 어느 스크린샷에서도 확인할 수 없다(속성 테이블 미표시). CAPTURE_NOTES와 같은 상태. 규칙 3 필드이므로 미수정.

## H6. OpendTect s3 상태줄 문자열의 판독 불확실 자리
- 제안값 `Line: 19981104-1-04_0037, TrcNr: 3798, SP: 991`은 2D Viewer 창에 윗반이 가려진 글자의 아랫반만 보고 읽은 것. `SP: 991`과 `TrcNr`는 확실하나 TrcNr 끝자리는 8/6 구분이 안 된다(`crops/opendtect__horizon_2dviewer__01__s3__status_tr.png`).
- 결정할 것: 제안값 유지 / 판독 가능한 앞부분 `Line: 19981104-1-04_0037`까지만 남김 / 항목 삭제.

## H7. 겹친 축 라벨 표기 관례
- OpendTect 2D viewer 상·하 축에 두 교차선 이름이 겹쳐 `20021203-2-03_00??`와 `???21203-2-02_0010`이 된다. s4 초안의 `20021203-2-03_00...21203-2-02_0010`으로 s3·s5를 통일했다. 다른 관례(예: 두 이름을 각각 잘린 채 기록)를 원하면 세 스텝을 함께 바꿔야 한다.

## H8. qgis__rule_classification__01 s1–s8 Layer Properties 탭 목록 맨 아래 행
- `Legend` 아래에 윗반만 보이는 행(`QGIS Server`로 추정)이 있다. 규칙의 "잘린 항목은 잘린 채"는 목록에 있는 항목에 대한 것이고 반쯤 가려진 행의 추가 여부는 규칙에 없어 추가하지 않았다.

## H9. `Duplicate Count` 헤더
- Q s2–s8 규칙 표의 마지막 헤더는 오른쪽 경계에서 `t`가 절반 잘린다. 글자가 식별되므로 `Duplicate Count` 유지. 엄격히 잘린 원문(`Duplicate Coun`)을 원하면 7개 스텝을 바꿔야 한다.

## H10. 상태 표기 관례
- 초안이 `(checked)`/`[checked]`/`(unchecked)`/`[selected]`를 시나리오·스텝마다 다르게 쓴다. 화면 사실이 아니어서 손대지 않았다. OpendTect s3에서 같은 요소의 plain/annotated 중복은 annotated 쪽을 남겼고, 화면에 두 번째 요소가 있는 경우(`Cross-line` 축 라벨, `19981104-1-04_0037` scene 라벨, viewer 트리의 `2D Horizon`/`FaultStickSet`/`PointSet`)만 plain을 함께 남겼다(GT_change_list 참조). 다른 관례를 원하면 알려 달라.

## H11. OpendTect s4에 추가한 `?`·`▷`
- Horizon Tracking Settings 창의 Help(`?`)·재생(`▷`) 버튼 글리프. s5 초안에는 vision이 넣었고 s4에는 없어 통일 목적으로 추가했다. 아이콘으로 보고 둘 다 빼는 것도 가능(그 경우 s5에서도 제거).

## H12. OpendTect s6·s7·s8
- 검수 제외(재캡처 대기). 초안 그대로. 참고: s7 초안은 `Cross-line 0`/`Step 0`(괄호 없음) 표기를 쓰고, s6 상태줄 `(212/493 (610573, …` 은 괄호가 하나 더 붙어 있어 재캡처 후 검수 시 확인 필요.

## H13. QGIS `Symbol Levels...`
- 화면 글리프는 `Symbol Levels···`(가운데 점 세 개). 초안 `Symbol Levels...` 유지. 마침표/쉼표 문제(H1)와 같은 글꼴 문제.
