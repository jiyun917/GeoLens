# Study 2 캡처 지시서 (사용자 작업, OpendTect 7.0 + F3 Demo)

작성 2026-09-21. 이 문서와 `scenarios_draft/*.json`, `data/workflows/horizon_autotrack_142a.json`, `fault_sticks_143b.json`은 **매뉴얼 본문만 보고** 스크린샷을 찍기 전에 작성·커밋했다(커밋 해시는 study 2 사전등록에 기록). 캡처는 매뉴얼 §1.4.2a·§1.4.3b의 순서를 따르되, 워크플로우 JSON을 보고 화면을 맞추지 않는다.

## 공통 규칙
- OpendTect 7.0, 영어 UI, F3 Demo survey. 이전 캡처와 같은 창 크기(약 1922×1041, 전체 OpendTect 창), JPEG.
- 각 장은 "그 스텝의 동작이 **끝난 뒤** 화면"이다(reached state). 다음 동작은 아직 하지 않은 상태여야 한다.
- 우클릭 메뉴·툴팁·마우스 커서 위 텍스트가 찍히지 않게 메뉴를 닫고 캡처한다(커서 자체는 무관). 단, 지시서에 "메뉴 열린 상태"라고 쓴 장은 없다.
- 파일명: `data/eval/screenshots/<scenario_id>/step_N.jpg` (N은 0부터). 한 장이라도 조건과 다르면 그 스텝만 다시 찍는다.
- 캡처 뒤 각 장이 아래 "화면 상태" 조건과 "보이면 안 되는 것"에 맞는지 스스로 확인하고, 다른 점이 있으면 `CAPTURE_NOTES.md`에 스텝별로 적는다(예: "s3: Steering 옵션이 없음(라이선스)").
- 캡처 중에는 모델 응답·벤치 결과를 보지 않는다. 캡처가 끝나면 GT(visible_elements)는 열거 스크립트가 만들고 외부 검토로 확정한다.

## 시나리오 A — `opendtect__horizon_autotrack__01` (매뉴얼 §1.4.2a, 7장)

준비(초기 상태, 캡처 안 함): Survey > Pre-Load > Seismic… 으로 `4 Dip steered median filter` pre-load. 트리 Random Line 우클릭 > Add Default Data → 서베이 중앙 random line에 표시. 3D Horizon 항목은 비어 있어야 함.

| 파일 | 화면 상태(캡처 조건) | 직전에 한 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0.jpg | 메인 창. Random Line에 4 Dip steered median filter 표시. 3D Horizon 비어 있음. Tracking Settings 창 없음 | Add Default Data 확인만 | Horizon Tracking Settings 창, <New Horizon 1>, 열린 메뉴 |
| step_1.jpg | `Horizon Tracking Settings - <New Horizon 1>` 창, **Mode 탭**: Section Auto-track, Method = Seed Trace. 트리에 <New Horizon 1> | 3D Horizon 우클릭 > New > Auto and Manual Tracking, Mode 설정 | Event/Correlation 탭 활성, seed |
| step_2.jpg | 같은 창 **Event 탭**: Event type = Peak. 나머지 기본값. "Picked on: 4 Dip steered median filter" | Event 탭 클릭, Peak 선택 | Correlation 탭 활성, Use Correlation Yes |
| step_3.jpg | 같은 창 **Correlation 탭**: Use Correlation = Yes, Correlation threshold = 60.0 | Correlation 탭, Yes, 60 | seed, 추적 패치 |
| step_4.jpg | random line의 Peak 반사면에 **seed 1개** 찍힘, <New Horizon 1> 트리에서 활성, Settings 창 열린 채(Auto-Track 아이콘 보임) | 반사면 클릭 1회 | 추적 패치, 열린 메뉴 |
| step_5.jpg | Auto-Track 실행 후 **패치**가 random line/3D scene에 보임. 잠금 전 | Auto-Track 아이콘 클릭 | 열린 우클릭 메뉴, 두 번째 seed |
| step_6.jpg | 패치 우클릭 > Tracking > **Lock** 완료(메뉴 닫힘). 목표 도달 장면 | Lock | 열린 메뉴, Lock 뒤에 찍은 새 seed |

