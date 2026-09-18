# routing dry-run v3 — routing_dryrun_v3_iter3_x5

code: 820e9933a6029bb01040f72f6740c424a4a755c8 dirty=False; knobs: {"AUX_THINKING_BUDGET": "0", "CHROMADB_PATH": "C:/Users/user/Downloads/GeoLens-paper/data/chromadb_v4", "CONFIDENCE_THRESHOLD": "0.7", "EMBED_MODEL": "BAAI/bge-m3", "FALLBACK_CTX_CHARS": "3900", "GEN_PROMPT_VERSION": null, "GOAL_STATE_HINT": null, "GRAPH_VECTOR_AUX": "0", "PARALLEL_RETRIEVAL": "1", "POST_COMPLETION_MODE": "soft", "RAG_KG_ENABLED": "0", "RERANK_PROMPT_VERSION": "v3", "ROUTED_VECTOR_QUERY": "goal", "ROUTER_EVIDENCE_GATE": null, "ROUTER_GRAPH_PRIOR": "1", "ROUTER_MATCHER": "embedding", "ROUTER_POOL_K": "5", "ROUTER_TWO_STAGE": null, "VISION_PROMPT_VERSION": "v3"}

## rep 0: correct 14/16; fallback 0; goal-state hints 5

| scenario | step | expected | picked | conf | gate | goal_state | ok | candidates (source:score) | rerank raw |
|---|---|---|---|---|---|---|---|---|---|
| survey_setup__01 | 0 | survey_setup | survey_setup_01_open_selection | 0.95 |  |  | ✓ | 01_open_selection[emb:0.79]; 02_open_new_survey_dialog[emb:0.73]; 05_select_survey[emb:0.68]; 01_data_load[emb:0.67]; 03_choose_initial_setup[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.87] | `{"id": "survey_setup_01_open_selection", "confidence": 0.95}` |
| survey_setup__01 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 02_open_new_survey_dialog[prior:1.00,emb:0.83]; 01_open_selection[prior:1.00,emb:0.75]; 03_choose_initial_setup[emb:0.75]; 05_select_survey[emb:0.69]; 01_data_load[emb:0.65]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{
  "id": "survey_setup_03_choose_initial_setup",
  "confide` |
| survey_setup__01 | 2 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 04_scan_segy[prior:1.00,emb:0.65]; 05_select_survey[prior:1.00,emb:0.74]; 03_choose_initial_setup[prior:1.00,emb:0.78]; 02_open_new_survey_dialog[emb:0.82]; 01_open_selection[emb:0.76]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{"id": "survey_setup_03_choose_initial_setup", "confidence":` |
| survey_setup__01 | 3 | survey_setup | survey_setup_05_select_survey | 0.90 |  | survey_setup_05_select_survey | ✓ | 04_scan_segy[prior:1.00]; 05_select_survey[prior:1.00,emb:0.70]; 03_choose_initial_setup[prior:1.00]; 01_main_window_ready[emb:0.66,clip:0.75]; 01_open_selection[emb:0.66]; 04_add_zslice[emb:0.66]; 02_open_new_survey_dialog[emb:0.64]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "survey_setup_05_select_survey", "confidence": 0.9}` |
| 3d_visualization__01 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 |  |  | ✓ | 05_select_survey[emb:0.74]; 01_main_window_ready[emb:0.72,clip:0.76]; 04_add_zslice[emb:0.69]; 01_open_selection[emb:0.69]; 05_all_slices_displayed[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "d3_visualization_01_main_window_ready", "confidence"` |
| 3d_visualization__01 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.90 |  |  | ✓ | 02_add_inline[prior:1.00]; 01_main_window_ready[prior:1.00,emb:0.71,clip:0.75]; 05_select_survey[emb:0.74]; 04_add_zslice[emb:0.72]; 01_open_selection[emb:0.71]; 03_add_crossline[emb:0.71]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{
  "id": "d3_visualization_02_add_inline",
  "confidence": ` |
| 3d_visualization__01 | 2 | d3_visualization | d3_visualization_03_add_crossline | 0.70 |  |  | ✓ | 03_add_crossline[prior:1.00]; 02_add_inline[prior:1.00]; 05_select_survey[emb:0.72]; 01_main_window_ready[emb:0.71,clip:0.82]; 01_open_selection[emb:0.69]; 04_add_zslice[emb:0.67]; 05_all_slices_displayed[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.83]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{
  "id": "d3_visualization_03_add_crossline",
  "confidence` |
| 3d_visualization__01 | 3 | d3_visualization | d3_visualization_04_add_zslice | 0.90 |  | d3_visualization_04_add_zslice | ✓ | 04_add_zslice[prior:1.00,emb:0.68]; 03_add_crossline[prior:1.00]; 05_select_survey[emb:0.68]; 01_main_window_ready[emb:0.67,clip:0.79]; 01_open_selection[emb:0.66]; 01_data_load[emb:0.63]; _follow_along_implementing_a_systematic_s_03[clip:0.81]; _follow_along_implementing_a_systematic_s_02[clip:0.81] | `{
  "id": "d3_visualization_04_add_zslice",
  "confidence": ` |
| attribute_computation__01 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_04_configure | 0.90 |  |  | ✗ | 02_open_attribute_tool[emb:0.81]; 04_configure[emb:0.74]; 01_ready_to_start[emb:0.74]; 03_select_type[emb:0.70]; 04_add_zslice[emb:0.69]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.88] | `{"id": "seismic_attribute_04_configure", "confidence": 0.9}` |
| attribute_computation__01 | 1 | seismic_attribute_03_select_type | seismic_attribute_04_configure | 0.95 |  |  | ✗ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.79]; 03_select_type[emb:0.74]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 2 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.79]; 03_select_type[emb:0.74]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 3 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.77]; 03_select_type[emb:0.75]; 01_ready_to_start[emb:0.72]; 04_add_zslice[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 4 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.77]; 02_open_attribute_tool[emb:0.76]; 01_ready_to_start[emb:0.71]; 03_select_type[emb:0.69]; 01_open_selection[emb:0.65]; _follow_along_implementing_a_systematic_s_03[clip:0.91]; 01_main_window_ready[clip:0.90] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 5 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00]; 03_add_crossline[emb:0.68]; 04_add_zslice[emb:0.68]; 01_main_window_ready[emb:0.68,clip:0.82]; 01_open_selection[emb:0.66]; 05_select_survey[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.82] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |
| attribute_computation__01 | 6 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 01_open_selection[emb:0.72]; 05_select_survey[emb:0.70]; 04_add_zslice[emb:0.69]; 01_main_window_ready[emb:0.69,clip:0.85]; 01_data_load[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.87] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |
| attribute_computation__01 | 7 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 04_add_zslice[emb:0.70]; 01_main_window_ready[emb:0.70,clip:0.82]; 03_add_crossline[emb:0.70]; 05_select_survey[emb:0.67]; 02_add_inline[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.82]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |

