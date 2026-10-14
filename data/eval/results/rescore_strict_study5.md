# Strict re-score of the study-5 test set (exploratory sensitivity analysis, outside the pre-registration)

Criterion: all expected_action_keywords present (version aliases 'Input layer'/'User-defined' allowed) or bare completion sentinel at a goal-reached step; pattern alternatives and allowed_alternatives NOT used. Replicate = mean over the 3 scenarios, n = 10.

## Step accuracy, strict (pre-registered scorer in parentheses)

| model | no_rag | vanilla_budget | vanilla_vector | linked_chunks (5x) | full_system |
|---|---|---|---|---|---|
| gemini | 0.515 ± 0.040 (0.835) | 0.522 ± 0.127 (0.780) | 0.557 ± 0.083 (0.859) | 0.539 ± 0.108 (0.819) | 0.774 ± 0.025 (0.963) |
| claude | 0.574 ± 0.052 (0.848) | 0.665 ± 0.043 (0.922) | 0.744 ± 0.044 (0.967) | 0.650 ± 0.030 (0.928) | 0.904 ± 0.011 (1.000) |
| gpt | 0.383 ± 0.048 (0.752) | 0.630 ± 0.079 (0.889) | 0.719 ± 0.043 (0.867) | 0.687 ± 0.029 (0.896) | 0.959 ± 0.011 (0.959) |

## Comparisons under the strict criterion (stratified permutation, 10,000, seed 42)

- full_system vs vanilla_budget: gemini Δ +0.252 (p 0.0001); claude Δ +0.239 (p 0.0001); gpt Δ +0.330 (p 0.0001) → direction 3/3, stratified Δ +0.2735, p 0.0001
- full_system vs vanilla_vector: gemini Δ +0.217 (p 0.0001); claude Δ +0.159 (p 0.0001); gpt Δ +0.241 (p 0.0001) → direction 3/3, stratified Δ +0.2056, p 0.0001
- full_system vs linked_chunks: gemini Δ +0.235 (p 0.0001); claude Δ +0.254 (p 0.0001); gpt Δ +0.272 (p 0.0001) → direction 3/3, stratified Δ +0.2537, p 0.0001
- linked_chunks vs vanilla_budget: gemini Δ +0.017 (p 0.7964); claude Δ -0.015 (p 0.4623); gpt Δ +0.057 (p 0.0553) → direction 2/3, stratified Δ +0.0198, p 0.3835

## Steps scored correct by the pre-registered scorer but not by the strict criterion (count / 30 responses)

| backend | scenario | step | keyword | loose-only |
|---|---|---|---|---|
| full_system | opendtect__spectral_decomp__01 | s0 | Add Color Blended | 20 |
| full_system | opendtect__spectral_decomp__01 | s3 | Attribute Set | 1 |
| full_system | qgis__aspect_north__01 | s0 | Raster calculator | 10 |
| full_system | qgis__aspect_north__01 | s3 | aspect_north | 10 |
| full_system | qgis__custom_projection__01 | s0 | Custom Projections | 5 |
| full_system | qgis__custom_projection__01 | s1 | Add new CRS | 10 |
| full_system | qgis__custom_projection__01 | s5 | CRS | 11 |
| vanilla_budget | opendtect__spectral_decomp__01 | s0 | Add Color Blended | 30 |
| vanilla_budget | opendtect__spectral_decomp__01 | s4 | Spectral Decomposition | 8 |
| vanilla_budget | opendtect__spectral_decomp__01 | s5 | 44 | 6 |
| vanilla_budget | opendtect__spectral_decomp__01 | s6 | 64 | 12 |
| vanilla_budget | opendtect__spectral_decomp__01 | s8 | 완료 | 14 |
| vanilla_budget | qgis__aspect_north__01 | s0 | Raster calculator | 23 |
| vanilla_budget | qgis__aspect_north__01 | s1 | aspect@1 | 10 |
| vanilla_budget | qgis__aspect_north__01 | s2 | Reference layer | 2 |
| vanilla_budget | qgis__aspect_north__01 | s3 | aspect_north | 23 |
| vanilla_budget | qgis__custom_projection__01 | s0 | Custom Projections | 25 |
| vanilla_budget | qgis__custom_projection__01 | s1 | Add new CRS | 12 |
| vanilla_budget | qgis__custom_projection__01 | s2 | Van der Grinten | 1 |
| vanilla_budget | qgis__custom_projection__01 | s5 | CRS | 9 |
| vanilla_budget | qgis__custom_projection__01 | s6 | Van der Grinten | 2 |
| vanilla_budget | qgis__custom_projection__01 | s7 | OK | 3 |
| vanilla_vector | opendtect__spectral_decomp__01 | s0 | Add Color Blended | 19 |
| vanilla_vector | opendtect__spectral_decomp__01 | s3 | Attribute Set | 10 |
| vanilla_vector | opendtect__spectral_decomp__01 | s4 | Spectral Decomposition | 10 |
| vanilla_vector | opendtect__spectral_decomp__01 | s5 | 44 | 14 |
| vanilla_vector | opendtect__spectral_decomp__01 | s6 | 64 | 14 |
| vanilla_vector | opendtect__spectral_decomp__01 | s8 | 완료 | 9 |
| vanilla_vector | qgis__aspect_north__01 | s0 | Raster calculator | 17 |
| vanilla_vector | qgis__aspect_north__01 | s1 | aspect@1 | 1 |
| vanilla_vector | qgis__aspect_north__01 | s2 | Reference layer | 5 |
| vanilla_vector | qgis__aspect_north__01 | s3 | aspect_north | 14 |
| vanilla_vector | qgis__custom_projection__01 | s0 | Custom Projections | 20 |
| vanilla_vector | qgis__custom_projection__01 | s1 | Add new CRS | 15 |
| vanilla_vector | qgis__custom_projection__01 | s2 | Van der Grinten | 5 |
| vanilla_vector | qgis__custom_projection__01 | s5 | CRS | 10 |
| no_rag | opendtect__spectral_decomp__01 | s0 | Add Color Blended | 30 |
| no_rag | opendtect__spectral_decomp__01 | s4 | Spectral Decomposition | 10 |
| no_rag | opendtect__spectral_decomp__01 | s5 | 44 | 19 |
| no_rag | opendtect__spectral_decomp__01 | s6 | 64 | 8 |
| no_rag | opendtect__spectral_decomp__01 | s8 | 완료 | 8 |
| no_rag | qgis__aspect_north__01 | s0 | Raster calculator | 28 |
| no_rag | qgis__aspect_north__01 | s2 | Reference layer | 16 |
| no_rag | qgis__aspect_north__01 | s3 | aspect_north | 28 |
| no_rag | qgis__custom_projection__01 | s0 | Custom Projections | 20 |
| no_rag | qgis__custom_projection__01 | s1 | Add new CRS | 30 |
| no_rag | qgis__custom_projection__01 | s2 | Van der Grinten | 10 |
| no_rag | qgis__custom_projection__01 | s4 | OK | 6 |
| no_rag | qgis__custom_projection__01 | s5 | CRS | 10 |
| no_rag | qgis__custom_projection__01 | s6 | Van der Grinten | 1 |
