# Retrieval replay — minilm (EMBED_MODEL=all-MiniLM-L6-v2, CHROMADB_PATH=./data/chromadb, KG position=last)

| scenario | target section | chunks (top-5 + ±1) | target hits | sections (in order) | ctx chars | ctx tokens | first 1,500 chars = manual text? |
|---|---|---|---|---|---|---|---|
| opendtect__3d_visualization__01 | 1.3.1a/1.3.1 | 11 | 0/11 | 1.2.1, 2.5.1a, 1.5, 1.4.4f, 1.2.2a, 2.5.1a, 2.5.1a, 1.5, 1.4.4f, 1.2.2a, 1.2.2a | 18814 | 5816 | yes |
| opendtect__attribute_computation__01 | 1.5.1a | 15 | 0/15 | 2.3.1g, 1.5.2a, 2.3.1f, 2.3.2b, 2.5.1a, 2.3.1g, 2.3.1g, 1.5.2a, 1.5.2a, 2.3.1f, 2.3.1f, 2.3.2b, 2.3.2b, 2.5.1a, 2.5.1a | 21829 | 6614 | yes |
| opendtect__survey_setup__01 | 1.2.2a | 9 | 6/9 | 1.2.2a, 1.2.2a, 1.4.4f, 1.2.2a, 1.2.2, 1.2.2a, 1.2.2a, 1.2.2a, 1.4.4f | 14652 | 4825 | yes |
| qgis__vector_buffer__01 | 6.2.6/6.2 | 9 | 0/9 | ★☆☆, ★☆☆, Creating, ★☆☆, ★☆☆, ★☆☆, ★☆☆, ★☆☆, ★☆☆ | 9149 | 2677 | yes |
