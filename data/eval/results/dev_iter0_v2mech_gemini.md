# dev iteration report — dev_iter0_v2mech_gemini

Runs: dev_iter0_v2mech_gemini_r0.json (n_rep=1); scorer v3; dev set = opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01 (16 steps).

Judgement rule: step accuracy from 1–2 runs is within noise and is NOT the primary criterion. Primary = (a) routing accuracy / confident-wrong routes, (b) target-section retrieval hit, (c) per-step loss classification. Latency goal = minimise the extra latency over vanilla.

## Backend summary (per-step means over scenarios × reps)

| backend | step_acc (scenario-avg) | step_acc (pooled) | hall rate | cost_total/step $ | gen $ | aux $ | latency s (charged) | latency s (wall) | ctx chars | target-section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| no_rag | 0.792 | 0.812 | 0.125 | 0.00654 | 0.00654 | 0.00000 | 9.59 | 9.59 | 0 | 0.00 |
| vanilla_vector | 0.750 | 0.688 | 0.125 | 0.01522 | 0.01522 | 0.00000 | 11.62 | 11.62 | 18888 | 0.75 |
| vanilla_budget | 0.792 | 0.750 | 0.125 | 0.00816 | 0.00816 | 0.00000 | 10.34 | 10.34 | 3900 | 0.75 |
| full_system | 0.750 | 0.750 | 0.125 | 0.01074 | 0.00942 | 0.00132 | 24.41 | 24.41 | 4210 | 0.94 |

## Per-scenario step accuracy (mean over reps)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| opendtect__survey_setup__01 | 0.750 | 1.000 | 1.000 | 0.750 |
| opendtect__3d_visualization__01 | 0.750 | 0.750 | 0.750 | 0.750 |
| opendtect__attribute_computation__01 | 0.875 | 0.500 | 0.625 | 0.750 |

## Latency by stage (mean seconds per step; inclusive stages marked ⊃ contain the exclusive ones)

- no stage_latency recorded in these runs (instrumentation added after they started).

- extra latency of full_system over vanilla_vector (charged): **+12.79 s/step**; over vanilla_budget: +14.07 s/step.

## full_system routing per step (rep-wise; expected = GT node or scenario workflow)

| scenario | step | rep | expected | picked node | conf | method | fallback | route ok | target hit fs/vv/vb | fs | vv | vb | no_rag | loss class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.80 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 1 | 0 | d3_visualization | d3_visualization_03_add_crossline | 0.70 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 2 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 | llm |  | ✓ | ✓/✗/✗ | ✓ | ✓ | ✓ | ✓ |  |
| 3d_visualization__01 | 3 | 0 | d3_visualization | d3_visualization_04_add_zslice | 0.00 | llm | Y | — | ✗/✗/✗ | ✗ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 0 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_04_configure | 0.90 | llm |  | ✗ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 1 | 0 | seismic_attribute_03_select_type | seismic_attribute_04_configure | 0.90 | llm |  | ✗ | ✓/✓/✓ | ✗ | ✗ | ✗ | ✗ |  |
| attribute_computation__01 | 2 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✓ |  |
| attribute_computation__01 | 3 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✗ | ✗ | ✓ |  |
| attribute_computation__01 | 4 | 0 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 5 | 0 | seismic_attribute_06_display | d3_visualization_01_main_window_ready | 0.70 | llm |  | ✗ | ✓/✓/✓ | ✓ | ✗ | ✓ | ✓ |  |
| attribute_computation__01 | 6 | 0 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| attribute_computation__01 | 7 | 0 | seismic_attribute_06_display | — | 0.00 | none | Y | — | ✓/✓/✓ | ✗ | ✓ | ✓ | ✓ | fallback_quality |
| survey_setup__01 | 0 | 0 | survey_setup | survey_setup_02_open_new_survey_dialog | 0.85 | llm |  | ✓ | ✓/✓/✓ | ✗ | ✓ | ✓ | ✗ | context_or_generation |
| survey_setup__01 | 1 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.80 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 2 | 0 | survey_setup | survey_setup_03_choose_initial_setup | 0.80 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |
| survey_setup__01 | 3 | 0 | survey_setup | survey_setup_05_select_survey | 0.70 | llm |  | ✓ | ✓/✓/✓ | ✓ | ✓ | ✓ | ✓ |  |

## (a) Routing summary (full_system)

