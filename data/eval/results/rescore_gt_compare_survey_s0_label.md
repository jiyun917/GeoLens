# Re-score with old vs new GT (v3 scorer) — old = 55e91ec, new = working tree

Files: 27. Metrics per (group, model, backend): step matches and hallucination flags summed over scenarios × steps × replicates.

| group | model | backend | n steps | step_acc old → new | Δpp | hall rate old → new | Δpp |
|---|---|---|---|---|---|---|---|
| dev_iter0 | gemini | full_system | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter0 | gemini | no_rag | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter0 | gemini | vanilla_budget | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter0 | gemini | vanilla_vector | 16 | 0.688 → 0.688 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter1 | gemini | full_system | 16 | 0.938 → 0.938 | +0.0 | 0.000 → 0.000 | +0.0 |
| dev_iter1 | gemini | no_rag | 16 | 0.750 → 0.750 | +0.0 | 0.000 → 0.000 | +0.0 |
| dev_iter1 | gemini | vanilla_budget | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter1 | gemini | vanilla_vector | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | full_system | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | no_rag | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | vanilla_budget | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | claude | vanilla_vector | 16 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gemini | full_system | 32 | 0.781 → 0.781 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gemini | no_rag | 32 | 0.656 → 0.656 | +0.0 | 0.031 → 0.031 | +0.0 |
| dev_iter4 | gemini | vanilla_budget | 32 | 0.719 → 0.719 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gemini | vanilla_vector | 32 | 0.719 → 0.719 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | full_system | 16 | 0.875 → 0.875 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | no_rag | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | vanilla_budget | 16 | 0.688 → 0.688 | +0.0 | 0.062 → 0.062 | +0.0 |
| dev_iter4 | gpt | vanilla_vector | 16 | 0.875 → 0.875 | +0.0 | 0.062 → 0.062 | +0.0 |
| latency_baseline | ? | full_system | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| latency_baseline | ? | vanilla_budget | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| latency_baseline | ? | vanilla_vector | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| unified4 | claude | full_system | 80 | 0.812 → 0.812 | +0.0 | 0.113 → 0.062 | -5.0 |
| unified4 | claude | graph_only | 80 | 0.787 → 0.787 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | claude | no_rag | 80 | 0.812 → 0.812 | +0.0 | 0.100 → 0.087 | -1.2 |
| unified4 | claude | state_path | 80 | 0.812 → 0.812 | +0.0 | 0.113 → 0.062 | -5.0 |
| unified4 | claude | vanilla_vector | 80 | 0.812 → 0.812 | +0.0 | 0.075 → 0.075 | +0.0 |
| unified4 | claude | vision_only | 80 | 0.812 → 0.812 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | gemini | full_system | 80 | 0.838 → 0.838 | +0.0 | 0.025 → 0.025 | +0.0 |
| unified4 | gemini | graph_only | 80 | 0.800 → 0.800 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | gemini | no_rag | 80 | 0.738 → 0.738 | +0.0 | 0.025 → 0.025 | +0.0 |
| unified4 | gemini | state_path | 80 | 0.887 → 0.887 | +0.0 | 0.075 → 0.025 | -5.0 |
| unified4 | gemini | vanilla_vector | 80 | 0.750 → 0.750 | +0.0 | 0.050 → 0.050 | +0.0 |
| unified4 | gemini | vision_only | 80 | 0.875 → 0.875 | +0.0 | 0.037 → 0.037 | +0.0 |
| unified4 | gpt | full_system | 80 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| unified4 | gpt | graph_only | 80 | 0.787 → 0.787 | +0.0 | 0.062 → 0.062 | +0.0 |
| unified4 | gpt | no_rag | 80 | 0.688 → 0.688 | +0.0 | 0.075 → 0.075 | +0.0 |
| unified4 | gpt | state_path | 80 | 0.800 → 0.800 | +0.0 | 0.138 → 0.075 | -6.2 |
| unified4 | gpt | vanilla_vector | 80 | 0.775 → 0.775 | +0.0 | 0.087 → 0.087 | +0.0 |
| unified4 | gpt | vision_only | 80 | 0.662 → 0.662 | +0.0 | 0.125 → 0.125 | +0.0 |
| unified4 | qwen | full_system | 80 | 0.487 → 0.487 | +0.0 | 0.300 → 0.237 | -6.2 |
| unified4 | qwen | graph_only | 80 | 0.487 → 0.487 | +0.0 | 0.300 → 0.300 | +0.0 |
| unified4 | qwen | no_rag | 80 | 0.475 → 0.475 | +0.0 | 0.212 → 0.212 | +0.0 |
| unified4 | qwen | state_path | 80 | 0.588 → 0.588 | +0.0 | 0.325 → 0.263 | -6.2 |
| unified4 | qwen | vanilla_vector | 80 | 0.487 → 0.487 | +0.0 | 0.438 → 0.438 | +0.0 |
| unified4 | qwen | vision_only | 80 | 0.575 → 0.575 | +0.0 | 0.388 → 0.388 | +0.0 |

