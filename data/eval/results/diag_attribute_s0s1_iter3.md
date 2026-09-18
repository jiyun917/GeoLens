# attribute s0/s1 diagnosis — iteration 3 code (820e993)

## step 0 (expected seismic_attribute_02_open_attribute_tool)

### 1. vision v3 output (verbatim)
```
{
 "current_dialog": "Attribute Set 3D",
 "window_titles": [
  "Attribute Set 3D",
  "OpenDTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]"
 ],
 "buttons": [
  "Select ...",
  "Add as new",
  "Close"
 ],
 "labels": [
  "Attribute set (<not saved>)",
  "Input Data (Seismic_data)",
  "Time gate (ms) (-28)",
  "Extension (Cross)",
  "Stepout inl: (1)",
  "crl: (1)",
  "Steering (None)",
  "Output statistic (Average)",
  "Attribute Name",
  "Save on Close (checked)"
 ],
 "field_values": [
  "Attribute set: <not saved>",
  "Input Data: Seismic_data",
  "Time gate (ms): -28",
  "Time gate (ms): 28",
  "Extension: Cross",
  "Stepout inl: 1",
  "Stepout crl: 1",
  "Steering: None",
  "Output statistic: Average",
  "Attribute Name: (empty)",
  "Save on Close: checked"
 ],
 "current_action": "Defining a 3D attribute set"
}
```

### 2. embedding scores (cosine, vision text ↔ node text) — pool rank in parentheses

