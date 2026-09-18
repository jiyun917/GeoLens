# Retrieval replay — bgem3 (EMBED_MODEL=BAAI/bge-m3, CHROMADB_PATH=./data/chromadb_v3, KG position=last)

| scenario | target section | chunks (top-5 + ±1) | target hits | sections (in order) | ctx chars | ctx tokens | first 1,500 chars = manual text? |
|---|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 1.3.1a/1.3.1 | 13 | 0/13 | 2.3.1c, 1.3, 2.6.3, 2.3.4a, 2.3.1g, 2.3.1c, 2.3.1c, 1.3, 2.6.3, 2.3.4a, 2.3.4a, 2.3.1g, 2.3.1g | 18949 | 5768 | yes |
| opendtect__attribute_computation__01 | 1.5.1a | 12 | 7/12 | 1.5.1a, 1.5.1a, 1.5.1a, 2.3.1c, 2.5.1a, 1.5.1a, 1.5.1a, 1.5.1a, 1.5.1a, 2.3.1c, 2.3.1c, 2.5.1a | 17337 | 5029 | yes |
| opendtect__survey_setup__01 | 1.2.2a | 8 | 7/8 | 1.2.2a, 1.2.2a, 1.2.2a, 1.2.2a, 1.2, 1.2.2a, 1.2.2a, 1.2.2a | 15841 | 5146 | yes |
| qgis__vector_buffer__01 | 6.2.6/6.2 | 8 | 0/8 | ★☆☆, ★☆☆, ★☆☆, ★☆☆, ★☆☆, ★☆☆, ★☆☆, ★☆☆ | 7326 | 2253 | yes |
