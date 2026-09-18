# Session-state leakage check — replay with stubs (no API), bench dev_iter4_v3_gemini_r0.json

| scenario | backend | order | steps with identical context vs alone | steps with identical rerank prompt vs alone | first differing step |
|---|---|---|---|---|---|
| 3d_visualization__01 | no_rag | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| 3d_visualization__01 | vanilla_vector | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| 3d_visualization__01 | vanilla_budget | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| 3d_visualization__01 | full_system | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| 3d_visualization__01 | full_system | fs→vv | 4/4 | 4/4 | — |
| 3d_visualization__01 | vanilla_vector | fs→vv | 4/4 | 4/4 | — |
| 3d_visualization__01 | vanilla_vector | vv→fs | 4/4 | 4/4 | — |
| 3d_visualization__01 | full_system | vv→fs | 4/4 | 4/4 | — |
| attribute_computation__01 | no_rag | bench order (no_rag→vv→vb→fs) | 8/8 | 8/8 | — |
| attribute_computation__01 | vanilla_vector | bench order (no_rag→vv→vb→fs) | 8/8 | 8/8 | — |
| attribute_computation__01 | vanilla_budget | bench order (no_rag→vv→vb→fs) | 8/8 | 8/8 | — |
| attribute_computation__01 | full_system | bench order (no_rag→vv→vb→fs) | 8/8 | 8/8 | — |
| attribute_computation__01 | full_system | fs→vv | 8/8 | 8/8 | — |
| attribute_computation__01 | vanilla_vector | fs→vv | 8/8 | 8/8 | — |
| attribute_computation__01 | vanilla_vector | vv→fs | 8/8 | 8/8 | — |
| attribute_computation__01 | full_system | vv→fs | 8/8 | 8/8 | — |
| survey_setup__01 | no_rag | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| survey_setup__01 | vanilla_vector | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| survey_setup__01 | vanilla_budget | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| survey_setup__01 | full_system | bench order (no_rag→vv→vb→fs) | 4/4 | 4/4 | — |
| survey_setup__01 | full_system | fs→vv | 4/4 | 4/4 | — |
| survey_setup__01 | vanilla_vector | fs→vv | 4/4 | 4/4 | — |
| survey_setup__01 | vanilla_vector | vv→fs | 4/4 | 4/4 | — |
| survey_setup__01 | full_system | vv→fs | 4/4 | 4/4 | — |

No difference: context blocks and rerank prompts are identical whether a backend runs alone or after other backends.
