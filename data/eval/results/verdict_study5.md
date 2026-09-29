# Study 5 verdict — mechanical application of the pre-registration (tags study5_opendtect + study5_qgis merged per replicate)

runs: gemini n=10, claude n=10, gpt n=10

## §5 judgement (replicate-level, strata = model; hall = v6 as scored)

### 비교 1 (full_system vs vanilla_budget)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.963 | 0.780 | +0.183 | 0.000 | 0.000 | 0.007 | ✓ |
| claude | 1.000 | 0.922 | +0.078 | 0.000 | 0.000 | 0.000 | ✓ |
| gpt | 0.959 | 0.889 | +0.070 | 0.000 | 0.137 | 0.000 | ✗ |

- step: direction 3/3 (ties 0), stratified raw p = 0.0001, Δ = +0.1105, significant reverse: none → 성립
- hall: full ≤ comparator in 2/3 → 성립
- **grade: A**

### 비교 2 (full_system vs vanilla_vector)

| model | full step_acc | comparator | Δ | per-model p | full hall | comparator hall | hall ok |
|---|---|---|---|---|---|---|---|
| gemini | 0.963 | 0.859 | +0.104 | 0.000 | 0.000 | 0.000 | ✓ |
| claude | 1.000 | 0.967 | +0.033 | 0.000 | 0.000 | 0.000 | ✓ |
| gpt | 0.959 | 0.867 | +0.093 | 0.000 | 0.137 | 0.000 | ✗ |

- step: direction 3/3 (ties 0), stratified raw p = 0.0001, Δ = +0.0765, significant reverse: none → 성립
- hall: full ≤ comparator in 2/3 → 성립
- **grade: A**

Holm (family 2): 비교 1 0.0001 → 0.0002; 비교 2 0.0001 → 0.0002. **Grades: 비교 1 = A, 비교 2 = A.**

## Descriptive (mean over replicates, 3 scenarios equally weighted)

| model | backend | step_acc | hall v6 | goal_completion | cost_total $/step | latency s/step |
|---|---|---|---|---|---|---|
| gemini | no_rag | 0.835 | 0.022 | 0.600 | 0.0075 | 10.5 |
| gemini | vanilla_budget | 0.780 | 0.007 | 0.633 | 0.0095 | 11.4 |
| gemini | vanilla_vector | 0.859 | 0.000 | 0.767 | 0.0127 | 10.6 |
| gemini | full_system | 0.963 | 0.000 | 0.800 | 0.0144 | 28.2 |
| claude | no_rag | 0.848 | 0.011 | 0.733 | 0.0067 | 2.7 |
| claude | vanilla_budget | 0.922 | 0.000 | 0.800 | 0.0109 | 4.0 |
| claude | vanilla_vector | 0.967 | 0.000 | 0.667 | 0.0192 | 3.5 |
| claude | full_system | 1.000 | 0.000 | 1.000 | 0.0163 | 19.6 |
| gpt | no_rag | 0.752 | 0.000 | 0.667 | 0.0036 | 1.9 |
| gpt | vanilla_budget | 0.889 | 0.000 | 0.667 | 0.0064 | 2.9 |
| gpt | vanilla_vector | 0.867 | 0.000 | 0.667 | 0.0123 | 2.3 |
| gpt | full_system | 0.959 | 0.137 | 1.000 | 0.0115 | 17.4 |

## Per-scenario step accuracy (mean over replicates)

| model | backend | spectral_decomp__01 | q:aspect_north__01 | q:custom_projection__01 |
|---|---|---|---|---|
| gemini | no_rag | 0.667 | 0.850 | 0.989 |
| gemini | vanilla_budget | 0.567 | 0.850 | 0.922 |
| gemini | vanilla_vector | 0.711 | 0.933 | 0.933 |
| gemini | full_system | 0.889 | 1.000 | 1.000 |
| claude | no_rag | 0.778 | 0.833 | 0.933 |
| claude | vanilla_budget | 0.800 | 0.967 | 1.000 |
| claude | vanilla_vector | 0.900 | 1.000 | 1.000 |
| claude | full_system | 1.000 | 1.000 | 1.000 |
| gpt | no_rag | 0.778 | 0.833 | 0.644 |
| gpt | vanilla_budget | 0.811 | 1.000 | 0.856 |
| gpt | vanilla_vector | 0.778 | 1.000 | 0.822 |
| gpt | full_system | 0.889 | 1.000 | 0.989 |

## Predictions