주의: step_3에서 Steering 옵션(DipSteer 탭, 매뉴얼 step 11)은 dip-steering 라이선스가 있을 때만 보인다. 있으면 No로 두고, 없으면 그대로 진행하고 노트에 적는다.

## 시나리오 B — `opendtect__fault_sticks__01` (매뉴얼 §1.4.3b, 9장)

준비(초기 상태, 캡처는 step_0으로): In-line 우클릭 > Add Default Data(4 Dip steered median filter). Position mode에서 inline을 110으로. View In-line. 우상단 녹색 사각형을 드래그해 단층 부위로 표시 영역 축소. FaultStickSet 항목은 비어 있어야 함.

| 파일 | 화면 상태(캡처 조건) | 직전에 한 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0.jpg | In-line 110, 4 Dip steered median filter, In-line view, 단층 부위 확대. FaultStickSet 비어 있음 | 초기 상태 준비 | <New FaultStickSet 1>, 열린 메뉴, Z-slice |
| step_1.jpg | 트리에 **<New FaultStickSet 1>**. 대화상자 없음 | FaultStickSet 우클릭 > New | Output selection 대화상자, FaultStickSet_01 |
| step_2.jpg | **Output selection** 대화상자: Output FaultStickSet 필드(비어 있거나 기본값), Select…, Replace in tree, OK/Cancel | <New FaultStickSet 1> 우클릭 > Save as… | 필드에 이미 FaultStickSet_01 입력됨 |
| step_3.jpg | 대화상자 닫힘, 트리 항목이 **FaultStickSet_01** | 이름 입력 후 OK | 대화상자, 열린 Display 하위 메뉴 |
| step_4.jpg | FaultStickSet_01 선택, Display > **Only at Sections** 켬, Position mode, Edit Sticks 아이콘 켬. **스틱 없음** | Only at Sections | 스틱, 열린 메뉴 |
| step_5.jpg | In-line 110에 **스틱 여러 개** 픽됨. 툴바 인라인 = 110 | 좌클릭+드래그로 스틱 픽 | 110이 아닌 인라인, Z-slice |
| step_6.jpg | 여러 인라인(110, 120, 130 …)에 스틱. **현재 인라인은 110이 아님**(예: 130) | Z/X 키로 이동하며 픽 | Z-slice, Similarity |
| step_7.jpg | **Z-slice 1500 ms**에 `9-1 Similarity on FEF seismic` 표시, View North(위에서 보기), 스틱 모두 **미선택(보라색)** | 빈 Z-slice 추가 → 1500 → View North → Stored attribute 9-1 Similarity | 녹색(선택된) 스틱, Fault_01A |
| step_8.jpg | 트리 Fault 아래 **Fault_01A**, 단층면이 scene에 보임. 대화상자 없음 | 스틱 선택 → Copy Selection to > Fault > Create Single New → Fault_01A → Go! | 두 번째 단층면, 열린 대화상자 |

## 캡처가 끝나면
1. 두 폴더(`data/eval/screenshots/opendtect__horizon_autotrack__01/`, `opendtect__fault_sticks__01/`)에 각각 7장·9장이 있는지 확인.
2. `CAPTURE_NOTES.md`에 매뉴얼과 달랐던 점(라이선스로 없는 옵션, 기본값 차이 등)을 스텝별로 적는다.
3. 알려 주면 이후는 제가 진행: GT 열거(gemini-2.5-pro, temperature 0) → 외부 검토 세션 → 사용자 승인 → no_rag 선정 실행(약 $1~2) → 사전등록 2 서명 → 확인 실행(약 $25~35).
