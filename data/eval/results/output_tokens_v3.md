# Output token distribution — v2 unified matrix

Per-step input/output token distribution and cost, aggregated across all scenarios × replicates for each (model, backend).

The cost paradox hypothesis: `output_tokens[full_system] < output_tokens[vanilla_vector]` on generator-costly models. If true, workflow context makes the generator emit tighter responses, and the net effect (input growth vs output shrinkage) is favorable for hybrid on models where output tokens are priced high (Claude, GPT, Gemini).


## gemini

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 160 | 550±77 | 9±4 | 9 | 6.011m |
| vanilla_vector | 160 | 6822±770 | 10±6 | 9 | 15.016m |
| vanilla_budget | 160 | 1884±105 | 10±6 | 9 | 8.008m |
| graph_only | 160 | 1512±67 | 11±6 | 10 | 8.125m |
| vision_only | 160 | 632±73 | 10±5 | 9 | 6.999m |
| full_system | 160 | 2290±230 | 11±7 | 10 | 9.641m |
| state_path | 160 | 1715±192 | 12±7 | 11 | 8.815m |

**Cost paradox check (gemini)**:  full_system input × 0.34, output × 1.06, cost × 0.64. ✗ hybrid emits longer output. ✓ hybrid cheaper.

## claude

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 160 | 2060±189 | 33±20 | 26 | 6.675m |
| vanilla_vector | 160 | 8295±659 | 32±19 | 26 | 25.361m |
| vanilla_budget | 160 | 3357±172 | 32±19 | 26 | 10.559m |
| graph_only | 160 | 3016±174 | 32±17 | 30 | 9.525m |
| vision_only | 160 | 2143±175 | 33±20 | 26 | 6.931m |
| full_system | 160 | 3788±299 | 25±14 | 24 | 11.745m |
| state_path | 160 | 3314±328 | 36±20 | 39 | 10.484m |

**Cost paradox check (claude)**:  full_system input × 0.46, output × 0.80, cost × 0.46. ✓ hybrid emits shorter output. ✓ hybrid cheaper.

## gpt

| backend | n | input mean | output mean | output median | cost mean ($) |
|---|---|---|---|---|---|
| no_rag | 160 | 1391±62 | 10±6 | 9 | 3.573m |
| vanilla_vector | 160 | 6694±599 | 10±5 | 10 | 16.839m |
| vanilla_budget | 160 | 2516±70 | 10±5 | 9 | 6.393m |
| graph_only | 160 | 2215±70 | 10±6 | 9 | 5.639m |
| vision_only | 160 | 1464±65 | 9±5 | 9 | 3.754m |
| full_system | 160 | 2900±197 | 11±7 | 11 | 7.364m |
| state_path | 160 | 2410±180 | 11±7 | 9 | 6.134m |

**Cost paradox check (gpt)**:  full_system input × 0.43, output × 1.11, cost × 0.44. ✗ hybrid emits longer output. ✓ hybrid cheaper.
