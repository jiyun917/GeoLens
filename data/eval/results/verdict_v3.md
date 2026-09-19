# v3 verdict — mechanical application of the signed pre-registration (§6.3, P1–P8)

QGIS test set runs: gemini n=10, claude n=10, gpt n=10 | dev set runs: gemini n=10, claude n=10, gpt n=10

## §6.3 judgement (QGIS test set, replicate-level, strata = model)

### 비교 1 (full_system vs vanilla_budget)

| model | full step_acc | comparator step_acc | Δ | per-model perm p | full hall | comparator hall | hall full ≤ comp |
|---|---|---|---|---|---|---|---|
| gemini | 1.000 | 0.988 | +0.012 | 1.000 | 0.125 | 0.138 | ✓ |
| claude | 0.887 | 0.875 | +0.012 | 1.000 | 0.350 | 0.225 | ✗ |
| gpt | 0.838 | 0.950 | -0.112 | 0.003 | 0.125 | 0.125 | ✓ |

- step accuracy: direction count 2/3 (ties 0), stratified raw p = 0.0684, observed Δ (mean over models) = -0.0292, significant reverse in: ['gpt'] → step condition 불성립
- hall: full ≤ comparator in 2/3 (gemini, gpt) → hall condition 성립
- **grade: B**

### 비교 2 (full_system vs vanilla_vector)

| model | full step_acc | comparator step_acc | Δ | per-model perm p | full hall | comparator hall | hall full ≤ comp |
|---|---|---|---|---|---|---|---|
| gemini | 1.000 | 1.000 | +0.000 | 1.000 | 0.125 | 0.163 | ✓ |
| claude | 0.887 | 0.875 | +0.012 | 1.000 | 0.350 | 0.275 | ✗ |
| gpt | 0.838 | 0.912 | -0.075 | 0.035 | 0.125 | 0.125 | ✓ |

- step accuracy: direction count 1/3 (ties 1), stratified raw p = 0.1384, observed Δ (mean over models) = -0.0208, significant reverse in: ['gpt'] → step condition 불성립
- hall: full ≤ comparator in 2/3 (gemini, gpt) → hall condition 성립
- **grade: C**

Holm over the two primary step-accuracy tests: 비교 1 p=0.0684 → 0.1368; 비교 2 p=0.1384 → 0.1384 (verdict uses raw p).

**Grades: 비교 1 = B, 비교 2 = C.**

## Descriptive (QGIS, mean over replicates; not part of the verdict)

| model | backend | step_acc | hall | goal_completion | cost_total $/step | latency s/step |
|---|---|---|---|---|---|---|
| gemini | no_rag | 1.000 | 0.125 | 1.000 | 0.0054 | 8.6 |
| gemini | vanilla_vector | 1.000 | 0.163 | 1.000 | 0.0102 | 10.2 |
| gemini | vanilla_budget | 0.988 | 0.138 | 1.000 | 0.0069 | 9.1 |
| gemini | graph_only | 1.000 | 0.125 | 1.000 | 0.0093 | 32.6 |
| gemini | vision_only | 0.988 | 0.138 | 1.000 | 0.0054 | 10.1 |
| gemini | state_path | 0.975 | 0.125 | 1.000 | 0.0104 | 32.1 |
| gemini | full_system | 1.000 | 0.125 | 1.000 | 0.0115 | 33.1 |
| claude | no_rag | 1.000 | 0.350 | 1.000 | 0.0071 | 2.9 |
| claude | vanilla_vector | 0.875 | 0.275 | 1.000 | 0.0179 | 4.2 |
| claude | vanilla_budget | 0.875 | 0.225 | 1.000 | 0.0104 | 3.3 |
| claude | graph_only | 0.887 | 0.125 | 1.000 | 0.0118 | 26.4 |
| claude | vision_only | 0.975 | 0.150 | 1.000 | 0.0072 | 4.5 |
| claude | state_path | 0.963 | 0.125 | 1.000 | 0.0132 | 25.1 |
| claude | full_system | 0.887 | 0.350 | 1.000 | 0.0143 | 26.4 |
| gpt | no_rag | 0.988 | 0.125 | 1.000 | 0.0038 | 1.9 |
| gpt | vanilla_vector | 0.912 | 0.125 | 1.000 | 0.0115 | 3.1 |
| gpt | vanilla_budget | 0.950 | 0.125 | 1.000 | 0.0063 | 2.2 |
| gpt | graph_only | 0.963 | 0.125 | 0.900 | 0.0074 | 25.4 |
| gpt | vision_only | 1.000 | 0.125 | 1.000 | 0.0039 | 3.3 |
| gpt | state_path | 1.000 | 0.125 | 1.000 | 0.0091 | 24.6 |
| gpt | full_system | 0.838 | 0.125 | 1.000 | 0.0098 | 25.5 |

