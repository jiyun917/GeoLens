# Iteration-4 dev bench report

Benches: dev_iter4_v3_claude_r0.json, dev_iter4_v3_gemini_r0.json, dev_iter4_v3_gemini_r1.json, dev_iter4_v3_gpt_r0.json

## C. step accuracy per model (scenario-avg, mean over reps)

| model | reps | full_system | vanilla_vector | vanilla_budget | no_rag | full > vv | full > vb |
|---|---|---|---|---|---|---|---|
| gemini | 2 | 0.792 | 0.771 | 0.771 | 0.708 | ✓ | ✓ |
| claude | 1 | 0.875 | 0.875 | 0.875 | 0.875 | = | = |
| gpt | 1 | 0.833 | 0.833 | 0.667 | 0.750 | = | ✓ |

## C. full_system losses classified (routing / context / generation / wording)

| model | routing | context | generation | wording |
|---|---|---|---|---|
| gemini | 0 | 0 | 5 | 2 |
| claude | 0 | 0 | 3 | 0 |
| gpt | 0 | 0 | 1 | 1 |

| model | rep | scenario | step | class | routed to | response | vv | vb |
|---|---|---|---|---|---|---|---|---|
| claude | 0 | attribute_computation__01 | 1 | generation | seismic_attribute_03_select_type | `Input Data를 "4 Dip steered median filter"로 변경하기 위해 Input Data 드롭다운(현재 "Seismic_d` | ✗ | ✗ |
| claude | 0 | attribute_computation__01 | 2 | generation | seismic_attribute_04_configure | `Input Data 드롭다운(현재 "Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.` | ✗ | ✗ |
| claude | 0 | attribute_computation__01 | 3 | generation | seismic_attribute_04_configure | `Input Data 드롭다운(현재 "Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.` | ✗ | ✗ |
| gemini | 0 | attribute_computation__01 | 1 | generation | seismic_attribute_03_select_type | `Input Data 옆에 있는 Seismic_data 드롭다운 메뉴를 클릭하세요.` | ✗ | ✗ |
| gemini | 0 | attribute_computation__01 | 5 | generation | seismic_attribute_06_display | `Tree scene 1의 250을 마우스 오른쪽 버튼으로 클릭하세요.` | ✗ | ✓ |
| gemini | 0 | survey_setup__01 | 0 | wording | survey_setup_01_open_selection | `녹색 더하기 아이콘을 클릭하세요.` | ✗ | ✓ |
| gemini | 1 | 3d_visualization__01 | 3 | generation | d3_visualization_04_add_zslice | `Add Default Data를 클릭하세요.` | ✓ | ✗ |
| gemini | 1 | attribute_computation__01 | 1 | generation | seismic_attribute_03_select_type | `Input Data 드롭다운 메뉴에서 4 Dip steered median filter를 선택하세요.` | ✗ | ✗ |
| gemini | 1 | attribute_computation__01 | 5 | generation | seismic_attribute_06_display | `Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.` | ✓ | ✓ |
| gemini | 1 | survey_setup__01 | 0 | wording | survey_setup_01_open_selection | `초록색 플러스 아이콘을 클릭하세요.` | ✓ | ✓ |
| gpt | 0 | 3d_visualization__01 | 2 | generation | d3_visualization_01_main_window_ready | `Z-slice를 우클릭하고 'Add Data'를 선택하세요.` | ✗ | ✗ |
| gpt | 0 | survey_setup__01 | 0 | wording | survey_setup_01_open_selection | `새로운 설문 아이콘을 클릭하세요.` | ✓ | ✗ |

## A. goal-state block fired early (attribute s5/s6): full_system response

