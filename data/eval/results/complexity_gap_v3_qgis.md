# Complexity-vs-gap analysis — unified3

Pre-registered prediction (see `v2_pre_registration.md § attribute prediction`): vanilla_vector should underperform on the complex attribute_computation scenario because retrieval will drift toward the theory pages (§1.5.1) instead of the procedure pages (§1.5.1a). full_system should recover via workflow routing. If the prediction is confirmed, the full − vanilla gap on step_accuracy should be **larger** on attribute_computation than on the two 4-step scenarios.

This table restricts to the two contrasts most relevant to the prediction: **full − vanilla** and **full − no_rag**, on step_accuracy (higher = better). Numbers are percentage points; positive means full wins. `Δ complex − simple` is the widening: attribute − mean(survey_setup, 3d_viz).

## full_system − vanilla_vector on Step Acc (pp)

| Model | survey_setup | 3d_viz | attribute (complex) | Δ complex − simple |
|---|---|---|---|---|
| gemini | — | — | — | — |
| claude | — | — | — | — |
| gpt | — | — | — | — |

## full_system − no_rag on Step Acc (pp)

| Model | survey_setup | 3d_viz | attribute (complex) | Δ complex − simple |
|---|---|---|---|---|
| gemini | — | — | — | — |
| claude | — | — | — | — |
| gpt | — | — | — | — |

## full_system − vanilla_vector on Hall Rate (pp, lower = better)

Same as above but on hallucination rate. Because lower is better, we report **vanilla − full** so positive still means full wins.

| Model | survey_setup | 3d_viz | attribute (complex) | Δ complex − simple |
|---|---|---|---|---|
| gemini | — | — | — | — |
| claude | — | — | — | — |
| gpt | — | — | — | — |

## Interpretation guide

- **Δ complex − simple > 0** on the full − vanilla row = hybrid advantage widens with complexity (**prediction confirmed** for that model).
- **Δ complex − simple ≈ 0** = flat effect (prediction unconfirmed, hybrid gives constant lift).
- **Δ complex − simple < 0** = hybrid narrows on complex workloads (prediction **refuted**).

The direction across the 4 models is the primary quantity of interest — a single model can flip due to small-n noise; a majority of models moving in the same direction is the pre-registered confirmation criterion.