- steps × reps: 16; routed (passed gate): 14; routed correct: 11 (0.79); fallback: 2 (0.12)
- confident-wrong routes (conf ≥ 0.70, wrong node/workflow): **3**
- confidence of correct routed picks: [0.7, 0.7, 0.8, 0.8, 0.8, 0.85, 0.9, 0.9, 0.9, 0.9, 0.9]
- confidence of wrong routed picks: [0.7, 0.9, 0.9]

### Confidence-threshold calibration (all pre-gate picks; kept = conf ≥ t passes the gate)

- correct picks (all): [0.0, 0.7, 0.7, 0.8, 0.8, 0.8, 0.85, 0.9, 0.9, 0.9, 0.9, 0.9]
- wrong picks (all): [0.7, 0.9, 0.9]

| t | correct kept | wrong kept | correct dropped (→ fallback) |
|---|---|---|---|
| 0.60 | 11 | 3 | 1 |
| 0.65 | 11 | 3 | 1 |
| 0.70 | 11 | 3 | 1 |
| 0.75 | 9 | 2 | 3 |
| 0.80 | 9 | 2 | 3 |
| 0.85 | 6 | 2 | 6 |
| 0.90 | 5 | 2 | 7 |
| 0.95 | 0 | 0 | 12 |

- smallest t with zero wrong picks kept: **0.95** (keeps 0 correct, drops 12 correct to fallback).

## (b) Target-section retrieval hit (context contains the scenario's target section)

| scenario | no_rag | vanilla_vector | vanilla_budget | full_system |
|---|---|---|---|---|
| survey_setup__01 | 0/4 | 4/4 | 4/4 | 4/4 |
| 3d_visualization__01 | 0/4 | 0/4 | 0/4 | 3/4 |
| attribute_computation__01 | 0/8 | 8/8 | 8/8 | 8/8 |

## (c) Losses vs vanilla (fs ✗ while vv or vb ✓): {'fallback_quality': 1, 'context_or_generation': 1}

## Fallback steps (full_system not routed): fs vs vanilla_vector (untruncated) vs vanilla_budget (3,900)

| scenario | step | rep | fs | vanilla_vector | vanilla_budget | fs ctx chars | vv ctx chars |
|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 3 | 0 | ✗ | ✗ | ✗ | 1526 | 22110 |
| attribute_computation__01 | 7 | 0 | ✗ | ✓ | ✓ | 1526 | 17876 |

- fallback steps: 2; matched — fs 0, vanilla_vector 1, vanilla_budget 1; steps where fs ✗ and vanilla_vector ✓ but vanilla_budget ✗ (truncation-attributable): **0**
- vanilla_vector untruncated context: mean 18888 chars, max 22110, median 17876 (fallback/vanilla_budget budget = 3900).
- no truncation-attributable loss on fallback steps; budget unchanged.

## Steps every backend failed (same rep) — response text and GT pattern

### 3d_visualization__01 step 3 rep 0

- GT pattern: `(?i)^\s*(완료|Done)\.?\s*$`
- GT keywords: ['완료']; allowed alternatives: [{'pattern': '(?i)\\b(Done)\\b', 'note': 'English completion sentinel'}, {'pattern': '(?i)\\b(In[- ]?line|Cross[- ]?line|Z[- ]?slice|3D Scene|Elements)\\b', 'note': 'Ground-truth element mention for the grounding validator.'}]
- **no_rag** (target hit ✗; sections —): `Add Default Data를 클릭하세요.`
- **vanilla_vector** (target hit ✗; sections 1.2.2a, 1.3, 2.3.1c, 2.6.3): `Add Default Data를 클릭합니다.`
- **vanilla_budget** (target hit ✗; sections 1.2.2a, 1.3, 2.6.3): `'Add Default Data'를 클릭하세요.`
- **full_system** (target hit ✗; sections 1.3): `컨텍스트 메뉴에서 Add Data를 선택하세요.`

### attribute_computation__01 step 1 rep 0

