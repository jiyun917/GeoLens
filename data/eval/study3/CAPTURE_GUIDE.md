# Study 3 캡처 지시서 (사용자 작업) — 총 28장

작성 2026-09-22. 워크플로우 3개와 시나리오 골격 3개(`scripts/study3_author.py`)는 **매뉴얼 본문만 보고** 캡처 전에 저작·커밋했다. 규칙은 study 2와 같다: 각 장은 그 스텝의 동작이 **끝난 뒤** 화면(다음 동작은 아직 안 한 상태), 우클릭 메뉴·툴팁은 닫고 캡처, 전체 앱 창, JPEG 또는 PNG(PNG면 제가 변환), 파일명 `data/eval/screenshots/<scenario_id>/step_N.jpg` (N은 0부터). 매뉴얼과 다른 점은 `data/eval/study3/CAPTURE_NOTES.md`에 스텝별로 적는다. 캡처 중 워크플로우 JSON을 보고 화면을 맞추지 않는다.

## 준비 (캡처 안 함)
- **QGIS Training Data**: `C:\Users\user\Downloads\QGIS-Training-Data-master\QGIS-Training-Data-master\exercise_data\` 를 쓴다.
- **B 준비**: 새 프로젝트에 `exercise_data/landuse.sqlite`의 landuse 레이어를 로드하고, 매뉴얼 §3.3.3대로 Field Calculator로 `AREA` 필드(`$area`, 실수)를 만들어 저장(편집 종료). 심볼로지는 Categorized(landuse 필드) 등 이전 분류 상태로 둔다(Rule-based가 아니면 무엇이든 됨).
- **D 준비**: `exercise_data/raster/SRTM/srtm_41_19.tif` 로드 → Raster › Raster terrain analysis › Aspect 로 `exercise_data/raster_analysis/aspect.tif` 생성(폴더가 없으면 만든다). Layers에 aspect가 표시된 상태로 시작. srtm은 지워도 되고 두어도 된다(노트에 적기).
- **C 준비**: OpendTect F3 Demo, 3D scene, 2D Line·2D Horizon 트리 항목이 비어 있는 상태.

## C — `opendtect__horizon_2dviewer__01` (매뉴얼 §1.4.2b, 9장)
| 파일 | 화면 상태 | 직전 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0 | 3D scene, 2D Line 비어 있음, 대화상자·2D viewer 없음 | (시작) | Select 2D Lines 대화상자, 2D Viewer |
| step_1 | **Select 2D Lines** 대화상자(목록에 Well correlation-Line, On OK 드롭다운), 아직 확정 전 | 2D Line 우클릭 > Add | 트리에 2D 라인, 2D Viewer |
| step_2 | 대화상자 닫힘, 트리 2D Line > Well correlation-Line > Seis, scene에 2D 라인 단면 | Well correlation-Line 선택 + On OK = Load default data + OK | 2D Viewer, 열린 메뉴 |
| step_3 | **2D Viewer - Line: Well correlation-Line** 창 열림(자체 트리, 2D Horizon 비어 있음) | Seis 우클릭 > Display > 2D Viewer | <New 2D Horizon>, Tracking Settings |
| step_4 | Horizon Tracking Settings 창(기본값: Section Auto-track, Adjacent Parent, Max, 80%) + 2D viewer 트리에 <New 2D Horizon>, **seed 없음** | 2D viewer 트리 2D Horizon 우클릭 > Track New | seed/horizon 선 |
| step_5 | 단면에 horizon 선(라인 전체 해석), <New 2D Horizon> 미저장 | Max 반사면에 seed 클릭(필요하면 여러 개) | Output selection 대화상자 |
| step_6 | **Output selection** 대화상자(Output 2D Horizon 필드 비어 있음) | <New 2D Horizon> 우클릭 > Save as | 이름 입력됨 |
| step_7 | 대화상자 닫힘, 2D viewer 트리에 저장 이름(예: 2D_Horizon), **2D viewer 아직 열림** | 이름 입력 + OK | 대화상자 |
| step_8 | 2D viewer 닫힘, 3D scene에 2D 라인 + horizon, 메인 트리 2D Horizon 아래 저장 이름 (목표) | 2D viewer 닫기 | 2D Viewer 창 |

## B — `qgis__rule_classification__01` (매뉴얼 §3.3.5, 10장)
| 파일 | 화면 상태 | 직전 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0 | 메인 창, landuse 로드(AREA 있음), 대화상자 없음 | (시작) | Layer Properties |
| step_1 | **Layer Properties - landuse**, Symbology 탭, 렌더러는 아직 Rule-based 아님 | landuse 속성 열기 + Symbology 탭 | Rule-based 선택됨 |
| step_2 | 렌더러 = **Rule-based**, 자동 변환된 규칙 여러 행, 선택 없음 | 드롭다운을 Rule-based로 | 빈 목록, Edit Rule |
| step_3 | 규칙 목록 **비어 있음** | 전체 선택 + Remove selected rules | 규칙 행, Edit Rule |
| step_4 | **Edit Rule** 대화상자, Label·Filter 비어 있음 | Add rule | 입력된 라벨 |
| step_5 | Symbology 목록에 규칙 1개(Swellendam city, "name" = 'Swellendam') | 규칙 1 입력 + OK | Edit Rule, 두 번째 규칙 |
| step_6 | 규칙 2개(+ Other residential) | 규칙 2 추가 | Edit Rule, 세 번째 규칙 |
| step_7 | 규칙 3개(+ Big non residential areas) | 규칙 3 추가 | Edit Rule, ELSE 규칙 |
| step_8 | 규칙 4개(마지막 Rule = ELSE), **아직 Apply 전**(뒤 지도는 이전 상태) | Else 규칙 추가 + Edit Rule OK | Edit Rule, 새 색으로 렌더된 지도 |
| step_9 | 지도에 4색 렌더링, Layers 범례에 4개 라벨(OK로 닫았거나 Apply 후 열린 채) (목표) | Apply/OK | 무관한 대화상자 |

색은 매뉴얼대로(진한 회청 / 연한 청회 / 중간 녹 / 연한 녹)면 되고 정확한 값은 자유. 규칙 1은 테두리 없음.

## D — `qgis__reclassify_raster__01` (매뉴얼 §7.3.10, 9장)
| 파일 | 화면 상태 | 직전 동작 | 보이면 안 되는 것 |
|---|---|---|---|
| step_0 | 메인 창, aspect 로드(Toolbox 열려 있어도 됨), Reclassify 대화상자 없음 | (시작) | Reclassify by table 대화상자 |
| step_1 | **Reclassify by Table** 대화상자, Raster layer 아직 aspect 아님(기본), 표 비어 있음 | Toolbox › Raster analysis › Reclassify by table | Fixed table 대화상자 |
| step_2 | Raster layer = **aspect**, Reclassification table = Fixed table (0x3) | aspect 선택 | Fixed table 대화상자 |
| step_3 | **Fixed table** 대화상자(Minimum/Maximum/Value), 행 없음 | Reclassification table의 … | 채워진 행 |
| step_4 | 대화상자로 복귀, **Fixed table (5x3)**, 출력은 아직 임시 파일 | Add Row ×5 + (0,45,1)(315,360,1)(45,135,2)(135,225,3)(225,315,4) + OK | Fixed table, reclassified.tif 경로 |
| step_5 | Reclassified raster = …/raster_analysis/**reclassified.tif**, 아직 Run 전 | … › Save to File | Layers의 reclassified |
| step_6 | 실행 완료, Layers에 **reclassified**(Singleband gray), 대화상자 닫힘 또는 Log 탭 | Run | Paletted 선택됨 |
| step_7 | **Layer Styling** 패널(reclassified), 렌더러 = Paletted/Unique values, 값 목록 **비어 있음** | Layer Styling 열고 렌더러 변경 | 값 1–4 목록 |
| step_8 | 값 1,2,3,4에 색 배정, 지도 4색 (목표) | Classify | 무관한 대화상자 |

## 끝나면
세 폴더에 9 + 10 + 9장이 있는지 확인하고 알려 주면, 이후는 제가 진행한다: GT 열거 → 외부 검토 → 승인 → preflight → no_rag 선정 실행(약 $1) → 개발 세트 + study 2 세트에서 R2·v5 검증 → 사전등록 3 서명 → 확인 실행(약 $35~45; Gemini 약 20,000원 추가 충전 필요 예상).