| model | rep | step | fired node | answered 완료? | step match | response |
|---|---|---|---|---|---|---|
| claude | 0 | 5 | seismic_attribute_06_display | no | ✓ | `Tree scene에서 **250** 항목을 우클릭하세요.` |
| claude | 0 | 6 | seismic_attribute_06_display | no | ✓ | `**OK** 버튼을 클릭하세요.` |
| gemini | 0 | 5 | seismic_attribute_06_display | no | ✗ | `Tree scene 1의 250을 마우스 오른쪽 버튼으로 클릭하세요.` |
| gemini | 0 | 6 | seismic_attribute_06_display | no | ✓ | `OK 버튼을 클릭하세요.` |
| gemini | 1 | 5 | seismic_attribute_06_display | no | ✗ | `Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.` |
| gemini | 1 | 6 | seismic_attribute_06_display | no | ✓ | `OK 버튼을 클릭하세요.` |
| gpt | 0 | 5 | seismic_attribute_06_display | no | ✓ | `In-line 번호 250를 우클릭하세요.` |
| gpt | 0 | 6 | seismic_attribute_06_display | no | ✓ | `OK 클릭하세요.` |

Early-completion answers: **0** of 8 early firings.

## B. routed correctly but full_system wrong — context vs expected action

### claude rep 0 · attribute_computation__01 step 1 · routed seismic_attribute_03_select_type

[Current Step] as given:
```
[Current Step] seismic_attribute > Step 3: 속성 유형 + 입력 데이터 선택 (파라미터 편집 직전)
Description: 매뉴얼 §1.5.1a step 2 결과: Attribute Type = Energy 선택 완료, Input Data = 4 Dip steered median filter 선택 완료. Energy-specific 파라미터 패널이 이제 표시되지만 사용자는 아직 Time gate 값을 편집하지 않음. Compute
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 4 속성 파라미터 최종 편집 + attribute set 저장 — Time gate 를 -28..+28 로 입력하고 Attribute Name 'Energy [-28,+28]' 를 입력하세요

```
- expected pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b` ; keywords: ['Time gate']
- response: `Input Data를 "4 Dip steered median filter"로 변경하기 위해 Input Data 드롭다운(현재 "Seismic_data")을 클릭하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 1, outgoing edge instruction 1)

### claude rep 0 · attribute_computation__01 step 2 · routed seismic_attribute_04_configure

[Current Step] as given:
```
[Current Step] seismic_attribute > Step 4: 속성 파라미터 최종 편집 + attribute set 저장
Description: 매뉴얼 §1.5.1a steps 3-5 결과의 통합 노드: Time gate 값 (-28..+28) 및 Attribute Name ('Energy [-28,+28]') 이미 입력 완료 → Add as new 로 set 에 추가 → Save on Close 체크 → Close 로 Attribute Set 3
```
[Possible Next Steps] as given:
```
  - Next (conditional) [if: batch_path]: Step 5 속성 계산 실행 (배치 경로 전용) — (배치 경로 선택 시) Batch Processing 다이얼로그를 열고 Go 로 실행하세요
  - Next (conditional) [if: on_the_fly_path]: Step 6 Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly) — (on-the-fly 경로) inline 250 을 표시하고 우클릭 → Add > Attribut
```
- expected pattern: `(?i)\b(Add as new|Add|추가|new)\b` ; keywords: ['Add as new']
- response: `Input Data 드롭다운(현재 "Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.`
- expected action is the **current node's action** (keyword hits: current-node description 1, outgoing edge instruction 0)

### claude rep 0 · attribute_computation__01 step 3 · routed seismic_attribute_04_configure

[Current Step] as given:
```
[Current Step] seismic_attribute > Step 4: 속성 파라미터 최종 편집 + attribute set 저장
Description: 매뉴얼 §1.5.1a steps 3-5 결과의 통합 노드: Time gate 값 (-28..+28) 및 Attribute Name ('Energy [-28,+28]') 이미 입력 완료 → Add as new 로 set 에 추가 → Save on Close 체크 → Close 로 Attribute Set 3
```
[Possible Next Steps] as given:
```
  - Next (conditional) [if: batch_path]: Step 5 속성 계산 실행 (배치 경로 전용) — (배치 경로 선택 시) Batch Processing 다이얼로그를 열고 Go 로 실행하세요
  - Next (conditional) [if: on_the_fly_path]: Step 6 Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly) — (on-the-fly 경로) inline 250 을 표시하고 우클릭 → Add > Attribut
```
- expected pattern: `(?i)\b(Close|Save on Close|Save|닫기|저장)\b` ; keywords: ['Close']
- response: `Input Data 드롭다운(현재 "Seismic_data")을 클릭하여 "4 Dip steered median filter"를 선택하세요.`
- expected action is the **current node's action** (keyword hits: current-node description 1, outgoing edge instruction 0)

