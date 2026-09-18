# Iteration-6 dev bench report (context assembly v5)

Benches: dev_iter6_v3_claude_r0.json, dev_iter6_v3_gemini_r0.json, dev_iter6_v3_gemini_r1.json, dev_iter6_v3_gpt_r0.json

## C. step accuracy per model (scenario-avg, mean over reps)

| model | reps | full_system | vanilla_vector | vanilla_budget | no_rag | full > vv | full > vb |
|---|---|---|---|---|---|---|---|
| gemini | 2 | 0.875 | 0.792 | 0.792 | 0.708 | ✓ | ✓ |
| claude | 1 | 1.000 | 0.875 | 0.875 | 0.875 | ✓ | ✓ |
| gpt | 1 | 0.833 | 0.750 | 0.667 | 0.750 | ✓ | ✓ |

## C. full_system losses classified (routing / context / generation / wording)

| model | routing | context | generation | wording |
|---|---|---|---|---|
| gemini | 0 | 0 | 2 | 2 |
| claude | 0 | 0 | 0 | 0 |
| gpt | 1 | 0 | 1 | 0 |

| model | rep | scenario | step | class | routed to | response | vv | vb |
|---|---|---|---|---|---|---|---|---|
| gemini | 0 | survey_setup__01 | 0 | wording | survey_setup_01_open_selection | `추가(+) 아이콘을 클릭하세요.` | ✓ | ✗ |
| gemini | 1 | attribute_computation__01 | 1 | generation | seismic_attribute_03_select_type | `Seismic_data 드롭다운을 클릭하세요.` | ✗ | ✗ |
| gemini | 1 | attribute_computation__01 | 5 | generation | seismic_attribute_06_display | `Tree scene 1에서 250을 마우스 오른쪽 버튼으로 클릭하세요.` | ✓ | ✓ |
| gemini | 1 | survey_setup__01 | 0 | wording | survey_setup_01_open_selection | `새 측량 추가(+) 아이콘을 클릭하세요.` | ✓ | ✓ |
| gpt | 0 | 3d_visualization__01 | 2 | generation | d3_visualization_01_main_window_ready | `Z-slice 카테고리를 우클릭하고 'Add Data'를 선택하세요.` | ✗ | ✗ |
| gpt | 0 | survey_setup__01 | 3 | routing | d3_visualization_01_main_window_ready | `Tree scene의 In-line 카테고리를 우클릭하고 Add Data 또는 Add Default Data를 선택하세요.` | ✗ | ✗ |

## A. goal-state block fired early (attribute s5/s6): full_system response

| model | rep | step | fired node | answered 완료? | step match | response |
|---|---|---|---|---|---|---|
| claude | 0 | 5 | seismic_attribute_06_display | no | ✓ | `Tree scene에서 **250** 항목을 우클릭하세요.` |
| claude | 0 | 6 | seismic_attribute_06_display | no | ✓ | `**OK** 버튼을 클릭하세요.` |
| gemini | 0 | 5 | seismic_attribute_06_display | no | ✓ | `트리에서 250을 우클릭하세요.` |
| gemini | 0 | 6 | seismic_attribute_06_display | no | ✓ | `OK 버튼을 클릭하세요.` |
| gemini | 1 | 5 | seismic_attribute_06_display | no | ✗ | `Tree scene 1에서 250을 마우스 오른쪽 버튼으로 클릭하세요.` |
| gemini | 1 | 6 | seismic_attribute_06_display | no | ✓ | `Energy [-28,+28]을 클릭하세요.` |
| gpt | 0 | 5 | seismic_attribute_06_display | no | ✓ | `우클릭하여 Add > Attribute 선택하세요.` |
| gpt | 0 | 6 | seismic_attribute_06_display | no | ✓ | `OK를 클릭하세요.` |

Early-completion answers: **0** of 8 early firings.

## B. routed correctly but full_system wrong — context vs expected action

### gemini rep 0 · survey_setup__01 step 0 · routed survey_setup_01_open_selection

[Current Step] as given:
```
—
```
[Possible Next Steps] as given:
```
—
```
- expected pattern: `(?i)\b(Survey|Create|New|Add)\b` ; keywords: ['Survey', 'Create', 'New']
- response: `추가(+) 아이콘을 클릭하세요.`
- expected action is the **next node's action** (keyword hits: current-node description 1, outgoing edge instruction 3)

### gemini rep 1 · attribute_computation__01 step 1 · routed seismic_attribute_03_select_type

[Current Step] as given:
```
—
```
[Possible Next Steps] as given:
```
—
```
- expected pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b` ; keywords: ['Time gate']
- response: `Seismic_data 드롭다운을 클릭하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 1, outgoing edge instruction 1)

### gemini rep 1 · attribute_computation__01 step 5 · routed seismic_attribute_06_display

[Current Step] as given:
```
—
```
[Possible Next Steps] as given:
```
—
```
- expected pattern: `(?i)\b(우클릭|right[- ]?click|Add.*Attribute|In[- ]?line|inline)\b` ; keywords: ['Add', 'Attribute']
- response: `Tree scene 1에서 250을 마우스 오른쪽 버튼으로 클릭하세요.`
- expected action is the **current node's action** (keyword hits: current-node description 2, outgoing edge instruction 0)

### gemini rep 1 · survey_setup__01 step 0 · routed survey_setup_01_open_selection

[Current Step] as given:
```
—
```
[Possible Next Steps] as given:
```
—
```
- expected pattern: `(?i)\b(Survey|Create|New|Add)\b` ; keywords: ['Survey', 'Create', 'New']
- response: `새 측량 추가(+) 아이콘을 클릭하세요.`
- expected action is the **next node's action** (keyword hits: current-node description 1, outgoing edge instruction 3)

### gpt rep 0 · 3d_visualization__01 step 2 · routed d3_visualization_01_main_window_ready

[Current Step] as given:
```
—
```
[Possible Next Steps] as given:
```
—
```
- expected pattern: `(?i)\b(Cross[- ]?line|Add.*Select.*Data|Add Default Data)\b` ; keywords: ['Cross-line', 'Add']
- response: `Z-slice 카테고리를 우클릭하고 'Add Data'를 선택하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 1, outgoing edge instruction 1)

