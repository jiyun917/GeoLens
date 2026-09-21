# 표본 오독률 (규칙 4) — 2026-09-21 외부 검수

대상 4장: horizon_autotrack step 1·4, fault_sticks step 2·7. 초안 `scenarios/*.json`의 `visible_elements` 전 항목을 스크린샷(및 `crops/` 3배 확대 크롭)과 대조했다.

**오독의 정의(이 검수에서 적용)**: 항목의 문자 내용이 화면 어디에도 없는 경우(환각·글자 오인). 화면 원문과 문자 내용은 같지만 괄호·주석·띄어쓰기 표기만 다른 항목(예: `In-line (130)` → 화면은 `In-line 130`, `Select...` → 화면은 `Select ...`, `WVA [checked]`)은 **표기 수정**으로 분류하고 오독에 넣지 않았다. 텍스트가 없는 아이콘을 기호로 옮긴 항목(`▷`)은 별도 열에 표시했다(엄격 계산 시 오독에 포함해도 5% 미만).

| 스크린샷 | 초안 항목 수 | 오독(화면에 없는 문자열) | 오독 건수 | 표기 수정 항목 | 아이콘→기호 항목 |
|---|---|---|---|---|---|
| horizon_autotrack step_1 | 58 | 없음 | 0 | `In-line (130)`, `Step (10)`, `Method (Seed Trace)` (3) | 없음 |
| horizon_autotrack step_4 | 67 | 없음 | 0 | `In-line (130)`, `Step (10)`, `Compare window (ms) (-40)`, `Correlation threshold (%) (60.0)`, `Data Display window (ms) (-48)`, `Nr Traces (5)` (6) | `▷` (1) |
| fault_sticks step_2 | 61 | 없음 | 0 | 없음 | 없음 |
| fault_sticks step_7 | 51 | 없음 | 0 | `Select...` (1) | 없음 |
| **합계** | **237** | | **0** | 10 | 1 |

- **표본 오독률: 0 / 237 = 0.0 %** (엄격 계산으로 `▷`를 오독에 포함해도 1 / 237 = 0.42 %). 5 % 기준 미만이므로 반영을 진행하고 `proposed/`를 작성했다.
- 표본 4장에서 **누락**(화면에 있으나 초안에 없는 라벨)은 별도로 3건 발견: hz step_1 `?`(도움말 버튼 글리프; 같은 창의 다른 스텝에는 열거됨), fs step_2 `1500`(Time 축 눈금, 단면에 일부 가려졌으나 판독 가능), hz step_4 매뉴얼 명명 아이콘 `Auto-Track (icon)`·`Retrack-All (icon)`. 누락은 오독률 분모·분자에 넣지 않았다(규칙 4는 오독만 계산).

## 표본 외 스텝에서 발견한 오독(참고)
표본 계산에는 포함하지 않았지만 전수 검수(규칙 1)에서 삭제·수정한 오독은 다음 4건이다: hz step_0 `N`, hz step_5 `N`(오리엔테이션 기즈모에 E·Z만 보임, N은 화면 안쪽 방향이라 표시되지 않음; `crops/opendtect__fault_sticks__01/gizmos_wide.png`, `crops/opendtect__horizon_autotrack__01/step_5_gizmo6x.png`), hz step_3 `F`(기즈모의 한 글자 `E`를 E와 F 둘로 읽음), fs step_8 `Tr`(단면에 가려진 Time 축 라벨, 보이는 글자는 `Ti`; `crops/opendtect__fault_sticks__01/step_8_misc.png`). 16장 전체 초안 항목 927개 중 4건 = 0.43 %.

## 대조에 쓴 크롭
- `crops/<scenario>/step_N_sheetA.png` : 제목표시줄·메뉴·아이콘 툴바·위치 툴바·(하단 편집 툴바)·상태 표시줄, 3배
- `crops/<scenario>/step_N_sheetB.png` : 트리 패널 상·하 + 오리엔테이션 기즈모, 3배
- `crops/<scenario>/step_N_dialog*.png` : 다이얼로그 제목·탭·필드, 3배 (fs step_2 는 `step_2_dialogsheet.png`, 6–8배 포함)
- `crops/<scenario>/step_N_scene*.png|jpg` : 3D 장면 축 라벨 (fs 0–5 는 카메라가 동일하여 `step_2_scene.png`·`step_0/4/5_scene1x.jpg`·`timeaxis_*.png` 로 대조)
