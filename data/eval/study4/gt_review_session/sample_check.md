# sample_check.md — 표본 오독률 (RULES.md 규칙 4)

검수일 2026-09-28. 표본 6장: spectral_decomp step 1·5, custom_projection step 4·7, aspect_north step 1·3.
방법: 초안 `scenarios/*.json`의 `visual_state_gt.visible_elements` 전 항목을 스크린샷과 대조. 작은 글자는 PIL로 3~16배 확대한 크롭(`crops/<scenario>/s<N>_*.png`)으로 확인했고, 마침표/쉼표·밑줄·대시처럼 확대해도 애매한 글리프는 픽셀 열(row) 맵을 직접 출력해 판정했다.

오독(misread) 정의: 초안 문자열이 화면 원문과 문자 단위로 다른 경우(철자·괄호·숫자·구두점·공백·대시 문자). 목록에 없는 라벨(누락)·표기 형식 차이(셀 병합, 여러 줄 연결, 앱이 자른 라벨의 마지막 글자 처리)는 오독으로 세지 않고 별도 표기.

## 결과

| 표본 | 항목 수 | 오독 | 오독률 | 오독 내용 |
|---|---:|---:|---:|---|
| opendtect__spectral_decomp__01 step 1 | 62 | 1 | 1.6 % | `...Demo_2023\Surfaces\Demo_0_--_FS4.hor` → 화면 `...Demo_2023\Surfaces\Demo_0_--__FS4.hor` (밑줄 하나 누락; y=659 밑줄 픽셀 런이 7·7·14 px → 세 번째는 밑줄 2개) |
| opendtect__spectral_decomp__01 step 5 | 64 | 0 | 0.0 % | — |
| qgis__custom_projection__01 step 4 | 63 | 2 | 3.2 % | (1) 표 행 `…BASEGEOGCRS["unknown","DATUM"["unknown","ELLIPSOID"["unknown",…` → 화면 `…BASEGEOGCRS["unknown",DATUM["unknown",ELLIPSOID["unknown",…` (DATUM·ELLIPSOID 주위의 따옴표는 화면에 없음) (2) Parameters 상자 `ID["EPSG",8807]],` → 화면 `ID["EPSG",8807]]],` (닫는 괄호 하나 누락) |
| qgis__custom_projection__01 step 7 | 67 | 0 | 0.0 % | — |
| qgis__aspect_north__01 step 1 | 95 | 1 | 1.1 % | `0.0°` → 화면 `0.0 °` (° 앞 공백 누락; 공백 폭 5 px) |
| qgis__aspect_north__01 step 3 | 98 | 2 | 2.0 % | (1) `*Untitled Project - QGIS` → 화면 `*Untitled Project — QGIS` (대시 런 13 px = em dash; 하이픈은 4~6 px) (2) `0.0°` → `0.0 °` |
| **합계** | **449** | **6** | **1.34 %** | 공백만 다른 2건을 제외한 엄격-비공백 기준 4/449 = 0.89 % |

→ 5 % 미만이므로 규칙 4에 따라 반영을 진행했다(`proposed/` 생성).

## 표본에서 오독으로 세지 않은 차이 (기록)

- custom_projection step 4: 안내문이 두 줄로 줄바꿈되어 있는데 초안은 첫 줄(`…for specifying a`)만 적음 → 둘째 줄 `CRS.`까지 완성(누락). 표 셀 두 개(`Van der Gri...` / `PROJCRS[…`)를 한 항목으로 병합 → 분리(형식). Parameters 상자의 보이는 15줄을 한 항목으로 연결 → 줄 단위 13항목(중복 2줄 제거)으로 분리(형식). `Canvas & Legen`은 패널 가장자리에서 'd'가 반쯤 잘린 라벨의 문자 그대로 읽기이며 s1~s3의 `Canvas & Legend`와 통일(형식).
- spectral_decomp step 1: `Demo 6 --> FS8 [unchecked]`는 목록 맨 아래 행이 절반만 보임(잘린 채 유지). `Demo 3 --> Top Foresets`는 '3'과 '-->' 사이 간격이 10 px로 다른 행(5~7 px)보다 넓어 공백 2개일 가능성이 있으나 판정 보류(GT_hold_list.md).

## 판정 근거 (확대해도 애매했던 글리프)

1. **QGIS 소수점 = 마침표.** 상태 표시줄 `Rotation`·`Coordinate`의 소수점 글리프는 1×2 px 점(기준선 행과 그 아래 행)으로, 같은 UI 글꼴의 문장 마침표(`here.` x=1045,y=180–181 / `CRS.` x=626,y=194–195)와 동일하다. 반면 좌표 구분 쉼표(`-6.8°, 176.6°`의 `, `)는 3행에 걸쳐 왼쪽 아래로 꼬리가 있다(F0 x=1194–1195,y=1021–1023; F4 y=1029–1031). 16배 최근접 확대 비교: `crops/decimal_mark_composite.png`. 따라서 초안의 `0,0 °`, `-6,8°, 176,6°`, `0,0°`는 오독이고 `0.0 °`, `-6.8°, 176.6°`가 화면 원문이다(초안이 같은 글리프를 `0.093473`에서는 마침표로 읽은 것과도 일치). RULES.md 규칙 1의 예시 `0,0 °`와 다르므로 GT_hold_list.md에 확인 요청으로 남김.
2. **em dash.** QGIS 창 제목 `*Untitled Project — QGIS`의 대시는 y=12 행에서 13 px 연속 런(x 114–126); OpendTect 제목 `2023 - [Scene 1]`의 하이픈은 4 px, `Raster Analysis - Raster Calculator`의 하이픈은 6 px. custom_projection 초안과 aspect_north step 0·1은 이미 `—`로 적혀 있다.
3. **밑줄 수.** OpendTect 경로 힌트의 밑줄은 y=659 한 행에 그려지며 런 길이 7 px(`_`)·14~15 px(`__`)로 구분된다(step 1: 7,7,14 / step 2: 7,7,15). 호라이즌 이름 `Demo 0 --> FS4`의 공백·`>`가 각각 `_`로 바뀐 파일명 `Demo_0_--__FS4.hor`와 일치.
4. **`aspect_north`(step 5, 표본 외).** 레이어 이름 `aspect`와 `north` 사이 간격은 6 px. 같은 글꼴에서 밑줄 `_`가 만드는 간격은 6~9 px(`raster_analysis/aspect_north` 7·7, `Sphere_Van_der_Grinten_I` 6·9·6·8), 공백은 4~5 px. 현재 레이어 밑줄(y=187)이 `_` 글리프 위치와 겹쳐 눈으로는 구분되지 않는다.
5. **F step 8 상태 표시줄.** 좌표 첫 자리는 `3`(x 1116–1120, y 1014–1021의 3자 형태) → `32014073, -11191302`. Scale 필드는 `:157344704`만 보이고 `1:`의 `1`은 필드 왼쪽에서 잘려 있다(`crops/qgis__custom_projection__01/s8_scale_nn.png`).