## Predictions P1–P8

- P1 (QGIS): vanilla_vector − no_rag step_acc per model: gemini +0.000, claude -0.125, gpt -0.075 → ≥ +3pp in 0/3 → 반증
- P1 (dev): vanilla_vector − no_rag step_acc per model: gemini +0.083, claude +0.000, gpt +0.058 → ≥ +3pp in 2/3 → 적중
- P2 (QGIS): cost_total full − vanilla_vector $/step per model: gemini +0.0013, claude -0.0036, gpt -0.0017 → full cheaper in 2/3 (prediction: full may not be cheaper — descriptive)
- P2 (dev): cost_total full − vanilla_vector $/step per model: gemini -0.0025, claude -0.0117, gpt -0.0073 → full cheaper in 3/3 (prediction: full may not be cheaper — descriptive)
- P3 (dev macro): full − vanilla_budget step_acc per model: gemini +0.092, claude +0.125, gpt +0.079 → ≥ 0 in 3/3 → 적중
- P4 (dev, bench mode): attribute routing correct per replicate: mean 7.83/8, min 7/8, replicates ≥ 5/8: 30/30 → 적중; whole dev set routing 464/480 (dry-run rule)
- P5 (QGIS, full_system routing telemetry):
  - gemini: (a) correct-workflow steps mean 7.10/8 (min 7) → ≥ 5/8 ✓; (b) fallback+none mean 0.90/8 (max 1) → ≤ 3/8 ✓
  - claude: (a) correct-workflow steps mean 7.10/8 (min 7) → ≥ 5/8 ✓; (b) fallback+none mean 0.90/8 (max 1) → ≤ 3/8 ✓
  - gpt: (a) correct-workflow steps mean 7.10/8 (min 7) → ≥ 5/8 ✓; (b) fallback+none mean 0.90/8 (max 1) → ≤ 3/8 ✓
  - (c) full ≥ vanilla_budget step_acc in 2/3 → 적중; (d) = P1 (QGIS): 반증
- P6 (dev, 3d_visualization): no_rag / vanilla_vector / full_system step_acc per model (mean over replicates):
  - gemini: 0.750 / 0.825 / 0.950 (spread 20.0pp) → ±5pp 밖 ✗
  - claude: 1.000 / 1.000 / 1.000 (spread 0.0pp) → ±5pp 내 ✓
  - gpt: 0.750 / 0.750 / 0.750 (spread 0.0pp) → ±5pp 내 ✓
- P7 (QGIS, axes where full_system may be inferior): gemini hall full 0.125 vs vanilla_vector 0.163, step_acc full 1.000 vs vanilla_vector 1.000; claude hall full 0.350 vs vanilla_vector 0.275, step_acc full 0.887 vs vanilla_vector 0.875; gpt hall full 0.125 vs vanilla_vector 0.125, step_acc full 0.838 vs vanilla_vector 0.912
- P8 (QGIS 비교 2 direction, no prediction): gemini +0.000, claude +0.012, gpt -0.075 → wins 1/3, ties 1
- §5.x (i) check (count only): full_system losses at QGIS s1/s3/s4 per model over 10 replicates: gemini s1=0/s3=0/s4=0, claude s1=0/s3=0/s4=0, gpt s1=0/s3=10/s4=3
- QGIS routing (bench mode, full_system): node-level correct per model: gemini 59/80, claude 62/80, gpt 61/80