## rep 1: correct 14/16; fallback 0; goal-state hints 5

| scenario | step | expected | picked | conf | gate | goal_state | ok | candidates (source:score) | rerank raw |
|---|---|---|---|---|---|---|---|---|---|
| survey_setup__01 | 0 | survey_setup | survey_setup_01_open_selection | 0.95 |  |  | ✓ | 01_open_selection[emb:0.79]; 02_open_new_survey_dialog[emb:0.73]; 05_select_survey[emb:0.68]; 01_data_load[emb:0.67]; 03_choose_initial_setup[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.87] | `{"id": "survey_setup_01_open_selection", "confidence": 0.95}` |
| survey_setup__01 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 02_open_new_survey_dialog[prior:1.00,emb:0.83]; 01_open_selection[prior:1.00,emb:0.75]; 03_choose_initial_setup[emb:0.76]; 05_select_survey[emb:0.69]; 04_scan_segy[emb:0.65]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{
  "id": "survey_setup_03_choose_initial_setup",
  "confide` |
| survey_setup__01 | 2 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 04_scan_segy[prior:1.00,emb:0.65]; 05_select_survey[prior:1.00,emb:0.74]; 03_choose_initial_setup[prior:1.00,emb:0.78]; 02_open_new_survey_dialog[emb:0.82]; 01_open_selection[emb:0.76]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{"id": "survey_setup_03_choose_initial_setup", "confidence":` |
| survey_setup__01 | 3 | survey_setup | survey_setup_05_select_survey | 0.90 |  | survey_setup_05_select_survey | ✓ | 04_scan_segy[prior:1.00]; 05_select_survey[prior:1.00,emb:0.70]; 03_choose_initial_setup[prior:1.00]; 01_main_window_ready[emb:0.66,clip:0.75]; 01_open_selection[emb:0.66]; 04_add_zslice[emb:0.66]; 02_open_new_survey_dialog[emb:0.64]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "survey_setup_05_select_survey", "confidence": 0.9}` |
| 3d_visualization__01 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 |  |  | ✓ | 05_select_survey[emb:0.74]; 01_main_window_ready[emb:0.72,clip:0.76]; 04_add_zslice[emb:0.69]; 01_open_selection[emb:0.69]; 05_all_slices_displayed[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "d3_visualization_01_main_window_ready", "confidence"` |
| 3d_visualization__01 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.90 |  |  | ✓ | 02_add_inline[prior:1.00]; 01_main_window_ready[prior:1.00,emb:0.71,clip:0.75]; 05_select_survey[emb:0.74]; 04_add_zslice[emb:0.72]; 01_open_selection[emb:0.71]; 03_add_crossline[emb:0.71]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "d3_visualization_02_add_inline", "confidence": 0.9}` |
| 3d_visualization__01 | 2 | d3_visualization | d3_visualization_03_add_crossline | 0.70 |  |  | ✓ | 03_add_crossline[prior:1.00]; 02_add_inline[prior:1.00]; 05_select_survey[emb:0.72]; 01_main_window_ready[emb:0.71,clip:0.82]; 01_open_selection[emb:0.69]; 04_add_zslice[emb:0.67]; 05_all_slices_displayed[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.83]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{
  "id": "d3_visualization_03_add_crossline",
  "confidence` |
| 3d_visualization__01 | 3 | d3_visualization | d3_visualization_04_add_zslice | 0.90 |  | d3_visualization_04_add_zslice | ✓ | 04_add_zslice[prior:1.00,emb:0.69]; 03_add_crossline[prior:1.00,emb:0.65]; 05_select_survey[emb:0.70]; 01_main_window_ready[emb:0.69,clip:0.79]; 01_open_selection[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.81]; _follow_along_implementing_a_systematic_s_02[clip:0.81] | `{
  "id": "d3_visualization_04_add_zslice",
  "confidence": ` |
| attribute_computation__01 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_03_select_type | 0.90 |  |  | ✗ | 02_open_attribute_tool[emb:0.81]; 04_configure[emb:0.74]; 01_ready_to_start[emb:0.74]; 03_select_type[emb:0.70]; 04_add_zslice[emb:0.69]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.88] | `{
  "id": "seismic_attribute_03_select_type",
  "confidence"` |
| attribute_computation__01 | 1 | seismic_attribute_03_select_type | seismic_attribute_04_configure | 0.90 |  |  | ✗ | 04_configure[prior:1.00,emb:0.76]; 03_select_type[prior:1.00,emb:0.74]; 02_open_attribute_tool[emb:0.79]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 2 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.79]; 03_select_type[emb:0.74]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 3 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.77]; 03_select_type[emb:0.75]; 01_ready_to_start[emb:0.72]; 04_add_zslice[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 4 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.77]; 02_open_attribute_tool[emb:0.77]; 01_ready_to_start[emb:0.71]; 03_select_type[emb:0.69]; 01_open_selection[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.91]; 01_main_window_ready[clip:0.90] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 5 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00]; 03_add_crossline[emb:0.68]; 04_add_zslice[emb:0.67]; 01_main_window_ready[emb:0.67,clip:0.82]; 01_open_selection[emb:0.66]; 02_add_inline[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.82] | `{
  "id": "seismic_attribute_06_display",
  "confidence": 0.` |
