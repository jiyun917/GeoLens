# Output token distribution — v2 unified matrix

Per-step input/output token distribution and cost, aggregated across all scenarios × replicates for each (model, backend).

The cost paradox hypothesis: `output_tokens[full_system] < output_tokens[vanilla_vector]` on generator-costly models. If true, workflow context makes the generator emit tighter responses, and the net effect (input growth vs output shrinkage) is favorable for hybrid on models where output tokens are priced high (Claude, GPT, Gemini).


## gemini

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 80 | 550±75 | 9±5 | 9 | 0.778m |
| vanilla_vector | 80 | 7565±768 | 10±6 | 10 | 9.558m |
| graph_only | 80 | 615±72 | 10±5 | 9 | 0.867m |
| vision_only | 80 | 637±76 | 10±6 | 9 | 0.897m |
| full_system | 80 | 1565±321 | 10±6 | 9 | 2.056m |
| state_path | 80 | 765±110 | 10±6 | 8 | 1.054m |

**Cost paradox check (gemini)**:  full_system input × 0.21, output × 0.97, cost × 0.22. ✓ hybrid emits shorter output. ✓ hybrid cheaper.

## claude

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 80 | 2056±178 | 33±19 | 36 | 6.666m |
| vanilla_vector | 80 | 9218±1081 | 32±20 | 26 | 28.134m |
| graph_only | 80 | 2145±175 | 36±23 | 26 | 6.972m |
| vision_only | 80 | 2169±178 | 34±18 | 32 | 7.015m |
| full_system | 80 | 3337±391 | 33±18 | 32 | 10.507m |
| state_path | 80 | 2331±186 | 35±19 | 32 | 7.517m |

**Cost paradox check (claude)**:  full_system input × 0.36, output × 1.04, cost × 0.37. ✗ hybrid emits longer output. ✓ hybrid cheaper.

## gpt

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 80 | 1394±71 | 11±6 | 10 | 3.593m |
| vanilla_vector | 80 | 7367±798 | 10±6 | 9 | 18.514m |
| graph_only | 80 | 1458±65 | 10±6 | 10 | 3.745m |
| vision_only | 80 | 1476±69 | 10±6 | 11 | 3.794m |
| full_system | 80 | 2339±308 | 9±6 | 8 | 5.941m |
| state_path | 80 | 1595±100 | 10±6 | 8 | 4.091m |

**Cost paradox check (gpt)**:  full_system input × 0.32, output × 0.96, cost × 0.32. ✓ hybrid emits shorter output. ✓ hybrid cheaper.

## qwen

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 80 | 514±438 | 446±249 | 356 | 0.000m |
| vanilla_vector | 80 | 7137±688 | 515±258 | 424 | 0.000m |
| graph_only | 80 | 649±657 | 518±275 | 422 | 0.000m |
| vision_only | 80 | 780±568 | 609±295 | 488 | 0.000m |
| full_system | 80 | 1452±507 | 510±268 | 387 | 0.000m |
| state_path | 80 | 633±349 | 459±264 | 352 | 0.000m |

**Cost paradox check (qwen)**:  full_system input × 0.20, output × 0.99, cost × nan. ✓ hybrid emits shorter output. ✗ hybrid pricier.
