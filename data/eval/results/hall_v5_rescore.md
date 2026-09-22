# 환각 정의 v5 재채점 (2차 분석; 정의 = data/eval/study2/hall_v5_definition.md; 재실행 없음, 원본 불변)

## Study 2 test set (tag study2)

| model | backend | hall v4 | hall v5 | Δ |
|---|---|---|---|---|
| gemini | no_rag | 0.100 | 0.043 | -0.057 |
| gemini | vanilla_budget | 0.127 | 0.021 | -0.106 |
| gemini | vanilla_vector | 0.071 | 0.000 | -0.071 |
| gemini | full_system | 0.094 | 0.000 | -0.094 |
| claude | no_rag | 0.133 | 0.011 | -0.122 |
| claude | vanilla_budget | 0.000 | 0.000 | +0.000 |
| claude | vanilla_vector | 0.142 | 0.000 | -0.142 |
| claude | full_system | 0.022 | 0.000 | -0.022 |
| gpt | no_rag | 0.014 | 0.000 | -0.014 |
| gpt | vanilla_budget | 0.057 | 0.000 | -0.057 |
| gpt | vanilla_vector | 0.035 | 0.000 | -0.035 |
| gpt | full_system | 0.144 | 0.000 | -0.144 |

## v3 QGIS test set (tag v3_qgis)

| model | backend | hall v4 | hall v5 | Δ |
|---|---|---|---|---|
| gemini | no_rag | 0.125 | 0.125 | +0.000 |
| gemini | vanilla_budget | 0.125 | 0.125 | +0.000 |
| gemini | vanilla_vector | 0.125 | 0.125 | +0.000 |
| gemini | full_system | 0.125 | 0.125 | +0.000 |
| gemini | graph_only | 0.113 | 0.113 | +0.000 |
| gemini | vision_only | 0.125 | 0.125 | +0.000 |
| gemini | state_path | 0.125 | 0.125 | +0.000 |
| claude | no_rag | 0.125 | 0.125 | +0.000 |
| claude | vanilla_budget | 0.125 | 0.125 | +0.000 |
| claude | vanilla_vector | 0.125 | 0.125 | +0.000 |
| claude | full_system | 0.125 | 0.125 | +0.000 |
| claude | graph_only | 0.125 | 0.125 | +0.000 |
| claude | vision_only | 0.125 | 0.125 | +0.000 |
| claude | state_path | 0.125 | 0.125 | +0.000 |
| gpt | no_rag | 0.125 | 0.125 | +0.000 |
| gpt | vanilla_budget | 0.125 | 0.125 | +0.000 |
| gpt | vanilla_vector | 0.125 | 0.125 | +0.000 |
| gpt | full_system | 0.125 | 0.125 | +0.000 |
| gpt | graph_only | 0.125 | 0.125 | +0.000 |
| gpt | vision_only | 0.125 | 0.125 | +0.000 |
| gpt | state_path | 0.125 | 0.125 | +0.000 |

## v3 OpendTect dev set (tag v3)

| model | backend | hall v4 | hall v5 | Δ |
|---|---|---|---|---|
| gemini | no_rag | 0.029 | 0.000 | -0.029 |
| gemini | vanilla_budget | 0.021 | 0.000 | -0.021 |
| gemini | vanilla_vector | 0.033 | 0.000 | -0.033 |
| gemini | full_system | 0.029 | 0.000 | -0.029 |
| gemini | graph_only | 0.017 | 0.000 | -0.017 |
| gemini | vision_only | 0.025 | 0.004 | -0.021 |
| gemini | state_path | 0.033 | 0.000 | -0.033 |
| claude | no_rag | 0.050 | 0.000 | -0.050 |
| claude | vanilla_budget | 0.042 | 0.000 | -0.042 |
| claude | vanilla_vector | 0.042 | 0.000 | -0.042 |
| claude | full_system | 0.042 | 0.000 | -0.042 |
| claude | graph_only | 0.042 | 0.000 | -0.042 |
| claude | vision_only | 0.046 | 0.000 | -0.046 |
| claude | state_path | 0.042 | 0.000 | -0.042 |
| gpt | no_rag | 0.050 | 0.000 | -0.050 |
| gpt | vanilla_budget | 0.042 | 0.000 | -0.042 |
| gpt | vanilla_vector | 0.046 | 0.000 | -0.046 |
| gpt | full_system | 0.104 | 0.025 | -0.079 |
| gpt | graph_only | 0.042 | 0.000 | -0.042 |
| gpt | vision_only | 0.046 | 0.000 | -0.046 |
| gpt | state_path | 0.058 | 0.017 | -0.042 |

## Study 2 — hall 조건을 v5로 재평가한 2차 분석 등급 (step accuracy 조건은 서명된 판정 그대로: 비교 1 성립, 비교 2 불성립)

- full_system vs vanilla_budget: gemini 0.000 vs 0.021 (✓, p 0.226); claude 0.000 vs 0.000 (✓, p 1.000); gpt 0.000 vs 0.000 (✓, p 1.000) → hall 조건 3/3 성립 → **2차 분석 등급 A** (서명된 등급 A′)
- full_system vs vanilla_vector: gemini 0.000 vs 0.000 (✓, p 1.000); claude 0.000 vs 0.000 (✓, p 1.000); gpt 0.000 vs 0.000 (✓, p 1.000) → hall 조건 3/3 성립 → **2차 분석 등급 B** (서명된 등급 B)

## v5에서 제외된 라벨(매뉴얼 절에 있음) 상위

- v3: 'OK' × 187
- study2: 'Manual Tracking' × 37
- study2: 'Add' × 21
- study2: 'QC' × 20
- study2: 'Properties' × 16
- study2: 'Left-click + drag' × 13
- study2: 'Z/X' × 12
- study2: 'Ctrl + Left-click' × 10
- v3: 'QC' × 9
- study2: 'Left-click' × 7
- study2: 'Display' × 3
- v3: 'Input Data 드롭다운' × 3
- study2: 'Display Only' × 2
- study2: 'sections only' × 2
- study2: 'Add/Display' × 2
- study2: 'OK' × 2
- study2: 'Ctrl+' × 2
- study2: 'Ctrl +' × 1
- study2: 'Attribute' × 1
- study2: 'Ctrl' × 1

## v5에서 남은 라벨(화면에도 매뉴얼 절에도 없음) 상위

- v3_qgis: 'OK' × 209
- v3: 'Add Data' × 5
- study2: 'Lock Horizon' × 3
- study2: 'Display Properties' × 2
- study2: 'Track Horizon 3D' × 1
- study2: 'Horizon auto-track' × 1
- study2: 'Lock/Unlock current patch' × 1
- study2: 'Lock/Unlock patch' × 1
- study2: 'Track Horizon' × 1
- study2: 'Lock patch' × 1
- v3: 'Dip steered median filter [SteeringCube]' × 1