- GT pattern: `(?i)\b(Time gate|-?28|Attribute Name|이름|입력|Enter)\b`
- GT keywords: ['Time gate']; allowed alternatives: [{'pattern': '(?i)\\b(입력|Enter|설정|Set).*(Time gate|Name|이름)\\b', 'note': 'Enter/set verb + target.'}, {'pattern': '(?i)\\b(Compute gradient)\\b', 'note': 'Compute gradient parameter is a valid focus (kept at No).'}]
- **no_rag** (target hit ✗; sections —): `Select... 버튼을 클릭하세요.`
- **vanilla_vector** (target hit ✓; sections 1.5.1a, 2.3.1c, 2.5.1a): `'Select...' 버튼을 클릭합니다.`
- **vanilla_budget** (target hit ✓; sections 1.5.1a): `'Seismic_data' 드롭다운 메뉴를 클릭하세요.`
- **full_system** (target hit ✓; sections 1.5.1a): `Energy 드롭다운 메뉴를 클릭하세요.`

## Criteria check

- FAIL — (a) confident-wrong routes == 0 (3)
- FAIL — (a) routing accuracy (routed steps) (11/14)
- PASS — (b) target-section hit fs ≥ vanilla_vector (0.94 vs 0.75)
- PASS — (b) target-section hit fs ≥ vanilla_budget (0.94 vs 0.75)
- FAIL — (c) no loss vs vanilla ({'fallback_quality': 1, 'context_or_generation': 1})

Secondary (noise-prone at n_rep ≤ 2; reported, not decisive):
- step_acc fs vs vanilla_vector: 0.750 vs 0.750; cost_total 0.01074 vs 0.01522; latency 24.41 vs 11.62 s (extra +12.79 s)
- step_acc fs vs vanilla_budget: 0.750 vs 0.792; cost_total 0.01074 vs 0.00816; latency 24.41 vs 10.34 s (extra +14.07 s)

**Primary criteria NOT met.**

## Loss detail (full_system lost to a vanilla baseline)

### attribute_computation__01 step 7 rep 0 — fallback_quality (picked=None conf=0.00 expected=seismic_attribute_06_display)

full_system response:
```
OK 버튼을 클릭하세요.
```
vanilla_vector response:
```
완료
```
full_system context sections: 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot, 1.5.1a Bright Spot
full_system context head:
```
[Manual Context (vector)]
[Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf, Section: 1.5.1a Bright Spot]
[Section: 1.5.1a Bright Spot, Page: 120, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf]
Workflow cont'd:
6. In the tree, right-click on In-line and
select Add Default Data.
7. Change the inline position to 250: select
the inline in the tree and type the position
using the position toolbar.
8. Add an extra attribute layer to inline 250:
right-click on the inline number in the tree
and go Add > Attribute.
9. The attributes available are organized in
three categories: Stored, Steering and
Attributes (from the active attribute set and
calculated on-the-fly).
Go to the Attributes section, select your
attribute Energy [-28, +28] and click Ok.

Workflow cont'd:

Results should look like this.

- 120 -

---

[Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf, Section: 1.5.1a Bright Spot]
[Section: 1.5.1a Bright Spot, Page: 123, Source: data/uploads/645b7cdf2690408da843
```

### survey_setup__01 step 0 rep 0 — context_or_generation (picked=survey_setup_02_open_new_survey_dialog conf=0.85 expected=survey_setup)

full_system response:
```
초록색 더하기 아이콘을 클릭하세요.
```
vanilla_vector response:
```
새 survey 아이콘을 클릭합니다.
```
full_system context sections: 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y, 1.2.2a Survey Setup & Load SEG-Y
full_system context head:
```
[Current Step] survey_setup > Step 2: Create New Survey 다이얼로그 열기
Description: Survey Setup and Selection 창에서 Add (+) 버튼을 클릭하여 Create New Survey 다이얼로그를 연다.

[Possible Next Steps]
  - Next (sequential): Step 3 Survey 이름 입력 및 Initial setup 선택 — Survey 이름을 입력하고 Initial setup 방식을 선택하세요

[Manual Context (graph)]
[Section: 1.2.2a Survey Setup & Load SEG-Y, Page: 22, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf]
Workflow cont'd:
4. Go to the Rawdata directory of F3 Demo and Select the Input SEG-Y file: \Raw data\Seismic_data.sgy.

Workflow cont'd:
5. The import wizard makes a quick scan of the SEG-Y volume and automatically fills-in relevant parameters for survey set-up and import.
If needed, the parameters required for SEG-Y import (under the Actually Use column) can be changed manually.
The bottom part shows the extracted geometry of the survey and the histogram of seismic amplitudes from the quick scan of the input SEG-Y volume.

- 22 -

[Manual Context (graph)]
[Section: 1.2.2a Survey Setup & Load SEG-Y, Page: 24, Source: data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-To-OpendTect-and-OpendTect-Pro
```