### gemini rep 0 · attribute_computation__01 step 1 · routed seismic_attribute_03_select_type

[Current Step] as given:
```
[Current Step] seismic_attribute > Step 3: 속성 유형 + 입력 데이터 선택 (파라미터 편집 직전)
Description: 매뉴얼 §1.5.1a step 2 결과: Attribute Type = Energy 선택 완료, Input Data = 4 Dip steered median filter 선택 완료. Energy-specific 파라미터 패널이 이제 표시되지만 사용자는 아직 Time gate 값을 편집하지 않음. Compute
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 4 속성 파라미터 최종 편집 + attribute set 저장 — Time gate 를 -28..+28 로 입력하고 Attribute Name 'Energy [-28,+28]' 를 입력하세요

```
- expected pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b` ; keywords: ['Time gate']
- response: `Input Data 옆에 있는 Seismic_data 드롭다운 메뉴를 클릭하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 1, outgoing edge instruction 1)

### gemini rep 0 · attribute_computation__01 step 5 · routed seismic_attribute_06_display

[Current Step] as given:
```
[Current Step] seismic_attribute > Step 6: Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)
Description: 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 7 결과 QC 분석 (통계·해석 단계) — 표시된 속성의 통계·분포를 QC 하세요

```
- expected pattern: `(?i)\b(우클릭|right[- ]?click|Add.*Attribute|In[- ]?line|inline)\b` ; keywords: ['Add', 'Attribute']
- response: `Tree scene 1의 250을 마우스 오른쪽 버튼으로 클릭하세요.`
- expected action is the **current node's action** (keyword hits: current-node description 2, outgoing edge instruction 0)

### gemini rep 0 · survey_setup__01 step 0 · routed survey_setup_01_open_selection

[Current Step] as given:
```
[Current Step] survey_setup > Step 1: Survey Setup and Selection 창 열기
Description: OpendTect 첫 실행 시 Survey Setup and Selection 창이 최상단에 열림. Survey Data Root 리스트에서 새 survey를 만들거나 기존 survey를 선택.
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 2 Create New Survey 다이얼로그 열기 — Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요

```
- expected pattern: `(?i)\b(Survey|Create|New|Add)\b` ; keywords: ['Survey', 'Create', 'New']
- response: `녹색 더하기 아이콘을 클릭하세요.`
- expected action is the **next node's action** (keyword hits: current-node description 1, outgoing edge instruction 3)

### gemini rep 1 · 3d_visualization__01 step 3 · routed d3_visualization_04_add_zslice

[Current Step] as given:
```
[Current Step] d3_visualization > Step 4: Z-slice 슬라이스 추가
Description: Tree scene의 Elements > Z-slice 카테고리 노드를 우클릭하고 'Add Data' 또는 'Add Default Data'를 선택하여 3D Scene에 Z-slice(시간/깊이 슬라이스)를 추가.
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 5 3D Scene에 3개 슬라이스 모두 표시 — 목표 달성 — 세 슬라이스가 모두 표시되면 목표 달성 — '완료'를 출력하세요

```
- expected pattern: `(?i)^\s*(완료|Done)\.?\s*$` ; keywords: ['완료']
- response: `Add Default Data를 클릭하세요.`
- expected action is the **next node's action** (keyword hits: current-node description 0, outgoing edge instruction 1)

### gemini rep 1 · attribute_computation__01 step 1 · routed seismic_attribute_03_select_type

