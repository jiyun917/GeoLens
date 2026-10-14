# Study 5x — exploratory ablation (outside the pre-registration): linked_chunks on the study-5 test set

files: study5x 60 (expected 60), study5 60. linked_chunks = full_system routing + same manual text, no structure block.

reps per model: gemini 10, claude 10, gpt 10

## Step accuracy (replicate mean, 3 scenarios equal weight)

| model | no_rag | vanilla_budget | linked_chunks | full_system | full − linked | linked − vanilla_budget |
|---|---|---|---|---|---|---|
| gemini | 0.835 | 0.780 | 0.819 | 0.963 | +0.144 | +0.039 |
| claude | 0.848 | 0.922 | 0.928 | 1.000 | +0.072 | +0.006 |
| gpt | 0.752 | 0.889 | 0.896 | 0.959 | +0.063 | +0.007 |

### full_system vs linked_chunks (structure block effect)

| model | full_system | linked_chunks | Δ | per-model p | n |
|---|---|---|---|---|---|
| gemini | 0.963 | 0.819 | +0.144 | 0.0001 | 10 |
| claude | 1.000 | 0.928 | +0.072 | 0.0001 | 10 |
| gpt | 0.959 | 0.896 | +0.063 | 0.0002 | 10 |
- direction 3/3 (ties 0), stratified Δ = +0.0932, raw p = 0.0001 (exploratory, not pre-registered)

### linked_chunks vs vanilla_budget (graph-selected text effect)

| model | linked_chunks | vanilla_budget | Δ | per-model p | n |
|---|---|---|---|---|---|
| gemini | 0.819 | 0.780 | +0.039 | 0.4385 | 10 |
| claude | 0.928 | 0.922 | +0.006 | 0.8587 | 10 |
| gpt | 0.896 | 0.889 | +0.007 | 0.6786 | 10 |
- direction 3/3 (ties 0), stratified Δ = +0.0173, raw p = 0.3387 (exploratory, not pre-registered)

## Hallucination rate v6, goal completion, cost, latency (replicate mean)

| model | backend | hall v6 | goal completion | cost $/step | latency s/step | context chars (mean) |
|---|---|---|---|---|---|---|
| gemini | vanilla_budget | 0.007 | 0.633 | 0.0095 | 11.4 | 3,900 |
| gemini | linked_chunks | 0.000 | 0.633 | 0.0123 | 32.3 | 3,874 |
| gemini | full_system | 0.000 | 0.800 | 0.0144 | 28.2 | 6,598 |
| claude | vanilla_budget | 0.000 | 0.800 | 0.0109 | 4.0 | 3,900 |
| claude | linked_chunks | 0.000 | 0.800 | 0.0135 | 24.1 | 3,875 |
| claude | full_system | 0.000 | 1.000 | 0.0163 | 19.6 | 6,638 |
| gpt | vanilla_budget | 0.000 | 0.667 | 0.0064 | 2.9 | 3,900 |
| gpt | linked_chunks | 0.000 | 0.667 | 0.0091 | 24.8 | 3,872 |
| gpt | full_system | 0.137 | 1.000 | 0.0115 | 17.4 | 6,625 |

## Per-scenario step accuracy (mean over replicates)

| model | backend | spectral_decomp__01 | q:aspect_north__01 | q:custom_projection__01 |
|---|---|---|---|---|
| gemini | vanilla_budget | 0.567 | 0.850 | 0.922 |
| gemini | linked_chunks | 0.644 | 0.867 | 0.944 |
| gemini | full_system | 0.889 | 1.000 | 1.000 |
| claude | vanilla_budget | 0.800 | 0.967 | 1.000 |
| claude | linked_chunks | 0.800 | 0.983 | 1.000 |
| claude | full_system | 1.000 | 1.000 | 1.000 |
| gpt | vanilla_budget | 0.811 | 1.000 | 0.856 |
| gpt | linked_chunks | 0.867 | 0.933 | 0.889 |
| gpt | full_system | 0.889 | 1.000 | 0.989 |

## Routing parity (node-level accuracy of the routed steps; same mechanism in both backends)

| model | linked_chunks | full_system |
|---|---|---|
| gemini | 221/240 = 0.921 | 213/240 = 0.888 |
| claude | 212/240 = 0.883 | 229/240 = 0.954 |
| gpt | 205/240 = 0.854 | 229/240 = 0.954 |
