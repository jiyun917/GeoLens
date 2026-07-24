# Claude hallucination asymmetry — v1 vs v2 re-check

Δ = hall_rate[full_system] − hall_rate[vanilla_vector] (negative → hybrid helps, positive → hybrid hurts).

| model | v1 full | v1 vanilla | v1 Δ | v2 full | v2 vanilla | v2 Δ | Δ shift |
|---|---|---|---|---|---|---|---|
| gemini | 0.100 | 0.150 | -5.0pp | 0.050 | 0.100 | -5.0pp | -0.0pp |
| claude | 0.350 | 0.225 | +12.5pp | 0.150 | 0.250 | -10.0pp | -22.5pp |
| gpt | 0.400 | 0.550 | -15.0pp | 0.550 | 0.475 | +7.5pp | +22.5pp |
| qwen | 0.475 | 0.675 | -20.0pp | 0.475 | 0.725 | -25.0pp | -5.0pp |

## Verdict

**v2 REJECTS asymmetry**: Claude no longer shows hybrid > vanilla in hall_rate. The v1 observation was likely a byproduct of workflow coverage gap. Drop from discussion, cite in methodology audit as a fixed-in-v2 artifact.
