# Vision-based routing dry-run — dev_embed (AUX_THINKING_BUDGET=0)

| scenario | steps | correct workflow | kept (conf≥0.7) | rerank none | aux cost/step | thinking tok/step | latency/step |
|---|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 4 | 2/4 | 2/4 | 2 | $1.37m | 0 | 18.2s |
| opendtect__attribute_computation__01 | 8 | 6/8 | 7/8 | 1 | $1.31m | 0 | 8.0s |
| opendtect__survey_setup__01 | 4 | 4/4 | 4/4 | 0 | $1.22m | 0 | 8.1s |

| scenario | step | expected | picked wf / node | conf | method | kept |
|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 0 | d3_visualization | d3_visualization / d3_visualization_01_main_window_ready | 0.8 | llm | True |
| opendtect__3d_visualization__01 | 1 | d3_visualization | d3_visualization / d3_visualization_04_add_zslice | 0.8 | llm | True |
| opendtect__3d_visualization__01 | 2 | d3_visualization | None / None | 0.0 | none | False |
| opendtect__3d_visualization__01 | 3 | d3_visualization | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 0 | seismic_attribute | seismic_attribute / seismic_attribute_04_configure | 0.9 | llm | True |
| opendtect__attribute_computation__01 | 1 | seismic_attribute | seismic_attribute / seismic_attribute_04_configure | 0.9 | llm | True |
| opendtect__attribute_computation__01 | 2 | seismic_attribute | seismic_attribute / seismic_attribute_04_configure | 0.85 | llm | True |
| opendtect__attribute_computation__01 | 3 | seismic_attribute | seismic_attribute / seismic_attribute_04_configure | 0.9 | llm | True |
| opendtect__attribute_computation__01 | 4 | seismic_attribute | seismic_attribute / seismic_attribute_04_configure | 0.8 | llm | True |
| opendtect__attribute_computation__01 | 5 | seismic_attribute | d3_visualization / d3_visualization_01_main_window_ready | 0.7 | llm | True |
| opendtect__attribute_computation__01 | 6 | seismic_attribute | seismic_attribute / seismic_attribute_06_display | 0.9 | llm | True |
| opendtect__attribute_computation__01 | 7 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__survey_setup__01 | 0 | survey_setup | survey_setup / survey_setup_02_open_new_survey_dialog | 0.8 | llm | True |
| opendtect__survey_setup__01 | 1 | survey_setup | survey_setup / survey_setup_03_choose_initial_setup | 0.9 | llm | True |
| opendtect__survey_setup__01 | 2 | survey_setup | survey_setup / survey_setup_03_choose_initial_setup | 0.8 | llm | True |
| opendtect__survey_setup__01 | 3 | survey_setup | survey_setup / survey_setup_05_select_survey | 0.7 | llm | True |
