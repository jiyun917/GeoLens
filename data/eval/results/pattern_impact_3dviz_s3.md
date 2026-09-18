# 3d_visualization step 3 — impact of the element-mention allowed alternative

A = current patterns (sentinel + 2 alternatives); B = without the alternative noted 'Ground-truth element mention'. Files: 22.

## Cells whose step-3 match changes (A → B)

| group | model | backend | file | response (head) | A | B |
|---|---|---|---|---|---|---|
| dev_iter1 | gemini | vanilla_vector | dev_iter1_v3_gemini_r0.json | `Tree scene 1에서 Z-slice를 마우스 오른쪽 버튼으로 클릭하세요.` | ✓ | ✗ |
| unified4 | claude | state_path | run_claude_unified4_r3_20260807T084832.json | `Tree scene 패널에서 **Z-slice** 노드를 우클릭하세요.` | ✓ | ✗ |
| unified4 | gemini | state_path | run_gemini_unified4_r3_20260807T043128.json | `Tree scene의 Z-slice에서 우클릭하고 Add Data를 선택하세요.` | ✓ | ✗ |
| unified4 | gpt | vision_only | run_gpt_unified4_r1_20260807T105516.json | `Z-slice에서 마우스 오른쪽 버튼을 클릭하세요.` | ✓ | ✗ |
| unified4 | gpt | state_path | run_gpt_unified4_r2_20260807T113738.json | `Z-slice 카테고리를 우클릭하고 'Add Data'를 선택하세요.` | ✓ | ✗ |
| unified4 | gpt | state_path | run_gpt_unified4_r5_20260807T134308.json | `Elements > Z-slice 카테고리 노드를 우클릭하세요.` | ✓ | ✗ |
| unified4 | qwen | no_rag | run_qwen_unified4_r1_20260807T142449.json | `In-line 카테고리 우클릭 후 'Add Data' 선택합니다.` | ✓ | ✗ |
| unified4 | qwen | vanilla_vector | run_qwen_unified4_r1_20260807T142449.json | `Z-slice 카테고리 우클릭 후 'Add Data' 선택` | ✓ | ✗ |
| unified4 | qwen | graph_only | run_qwen_unified4_r1_20260807T142449.json | `Z-slice 카테고리 우클릭 후 'Add Data' 선택하여 seismic 볼륨 로드합니다.` | ✓ | ✗ |
| unified4 | qwen | vision_only | run_qwen_unified4_r1_20260807T142449.json | `Z-slice 카테고리 우클릭 → 'Add Data' 선택` | ✓ | ✗ |
| unified4 | qwen | state_path | run_qwen_unified4_r1_20260807T142449.json | `Z-slice 카테고리 노드를 우클릭한 후 'Add Data'를 선택하여 기본 seismic 데이터를 로드합니다.` | ✓ | ✗ |
| unified4 | qwen | graph_only | run_qwen_unified4_r2_20260807T151241.json | `Z-slice 카테고리 우클릭 후 컨텍스트 메뉴의 'Add Data' 선택` | ✓ | ✗ |
| unified4 | qwen | full_system | run_qwen_unified4_r2_20260807T151241.json | `3D Scene 패널이 비어 있는 초기 상태에서 'Close' 또는 'X' 버튼을 클릭하여 다이얼로그를 닫습니다.` | ✓ | ✗ |
| unified4 | qwen | state_path | run_qwen_unified4_r2_20260807T151241.json | `Z-slice 카테고리 노드 우클릭 → 'Add Data' 선택 (또는 'Add Default Data' 선택)` | ✓ | ✗ |
| unified4 | qwen | no_rag | run_qwen_unified4_r3_20260807T155946.json | `In-line, Cross-line, Z-slice 중 다음 범주를 우클릭하고 '데이터 추가'를 선택하십시오.` | ✓ | ✗ |
| unified4 | qwen | vision_only | run_qwen_unified4_r3_20260807T155946.json | `In-line 카테고리 우클릭 → 'Add Data' 선택` | ✓ | ✗ |
| unified4 | qwen | vanilla_vector | run_qwen_unified4_r4_20260807T164820.json | `Right-click on 'In-line' in the F3 Demo survey and select 'Add Data' from the context menu to load the seismic volume fo` | ✓ | ✗ |
| unified4 | qwen | vanilla_vector | run_qwen_unified4_r5_20260807T173614.json | `Click OK in the survey creation dialog to finalize setup and load seismic data into 3D scene.` | ✓ | ✗ |
| unified4 | qwen | graph_only | run_qwen_unified4_r5_20260807T173614.json | `Z-slice 카테고리 우클릭 후 'Add Data' 선택.` | ✓ | ✗ |

## Step-3 match counts per model × backend (n replicates): A → B

| group | model | backend | n | matched A | matched B |
|---|---|---|---|---|---|
| dev_iter0 | gemini | full_system | 1 | 0 | 0 |
| dev_iter0 | gemini | no_rag | 1 | 0 | 0 |
| dev_iter0 | gemini | vanilla_budget | 1 | 0 | 0 |
| dev_iter0 | gemini | vanilla_vector | 1 | 0 | 0 |
| dev_iter1 | gemini | full_system | 1 | 0 | 0 |
| dev_iter1 | gemini | no_rag | 1 | 0 | 0 |
| dev_iter1 | gemini | vanilla_budget | 1 | 0 | 0 |
| dev_iter1 | gemini | vanilla_vector | 1 | 1 | 0 |
| unified4 | claude | full_system | 5 | 5 | 5 |
| unified4 | claude | graph_only | 5 | 5 | 5 |
| unified4 | claude | no_rag | 5 | 5 | 5 |
| unified4 | claude | state_path | 5 | 5 | 4 |
| unified4 | claude | vanilla_vector | 5 | 5 | 5 |
| unified4 | claude | vision_only | 5 | 5 | 5 |
| unified4 | gemini | full_system | 5 | 5 | 5 |
| unified4 | gemini | graph_only | 5 | 2 | 2 |
| unified4 | gemini | no_rag | 5 | 3 | 3 |
| unified4 | gemini | state_path | 5 | 5 | 4 |
| unified4 | gemini | vanilla_vector | 5 | 5 | 5 |
| unified4 | gemini | vision_only | 5 | 5 | 5 |
| unified4 | gpt | full_system | 5 | 5 | 5 |
| unified4 | gpt | graph_only | 5 | 5 | 5 |
| unified4 | gpt | no_rag | 5 | 3 | 3 |
| unified4 | gpt | state_path | 5 | 5 | 3 |
| unified4 | gpt | vanilla_vector | 5 | 5 | 5 |
| unified4 | gpt | vision_only | 5 | 4 | 3 |
| unified4 | qwen | full_system | 5 | 5 | 4 |
| unified4 | qwen | graph_only | 5 | 4 | 1 |
| unified4 | qwen | no_rag | 5 | 4 | 2 |
| unified4 | qwen | state_path | 5 | 5 | 3 |
| unified4 | qwen | vanilla_vector | 5 | 5 | 2 |
| unified4 | qwen | vision_only | 5 | 4 | 2 |