| attribute_computation__01 | 6 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 01_open_selection[emb:0.72]; 05_select_survey[emb:0.70]; 04_add_zslice[emb:0.69]; 01_main_window_ready[emb:0.69,clip:0.85]; 01_data_load[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.87] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |
| attribute_computation__01 | 7 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 04_add_zslice[emb:0.69]; 03_add_crossline[emb:0.69]; 01_main_window_ready[emb:0.69,clip:0.82]; 02_add_inline[emb:0.67]; 01_open_selection[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.82]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |

## rep 2: correct 14/16; fallback 0; goal-state hints 5

| scenario | step | expected | picked | conf | gate | goal_state | ok | candidates (source:score) | rerank raw |
|---|---|---|---|---|---|---|---|---|---|
| survey_setup__01 | 0 | survey_setup | survey_setup_01_open_selection | 0.95 |  |  | ✓ | 01_open_selection[emb:0.79]; 02_open_new_survey_dialog[emb:0.73]; 05_select_survey[emb:0.68]; 01_data_load[emb:0.67]; 03_choose_initial_setup[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.87] | `{"id": "survey_setup_01_open_selection", "confidence": 0.95}` |
| survey_setup__01 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 02_open_new_survey_dialog[prior:1.00,emb:0.83]; 01_open_selection[prior:1.00,emb:0.75]; 03_choose_initial_setup[emb:0.76]; 05_select_survey[emb:0.69]; 04_scan_segy[emb:0.65]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{
  "id": "survey_setup_03_choose_initial_setup",
  "confide` |
| survey_setup__01 | 2 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 04_scan_segy[prior:1.00,emb:0.66]; 05_select_survey[prior:1.00,emb:0.74]; 03_choose_initial_setup[prior:1.00,emb:0.79]; 02_open_new_survey_dialog[emb:0.83]; 01_open_selection[emb:0.74]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{
  "id": "survey_setup_03_choose_initial_setup",
  "confide` |
| survey_setup__01 | 3 | survey_setup | survey_setup_05_select_survey | 0.90 |  | survey_setup_05_select_survey | ✓ | 04_scan_segy[prior:1.00]; 05_select_survey[prior:1.00,emb:0.70]; 03_choose_initial_setup[prior:1.00]; 01_main_window_ready[emb:0.66,clip:0.75]; 01_open_selection[emb:0.66]; 04_add_zslice[emb:0.66]; 02_open_new_survey_dialog[emb:0.64]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "survey_setup_05_select_survey", "confidence": 0.9}` |
| 3d_visualization__01 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 |  |  | ✓ | 05_select_survey[emb:0.74]; 01_main_window_ready[emb:0.72,clip:0.76]; 04_add_zslice[emb:0.69]; 01_open_selection[emb:0.69]; 05_all_slices_displayed[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "d3_visualization_01_main_window_ready", "confidence"` |
| 3d_visualization__01 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.90 |  |  | ✓ | 02_add_inline[prior:1.00]; 01_main_window_ready[prior:1.00,emb:0.70,clip:0.75]; 05_select_survey[emb:0.73]; 04_add_zslice[emb:0.71]; 03_add_crossline[emb:0.71]; 01_open_selection[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{
  "id": "d3_visualization_02_add_inline",
  "confidence": ` |
| 3d_visualization__01 | 2 | d3_visualization | d3_visualization_03_add_crossline | 0.90 |  |  | ✓ | 03_add_crossline[prior:1.00,emb:0.66]; 02_add_inline[prior:1.00]; 01_main_window_ready[emb:0.72,clip:0.82]; 05_select_survey[emb:0.71]; 01_open_selection[emb:0.69]; 04_add_zslice[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.83]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{
  "id": "d3_visualization_03_add_crossline",
  "confidence` |
| 3d_visualization__01 | 3 | d3_visualization | d3_visualization_04_add_zslice | 0.90 |  | d3_visualization_04_add_zslice | ✓ | 04_add_zslice[prior:1.00,emb:0.68]; 03_add_crossline[prior:1.00]; 05_select_survey[emb:0.68]; 01_main_window_ready[emb:0.67,clip:0.79]; 01_open_selection[emb:0.66]; 01_data_load[emb:0.63]; _follow_along_implementing_a_systematic_s_03[clip:0.81]; _follow_along_implementing_a_systematic_s_02[clip:0.81] | `{
  "id": "d3_visualization_04_add_zslice",
  "confidence": ` |
| attribute_computation__01 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_03_select_type | 0.90 |  |  | ✗ | 02_open_attribute_tool[emb:0.81]; 04_configure[emb:0.74]; 01_ready_to_start[emb:0.74]; 03_select_type[emb:0.70]; 04_add_zslice[emb:0.69]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.88] | `{
  "id": "seismic_attribute_03_select_type",
  "confidence"` |
| attribute_computation__01 | 1 | seismic_attribute_03_select_type | seismic_attribute_04_configure | 0.90 |  |  | ✗ | 04_configure[prior:1.00,emb:0.76]; 03_select_type[prior:1.00,emb:0.74]; 02_open_attribute_tool[emb:0.79]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 2 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.79]; 03_select_type[emb:0.74]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 3 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.77]; 03_select_type[emb:0.76]; 01_ready_to_start[emb:0.72]; 04_add_zslice[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 4 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.77]; 02_open_attribute_tool[emb:0.76]; 01_ready_to_start[emb:0.71]; 03_select_type[emb:0.69]; 01_open_selection[emb:0.65]; _follow_along_implementing_a_systematic_s_03[clip:0.91]; 01_main_window_ready[clip:0.90] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 5 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00]; 03_add_crossline[emb:0.68]; 04_add_zslice[emb:0.67]; 01_main_window_ready[emb:0.67,clip:0.82]; 01_open_selection[emb:0.66]; 02_add_inline[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.82] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |
| attribute_computation__01 | 6 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 01_open_selection[emb:0.72]; 05_select_survey[emb:0.70]; 04_add_zslice[emb:0.70]; 01_data_load[emb:0.69]; 01_data_load[emb:0.69]; _follow_along_implementing_a_systematic_s_03[clip:0.87]; 01_main_window_ready[clip:0.85] | `{
  "id": "seismic_attribute_06_display",
  "confidence": 0.` |
