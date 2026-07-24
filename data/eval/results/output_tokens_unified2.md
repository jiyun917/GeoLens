# Output token distribution — v2 unified matrix

Per-step input/output token distribution and cost, aggregated across all scenarios × replicates for each (model, backend).

The cost paradox hypothesis: `output_tokens[full_system] < output_tokens[vanilla_vector]` on generator-costly models. If true, workflow context makes the generator emit tighter responses, and the net effect (input growth vs output shrinkage) is favorable for hybrid on models where output tokens are priced high (Claude, GPT, Gemini).


## gemini

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 40 | 480±22 | 10±5 | 10 | 0.703m |
| vanilla_vector | 40 | 7362±653 | 10±6 | 10 | 9.304m |
| graph_only | 40 | 548±21 | 11±6 | 12 | 0.792m |
| vision_only | 40 | 564±21 | 11±5 | 12 | 0.813m |
| full_system | 40 | 2051±252 | 10±6 | 9 | 2.661m |
| state_path | 40 | 1176±314 | 9±6 | 8 | 1.563m |

**Cost paradox check (gemini)**:  full_system input × 0.28, output × 0.97, cost × 0.29. ✓ hybrid emits shorter output. ✓ hybrid cheaper.

## claude

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 40 | 1893±44 | 25±21 | 21 | 6.057m |
| vanilla_vector | 40 | 8875±768 | 34±22 | 23 | 27.131m |
| graph_only | 40 | 1989±36 | 27±17 | 23 | 6.367m |
| vision_only | 40 | 2004±36 | 28±16 | 23 | 6.424m |
| full_system | 40 | 3720±230 | 33±19 | 26 | 11.660m |
| state_path | 40 | 2720±309 | 34±22 | 28 | 8.674m |

**Cost paradox check (claude)**:  full_system input × 0.42, output × 0.99, cost × 0.43. ✓ hybrid emits shorter output. ✓ hybrid cheaper.

## gpt

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 40 | 1328±20 | 13±8 | 11 | 3.452m |
| vanilla_vector | 40 | 7200±652 | 11±5 | 11 | 18.112m |
| graph_only | 40 | 1396±19 | 12±6 | 12 | 3.605m |
| vision_only | 40 | 1409±20 | 12±5 | 12 | 3.644m |
| full_system | 40 | 2755±205 | 13±7 | 11 | 7.013m |
| state_path | 40 | 1922±284 | 13±8 | 17 | 4.939m |

**Cost paradox check (gpt)**:  full_system input × 0.38, output × 1.12, cost × 0.39. ✗ hybrid emits longer output. ✓ hybrid cheaper.

## qwen

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 40 | 614±547 | 549±307 | 425 | 0.000m |
| vanilla_vector | 40 | 6888±925 | 491±232 | 398 | 0.000m |
| graph_only | 40 | 547±538 | 449±278 | 304 | 0.000m |
| vision_only | 40 | 389±231 | 495±269 | 392 | 0.000m |
| full_system | 40 | 1805±304 | 403±209 | 326 | 0.000m |
| state_path | 40 | 935±282 | 417±244 | 318 | 0.000m |

**Cost paradox check (qwen)**:  full_system input × 0.26, output × 0.82, cost × nan. ✓ hybrid emits shorter output. ✗ hybrid pricier.
