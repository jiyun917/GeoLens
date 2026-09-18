# Retrieval replay — bgem3_v4 (EMBED_MODEL=BAAI/bge-m3, CHROMADB_PATH=./data/chromadb_v4, KG position=last)

| scenario | target section | chunks (top-5 + ±1) | target hits | sections (in order) | ctx chars | ctx tokens | first 1,500 chars = manual text? |
|---|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 1.3.1a/1.3.1 | 13 | 0/13 | 1.3, 2.6.3, 1.2.2a, 1.2.2a, 2.3.1c, 1.3, 2.6.3, 1.2.2a, 1.2.2a, 1.2.2a, 1.2.2a, 2.3.1c, 2.3.1c | 21002 | 6326 | yes |
| opendtect__attribute_computation__01 | 1.5.1a | 12 | 7/12 | 1.5.1a, 1.5.1a, 1.5.1a, 2.5.1a, 2.3.1c, 1.5.1a, 1.5.1a, 1.5.1a, 1.5.1a, 2.5.1a, 2.3.1c, 2.3.1c | 16768 | 4727 | yes |
| opendtect__survey_setup__01 | 1.2.2a | 9 | 7/9 | 1.2.2a, 1.2.2a, 1.2.2a, 1.2.2b, 1.2.2a, 1.2.2a, 1.2.2a, 1.2.2b, 1.2.2a | 16582 | 5386 | yes |
| qgis__vector_buffer__01 | 6.2.6/6.2 | 0 | 0/0 |  | 0 | 0 | no (KG block first) |
