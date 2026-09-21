# linked_chunks re-link — study2 — v4 index (./data/chromadb_v4, BAAI/bge-m3), 2026-09-21

Mechanism: chunk_mapper.map_node_to_chunks (unchanged): query = workflow label + title + description + screenshot keywords; top-3 by embedding distance.
Section provenance (v3): node.manual_sections restricts candidates to the node's source section(s) first (see SECTIONS in this script).

| workflow | node | manual_sections | old ids resolve? | new chunk (section, p.) | distance |
|---|---|---|---|---|---|
| horizon_autotrack_142a | horizon_autotrack_142a_01_random_line_loaded | 1.4.2a | 0/0 | 1.4.2a 3D Auto-track p.69; 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.71 | 0.559, 0.696, nan |
| horizon_autotrack_142a | horizon_autotrack_142a_02_tracking_settings_open | 1.4.2a | 0/0 | 1.4.2a 3D Auto-track p.70; 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.69 | 0.437, 0.441, nan |
| horizon_autotrack_142a | horizon_autotrack_142a_03_event_peak_set | 1.4.2a | 0/0 | 1.4.2a 3D Auto-track p.70; 1.4.2a 3D Auto-track p.77; 1.4.2a 3D Auto-track p.76 | 0.513, 0.598, nan |
| horizon_autotrack_142a | horizon_autotrack_142a_04_correlation_set | 1.4.2a | 0/0 | 1.4.2a 3D Auto-track p.70; 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.71 | 0.572, 0.635, 0.704 |
| horizon_autotrack_142a | horizon_autotrack_142a_05_seed_picked | 1.4.2a | 0/0 | 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.73; 1.4.2a 3D Auto-track p.69 | 0.543, 0.660, 0.677 |
| horizon_autotrack_142a | horizon_autotrack_142a_06_patch_tracked | 1.4.2a | 0/0 | 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.69; 1.4.2a 3D Auto-track p.74 | 0.352, 0.544, 0.557 |
| horizon_autotrack_142a | horizon_autotrack_142a_07_patch_locked | 1.4.2a | 0/0 | 1.4.2a 3D Auto-track p.73; 1.4.2a 3D Auto-track p.72; 1.4.2a 3D Auto-track p.74 | 0.496, 0.631, 0.652 |
| fault_sticks_143b | fault_sticks_143b_01_inline_110_loaded | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.88; 1.4.3b Fault Sticks p.87; 1.4.3b Fault Sticks p.89 | 0.610, nan, nan |
| fault_sticks_143b | fault_sticks_143b_02_new_faultstickset | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.88; 1.4.3b Fault Sticks p.91; 1.4.3b Fault Sticks p.90 | 0.699, 0.748, 0.753 |
| fault_sticks_143b | fault_sticks_143b_03_save_as_dialog | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.88; 1.4.3b Fault Sticks p.87; 1.4.3b Fault Sticks p.91 | 0.627, 0.688, nan |
| fault_sticks_143b | fault_sticks_143b_04_faultstickset_saved | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.88; 1.4.3b Fault Sticks p.87; 1.4.3b Fault Sticks p.91 | 0.767, 0.790, nan |
| fault_sticks_143b | fault_sticks_143b_05_only_at_sections | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.88; 1.4.3b Fault Sticks p.87; 1.4.3b Fault Sticks p.89 | 0.681, 0.722, nan |
| fault_sticks_143b | fault_sticks_143b_06_sticks_on_inline_110 | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.88; 1.4.3b Fault Sticks p.89; 1.4.3b Fault Sticks p.87 | 0.547, 0.594, nan |
| fault_sticks_143b | fault_sticks_143b_07_sticks_on_several_inlines | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.89; 1.4.3b Fault Sticks p.87; 1.4.3b Fault Sticks p.88 | 0.467, 0.650, nan |
| fault_sticks_143b | fault_sticks_143b_08_zslice_similarity | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.90; 1.4.3b Fault Sticks p.89; 1.4.3b Fault Sticks p.87 | 0.435, 0.629, nan |
| fault_sticks_143b | fault_sticks_143b_09_fault_plane_created | 1.4.3b | 0/0 | 1.4.3b Fault Sticks p.91; 1.4.3b Fault Sticks p.90; 1.4.3b Fault Sticks p.87 | 0.464, 0.601, nan |

Wall-clock for this relink run (model load + 16 nodes): 19.4 s.
