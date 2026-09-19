# Output token distribution — v2 unified matrix

Per-step input/output token distribution and cost, aggregated across all scenarios × replicates for each (model, backend).

The cost paradox hypothesis: `output_tokens[full_system] < output_tokens[vanilla_vector]` on generator-costly models. If true, workflow context makes the generator emit tighter responses, and the net effect (input growth vs output shrinkage) is favorable for hybrid on models where output tokens are priced high (Claude, GPT, Gemini).


## gemini

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 80 | 636±30 | 9±4 | 9 | 5.397m |
| vanilla_vector | 80 | 4227±32 | 9±4 | 11 | 10.177m |
| vanilla_budget | 80 | 1803±30 | 9±4 | 9 | 6.932m |
| graph_only | 80 | 1435±307 | 9±4 | 10 | 7.238m |
| vision_only | 80 | 715±30 | 9±4 | 10 | 5.379m |
| full_system | 80 | 2100±139 | 9±4 | 9 | 8.704m |
| state_path | 80 | 1558±331 | 8±3 | 9 | 7.488m |

**Cost paradox check (gemini)**:  full_system input × 0.50, output × 0.95, cost × 0.86. ✓ hybrid emits shorter output. ✓ hybrid cheaper.

## claude

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 80 | 2184±97 | 36±22 | 28 | 7.098m |
| vanilla_vector | 80 | 5825±78 | 29±17 | 27 | 17.918m |
| vanilla_budget | 80 | 3325±78 | 30±17 | 27 | 10.425m |
| graph_only | 80 | 3073±371 | 31±18 | 27 | 9.689m |
| vision_only | 80 | 2238±78 | 30±14 | 27 | 7.163m |
| full_system | 80 | 3690±189 | 26±11 | 27 | 11.463m |
| state_path | 80 | 3243±406 | 30±17 | 28 | 10.182m |

**Cost paradox check (claude)**:  full_system input × 0.63, output × 0.89, cost × 0.64. ✓ hybrid emits shorter output. ✓ hybrid cheaper.

## gpt

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 80 | 1472±24 | 8±3 | 8 | 3.758m |
| vanilla_vector | 80 | 4587±25 | 8±3 | 8 | 11.547m |
| vanilla_budget | 80 | 2478±20 | 6±2 | 6 | 6.256m |
| graph_only | 80 | 2185±288 | 8±3 | 10 | 5.545m |
| vision_only | 80 | 1538±25 | 8±3 | 8 | 3.924m |
| full_system | 80 | 2779±135 | 9±5 | 10 | 7.043m |
| state_path | 80 | 2318±282 | 8±3 | 10 | 5.879m |

**Cost paradox check (gpt)**:  full_system input × 0.61, output × 1.19, cost × 0.61. ✗ hybrid emits longer output. ✓ hybrid cheaper.