## Flipped step results (33)

| group | model | backend | file | scenario | step | match old→new | hall old→new | response |
|---|---|---|---|---|---|---|---|---|
| unified4 | claude | full_system | run_claude_unified4_r1_20260807T072511.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼(초록색 위쪽 화살표 아이콘, 툴바 상단)을 클릭하여 Create New Survey 다이얼로그를 여세요.` |
| unified4 | claude | state_path | run_claude_unified4_r1_20260807T072511.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `오른쪽 툴바에서 **Add (+) 버튼** (가장 위의 녹색 + 아이콘)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | claude | full_system | run_claude_unified4_r3_20260807T084832.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `새 survey를 추가하기 위해 툴바의 **Add (+) 버튼** (상단 녹색 + 아이콘)을 클릭하세요.` |
| unified4 | claude | state_path | run_claude_unified4_r3_20260807T084832.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `툴바에서 Add (+) 버튼(녹색 위쪽 화살표 아이콘, 가장 상단)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | claude | no_rag | run_claude_unified4_r4_20260807T093052.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `새 Survey를 생성하기 위해 툴바의 "Add" (녹색 + 아이콘) 버튼을 클릭하세요.` |
| unified4 | claude | full_system | run_claude_unified4_r4_20260807T093052.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `새 survey를 생성하기 위해 툴바의 **Add(+) 버튼** (상단 녹색 + 아이콘)을 클릭하세요.` |
| unified4 | claude | state_path | run_claude_unified4_r4_20260807T093052.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `오른쪽 툴바에서 Add (+) 버튼(상단 녹색 화살표 아이콘)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | claude | full_system | run_claude_unified4_r5_20260807T101322.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `새 survey를 추가하기 위해 툴바에서 **Add (+) 버튼** (녹색 위쪽 화살표 아이콘, 가장 상단)을 클릭하세요.` |
| unified4 | claude | state_path | run_claude_unified4_r5_20260807T101322.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `오른쪽 툴바 상단의 **Add (+) 버튼** (녹색 상향 화살표 아이콘)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | gemini | state_path | run_gemini_unified4_r1_20260807T023501.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add(+) 아이콘을 클릭하세요.` |
| unified4 | gemini | state_path | run_gemini_unified4_r2_20260807T033321.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add(+) 버튼을 클릭하세요.` |
| unified4 | gemini | state_path | run_gemini_unified4_r4_20260807T052902.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add(+) 아이콘을 클릭하세요.` |
| unified4 | gemini | state_path | run_gemini_unified4_r5_20260807T062650.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 아이콘을 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r1_20260807T105516.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r1_20260807T105516.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | full_system | run_gpt_unified4_r2_20260807T113738.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r2_20260807T113738.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | full_system | run_gpt_unified4_r3_20260807T121717.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r3_20260807T121717.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | full_system | run_gpt_unified4_r4_20260807T130044.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r4_20260807T130044.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | full_system | run_gpt_unified4_r5_20260807T134308.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r5_20260807T134308.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | qwen | full_system | run_qwen_unified4_r1_20260807T142449.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Survey Setup and Selection 창에서 'Add (+)' 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
| unified4 | qwen | state_path | run_qwen_unified4_r1_20260807T142449.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Survey Setup and Selection 창에서 Add (+) 버튼을 클릭합니다.` |
| unified4 | qwen | full_system | run_qwen_unified4_r2_20260807T151241.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼 클릭하여 새 Survey 생성 창 열기` |
| unified4 | qwen | state_path | run_qwen_unified4_r2_20260807T151241.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Survey Setup and Selection 창에서 Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
| unified4 | qwen | full_system | run_qwen_unified4_r3_20260807T155946.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기` |
| unified4 | qwen | state_path | run_qwen_unified4_r3_20260807T155946.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Survey Setup and Selection 창에서 Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
| unified4 | qwen | full_system | run_qwen_unified4_r4_20260807T164820.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | qwen | state_path | run_qwen_unified4_r4_20260807T164820.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기` |
| unified4 | qwen | full_system | run_qwen_unified4_r5_20260807T173614.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Add (+) 버튼 클릭하여 새 Survey 생성 창 열기` |
| unified4 | qwen | state_path | run_qwen_unified4_r5_20260807T173614.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Survey Setup and Selection 창에서 Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
