# Evidence-gate offline evaluation — picks of dev_iter0_v2mech_gemini_r0.json

Rule: confirm iff (i) expected_dialog ⊂ vision v3 window titles/dialog (normalised) OR (ii) pick == last confirmed node or its successor OR (iii) pick is embedding top-1 with gap ≥ margin; without a last confirmed node only (i)/(iii).
Vision v3 recomputed offline on the dev screenshots (cache: data/eval/results/evidence_gate_offline_vision_v3.json); (ii) uses the run's own confirmed sequence; (iii) reported for the all-node pool and for the two-stage pool (top-2 goal workflows + session workflow).

| scenario | step | picked | conf | correct | (i) dialog | (ii) graph (last) | top-1 all / gap | top-1 pool / gap | windows (vision v3) |
|---|---|---|---|---|---|---|---|---|---|
| 3d_visualization__01 | 0 | d3_visualization_01_main_window_ready | 0.80 | ✓ | ✗ | ✗ (—) | survey_setup_05_select_survey / 0.021 | d3_visualization_01_main_window_ready / 0.035 | ['OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : My_F3_Survey - [Scene 1]'] |
| 3d_visualization__01 | 1 | d3_visualization_03_add_crossline | 0.70 | ✓ | ✗ | ✗ (d3_visualization_01_main_window_ready) | survey_setup_05_select_survey / 0.020 | d3_visualization_03_add_crossline / 0.005 | ['OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : My_F3_Survey - [Scene 1]'] |
| 3d_visualization__01 | 2 | d3_visualization_01_main_window_ready | 0.90 | ✓ | ✗ | ✗ (d3_visualization_03_add_crossline) | survey_setup_05_select_survey / 0.017 | d3_visualization_01_main_window_ready / 0.024 | ['OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : My_F3_Survey - [Scene 1]'] |
| 3d_visualization__01 | 3 | d3_visualization_04_add_zslice | 0.00 | ✓ | ✗ | ✗ (d3_visualization_01_main_window_ready) | survey_setup_05_select_survey / 0.025 | d3_visualization_01_main_window_ready / 0.010 | ['OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : My_F3_Survey - [Scene 1]'] |
| attribute_computation__01 | 0 | seismic_attribute_04_configure | 0.90 | ✗ | ✓ ['Attribute Set 3D'] | ✗ (—) | seismic_attribute_01_ready_to_start / 0.013 | seismic_attribute_01_ready_to_start / 0.013 | ['Attribute Set 3D', 'OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| attribute_computation__01 | 1 | seismic_attribute_04_configure | 0.90 | ✗ | ✓ ['Attribute Set 3D'] | ✓ (seismic_attribute_04_configure) | seismic_attribute_04_configure / 0.008 | seismic_attribute_04_configure / 0.008 | ['Attribute Set 3D', 'OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| attribute_computation__01 | 2 | seismic_attribute_04_configure | 0.90 | ✓ | ✓ ['Attribute Set 3D'] | ✓ (seismic_attribute_04_configure) | seismic_attribute_04_configure / 0.019 | seismic_attribute_04_configure / 0.019 | ['Attribute Set 3D', 'OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| attribute_computation__01 | 3 | seismic_attribute_04_configure | 0.90 | ✓ | ✓ ['Attribute Set 3D'] | ✓ (seismic_attribute_04_configure) | seismic_attribute_04_configure / 0.008 | seismic_attribute_04_configure / 0.008 | ['Attribute Set 3D', 'OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| attribute_computation__01 | 4 | seismic_attribute_04_configure | 0.90 | ✓ | ✓ ['Attribute Set 3D'] | ✓ (seismic_attribute_04_configure) | seismic_attribute_04_configure / 0.051 | seismic_attribute_04_configure / 0.051 | ['Save Attribute as', 'Attribute Set 3D', 'OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| attribute_computation__01 | 5 | d3_visualization_01_main_window_ready | 0.70 | ✗ | ✗ | ✗ (seismic_attribute_04_configure) | d3_visualization_01_main_window_ready / 0.013 | d3_visualization_01_main_window_ready / 0.013 | ['OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| attribute_computation__01 | 6 | seismic_attribute_06_display | 0.90 | ✓ | ✗ | ✗ (d3_visualization_01_main_window_ready) | survey_setup_01_open_selection / 0.013 | d3_visualization_01_main_window_ready / 0.002 | ['Select', 'OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| attribute_computation__01 | 7 | — | 0.00 | — | ✗ | ✗ (seismic_attribute_06_display) | d3_visualization_04_add_zslice / 0.011 | d3_visualization_04_add_zslice / 0.011 | ['OpendTect 7.0.9 (Windows) *UPDATE AVAILABLE* : seismic_data - [Scene 1]'] |
| survey_setup__01 | 0 | survey_setup_02_open_new_survey_dialog | 0.85 | ✓ | ✗ | ✗ (—) | survey_setup_01_open_selection / 0.041 | survey_setup_01_open_selection / 0.041 | ['Survey Setup and Selection'] |
| survey_setup__01 | 1 | survey_setup_03_choose_initial_setup | 0.80 | ✓ | ✓ ['Create New Survey'] | ✓ (survey_setup_02_open_new_survey_dialog) | survey_setup_02_open_new_survey_dialog / 0.086 | survey_setup_02_open_new_survey_dialog / 0.086 | ['Create New Survey', 'Survey Setup and Selection'] |
| survey_setup__01 | 2 | survey_setup_03_choose_initial_setup | 0.80 | ✓ | ✓ ['Create New Survey'] | ✓ (survey_setup_03_choose_initial_setup) | survey_setup_02_open_new_survey_dialog / 0.045 | survey_setup_02_open_new_survey_dialog / 0.045 | ['Create New Survey', 'Survey Setup and Selection'] |
| survey_setup__01 | 3 | survey_setup_05_select_survey | 0.70 | ✓ | ✗ | ✓ (survey_setup_03_choose_initial_setup) | survey_setup_05_select_survey / 0.010 | survey_setup_05_select_survey / 0.046 | ['OpendTect 7.0.9 (Windows) *UPDATE AVAILABLE* : My_F3_Survey - [Scene 1]'] |

## Margin sweep for (iii) — confirmed = (i) or (ii) or (iii); counts over the run's picks (routed AND gated ones)

| pool | margin | wrong picks filtered | wrong picks confirmed | correct picks confirmed | correct picks dropped |
|---|---|---|---|---|---|
| all nodes | 0.00 | 0 | 3 | 6 | 6 |
| all nodes | 0.01 | 0 | 3 | 6 | 6 |
| all nodes | 0.02 | 1 | 2 | 6 | 6 |
| all nodes | 0.03 | 1 | 2 | 6 | 6 |
| all nodes | 0.04 | 1 | 2 | 6 | 6 |
| all nodes | 0.05 | 1 | 2 | 6 | 6 |
| all nodes | 0.08 | 1 | 2 | 6 | 6 |
| two-stage | 0.00 | 0 | 3 | 9 | 3 |
| two-stage | 0.01 | 0 | 3 | 8 | 4 |
| two-stage | 0.02 | 1 | 2 | 8 | 4 |
| two-stage | 0.03 | 1 | 2 | 7 | 5 |
| two-stage | 0.04 | 1 | 2 | 6 | 6 |
| two-stage | 0.05 | 1 | 2 | 6 | 6 |
| two-stage | 0.08 | 1 | 2 | 6 | 6 |

Picks evaluated: 15 (correct 12, wrong 3).
