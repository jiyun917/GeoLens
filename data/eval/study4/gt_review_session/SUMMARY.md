# SUMMARY.md — Study 4 GT 외부 검수 결과 (2026-09-28)

범위: `data/eval/study4/gt_review_session/` 안의 24장 스크린샷과 GT 초안 3개. RULES.md 규칙 1~5 적용. 파이프라인·벤치 미실행, git 미사용, 폴더 밖 파일 미열람.

## 1. 표본 오독률 (규칙 4)
6장(spectral_decomp 1·5, custom_projection 4·7, aspect_north 1·3) 449항목 중 오독 6건 = **1.34 %** (공백만 다른 2건 제외 시 0.89 %) → 5 % 미만, 반영 진행. 세부는 `sample_check.md`.

## 2. 전수 검수 결과 (visible_elements 항목 수 기준)

| 시나리오 | 검수 항목 | 삭제 | 수정 | 추가 | 결과 항목 |
|---|---:|---:|---:|---:|---:|
| opendtect__spectral_decomp__01 (9 step) | 526 | 0 | 9 | 15 | 541 |
| qgis__custom_projection__01 (9 step) | 464 | 1 | 12 | 18 | 481 |
| qgis__aspect_north__01 (6 step) | 508 | 0 | 11 | 3 | 511 |
| **합계** | **1498** | **1** | **32** | **36** | **1533** |

수정 32건의 내역: 문자 오독 정정(소수점 쉼표→마침표 4, `°` 앞 공백 5, 창 제목 하이픈→em dash 4, 경로 밑줄 누락 2, `SEC-Y`→`SEG-Y`, `v7.0.9`→`V7.0.9`, `->`→`-->`, 좌표 숫자 2, `aspect north`→`aspect_north`, `Scene 1 (checked)`→`Scene 1`), 잘린 항목 표기 정리(합성 `...` 제거 5, 잘린 Scale 값 1), 형식 정리(표 셀 분리·따옴표 오독 정정 1, WKT 줄 단위 분리·괄호 오독 정정 1, 안내문 둘째 줄 완성 2, `Canvas & Legend` 통일 1).
추가 36건: `SEG-Y`(6), `Attribute Set 3D (icon)`(9, 매뉴얼 명명 아이콘), `Add new CRS (icon)`(4), `new CRS`(1), WKT 보이는 줄(13줄 중 기존 항목 대체분 제외 12), `Cancel`(3). 삭제 1건: F s0 `oceans (checked)`(중복).
data_state 정정 6건(E s1·s2·s3·s8, F s8, G s3): 경로 밑줄, 가림 사실, `화면상 확인 불가, 세션 이력 기준` 문구 3곳, F s8 좌표/Scale 표시. `current_dialog`·`current_action`은 전부 화면과 일치해 변경 없음.

## 3. 주요 발견
- **QGIS 소수점은 마침표**(`0.0 °`, `-6.8°, 176.6°`). 확대 이미지에서는 쉼표처럼 보이지만 픽셀 글리프가 문장 마침표와 동일하고 구분 쉼표(꼬리 있음)와 다름(`crops/decimal_mark_composite.png`). RULES.md 예시 `0,0 °`와 어긋나므로 확인 요청(GT_hold_list.md B-1).
- OpendTect 경로 힌트는 `Demo_0_--__FS4.hor`/`Demo_1_--__MFS4.hor`(밑줄 2개). F s8 좌표는 `32014073`(초안 82014073), Scale 필드는 `:157344704`만 보임(선행 `1` 잘림). G s5 좌표는 `1051440`(초안 1051441), 레이어 이름은 `aspect_north`.
- custom_projection s4의 표 행에 초안이 없는 따옴표(`"DATUM"[`, `"ELLIPSOID"[`)가 들어 있었고 Parameters 상자 텍스트에서 닫는 괄호 하나가 빠져 있었음(`ID["EPSG",8807]]],`).
- capture_instructions와 화면의 차이 11건은 `GT_change_list.md` 마지막 표에 기록(수정하지 않음): E 대화상자 제목(Select Horizons/Positions), E s4 Input Data 자동 채움, F s4 METHOD 줄 미표시, F s7 `User-defined`, G 라벨 `Input layers`·`Expression is valid` 없음 등.

## 4. 보류 (`GT_hold_list.md`)
규칙 3 필드 6건(F s6 패턴 `User Defined` vs 화면 `User-defined`, G s2 키워드 `Reference layer` vs 화면 `Input layers`, G goal 서술, E s1 `Select ...` 표기 등 — 수정하지 않음), 판단 보류 13건(소수점 문자 확인, `...`/`…` 문자, 아이콘 글리프 항목 `?`/`ε`/`+`/`-`, 공백 2개 가능성, 가려지거나 잘린 라벨 표기, `Attribute Set 3D (icon)` 이름, `aspect_north` 판정 근거, `oceans (checked)` 삭제 등).

## 5. 산출물
- `proposed/opendtect__spectral_decomp__01.json`, `proposed/qgis__custom_projection__01.json`, `proposed/qgis__aspect_north__01.json` — GT 필드(visible_elements, data_state)만 변경, 키 순서·indent 2·ensure_ascii=False 유지, 규칙 3 필드 불변(스크립트 검증).
- `GT_change_list.md`, `GT_hold_list.md`, `sample_check.md`, `SUMMARY.md`(파일 쓰기 도구가 이름을 거부해 Python으로 저장).
- `crops/` — 검수에 사용한 확대 크롭(시나리오별 폴더, `full/` 반크기 전체 화면, `montage/`, `decimal_mark_composite.png`).
