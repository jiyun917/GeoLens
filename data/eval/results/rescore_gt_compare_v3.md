# Re-score with old vs new GT (v3 scorer) — old = 44fa1ab~1, new = working tree

Files: 23. Metrics per (group, model, backend): step matches and hallucination flags summed over scenarios × steps × replicates.

| group | model | backend | n steps | step_acc old → new | Δpp | hall rate old → new | Δpp |
|---|---|---|---|---|---|---|---|
| dev_iter0 | gemini | full_system | 16 | 0.750 → 0.750 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter0 | gemini | no_rag | 16 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter0 | gemini | vanilla_budget | 16 | 0.750 → 0.750 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter0 | gemini | vanilla_vector | 16 | 0.688 → 0.688 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter1 | gemini | full_system | 16 | 0.938 → 0.938 | +0.0 | 0.062 → 0.000 | -6.2 |
| dev_iter1 | gemini | no_rag | 16 | 0.750 → 0.750 | +0.0 | 0.062 → 0.000 | -6.2 |
| dev_iter1 | gemini | vanilla_budget | 16 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter1 | gemini | vanilla_vector | 16 | 0.750 → 0.750 | +0.0 | 0.125 → 0.062 | -6.2 |
| latency_baseline | ? | full_system | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| latency_baseline | ? | vanilla_budget | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| latency_baseline | ? | vanilla_vector | 4 | 1.000 → 1.000 | +0.0 | 0.000 → 0.000 | +0.0 |
| unified4 | claude | full_system | 80 | 0.812 → 0.812 | +0.0 | 0.125 → 0.113 | -1.2 |
| unified4 | claude | graph_only | 80 | 0.787 → 0.787 | +0.0 | 0.125 → 0.062 | -6.2 |
| unified4 | claude | no_rag | 80 | 0.812 → 0.812 | +0.0 | 0.163 → 0.100 | -6.2 |
| unified4 | claude | state_path | 80 | 0.812 → 0.812 | +0.0 | 0.125 → 0.113 | -1.2 |
| unified4 | claude | vanilla_vector | 80 | 0.812 → 0.812 | +0.0 | 0.138 → 0.075 | -6.2 |
| unified4 | claude | vision_only | 80 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| unified4 | gemini | full_system | 80 | 0.838 → 0.838 | +0.0 | 0.087 → 0.025 | -6.2 |
| unified4 | gemini | graph_only | 80 | 0.800 → 0.800 | +0.0 | 0.125 → 0.062 | -6.2 |
| unified4 | gemini | no_rag | 80 | 0.738 → 0.738 | +0.0 | 0.087 → 0.025 | -6.2 |
| unified4 | gemini | state_path | 80 | 0.887 → 0.887 | +0.0 | 0.087 → 0.075 | -1.2 |
| unified4 | gemini | vanilla_vector | 80 | 0.750 → 0.750 | +0.0 | 0.113 → 0.050 | -6.2 |
| unified4 | gemini | vision_only | 80 | 0.875 → 0.875 | +0.0 | 0.100 → 0.037 | -6.2 |
| unified4 | gpt | full_system | 80 | 0.812 → 0.812 | +0.0 | 0.125 → 0.125 | +0.0 |
| unified4 | gpt | graph_only | 80 | 0.787 → 0.787 | +0.0 | 0.125 → 0.062 | -6.2 |
| unified4 | gpt | no_rag | 80 | 0.688 → 0.688 | +0.0 | 0.138 → 0.075 | -6.2 |
| unified4 | gpt | state_path | 80 | 0.800 → 0.800 | +0.0 | 0.138 → 0.138 | +0.0 |
| unified4 | gpt | vanilla_vector | 80 | 0.775 → 0.775 | +0.0 | 0.150 → 0.087 | -6.2 |
| unified4 | gpt | vision_only | 80 | 0.662 → 0.662 | +0.0 | 0.163 → 0.125 | -3.8 |
| unified4 | qwen | full_system | 80 | 0.487 → 0.487 | +0.0 | 0.237 → 0.300 | +6.2 |
| unified4 | qwen | graph_only | 80 | 0.487 → 0.487 | +0.0 | 0.300 → 0.300 | +0.0 |
| unified4 | qwen | no_rag | 80 | 0.475 → 0.475 | +0.0 | 0.225 → 0.212 | -1.2 |
| unified4 | qwen | state_path | 80 | 0.588 → 0.588 | +0.0 | 0.263 → 0.325 | +6.2 |
| unified4 | qwen | vanilla_vector | 80 | 0.487 → 0.487 | +0.0 | 0.450 → 0.438 | -1.2 |
| unified4 | qwen | vision_only | 80 | 0.575 → 0.575 | +0.0 | 0.388 → 0.388 | +0.0 |

