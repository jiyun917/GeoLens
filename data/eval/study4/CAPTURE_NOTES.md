# Study 4 캡처 노트 (2026-09-28, 사용자 캡처 / 채팅 검증; 세션 기록)

사용자가 24장(E 9, F 9, G 6)을 PNG로 캡처(창 캡처 1920×1032 또는 1922×1041). 재캡처 없음. 원본은 `originals_png/`, 벤치용 JPEG(quality 92)는 `data/eval/screenshots/<scenario_id>/step_N.jpg`(세션이 변환). 아래는 사용자가 적어 온 버전·데이터 차이이며, GT·signature 정정은 K1 절차(문자열만)와 GT 결정 로그(H-항목)로 처리한다.

## E — `opendtect__spectral_decomp__01` (OpendTect 7.0.9, F3 Demo 2023)
- step_1: 대화상자 제목 **'Select Horizons'**(지시서·워크플로우: 'Select Input Horizon(s)'); Area subselection 기본값 '100/300-750/1250 (463 samples)' 표시.
- step_2: 제목 **'Positions'**, 부제 'Specify Positions'(지시서: 'Position'/'Specify Position').
- step_3: OK(display) 뒤 **'Select RGB Attributes'** 창(Red/Green/Blue/Alpha)이 추가로 뜸 → 비운 채 OK로 통과, 미캡처. 트리 하위 레이어 = `<right-click>`×3(R/G/B) + `Z values`(지시서: "4개 속성 레이어").
- step_4: Input Data가 **'4 Dip steered median filter'로 자동 채워짐**(비울 수 없음), 기본 속성 종류 Similarity. 원본이 1920×1080 전체화면이라 작업표시줄 제거 후 1920×1032로 교체.
- step_0~2: 이전 세션의 트래킹 툴바가 남아 있음(GT 무관).
- step_8: Save on Close, 세트 이름 'Spectral Decomposition'(사용자 확인 필요 — GT는 창 닫힘·목표 도달만 봄).

## F — `qgis__custom_projection__01`
- 정정 없음. 대화상자 'Options — User Defined CRS'; step_2 새 행 이름 'new CRS'; Project Properties — CRS에서 **'User-defined'** 그룹, USER:100000.
- step_4: Parameters 칸이 WKT 끝부분으로 스크롤됨(METHOD 줄 미표시; 표 행에 PROJCRS 표시).

## G — `qgis__aspect_north__01` (QGIS 3.44)
- step_1: 제목 'Raster Analysis - Raster Calculator'(저작과 일치); **'Reference layer(s)' → 'Input layers'**('0 inputs selected'); Layers·Operators 패널은 ε 표현식 빌더 안; Output extent / cell size / CRS / Advanced Parameters 필드 추가.
- step_2: Expression `"aspect@1" <= 90 OR "aspect@1" >= 270`(따옴표 포함); 'Expression is valid' 문구 없음.
- step_3: **'1 input selected'**(단수).
- step_3→4 사이 Windows 'Save file' 대화상자 미캡처.
- step_4: Calculated = `C:/GeoLensData/raster_analysis/aspect_north.tif`.

## 처리 계획
- K1(문자열만, 워크플로우 스테이징): E 노드 02 dialog 'Select Horizons', 03 'Positions'/'Specify Positions', 04 키워드 `<right-click>`·`Z values`; G 노드 02·04 'Reference layer(s)' → 'Input layers', '1 inputs selected' → '1 input selected', 03 'Expression is valid' 제거. 매뉴얼 이름은 별칭으로 남긴다(모델은 매뉴얼 이름으로 답할 수 있음).
- GT(H-항목, 결정 로그): G s2 패턴에 'Input layer(s)' 추가(매뉴얼 'Reference layer'와 병기); E s3 시나리오 설명에 'Select RGB Attributes' 통과 사실 기재. 나머지 패턴·키워드 불변.
