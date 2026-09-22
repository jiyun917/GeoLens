# linked_chunks re-link — study3_ot — v4 index (./data/chromadb_v4, BAAI/bge-m3), 2026-09-22

Mechanism: chunk_mapper.map_node_to_chunks (unchanged): query = workflow label + title + description + screenshot keywords; top-3 by embedding distance.
Section provenance (v3): node.manual_sections restricts candidates to the node's source section(s) first (see SECTIONS in this script).

| workflow | node | manual_sections | old ids resolve? | new chunk (section, p.) | distance |
|---|---|---|---|---|---|
| horizon_2dviewer_142b | horizon_2dviewer_142b_01_scene_no_2dline | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.82; 1.4.2b Tracking In 2D Viewer p.78; 1.4.2b Tracking In 2D Viewer p.80 | 0.738, 0.792, 0.807 |
| horizon_2dviewer_142b | horizon_2dviewer_142b_02_select_2dlines_dialog | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.78; 1.4.2b Tracking In 2D Viewer p.79; 1.4.2b Tracking In 2D Viewer p.82 | 0.640, 0.694, nan |
| horizon_2dviewer_142b | horizon_2dviewer_142b_03_2dline_loaded | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.78; 1.4.2b Tracking In 2D Viewer p.82; 1.4.2b Tracking In 2D Viewer p.79 | 0.542, 0.712, nan |
| horizon_2dviewer_142b | horizon_2dviewer_142b_04_2dviewer_open | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.78; 1.4.2b Tracking In 2D Viewer p.79; 1.4.2b Tracking In 2D Viewer p.82 | 0.508, 0.601, 0.642 |
| horizon_2dviewer_142b | horizon_2dviewer_142b_05_track_new_settings | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.79; 1.4.2b Tracking In 2D Viewer p.80; 1.4.2b Tracking In 2D Viewer p.82 | 0.328, nan, nan |
| horizon_2dviewer_142b | horizon_2dviewer_142b_06_seed_picked_tracked | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.81; 1.4.2b Tracking In 2D Viewer p.82; 1.4.2b Tracking In 2D Viewer p.79 | 0.588, 0.590, 0.605 |
| horizon_2dviewer_142b | horizon_2dviewer_142b_07_save_as_dialog | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.82; 1.4.2b Tracking In 2D Viewer p.79; 1.4.2b Tracking In 2D Viewer p.80 | 0.548, nan, nan |
| horizon_2dviewer_142b | horizon_2dviewer_142b_08_horizon_saved | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.82; 1.4.2b Tracking In 2D Viewer p.80; 1.4.2b Tracking In 2D Viewer p.78 | 0.502, 0.716, nan |
| horizon_2dviewer_142b | horizon_2dviewer_142b_09_viewer_closed_horizon_in_scene | 1.4.2b | 0/0 | 1.4.2b Tracking In 2D Viewer p.82; 1.4.2b Tracking In 2D Viewer p.78; 1.4.2b Tracking In 2D Viewer p.79 | 0.421, 0.518, 0.587 |

Wall-clock for this relink run (model load + 9 nodes): 16.5 s.
