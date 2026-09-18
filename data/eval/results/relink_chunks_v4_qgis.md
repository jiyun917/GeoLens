# linked_chunks re-link — qgis — v4 index (./data/chromadb_v4, BAAI/bge-m3), 2026-09-18

Mechanism: chunk_mapper.map_node_to_chunks (unchanged): query = workflow label + title + description + screenshot keywords; top-3 by embedding distance.
Section provenance (v3): node.manual_sections restricts candidates to the node's source section(s) first (see SECTIONS in this script).

| workflow | node | manual_sections | old ids resolve? | new chunk (section, p.) | distance |
|---|---|---|---|---|---|
| qgis_vector_buffer | qgis_vector_buffer_01_open_toolbox | ★☆☆ Follow Along: Analyzing the Problem | 3/3 | ★☆☆ Follow Along: Analyzing the Problem: p.214; ★☆☆ Follow Along: Analyzing the Problem: p.213; ★☆☆ Follow Along: Analyzing the Problem: p.216 | 0.670, nan, nan |
| qgis_vector_buffer | qgis_vector_buffer_02_search_algorithm | ★☆☆ Follow Along: Analyzing the Problem | 3/3 | ★☆☆ Follow Along: Analyzing the Problem: p.214; ★☆☆ Follow Along: Analyzing the Problem: p.213; ★☆☆ Follow Along: Analyzing the Problem: p.216 | 0.542, 0.670, nan |
| qgis_vector_buffer | qgis_vector_buffer_03_configure_buffer | ★☆☆ Follow Along: Analyzing the Problem | 3/3 | ★☆☆ Follow Along: Analyzing the Problem: p.214; ★☆☆ Follow Along: Analyzing the Problem: p.218; ★☆☆ Follow Along: Analyzing the Problem: p.216 | 0.402, 0.418, 0.491 |
| qgis_vector_buffer | qgis_vector_buffer_04_save_output | ★☆☆ Follow Along: Analyzing the Problem | 3/3 | ★☆☆ Follow Along: Analyzing the Problem: p.216; ★☆☆ Follow Along: Analyzing the Problem: p.214; ★☆☆ Follow Along: Analyzing the Problem: p.218 | 0.547, 0.554, nan |
| qgis_vector_buffer | qgis_vector_buffer_05_run_and_render | ★☆☆ Follow Along: Analyzing the Problem | 3/3 | ★☆☆ Follow Along: Analyzing the Problem: p.218; ★☆☆ Follow Along: Analyzing the Problem: p.214; ★☆☆ Follow Along: Analyzing the Problem: p.216 | 0.440, 0.504, 0.522 |

Wall-clock for this relink run (model load + 5 nodes): 15.8 s.
