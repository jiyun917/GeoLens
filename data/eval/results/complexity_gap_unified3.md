# Complexity-vs-gap analysis — unified3

Pre-registered prediction (see `v2_pre_registration.md § attribute prediction`): vanilla_vector should underperform on the complex attribute_computation scenario because retrieval will drift toward the theory pages (§1.5.1) instead of the procedure pages (§1.5.1a). full_system should recover via workflow routing. If the prediction is confirmed, the full − vanilla gap on step_accuracy should be **larger** on attribute_computation than on the two 4-step scenarios.

This table restricts to the two contrasts most relevant to the prediction: **full − vanilla** and **full − no_rag**, on step_accuracy (higher = better). Numbers are percentage points; positive means full wins. `Δ complex − simple` is the widening: attribute − mean(survey_setup, 3d_viz).

## full_system − vanilla_vector on Step Acc (pp)

| Model | survey_setup | 3d_viz | attribute (complex) | Δ complex − simple |
|---|---|---|---|---|
| gemini | +5.0 | -5.0 | +20.0 | +20.0 |
| claude | +0.0 | +0.0 | +2.5 | +2.5 |
| gpt | +35.0 | +0.0 | -25.0 | -42.5 |
| qwen | +45.0 | +15.0 | -2.5 | -32.5 |

## full_system − no_rag on Step Acc (pp)

| Model | survey_setup | 3d_viz | attribute (complex) | Δ complex − simple |
|---|---|---|---|---|
| gemini | +15.0 | +35.0 | +5.0 | -20.0 |
| claude | +0.0 | +0.0 | -5.0 | -5.0 |
| gpt | +25.0 | +0.0 | -2.5 | -15.0 |
| qwen | +45.0 | -5.0 | +12.5 | -7.5 |

## full_system − vanilla_vector on Hall Rate (pp, lower = better)

Same as above but on hallucination rate. Because lower is better, we report **vanilla − full** so positive still means full wins.

| Model | survey_setup | 3d_viz | attribute (complex) | Δ complex − simple |
|---|---|---|---|---|
| gemini | +5.0 | +0.0 | +5.0 | +2.5 |
| claude | +15.0 | +0.0 | +0.0 | -7.5 |
| gpt | +5.0 | +10.0 | +7.5 | +0.0 |
| qwen | +15.0 | -10.0 | -22.5 | -25.0 |

## Interpretation guide

- **Δ complex − simple > 0** on the full − vanilla row = hybrid advantage widens with complexity (**prediction confirmed** for that model).
- **Δ complex − simple ≈ 0** = flat effect (prediction unconfirmed, hybrid gives constant lift).
- **Δ complex − simple < 0** = hybrid narrows on complex workloads (prediction **refuted**).

The direction across the 4 models is the primary quantity of interest — a single model can flip due to small-n noise; a majority of models moving in the same direction is the pre-registered confirmation criterion.