| attribute_computation__01 | 7 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 04_add_zslice[emb:0.70]; 01_main_window_ready[emb:0.70,clip:0.82]; 03_add_crossline[emb:0.70]; 05_select_survey[emb:0.67]; 02_add_inline[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.82]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |

## rep 3: correct 14/16; fallback 0; goal-state hints 5

| scenario | step | expected | picked | conf | gate | goal_state | ok | candidates (source:score) | rerank raw |
|---|---|---|---|---|---|---|---|---|---|
| survey_setup__01 | 0 | survey_setup | survey_setup_01_open_selection | 0.95 |  |  | ✓ | 01_open_selection[emb:0.79]; 02_open_new_survey_dialog[emb:0.73]; 05_select_survey[emb:0.68]; 01_data_load[emb:0.67]; 03_choose_initial_setup[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.87] | `{"id": "survey_setup_01_open_selection", "confidence": 0.95}` |
| survey_setup__01 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 02_open_new_survey_dialog[prior:1.00,emb:0.83]; 01_open_selection[prior:1.00,emb:0.75]; 03_choose_initial_setup[emb:0.75]; 05_select_survey[emb:0.69]; 01_data_load[emb:0.65]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{
  "id": "survey_setup_03_choose_initial_setup",
  "confide` |
| survey_setup__01 | 2 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 04_scan_segy[prior:1.00,emb:0.65]; 05_select_survey[prior:1.00,emb:0.74]; 03_choose_initial_setup[prior:1.00,emb:0.78]; 02_open_new_survey_dialog[emb:0.82]; 01_open_selection[emb:0.76]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{"id": "survey_setup_03_choose_initial_setup", "confidence":` |
| survey_setup__01 | 3 | survey_setup | survey_setup_05_select_survey | 0.90 |  | survey_setup_05_select_survey | ✓ | 04_scan_segy[prior:1.00]; 05_select_survey[prior:1.00,emb:0.70]; 03_choose_initial_setup[prior:1.00]; 01_main_window_ready[emb:0.66,clip:0.75]; 01_open_selection[emb:0.66]; 04_add_zslice[emb:0.66]; 02_open_new_survey_dialog[emb:0.64]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "survey_setup_05_select_survey", "confidence": 0.9}` |
| 3d_visualization__01 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 |  |  | ✓ | 05_select_survey[emb:0.74]; 01_main_window_ready[emb:0.72,clip:0.76]; 04_add_zslice[emb:0.69]; 01_open_selection[emb:0.69]; 05_all_slices_displayed[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "d3_visualization_01_main_window_ready", "confidence"` |
| 3d_visualization__01 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.90 |  |  | ✓ | 02_add_inline[prior:1.00]; 01_main_window_ready[prior:1.00,emb:0.70,clip:0.75]; 05_select_survey[emb:0.73]; 04_add_zslice[emb:0.71]; 03_add_crossline[emb:0.71]; 01_open_selection[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{
  "id": "d3_visualization_02_add_inline",
  "confidence": ` |
| 3d_visualization__01 | 2 | d3_visualization | d3_visualization_03_add_crossline | 0.90 |  |  | ✓ | 03_add_crossline[prior:1.00,emb:0.66]; 02_add_inline[prior:1.00]; 01_main_window_ready[emb:0.72,clip:0.82]; 05_select_survey[emb:0.71]; 01_open_selection[emb:0.69]; 04_add_zslice[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.83]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{
  "id": "d3_visualization_03_add_crossline",
  "confidence` |
| 3d_visualization__01 | 3 | d3_visualization | d3_visualization_04_add_zslice | 0.90 |  | d3_visualization_04_add_zslice | ✓ | 04_add_zslice[prior:1.00,emb:0.68]; 03_add_crossline[prior:1.00]; 05_select_survey[emb:0.68]; 01_main_window_ready[emb:0.67,clip:0.79]; 01_open_selection[emb:0.66]; 01_data_load[emb:0.63]; _follow_along_implementing_a_systematic_s_03[clip:0.81]; _follow_along_implementing_a_systematic_s_02[clip:0.81] | `{
  "id": "d3_visualization_04_add_zslice",
  "confidence": ` |
| attribute_computation__01 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_04_configure | 0.95 |  |  | ✗ | 02_open_attribute_tool[emb:0.80]; 04_configure[emb:0.74]; 01_ready_to_start[emb:0.73]; 03_select_type[emb:0.71]; 03_add_crossline[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.88] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 1 | seismic_attribute_03_select_type | seismic_attribute_04_configure | 0.95 |  |  | ✗ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.78]; 03_select_type[emb:0.75]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 2 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.79]; 03_select_type[emb:0.74]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 3 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.77]; 03_select_type[emb:0.76]; 01_ready_to_start[emb:0.72]; 04_add_zslice[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 4 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.77]; 02_open_attribute_tool[emb:0.76]; 01_ready_to_start[emb:0.71]; 03_select_type[emb:0.69]; 01_open_selection[emb:0.65]; _follow_along_implementing_a_systematic_s_03[clip:0.91]; 01_main_window_ready[clip:0.90] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 5 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00]; 03_add_crossline[emb:0.68]; 04_add_zslice[emb:0.67]; 01_main_window_ready[emb:0.67,clip:0.82]; 01_open_selection[emb:0.66]; 02_add_inline[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.82] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |
| attribute_computation__01 | 6 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 01_open_selection[emb:0.72]; 05_select_survey[emb:0.70]; 04_add_zslice[emb:0.69]; 01_main_window_ready[emb:0.69,clip:0.85]; 01_data_load[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.87] | `{
  "id": "seismic_attribute_06_display",
  "confidence": 0.` |