| node | before (2026-08-07 signature) | after (iteration 3) |
|---|---|---|
| 02_open_attribute_tool | 0.7424 (#2) | 0.8045 (#1) |
| 03_select_type | 0.6728 (#8) | 0.7126 (#4) |
| 04_configure | 0.7522 (#1) | 0.7389 (#2) |

top-5 after: 02_open_attribute_tool=0.8045, 04_configure=0.7389, 01_ready_to_start=0.7315, 03_select_type=0.7126, 03_add_crossline=0.6992
top-5 before: 04_configure=0.7522, 02_open_attribute_tool=0.7424, 01_ready_to_start=0.7315, 03_add_crossline=0.6992, 02_add_inline=0.6991

### 3. near-tie prior condition (ROUTER_TIE_MARGIN = 0.020)

expected_dialog groups within the top-5 pool: {"attributeset3d": [["02_open_attribute_tool", 0.8045], ["04_configure", 0.7389], ["03_select_type", 0.7126]], "opendtectmainwindow": [["01_ready_to_start", 0.7315]], "opendtectmainwindowinlinedisplayed": [["03_add_crossline", 0.6992]]}
tie prior result (last confirmed = none): None
02/03/04 present in the top-5 pool: ['02_open_attribute_tool', '04_configure', '03_select_type']

### 4. rerank input — candidate lines of 02/03/04 (as rendered, iteration-3 prompt)
```
id="seismic_attribute_02_open_attribute_tool" step=2
   title: Attribute Set 3D 창 열림 (on-the-fly 경로 진입)
   desc: 매뉴얼 §1.5.1a step 1 결과: toolbar Attribute 3D 아이콘 클릭으로 Attribute Set 3D 창이 방금 열림. 비어 있는 attribute set 상태, Attribute Type d
   expected dialog: Attribute Set 3D
   expected elements: attribute type dropdown default similarity, attribute set not saved, attribute list empty, attribute name blank, time gate default -28 28, add as new button
   keywords: Attribute Set 3D, Attribute set (<not saved>), attribute type: Similarity (default, not yet changed), Time gate (ms) (-28) 28 (default values), Input Data (Seis
id="seismic_attribute_03_select_type" step=3
   title: 속성 유형 + 입력 데이터 선택 (파라미터 편집 직전)
   desc: 매뉴얼 §1.5.1a step 2 결과: Attribute Type = Energy 선택 완료, Input Data = 4 Dip steered median filter 선택 완료. Energy-specific 파라
   expected dialog: Attribute Set 3D
   expected elements: attribute type energy selected, output energy, compute gradient toggle, attribute name blank, attribute list empty
   keywords: Attribute Set 3D, attribute type: Energy (selected), Output (Energy), Compute gradient Yes / No, Time gate (ms) (-28) 28, Attribute Name (empty) — not yet enter
id="seismic_attribute_04_configure" step=4
   title: 속성 파라미터 최종 편집 + attribute set 저장
   desc: 매뉴얼 §1.5.1a steps 3-5 결과의 통합 노드: Time gate 값 (-28..+28) 및 Attribute Name ('Energy [-28,+28]') 이미 입력 완료 → Add as new 로 se
   expected dialog: Attribute Set 3D / Save Attribute as / Save Attribute Set
   expected elements: attribute name filled energy -28 28, energy entry in attribute list, save on close checkbox, save attribute as dialog, attribute set name field
   keywords: Attribute Name (Energy [-28,+28]), Energy [-28,+28] listed in the attribute set, Save on Close (checked), Save Attribute as, Select Output Attribute, Name (my f
```
## step 1 (expected seismic_attribute_03_select_type)

### 1. vision v3 output (verbatim)
```
{
 "current_dialog": "Attribute Set 3D",
 "window_titles": [
  "Attribute Set 3D",
  "OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]"
 ],
 "buttons": [
  "Select ...",
  "Add as new",
  "Close"
 ],
 "labels": [
  "Attribute set (<not saved>)",
  "<All>",
  "Energy",
  "Input Data (Seismic_data)",
  "Time gate (ms) (-28)",
  "28",
  "Compute gradient",
  "Yes",
  "No",
  "Output (Energy)",
  "Attribute Name",
  "Save on Close (checked)"
 ],
 "field_values": [
  "Attribute set: <not saved>",
  "<All>: <All>",
  "Energy: Energy",
  "Input Data: Seismic_data",
  "Time gate (ms): -28",
  "Time gate (ms): 28",
  "Compute gradient: No",
  "Output: Energy",
  "Attribute Name: (empty)",
  "Save on Close: checked"
 ],
 "current_action": "Defining a 3D attribute set"
}
```

### 2. embedding scores (cosine, vision text ↔ node text) — pool rank in parentheses

| node | before (2026-08-07 signature) | after (iteration 3) |
|---|---|---|
| 02_open_attribute_tool | 0.7215 (#3) | 0.7869 (#1) |
| 03_select_type | 0.6917 (#5) | 0.7435 (#3) |
| 04_configure | 0.7702 (#1) | 0.7573 (#2) |

top-5 after: 02_open_attribute_tool=0.7869, 04_configure=0.7573, 03_select_type=0.7435, 01_ready_to_start=0.7313, 04_add_zslice=0.6987
top-5 before: 04_configure=0.7702, 01_ready_to_start=0.7313, 02_open_attribute_tool=0.7215, 04_add_zslice=0.6987, 03_select_type=0.6917

### 3. near-tie prior condition (ROUTER_TIE_MARGIN = 0.020)

expected_dialog groups within the top-5 pool: {"attributeset3d": [["02_open_attribute_tool", 0.7869], ["04_configure", 0.7573], ["03_select_type", 0.7435]], "opendtectmainwindow": [["01_ready_to_start", 0.7313]], "opendtectmainwindowinlinecrosslinedisplayed": [["04_add_zslice", 0.6987]]}
tie prior result (last confirmed = 02): None
02/03/04 present in the top-5 pool: ['02_open_attribute_tool', '04_configure', '03_select_type']

### 4. rerank input — candidate lines of 02/03/04 (as rendered, iteration-3 prompt)
```
id="seismic_attribute_02_open_attribute_tool" step=2
   title: Attribute Set 3D 창 열림 (on-the-fly 경로 진입)
   desc: 매뉴얼 §1.5.1a step 1 결과: toolbar Attribute 3D 아이콘 클릭으로 Attribute Set 3D 창이 방금 열림. 비어 있는 attribute set 상태, Attribute Type d
   expected dialog: Attribute Set 3D
   expected elements: attribute type dropdown default similarity, attribute set not saved, attribute list empty, attribute name blank, time gate default -28 28, add as new button
   keywords: Attribute Set 3D, Attribute set (<not saved>), attribute type: Similarity (default, not yet changed), Time gate (ms) (-28) 28 (default values), Input Data (Seis
id="seismic_attribute_03_select_type" step=3
   title: 속성 유형 + 입력 데이터 선택 (파라미터 편집 직전)
   desc: 매뉴얼 §1.5.1a step 2 결과: Attribute Type = Energy 선택 완료, Input Data = 4 Dip steered median filter 선택 완료. Energy-specific 파라
   expected dialog: Attribute Set 3D
   expected elements: attribute type energy selected, output energy, compute gradient toggle, attribute name blank, attribute list empty
   keywords: Attribute Set 3D, attribute type: Energy (selected), Output (Energy), Compute gradient Yes / No, Time gate (ms) (-28) 28, Attribute Name (empty) — not yet enter
id="seismic_attribute_04_configure" step=4
   title: 속성 파라미터 최종 편집 + attribute set 저장
   desc: 매뉴얼 §1.5.1a steps 3-5 결과의 통합 노드: Time gate 값 (-28..+28) 및 Attribute Name ('Energy [-28,+28]') 이미 입력 완료 → Add as new 로 se
   expected dialog: Attribute Set 3D / Save Attribute as / Save Attribute Set
   expected elements: attribute name filled energy -28 28, energy entry in attribute list, save on close checkbox, save attribute as dialog, attribute set name field
   keywords: Attribute Name (Energy [-28,+28]), Energy [-28,+28] listed in the attribute set, Save on Close (checked), Save Attribute as, Select Output Attribute, Name (my f
```

## 5. scoring impact of the s0/s1 route (iteration 0 and 1 records)

| run | step | full_system routed to | fs matched | vanilla_vector | vanilla_budget | no_rag |
|---|---|---|---|---|---|---|
| dev_iter0_v2mech_gemini_r0 | 0 | seismic_attribute_04_configure (0.9) | ✓ | ✓ | ✓ | ✓ |
| dev_iter0_v2mech_gemini_r0 | 1 | seismic_attribute_04_configure (0.9) | ✗ | ✗ | ✗ | ✗ |
| dev_iter1_v3_gemini_r0 | 0 | seismic_attribute_02_open_attribute_tool (0.95) | ✓ | ✓ | ✓ | ✓ |
| dev_iter1_v3_gemini_r0 | 1 | seismic_attribute_03_select_type (0.9) | ✓ | ✗ | ✗ | ✗ |
