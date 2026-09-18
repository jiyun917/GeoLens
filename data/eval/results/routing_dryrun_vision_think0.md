# Vision-based routing dry-run — think0 (AUX_THINKING_BUDGET=0)

| scenario | steps | correct workflow | kept (conf≥0.7) | rerank none | aux cost/step | thinking tok/step | latency/step |
|---|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 4 | 3/4 | 3/4 | 1 | $1.41m | 0 | 17.8s |
| opendtect__attribute_computation__01 | 8 | 0/8 | 3/8 | 4 | $1.41m | 0 | 8.3s |
| opendtect__survey_setup__01 | 4 | 4/4 | 4/4 | 0 | $1.18m | 0 | 8.2s |
| qgis__vector_buffer__01 | 8 | 5/8 | 7/8 | 1 | $1.16m | 0 | 11.1s |

| scenario | step | expected | picked wf / node | conf | method | kept |
|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 0 | d3_visualization | d3_visualization / d3_visualization_01_main_window_ready | 0.8 | llm | True |
| opendtect__3d_visualization__01 | 1 | d3_visualization | d3_visualization / d3_visualization_03_add_crossline | 0.8 | llm | True |
| opendtect__3d_visualization__01 | 2 | d3_visualization | d3_visualization / d3_visualization_05_all_slices_displayed | 0.8 | llm | True |
| opendtect__3d_visualization__01 | 3 | d3_visualization | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 0 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 1 | seismic_attribute | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.5 | llm | False |
| opendtect__attribute_computation__01 | 2 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 3 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 4 | seismic_attribute | horizon_tracking / horizon_tracking_08_save | 0.7 | llm | True |
| opendtect__attribute_computation__01 | 5 | seismic_attribute | d3_visualization / d3_visualization_01_main_window_ready | 0.8 | llm | True |
| opendtect__attribute_computation__01 | 6 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 7 | seismic_attribute | d3_visualization / d3_visualization_01_main_window_ready | 0.8 | llm | True |
| opendtect__survey_setup__01 | 0 | survey_setup | survey_setup / survey_setup_01_open_selection | 0.9 | llm | True |
| opendtect__survey_setup__01 | 1 | survey_setup | survey_setup / survey_setup_03_choose_initial_setup | 0.9 | llm | True |
| opendtect__survey_setup__01 | 2 | survey_setup | survey_setup / survey_setup_03_choose_initial_setup | 0.9 | llm | True |
| opendtect__survey_setup__01 | 3 | survey_setup | survey_setup / survey_setup_05_select_survey | 0.8 | llm | True |
| qgis__vector_buffer__01 | 0 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_01_open_toolbox | 0.8 | llm | True |
| qgis__vector_buffer__01 | 1 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_02_search_algorithm | 0.9 | llm | True |
| qgis__vector_buffer__01 | 2 | qgis_vector_buffer | None / None | 0.0 | none | False |
| qgis__vector_buffer__01 | 3 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_03_configure_buffer | 0.9 | llm | True |
| qgis__vector_buffer__01 | 4 | qgis_vector_buffer | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.7 | llm | True |
| qgis__vector_buffer__01 | 5 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_03_configure_buffer | 0.8 | llm | True |
| qgis__vector_buffer__01 | 6 | qgis_vector_buffer | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.7 | llm | True |
| qgis__vector_buffer__01 | 7 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_05_run_and_render | 0.7 | llm | True |
