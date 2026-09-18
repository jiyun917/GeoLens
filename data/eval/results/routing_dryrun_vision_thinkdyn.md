# Vision-based routing dry-run — thinkdyn (AUX_THINKING_BUDGET=-1)

| scenario | steps | correct workflow | kept (conf≥0.7) | rerank none | aux cost/step | thinking tok/step | latency/step |
|---|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 4 | 3/4 | 3/4 | 0 | $7.50m | 2471 | 28.6s |
| opendtect__attribute_computation__01 | 8 | 0/8 | 3/8 | 3 | $8.05m | 2645 | 21.5s |
| opendtect__survey_setup__01 | 4 | 4/4 | 4/4 | 0 | $6.50m | 2142 | 18.5s |
| qgis__vector_buffer__01 | 8 | 6/8 | 8/8 | 0 | $5.39m | 1732 | 19.3s |

| scenario | step | expected | picked wf / node | conf | method | kept |
|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 0 | d3_visualization | d3_visualization / d3_visualization_01_main_window_ready | 0.95 | llm | True |
| opendtect__3d_visualization__01 | 1 | d3_visualization | d3_visualization / d3_visualization_01_main_window_ready | 0.6 | llm | False |
| opendtect__3d_visualization__01 | 2 | d3_visualization | fault_interpretation / fault_interpretation_02_display | 0.85 | llm | True |
| opendtect__3d_visualization__01 | 3 | d3_visualization | d3_visualization / d3_visualization_01_main_window_ready | 0.9 | llm | True |
| opendtect__attribute_computation__01 | 0 | seismic_attribute | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.6 | llm | False |
| opendtect__attribute_computation__01 | 1 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 2 | seismic_attribute | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.7 | llm | True |
| opendtect__attribute_computation__01 | 3 | seismic_attribute | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.6 | llm | False |
| opendtect__attribute_computation__01 | 4 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 5 | seismic_attribute | d3_visualization / d3_visualization_01_main_window_ready | 0.9 | llm | True |
| opendtect__attribute_computation__01 | 6 | seismic_attribute | None / None | 0.0 | none | False |
| opendtect__attribute_computation__01 | 7 | seismic_attribute | d3_visualization / d3_visualization_01_main_window_ready | 0.9 | llm | True |
| opendtect__survey_setup__01 | 0 | survey_setup | survey_setup / survey_setup_01_open_selection | 0.95 | llm | True |
| opendtect__survey_setup__01 | 1 | survey_setup | survey_setup / survey_setup_03_choose_initial_setup | 0.95 | llm | True |
| opendtect__survey_setup__01 | 2 | survey_setup | survey_setup / survey_setup_03_choose_initial_setup | 0.9 | llm | True |
| opendtect__survey_setup__01 | 3 | survey_setup | survey_setup / survey_setup_05_select_survey | 0.7 | llm | True |
| qgis__vector_buffer__01 | 0 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_01_open_toolbox | 0.95 | llm | True |
| qgis__vector_buffer__01 | 1 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_01_open_toolbox | 0.9 | llm | True |
| qgis__vector_buffer__01 | 2 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_02_search_algorithm | 0.9 | llm | True |
| qgis__vector_buffer__01 | 3 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_03_configure_buffer | 0.95 | llm | True |
| qgis__vector_buffer__01 | 4 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_03_configure_buffer | 0.9 | llm | True |
| qgis__vector_buffer__01 | 5 | qgis_vector_buffer | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.7 | llm | True |
| qgis__vector_buffer__01 | 6 | qgis_vector_buffer | auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s / auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s_03 | 0.7 | llm | True |
| qgis__vector_buffer__01 | 7 | qgis_vector_buffer | qgis_vector_buffer / qgis_vector_buffer_05_run_and_render | 0.95 | llm | True |
