# Re-score with old vs new GT (v3 scorer) — old = 44fa1ab~1, new = working tree

Files: 4. Metrics per (group, model, backend): step matches and hallucination flags summed over scenarios × steps × replicates.

| group | model | backend | n steps | step_acc old → new | Δpp | hall rate old → new | Δpp |
|---|---|---|---|---|---|---|---|
| dev_iter4 | claude | full_system | 16 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | claude | no_rag | 16 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | claude | vanilla_budget | 16 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | claude | vanilla_vector | 16 | 0.812 → 0.812 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | gemini | full_system | 32 | 0.781 → 0.781 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | gemini | no_rag | 32 | 0.656 → 0.656 | +0.0 | 0.094 → 0.031 | -6.2 |
| dev_iter4 | gemini | vanilla_budget | 32 | 0.719 → 0.719 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | gemini | vanilla_vector | 32 | 0.719 → 0.719 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | gpt | full_system | 16 | 0.875 → 0.875 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | gpt | no_rag | 16 | 0.750 → 0.750 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | gpt | vanilla_budget | 16 | 0.688 → 0.688 | +0.0 | 0.125 → 0.062 | -6.2 |
| dev_iter4 | gpt | vanilla_vector | 16 | 0.875 → 0.875 | +0.0 | 0.125 → 0.062 | -6.2 |

## Flipped step results (16)

| group | model | backend | file | scenario | step | match old→new | hall old→new | response |
|---|---|---|---|---|---|---|---|---|
| dev_iter4 | claude | no_rag | dev_iter4_v3_claude_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그의 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭한다` |
| dev_iter4 | claude | vanilla_vector | dev_iter4_v3_claude_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그에서 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하` |
| dev_iter4 | claude | vanilla_budget | dev_iter4_v3_claude_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하세요.` |
| dev_iter4 | claude | full_system | dev_iter4_v3_claude_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `"Save Attribute as" 다이얼로그의 Name 필드에 'my first attribute set'이 이미 입력되어 있으므로 **OK** 버튼을 클릭하세` |
| dev_iter4 | gemini | no_rag | dev_iter4_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter4 | gemini | vanilla_vector | dev_iter4_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하십시오.` |
| dev_iter4 | gemini | vanilla_budget | dev_iter4_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| dev_iter4 | gemini | full_system | dev_iter4_v3_gemini_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter4 | gemini | no_rag | dev_iter4_v3_gemini_r1.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter4 | gemini | vanilla_vector | dev_iter4_v3_gemini_r1.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| dev_iter4 | gemini | vanilla_budget | dev_iter4_v3_gemini_r1.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭합니다.` |
| dev_iter4 | gemini | full_system | dev_iter4_v3_gemini_r1.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter4 | gpt | no_rag | dev_iter4_v3_gpt_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭.` |
| dev_iter4 | gpt | vanilla_vector | dev_iter4_v3_gpt_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 버튼을 클릭하세요.` |
| dev_iter4 | gpt | vanilla_budget | dev_iter4_v3_gpt_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK를 클릭하세요.` |
| dev_iter4 | gpt | full_system | dev_iter4_v3_gpt_r0.json | attribute_computation__01 | 4 | ✓→✓ | ✓→✗ | `OK 클릭하세요.` |