[Current Step] as given:
```
[Current Step] seismic_attribute > Step 3: 속성 유형 + 입력 데이터 선택 (파라미터 편집 직전)
Description: 매뉴얼 §1.5.1a step 2 결과: Attribute Type = Energy 선택 완료, Input Data = 4 Dip steered median filter 선택 완료. Energy-specific 파라미터 패널이 이제 표시되지만 사용자는 아직 Time gate 값을 편집하지 않음. Compute
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 4 속성 파라미터 최종 편집 + attribute set 저장 — Time gate 를 -28..+28 로 입력하고 Attribute Name 'Energy [-28,+28]' 를 입력하세요

```
- expected pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b` ; keywords: ['Time gate']
- response: `Input Data 드롭다운 메뉴에서 4 Dip steered median filter를 선택하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 1, outgoing edge instruction 1)

### gemini rep 1 · attribute_computation__01 step 5 · routed seismic_attribute_06_display

[Current Step] as given:
```
[Current Step] seismic_attribute > Step 6: Inline 우클릭 → Add > Attribute → Select dialog → Energy 렌더 (on-the-fly)
Description: 매뉴얼 §1.5.1a steps 6-9 통합: (a) Tree scene 에 In-line default data 추가 및 inline 번호 250 변경 후 표시된 inline 을 우클릭, (b) Add > Attribute submenu 
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 7 결과 QC 분석 (통계·해석 단계) — 표시된 속성의 통계·분포를 QC 하세요

```
- expected pattern: `(?i)\b(우클릭|right[- ]?click|Add.*Attribute|In[- ]?line|inline)\b` ; keywords: ['Add', 'Attribute']
- response: `Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.`
- expected action is the **current node's action** (keyword hits: current-node description 2, outgoing edge instruction 0)

### gemini rep 1 · survey_setup__01 step 0 · routed survey_setup_01_open_selection

[Current Step] as given:
```
[Current Step] survey_setup > Step 1: Survey Setup and Selection 창 열기
Description: OpendTect 첫 실행 시 Survey Setup and Selection 창이 최상단에 열림. Survey Data Root 리스트에서 새 survey를 만들거나 기존 survey를 선택.
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 2 Create New Survey 다이얼로그 열기 — Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요

```
- expected pattern: `(?i)\b(Survey|Create|New|Add)\b` ; keywords: ['Survey', 'Create', 'New']
- response: `초록색 플러스 아이콘을 클릭하세요.`
- expected action is the **next node's action** (keyword hits: current-node description 1, outgoing edge instruction 3)

### gpt rep 0 · 3d_visualization__01 step 2 · routed d3_visualization_01_main_window_ready

[Current Step] as given:
```
[Current Step] d3_visualization > Step 1: Main Window / Tree scene 준비 상태
Description: Survey가 로드된 상태에서 Main Window와 Tree scene 패널이 열려 있고, Elements 그룹 아래 In-line/Cross-line/Z-slice 카테고리 노드가 표시되나 3D Scene 패널은 비어 있는 초기 상태.
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 2 In-line 슬라이스 추가 — Tree scene의 In-line 카테고리를 우클릭하고 Add Data (첫번째 옵션) 또는 Add Default Data를 선택하세요

```
- expected pattern: `(?i)\b(Cross[- ]?line|Add.*Select.*Data|Add Default Data)\b` ; keywords: ['Cross-line', 'Add']
- response: `Z-slice를 우클릭하고 'Add Data'를 선택하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 1, outgoing edge instruction 1)

### gpt rep 0 · survey_setup__01 step 0 · routed survey_setup_01_open_selection

[Current Step] as given:
```
[Current Step] survey_setup > Step 1: Survey Setup and Selection 창 열기
Description: OpendTect 첫 실행 시 Survey Setup and Selection 창이 최상단에 열림. Survey Data Root 리스트에서 새 survey를 만들거나 기존 survey를 선택.
```
[Possible Next Steps] as given:
```
  - Next (sequential): Step 2 Create New Survey 다이얼로그 열기 — Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요

```
- expected pattern: `(?i)\b(Survey|Create|New|Add)\b` ; keywords: ['Survey', 'Create', 'New']
- response: `새로운 설문 아이콘을 클릭하세요.`
- expected action is the **next node's action** (keyword hits: current-node description 1, outgoing edge instruction 3)