| attribute_computation__01 | 7 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 04_add_zslice[emb:0.70]; 01_main_window_ready[emb:0.70,clip:0.82]; 03_add_crossline[emb:0.70]; 05_select_survey[emb:0.67]; 02_add_inline[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.82]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |

## rep 4: correct 13/16; fallback 0; goal-state hints 4

| scenario | step | expected | picked | conf | gate | goal_state | ok | candidates (source:score) | rerank raw |
|---|---|---|---|---|---|---|---|---|---|
| survey_setup__01 | 0 | survey_setup | survey_setup_01_open_selection | 0.95 |  |  | ✓ | 01_open_selection[emb:0.79]; 02_open_new_survey_dialog[emb:0.73]; 05_select_survey[emb:0.68]; 01_data_load[emb:0.67]; 03_choose_initial_setup[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.87] | `{"id": "survey_setup_01_open_selection", "confidence": 0.95}` |
| survey_setup__01 | 1 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 02_open_new_survey_dialog[prior:1.00,emb:0.83]; 01_open_selection[prior:1.00,emb:0.75]; 03_choose_initial_setup[emb:0.75]; 05_select_survey[emb:0.69]; 01_data_load[emb:0.65]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{
  "id": "survey_setup_03_choose_initial_setup",
  "confide` |
| survey_setup__01 | 2 | survey_setup | survey_setup_03_choose_initial_setup | 0.95 |  |  | ✓ | 04_scan_segy[prior:1.00,emb:0.65]; 05_select_survey[prior:1.00,emb:0.74]; 03_choose_initial_setup[prior:1.00,emb:0.78]; 02_open_new_survey_dialog[emb:0.82]; 01_open_selection[emb:0.76]; 01_main_window_ready[clip:0.92]; _follow_along_implementing_a_systematic_s_03[clip:0.90] | `{"id": "survey_setup_03_choose_initial_setup", "confidence":` |
| survey_setup__01 | 3 | survey_setup | d3_visualization_01_main_window_ready | 0.90 |  |  | ✗ | 04_scan_segy[prior:1.00]; 05_select_survey[prior:1.00,emb:0.73]; 03_choose_initial_setup[prior:1.00]; 01_main_window_ready[emb:0.72,clip:0.75]; 04_add_zslice[emb:0.70]; 01_open_selection[emb:0.69]; 03_add_crossline[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{"id": "d3_visualization_01_main_window_ready", "confidence"` |
| 3d_visualization__01 | 0 | d3_visualization | d3_visualization_01_main_window_ready | 0.90 |  |  | ✓ | 05_select_survey[emb:0.72]; 01_main_window_ready[emb:0.71,clip:0.76]; 01_open_selection[emb:0.69]; 04_add_zslice[emb:0.68]; 05_all_slices_displayed[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{
  "id": "d3_visualization_01_main_window_ready",
  "confid` |
| 3d_visualization__01 | 1 | d3_visualization | d3_visualization_02_add_inline | 0.90 |  |  | ✓ | 02_add_inline[prior:1.00]; 01_main_window_ready[prior:1.00,emb:0.70,clip:0.75]; 05_select_survey[emb:0.73]; 04_add_zslice[emb:0.71]; 03_add_crossline[emb:0.71]; 01_open_selection[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.75] | `{
  "id": "d3_visualization_02_add_inline",
  "confidence": ` |
| 3d_visualization__01 | 2 | d3_visualization | d3_visualization_03_add_crossline | 0.70 |  |  | ✓ | 03_add_crossline[prior:1.00]; 02_add_inline[prior:1.00]; 05_select_survey[emb:0.72]; 01_main_window_ready[emb:0.71,clip:0.82]; 01_open_selection[emb:0.69]; 04_add_zslice[emb:0.67]; 05_all_slices_displayed[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.83]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{
  "id": "d3_visualization_03_add_crossline",
  "confidence` |
| 3d_visualization__01 | 3 | d3_visualization | d3_visualization_04_add_zslice | 0.90 |  | d3_visualization_04_add_zslice | ✓ | 04_add_zslice[prior:1.00,emb:0.69]; 03_add_crossline[prior:1.00,emb:0.65]; 05_select_survey[emb:0.70]; 01_main_window_ready[emb:0.69,clip:0.79]; 01_open_selection[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.81]; _follow_along_implementing_a_systematic_s_02[clip:0.81] | `{
  "id": "d3_visualization_04_add_zslice",
  "confidence": ` |
| attribute_computation__01 | 0 | seismic_attribute_02_open_attribute_tool | seismic_attribute_03_select_type | 0.90 |  |  | ✗ | 02_open_attribute_tool[emb:0.81]; 04_configure[emb:0.74]; 01_ready_to_start[emb:0.74]; 03_select_type[emb:0.70]; 04_add_zslice[emb:0.69]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.88] | `{
  "id": "seismic_attribute_03_select_type",
  "confidence"` |
| attribute_computation__01 | 1 | seismic_attribute_03_select_type | seismic_attribute_04_configure | 0.95 |  |  | ✗ | 04_configure[prior:1.00,emb:0.76]; 03_select_type[prior:1.00,emb:0.74]; 02_open_attribute_tool[emb:0.79]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{"id": "seismic_attribute_04_configure", "confidence": 0.95}` |
| attribute_computation__01 | 2 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.77]; 02_open_attribute_tool[emb:0.78]; 03_select_type[emb:0.74]; 01_ready_to_start[emb:0.73]; 04_add_zslice[emb:0.70]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 3 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.95 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.76]; 02_open_attribute_tool[emb:0.77]; 03_select_type[emb:0.75]; 01_ready_to_start[emb:0.72]; 04_add_zslice[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.90]; 01_main_window_ready[clip:0.89] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 4 | seismic_attribute_04_configure | seismic_attribute_04_configure | 0.90 |  |  | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00,emb:0.77]; 02_open_attribute_tool[emb:0.77]; 01_ready_to_start[emb:0.71]; 03_select_type[emb:0.69]; 01_open_selection[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.91]; 01_main_window_ready[clip:0.90] | `{
  "id": "seismic_attribute_04_configure",
  "confidence": ` |
| attribute_computation__01 | 5 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 05_compute[prior:1.00]; 06_display[prior:1.00]; 04_configure[prior:1.00]; 03_add_crossline[emb:0.68]; 04_add_zslice[emb:0.68]; 01_main_window_ready[emb:0.68,clip:0.82]; 01_open_selection[emb:0.66]; 05_select_survey[emb:0.66]; _follow_along_implementing_a_systematic_s_03[clip:0.82] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |
| attribute_computation__01 | 6 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 01_open_selection[emb:0.72]; 05_select_survey[emb:0.70]; 04_add_zslice[emb:0.69]; 01_main_window_ready[emb:0.69,clip:0.85]; 01_data_load[emb:0.68]; _follow_along_implementing_a_systematic_s_03[clip:0.87] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |
| attribute_computation__01 | 7 | seismic_attribute_06_display | seismic_attribute_06_display | 0.90 |  | seismic_attribute_06_display | ✓ | 07_qc_analyze[prior:1.00]; 06_display[prior:1.00]; 04_add_zslice[emb:0.70]; 01_main_window_ready[emb:0.70,clip:0.82]; 03_add_crossline[emb:0.70]; 05_select_survey[emb:0.67]; 02_add_inline[emb:0.67]; _follow_along_implementing_a_systematic_s_03[clip:0.82]; _follow_along_implementing_a_systematic_s_02[clip:0.80] | `{"id": "seismic_attribute_06_display", "confidence": 0.9}` |

