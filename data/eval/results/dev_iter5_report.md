# Iteration-5 dev bench report (context assembly v4; Gemini x2 only — Claude cut off by Gemini credit depletion, GPT not started)

Benches: dev_iter5_v3_gemini_r0.json, dev_iter5_v3_gemini_r1.json

## C. step accuracy per model (scenario-avg, mean over reps)

| model | reps | full_system | vanilla_vector | vanilla_budget | no_rag | full > vv | full > vb |
|---|---|---|---|---|---|---|---|
| gemini | 2 | 0.854 | 0.854 | 0.750 | 0.750 | = | ✓ |

## C. full_system losses classified (routing / context / generation / wording)

| model | routing | context | generation | wording |
|---|---|---|---|---|
| gemini | 0 | 0 | 3 | 1 |
| claude | 0 | 0 | 0 | 0 |
| gpt | 0 | 0 | 0 | 0 |

| model | rep | scenario | step | class | routed to | response | vv | vb |
|---|---|---|---|---|---|---|---|---|
| gemini | 0 | 3d_visualization__01 | 3 | generation | d3_visualization_03_add_crossline | `Add Default Data를 클릭하세요.` | ✓ | ✗ |
| gemini | 0 | survey_setup__01 | 0 | wording | survey_setup_01_open_selection | `새 서베이 추가 아이콘을 클릭하세요.` | ✓ | ✗ |
| gemini | 1 | 3d_visualization__01 | 3 | generation | d3_visualization_03_add_crossline | `Add Default Data를 클릭하세요.` | ✓ | ✗ |
| gemini | 1 | attribute_computation__01 | 5 | generation | seismic_attribute_06_display | `Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.` | ✓ | ✓ |

## A. goal-state block fired early (attribute s5/s6): full_system response

| model | rep | step | fired node | answered 완료? | step match | response |
|---|---|---|---|---|---|---|
| gemini | 0 | 5 | seismic_attribute_06_display | no | ✓ | `Tree scene의 In-line 아래에 있는 250을 마우스 오른쪽 버튼으로 클릭하고 Add > Attribute를 선택하세요.` |
| gemini | 0 | 6 | seismic_attribute_06_display | no | ✓ | `OK 버튼을 클릭하세요.` |
| gemini | 1 | 5 | seismic_attribute_06_display | no | ✗ | `Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.` |
| gemini | 1 | 6 | seismic_attribute_06_display | no | ✓ | `OK 버튼을 클릭하세요.` |

Early-completion answers: **0** of 4 early firings.

## B. routed correctly but full_system wrong — context vs expected action

### gemini rep 0 · 3d_visualization__01 step 3 · routed d3_visualization_03_add_crossline

[Current Step] as given:
```
—
```
[Possible Next Steps] as given:
```
—
```
- expected pattern: `(?i)^\s*(완료|Done)\.?\s*$` ; keywords: ['완료']
- response: `Add Default Data를 클릭하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 0, outgoing edge instruction 0)

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
- response: `새 서베이 추가 아이콘을 클릭하세요.`
- expected action is the **next node's action** (keyword hits: current-node description 1, outgoing edge instruction 3)

### gemini rep 1 · 3d_visualization__01 step 3 · routed d3_visualization_03_add_crossline

[Current Step] as given:
```
—
```
[Possible Next Steps] as given:
```
—
```
- expected pattern: `(?i)^\s*(완료|Done)\.?\s*$` ; keywords: ['완료']
- response: `Add Default Data를 클릭하세요.`
- expected action is the **ambiguous** (keyword hits: current-node description 0, outgoing edge instruction 0)

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
- response: `Tree scene에서 250을 마우스 오른쪽 버튼으로 클릭하세요.`
- expected action is the **current node's action** (keyword hits: current-node description 2, outgoing edge instruction 0)

