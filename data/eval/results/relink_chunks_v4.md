# linked_chunks re-link — v4 index (./data/chromadb_v4, BAAI/bge-m3), 2026-09-18

Mechanism: chunk_mapper.map_node_to_chunks (unchanged): query = workflow label + title + description + screenshot keywords; top-3 by embedding distance.
Section provenance (v3): node.manual_sections restricts candidates to the node's source section(s) first (see SECTIONS in this script).

| workflow | node | manual_sections | old ids resolve? | new chunk (section, p.) | distance |
|---|---|---|---|---|---|
| survey_setup | survey_setup_01_open_selection | 1.2.2a, 1.2  | 3/3 | 1.2 Set up a Survey & Load Data p.18; 1.2.2a Survey Setup & Load SEG-Y p.21; 1.2.2a Survey Setup & Load SEG-Y p.25 | 0.560, nan, nan |
| survey_setup | survey_setup_02_open_new_survey_dialog | 1.2.2a | 3/3 | 1.2.2a Survey Setup & Load SEG-Y p.21; 1.2.2a Survey Setup & Load SEG-Y p.25; 1.2.2a Survey Setup & Load SEG-Y p.24 | 0.605, nan, nan |
| survey_setup | survey_setup_03_choose_initial_setup | 1.2.2a | 3/3 | 1.2.2a Survey Setup & Load SEG-Y p.22; 1.2.2a Survey Setup & Load SEG-Y p.25; 1.2.2a Survey Setup & Load SEG-Y p.24 | 0.451, 0.545, 0.554 |
| survey_setup | survey_setup_04_scan_segy | 1.2.2a, 1.2.2b | 3/3 | 1.2.2a Survey Setup & Load SEG-Y p.22; 1.2.2a Survey Setup & Load SEG-Y p.24; 1.2.2b Load SEG-Y p.31 | 0.475, 0.526, 0.535 |
| survey_setup | survey_setup_05_select_survey | 1.2.2a | 3/3 | 1.2.2a Survey Setup & Load SEG-Y p.21; 1.2.2a Survey Setup & Load SEG-Y p.22; 1.2.2a Survey Setup & Load SEG-Y p.25 | nan, nan, nan |
| d3_visualization | d3_visualization_01_main_window_ready | 1.3.1 , 1.3.1a | 3/3 | 1.3.1 Tree, Scene & Elements p.45; 1.3.1a Display An Inline p.46; 2.3.2b Volume Curvature And Others p.225 | 0.580, nan, 0.744 |
| d3_visualization | d3_visualization_02_add_inline | 1.3.1a, 1.3.1  | 3/3 | 1.3.1a Display An Inline p.46; 1.3.1 Tree, Scene & Elements p.45; 2.3.1c Dip-steered Similarity p.199 | nan, nan, 0.645 |
| d3_visualization | d3_visualization_03_add_crossline | 1.3.1a, 1.3.1  | 3/3 | 1.3.1 Tree, Scene & Elements p.45; 1.3.1a Display An Inline p.46; 2.4.2d Systems Tracts p.330 | nan, nan, 0.739 |
| d3_visualization | d3_visualization_04_add_zslice | 1.3.1a, 1.3.1  | 3/3 | 1.3.1 Tree, Scene & Elements p.45; 1.3.1a Display An Inline p.46; 2.3.2b Volume Curvature And Others p.225 | nan, nan, 0.578 |
| d3_visualization | d3_visualization_05_all_slices_displayed | 1.3.1a, 1.3.1  | 3/3 | 1.3.1a Display An Inline p.46; 1.3.1 Tree, Scene & Elements p.45; 2.3.2b Volume Curvature And Others p.225 | 0.786, 0.820, 0.844 |
| seismic_attribute | seismic_attribute_01_ready_to_start | 1.5.1a, 1.5.1 , 1.5  | 3/3 | 1.5 Attribute Analysis & Cross-plots p.113; 1.5.1a Bright Spot p.126; 1.5.1a Bright Spot p.124 | 0.621, nan, nan |
| seismic_attribute | seismic_attribute_02_open_attribute_tool | 1.5.1a | 3/3 | 1.5.1a Bright Spot p.119; 1.5.1a Bright Spot p.124; 1.5.1a Bright Spot p.123 | nan, nan, nan |
| seismic_attribute | seismic_attribute_03_select_type | 1.5.1a | 3/3 | 1.5.1a Bright Spot p.126; 1.5.1a Bright Spot p.119; 1.5.1a Bright Spot p.123 | 0.644, 0.673, nan |
| seismic_attribute | seismic_attribute_04_configure | 1.5.1a | 3/3 | 1.5.1a Bright Spot p.119; 1.5.1a Bright Spot p.126; 1.5.1a Bright Spot p.123 | 0.439, 0.491, 0.641 |
| seismic_attribute | seismic_attribute_05_compute | 1.5.1a | 3/3 | 1.5.1a Bright Spot p.126; 1.5.1a Bright Spot p.128; 1.5.1a Bright Spot p.127 | 0.682, nan, nan |
| seismic_attribute | seismic_attribute_06_display | 1.5.1a | 3/3 | 1.5.1a Bright Spot p.120; 1.5.1a Bright Spot p.123; 1.5.1a Bright Spot p.119 | 0.499, 0.580, nan |
| seismic_attribute | seismic_attribute_07_qc_analyze | 1.5.1a | 3/3 | 1.5.1a Bright Spot p.126; 1.5.1a Bright Spot p.124; 1.5.1a Bright Spot p.118 | nan, nan, nan |
| fault_interpretation | fault_interpretation_01_data_load | 1.4.3 | 3/3 | 1.4.3 Fault Interpretation p.83; 1.4.3b Fault Sticks p.87; 1.4.3a Fault Planes p.84 | nan, nan, nan |
| fault_interpretation | fault_interpretation_02_display | 1.4.3 | 3/3 | 1.4.3b Fault Sticks p.89; 1.4.3a Fault Planes p.86; 1.4.3a Fault Planes p.84 | nan, nan, nan |
| fault_interpretation | fault_interpretation_03_apply_attribute | 1.4.3 | 3/3 | 1.4.3b Fault Sticks p.90; 1.4.3 Fault Interpretation p.83; 1.4.3b Fault Sticks p.89 | nan, nan, nan |
| fault_interpretation | fault_interpretation_04_open_fault_tool | 1.4.3 | 3/3 | 1.4.3b Fault Sticks p.91; 1.4.3 Fault Interpretation p.83; 1.4.3a Fault Planes p.84 | 0.761, 0.811, nan |
| fault_interpretation | fault_interpretation_05_pick_fault | 1.4.3 | 3/3 | 1.4.3 Fault Interpretation p.83; 1.4.3a Fault Planes p.85; 1.4.3b Fault Sticks p.89 | 0.582, 0.589, 0.613 |
| fault_interpretation | fault_interpretation_06_fault_plane | 1.4.3 | 3/3 | 1.4.3 Fault Interpretation p.83; 1.4.3a Fault Planes p.84; 1.4.3b Fault Sticks p.91 | 0.731, 0.747, nan |
| fault_interpretation | fault_interpretation_07_qc | 1.4.3 | 3/3 | 1.4.3 Fault Interpretation p.83; 1.4.3b Fault Sticks p.88; 1.4.3b Fault Sticks p.91 | 0.797, nan, nan |
| fault_interpretation | fault_interpretation_08_save | 1.4.3 | 3/3 | 1.4.3 Fault Interpretation p.83; 1.4.3b Fault Sticks p.90; 1.4.3b Fault Sticks p.91 | 0.774, nan, nan |
| horizon_tracking | horizon_tracking_01_data_load | 1.4.2 | 3/3 | 1.4.2a 3D Auto-track p.69; 1.4.2 Horizon Tracking p.67; 1.4.2b Tracking In 2D Viewer p.78 | 0.746, nan, nan |
| horizon_tracking | horizon_tracking_02_display_inline | 1.4.2 | 3/3 | 1.4.2a 3D Auto-track p.69; 1.4.2a 3D Auto-track p.72; 1.4.2b Tracking In 2D Viewer p.82 | 0.746, nan, nan |
| horizon_tracking | horizon_tracking_03_open_tracking | 1.4.2 | 3/3 | 1.4.2a 3D Auto-track p.72; 1.4.2b Tracking In 2D Viewer p.79; 1.4.2b Tracking In 2D Viewer p.80 | 0.617, 0.625, 0.635 |
| horizon_tracking | horizon_tracking_04_seed_pick | 1.4.2 | 3/3 | 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.73; 1.4.2a 3D Auto-track p.70 | 0.592, 0.659, nan |
| horizon_tracking | horizon_tracking_05_configure_params | 1.4.2 | 3/3 | 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.77; 1.4.2b Tracking In 2D Viewer p.79 | 0.636, 0.707, nan |
| horizon_tracking | horizon_tracking_06_auto_track | 1.4.2 | 3/3 | 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.69; 1.4.2 Horizon Tracking p.67 | 0.605, 0.638, nan |
| horizon_tracking | horizon_tracking_07_qc_review | 1.4.2 | 3/3 | 1.4.2a 3D Auto-track p.74; 1.4.2b Tracking In 2D Viewer p.80; 1.4.2a 3D Auto-track p.72 | 0.668, 0.756, nan |
| horizon_tracking | horizon_tracking_08_save | 1.4.2 | 3/3 | 1.4.2b Tracking In 2D Viewer p.82; 1.4.2b Tracking In 2D Viewer p.80; 1.4.2a 3D Auto-track p.72 | 0.758, nan, nan |