## Flipped step results (132)

| group | model | backend | file | scenario | step | match old→new | hall old→new | response |
|---|---|---|---|---|---|---|---|---|
| unified4 | claude | no_rag | run_claude_unified4_r1_20260807T072511.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'Save Attribute as' 다이얼로그의 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하세` |
| unified4 | claude | vanilla_vector | run_claude_unified4_r1_20260807T072511.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 입력되어 있으므로 OK 버튼을 클릭합니다.` |
| unified4 | claude | graph_only | run_claude_unified4_r1_20260807T072511.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하` |
| unified4 | claude | vision_only | run_claude_unified4_r1_20260807T072511.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그의 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하세` |
| unified4 | claude | full_system | run_claude_unified4_r1_20260807T072511.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | state_path | run_claude_unified4_r1_20260807T072511.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `Name 필드에 'my first attribute set'이 입력되어 있으므로 **OK** 버튼을 클릭하세요.` |
| unified4 | claude | full_system | run_claude_unified4_r1_20260807T072511.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼(초록색 위쪽 화살표 아이콘, 툴바 상단)을 클릭하여 Create New Survey 다이얼로그를 여세요.` |
| unified4 | claude | state_path | run_claude_unified4_r1_20260807T072511.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `오른쪽 툴바에서 **Add (+) 버튼** (가장 위의 녹색 + 아이콘)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | claude | no_rag | run_claude_unified4_r2_20260807T080539.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 OK 버튼을 클릭하세요.` |
| unified4 | claude | vanilla_vector | run_claude_unified4_r2_20260807T080539.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그의 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합니` |
| unified4 | claude | graph_only | run_claude_unified4_r2_20260807T080539.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | vision_only | run_claude_unified4_r2_20260807T080539.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 입력된 상태이므로 **OK** 버튼을 클릭하세요.` |
| unified4 | claude | full_system | run_claude_unified4_r2_20260807T080539.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하` |
| unified4 | claude | state_path | run_claude_unified4_r2_20260807T080539.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 입력되어 있으므로 **OK 버튼을 클릭**하세요.` |
| unified4 | claude | no_rag | run_claude_unified4_r3_20260807T084832.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | vanilla_vector | run_claude_unified4_r3_20260807T084832.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하세요.` |
| unified4 | claude | graph_only | run_claude_unified4_r3_20260807T084832.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하` |
| unified4 | claude | vision_only | run_claude_unified4_r3_20260807T084832.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | full_system | run_claude_unified4_r3_20260807T084832.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK 버튼을 클릭**합` |
| unified4 | claude | state_path | run_claude_unified4_r3_20260807T084832.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK 버튼을 클릭**하` |
| unified4 | claude | full_system | run_claude_unified4_r3_20260807T084832.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `새 survey를 추가하기 위해 툴바의 **Add (+) 버튼** (상단 녹색 + 아이콘)을 클릭하세요.` |
| unified4 | claude | state_path | run_claude_unified4_r3_20260807T084832.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `툴바에서 Add (+) 버튼(녹색 위쪽 화살표 아이콘, 가장 상단)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | claude | no_rag | run_claude_unified4_r4_20260807T093052.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 OK 버튼을 클릭하세요.` |
| unified4 | claude | vanilla_vector | run_claude_unified4_r4_20260807T093052.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로, OK 버튼을 클릭합니다.` |
| unified4 | claude | graph_only | run_claude_unified4_r4_20260807T093052.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | vision_only | run_claude_unified4_r4_20260807T093052.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하` |
| unified4 | claude | full_system | run_claude_unified4_r4_20260807T093052.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | state_path | run_claude_unified4_r4_20260807T093052.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하` |
| unified4 | claude | no_rag | run_claude_unified4_r4_20260807T093052.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `새 Survey를 생성하기 위해 툴바의 "Add" (녹색 + 아이콘) 버튼을 클릭하세요.` |
| unified4 | claude | full_system | run_claude_unified4_r4_20260807T093052.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `새 survey를 생성하기 위해 툴바의 **Add(+) 버튼** (상단 녹색 + 아이콘)을 클릭하세요.` |
| unified4 | claude | state_path | run_claude_unified4_r4_20260807T093052.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `오른쪽 툴바에서 Add (+) 버튼(상단 녹색 화살표 아이콘)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | claude | no_rag | run_claude_unified4_r5_20260807T101322.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 OK 버튼을 클릭하세요.` |
| unified4 | claude | vanilla_vector | run_claude_unified4_r5_20260807T101322.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합니다.` |
| unified4 | claude | graph_only | run_claude_unified4_r5_20260807T101322.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | vision_only | run_claude_unified4_r5_20260807T101322.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭합` |
| unified4 | claude | full_system | run_claude_unified4_r5_20260807T101322.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하` |
| unified4 | claude | state_path | run_claude_unified4_r5_20260807T101322.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK 버튼을 클릭**합` |
| unified4 | claude | no_rag | run_claude_unified4_r5_20260807T101322.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `새 Survey를 생성하기 위해 툴바의 "Add new survey" 버튼(+ 아이콘)을 클릭하세요.` |
| unified4 | claude | full_system | run_claude_unified4_r5_20260807T101322.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `새 survey를 추가하기 위해 툴바에서 **Add (+) 버튼** (녹색 위쪽 화살표 아이콘, 가장 상단)을 클릭하세요.` |
| unified4 | claude | state_path | run_claude_unified4_r5_20260807T101322.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `오른쪽 툴바 상단의 **Add (+) 버튼** (녹색 상향 화살표 아이콘)을 클릭하여 Create New Survey 다이얼로그를 엽니다.` |
| unified4 | gemini | no_rag | run_gemini_unified4_r1_20260807T023501.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | vanilla_vector | run_gemini_unified4_r1_20260807T023501.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | graph_only | run_gemini_unified4_r1_20260807T023501.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭하세요.` |
| unified4 | gemini | vision_only | run_gemini_unified4_r1_20260807T023501.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | full_system | run_gemini_unified4_r1_20260807T023501.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| unified4 | gemini | state_path | run_gemini_unified4_r1_20260807T023501.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | state_path | run_gemini_unified4_r1_20260807T023501.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add(+) 아이콘을 클릭하세요.` |
| unified4 | gemini | no_rag | run_gemini_unified4_r2_20260807T033321.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | vanilla_vector | run_gemini_unified4_r2_20260807T033321.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭합니다.` |
| unified4 | gemini | graph_only | run_gemini_unified4_r2_20260807T033321.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | vision_only | run_gemini_unified4_r2_20260807T033321.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | full_system | run_gemini_unified4_r2_20260807T033321.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| unified4 | gemini | state_path | run_gemini_unified4_r2_20260807T033321.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | state_path | run_gemini_unified4_r2_20260807T033321.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add(+) 버튼을 클릭하세요.` |
| unified4 | gemini | no_rag | run_gemini_unified4_r3_20260807T043128.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| unified4 | gemini | vanilla_vector | run_gemini_unified4_r3_20260807T043128.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | graph_only | run_gemini_unified4_r3_20260807T043128.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하십시오.` |
| unified4 | gemini | vision_only | run_gemini_unified4_r3_20260807T043128.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭하세요.` |
| unified4 | gemini | full_system | run_gemini_unified4_r3_20260807T043128.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| unified4 | gemini | state_path | run_gemini_unified4_r3_20260807T043128.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | no_rag | run_gemini_unified4_r4_20260807T052902.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| unified4 | gemini | vanilla_vector | run_gemini_unified4_r4_20260807T052902.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | graph_only | run_gemini_unified4_r4_20260807T052902.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | vision_only | run_gemini_unified4_r4_20260807T052902.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | full_system | run_gemini_unified4_r4_20260807T052902.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| unified4 | gemini | state_path | run_gemini_unified4_r4_20260807T052902.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | state_path | run_gemini_unified4_r4_20260807T052902.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add(+) 아이콘을 클릭하세요.` |
| unified4 | gemini | no_rag | run_gemini_unified4_r5_20260807T062650.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | vanilla_vector | run_gemini_unified4_r5_20260807T062650.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | graph_only | run_gemini_unified4_r5_20260807T062650.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | vision_only | run_gemini_unified4_r5_20260807T062650.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | full_system | run_gemini_unified4_r5_20260807T062650.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| unified4 | gemini | state_path | run_gemini_unified4_r5_20260807T062650.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭합니다.` |
| unified4 | gemini | state_path | run_gemini_unified4_r5_20260807T062650.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 아이콘을 클릭하세요.` |
| unified4 | gpt | no_rag | run_gpt_unified4_r1_20260807T105516.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | vanilla_vector | run_gpt_unified4_r1_20260807T105516.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭하세요.` |
| unified4 | gpt | graph_only | run_gpt_unified4_r1_20260807T105516.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `이름에 'my first attribute set'을 입력하고 OK를 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r1_20260807T105516.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK를 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r1_20260807T105516.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r1_20260807T105516.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add 버튼을 클릭하여 Create New Survey 다이얼로그를 여세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r1_20260807T105516.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | no_rag | run_gpt_unified4_r2_20260807T113738.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | vanilla_vector | run_gpt_unified4_r2_20260807T113738.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭.` |
| unified4 | gpt | graph_only | run_gpt_unified4_r2_20260807T113738.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭.` |
| unified4 | gpt | full_system | run_gpt_unified4_r2_20260807T113738.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r2_20260807T113738.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK를 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r2_20260807T113738.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r2_20260807T113738.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | no_rag | run_gpt_unified4_r3_20260807T121717.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | vanilla_vector | run_gpt_unified4_r3_20260807T121717.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭하세요.` |
| unified4 | gpt | graph_only | run_gpt_unified4_r3_20260807T121717.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭하세요.` |
| unified4 | gpt | vision_only | run_gpt_unified4_r3_20260807T121717.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r3_20260807T121717.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 클릭.` |
| unified4 | gpt | state_path | run_gpt_unified4_r3_20260807T121717.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK를 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r3_20260807T121717.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r3_20260807T121717.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | no_rag | run_gpt_unified4_r4_20260807T130044.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭하세요.` |
| unified4 | gpt | vanilla_vector | run_gpt_unified4_r4_20260807T130044.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭하세요.` |
| unified4 | gpt | graph_only | run_gpt_unified4_r4_20260807T130044.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | vision_only | run_gpt_unified4_r4_20260807T130044.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭.` |
| unified4 | gpt | full_system | run_gpt_unified4_r4_20260807T130044.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `이름 입력란에 'my first attribute set' 입력 후 OK 클릭.` |
| unified4 | gpt | state_path | run_gpt_unified4_r4_20260807T130044.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r4_20260807T130044.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r4_20260807T130044.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭합니다.` |
| unified4 | gpt | no_rag | run_gpt_unified4_r5_20260807T134308.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `이름 칸에 'my first attribute set'을 입력한 다음 OK를 클릭하세요.` |
| unified4 | gpt | vanilla_vector | run_gpt_unified4_r5_20260807T134308.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭.` |
| unified4 | gpt | graph_only | run_gpt_unified4_r5_20260807T134308.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK를 클릭하세요.` |
| unified4 | gpt | vision_only | run_gpt_unified4_r5_20260807T134308.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r5_20260807T134308.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r5_20260807T134308.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK'를 클릭하세요.` |
| unified4 | gpt | full_system | run_gpt_unified4_r5_20260807T134308.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | gpt | state_path | run_gpt_unified4_r5_20260807T134308.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | qwen | vanilla_vector | run_qwen_unified4_r1_20260807T142449.json | survey_setup__01 | 0 | ✓→✓ | ✓→✗ | `Survey Setup and Selection 창에서 'My_New_Survey'를 선택하고 Select 버튼 클릭.` |
| unified4 | qwen | full_system | run_qwen_unified4_r1_20260807T142449.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Survey Setup and Selection 창에서 'Add (+)' 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
| unified4 | qwen | state_path | run_qwen_unified4_r1_20260807T142449.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Survey Setup and Selection 창에서 Add (+) 버튼을 클릭합니다.` |
| unified4 | qwen | full_system | run_qwen_unified4_r2_20260807T151241.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼 클릭하여 새 Survey 생성 창 열기` |
| unified4 | qwen | state_path | run_qwen_unified4_r2_20260807T151241.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Survey Setup and Selection 창에서 Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
| unified4 | qwen | no_rag | run_qwen_unified4_r3_20260807T155946.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'Energy [-28,+28]'를 Attributes (on-the-fly)에서 선택하고 OK 클릭하여 Inline 250에 Energy 속성 색상 매핑 완료.` |
| unified4 | qwen | full_system | run_qwen_unified4_r3_20260807T155946.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기` |
| unified4 | qwen | state_path | run_qwen_unified4_r3_20260807T155946.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Survey Setup and Selection 창에서 Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
| unified4 | qwen | full_system | run_qwen_unified4_r4_20260807T164820.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼을 클릭하세요.` |
| unified4 | qwen | state_path | run_qwen_unified4_r4_20260807T164820.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기` |
| unified4 | qwen | full_system | run_qwen_unified4_r5_20260807T173614.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Add (+) 버튼 클릭하여 새 Survey 생성 창 열기` |
| unified4 | qwen | state_path | run_qwen_unified4_r5_20260807T173614.json | survey_setup__01 | 0 | ✓→✓ | ✗→✓ | `Survey Setup and Selection 창에서 Add (+) 버튼 클릭하여 Create New Survey 다이얼로그 열기.` |
| dev_iter0 | gemini | no_rag | dev_iter0_v2mech_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter0 | gemini | vanilla_vector | dev_iter0_v2mech_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭합니다.` |
| dev_iter0 | gemini | vanilla_budget | dev_iter0_v2mech_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter0 | gemini | full_system | dev_iter0_v2mech_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter1 | gemini | no_rag | dev_iter1_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter1 | gemini | vanilla_vector | dev_iter1_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| dev_iter1 | gemini | vanilla_budget | dev_iter1_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| dev_iter1 | gemini | full_system | dev_iter1_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `'OK' 버튼을 클릭하세요.` |