- Q1/Q7 no_rag mean step_acc per model: gemini 0.835, claude 0.848, gpt 0.752
- Q2 vanilla_budget − no_rag: gemini -0.056, claude +0.074, gpt +0.137 → ≥ +3pp in 2/3 → 적중
- Q3 비교 1 direction 3/3, p 0.0001 → 적중
- Q4 비교 2 direction 3/3, reverse none → 적중
- Q5 hall(v6) full ≤ vanilla_budget 2/3, ≤ vanilla_vector 2/3 → 적중
- Q6 routing gemini: spectral_decomp__01 wf 80/90, node 78/90, R2 0, R1 0; q:aspect_north__01 wf 60/60, node 50/60, R2 4, R1 0; q:custom_projection__01 wf 87/90, node 85/90, R2 0, R1 0
- Q6 routing claude: spectral_decomp__01 wf 80/90, node 80/90, R2 0, R1 0; q:aspect_north__01 wf 60/60, node 60/60, R2 7, R1 0; q:custom_projection__01 wf 90/90, node 89/90, R2 0, R1 0
- Q6 routing gpt: spectral_decomp__01 wf 80/90, node 79/90, R2 0, R1 0; q:aspect_north__01 wf 60/60, node 60/60, R2 16, R1 0; q:custom_projection__01 wf 90/90, node 90/90, R2 0, R1 0

## Post-hoc notes (2026-09-29, after the mechanical verdict; no GT/scorer/mechanism change)

- **Q5 label correction.** The script prints Q5 with the §5 threshold (≥ 2/3). Pre-registration 5 §4 states Q5 as "각 3/3", so Q5 is **반증** (2/3 and 2/3): GPT full_system hall v6 = 0.137 vs 0.000 for both comparators. The grade (A/A) is unaffected because §5 uses the 2/3 condition.
- **GPT full_system hall v6 sources (0.137 = 37 flags / 240 steps, three systematic label mismatches):** spectral_decomp s0 'Attribute 3D' 10/10 (screen: 'Attribute Set 3D' toolbar icon; GPT shortened the label); aspect_north s2 'OK' 10/10 (GPT tells the user to click OK in the Raster Calculator dialog, which has Run/Close — a real instruction error, though the step still matched on the Input layers action); custom_projection s6 'Defined Coordinate Systems' 10/10 (manual wording 'User Defined Coordinate Systems'; screen shows 'User-defined'); spectral_decomp s4 'Output frequency 24 Hz' 2/10 (value not shown on screen). Other flags: Gemini no_rag custom_projection s3 (WKT tokens 5/10) and s6 (1/10), Claude no_rag s3 (3/10), Gemini vanilla_budget spectral_decomp s8 'Output frequency (Hz) 44.0' (2/10).
- **Q6 detail.** Node-level routing accuracy (full_system, 240 steps per model): gemini 213/240 = 0.888, claude 229/240 = 0.954, gpt 229/240 = 0.954 → all ≥ 0.85 (per-scenario minimum: gemini aspect_north 50/60 = 0.833). R3 screen-delta advances: 57 in 720 full_system steps, 5 landed on a non-GT node (all Gemini; 5/720 = 0.69% ≤ 2%). R2 history advances: 27, all on the GT node. Gemini route_method 'none' 3 steps (custom_projection s0, replicates 5/6/9: rerank call failed after retries → no workflow context, fallback path) and fallback_activated on aspect_north s5 2 steps.
- **Q7 (F s4, WKT).** As worded ("no_rag는 PROJCRS 문자열을 내지 못하고 RAG 백엔드는 낸다") the prediction is **반증**: no backend of any model emits the PROJCRS string at s4 except Gemini vanilla_budget/vanilla_vector 2/10 each; s4 is matched through the other pattern alternatives (Parameters / WKT / paste instruction). Matched at s4: Claude 10/10 for all four backends; Gemini no_rag 10, vanilla 8/8, full 10; GPT no_rag 3/10 vs vanilla_budget 9, vanilla_vector 7, full 10.
- **Deviations recorded in the logs.** Gemini prepayment credits depleted (402) during QGIS replicate 4 (2026-09-28 23:04Z, 3 QGIS files written); in-progress replicate discarded before any file was written; a resume at 00:09Z before the top-up landed was stopped at 00:09:39Z (no file); resumed 00:10:43Z after a 20,000 KRW top-up; complete 02:49:28Z. Claude complete 23:03Z, GPT 22:41Z, both without interruption. Judge coverage: 1 step without a consensus judgement (Gemini opendtect r1, vanilla_budget, 8/9 judged); judge is descriptive only. Step errors: 0 of 2,880.
- **Unfavorable numbers.** full_system latency per step 17–28 s vs 2–11 s for the comparators (vision + rerank + generation), cost per step above vanilla_budget for all models and above vanilla_vector for Gemini; Gemini vanilla_budget < no_rag on step accuracy (Q2 2/3); GPT full_system hall v6 above both comparators.
