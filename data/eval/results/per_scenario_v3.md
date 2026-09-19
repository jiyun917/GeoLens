# Per-scenario breakdown — unified3

Cells report mean ± sample SD over n=5 replicates. Each scenario value is the mean over that scenario's steps.

## Step Acc (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 85.0±12.9 | 75.0±0.0 | 60.0±11.5 |
| gemini / vanilla_vector | 100.0±0.0 | 82.5±12.1 | 62.5±14.4 |
| gemini / vanilla_budget | 87.5±13.2 | 85.0±12.9 | 73.8±15.0 |
| gemini / graph_only | 82.5±12.1 | 85.0±12.9 | 68.8±12.1 |
| gemini / vision_only | 77.5±7.9 | 87.5±13.2 | 70.0±13.4 |
| gemini / full_system | 82.5±12.1 | 95.0±10.5 | 96.2±6.0 |
| gemini / state_path | 70.0±15.8 | 85.0±17.5 | 86.2±9.2 |
| claude / no_rag | 100.0±0.0 | 100.0±0.0 | 62.5±0.0 |
| claude / vanilla_vector | 100.0±0.0 | 100.0±0.0 | 62.5±0.0 |
| claude / vanilla_budget | 100.0±0.0 | 100.0±0.0 | 62.5±0.0 |
| claude / graph_only | 100.0±0.0 | 100.0±0.0 | 62.5±0.0 |
| claude / vision_only | 100.0±0.0 | 100.0±0.0 | 62.5±0.0 |
| claude / full_system | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / state_path | 92.5±12.1 | 100.0±0.0 | 62.5±0.0 |
| gpt / no_rag | 62.5±13.2 | 75.0±0.0 | 75.0±0.0 |
| gpt / vanilla_vector | 60.0±12.9 | 75.0±0.0 | 95.0±8.7 |
| gpt / vanilla_budget | 65.0±12.9 | 75.0±0.0 | 77.5±7.9 |
| gpt / graph_only | 97.5±7.9 | 75.0±0.0 | 83.8±15.6 |
| gpt / vision_only | 87.5±17.7 | 72.5±14.2 | 75.0±11.8 |
| gpt / full_system | 77.5±18.4 | 75.0±0.0 | 88.8±4.0 |
| gpt / state_path | 85.0±17.5 | 87.5±13.2 | 100.0±0.0 |

## Hall Rate (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 0.0±0.0 | 0.0±0.0 | 8.8±6.0 |
| gemini / vanilla_vector | 0.0±0.0 | 0.0±0.0 | 10.0±5.3 |
| gemini / vanilla_budget | 0.0±0.0 | 0.0±0.0 | 6.2±6.6 |
| gemini / graph_only | 0.0±0.0 | 0.0±0.0 | 5.0±6.5 |
| gemini / vision_only | 0.0±0.0 | 0.0±0.0 | 7.5±6.5 |
| gemini / full_system | 0.0±0.0 | 0.0±0.0 | 8.8±6.0 |
| gemini / state_path | 0.0±0.0 | 0.0±0.0 | 10.0±5.3 |
| claude / no_rag | 0.0±0.0 | 0.0±0.0 | 15.0±5.3 |
| claude / vanilla_vector | 0.0±0.0 | 0.0±0.0 | 12.5±0.0 |
| claude / vanilla_budget | 0.0±0.0 | 0.0±0.0 | 12.5±0.0 |
| claude / graph_only | 0.0±0.0 | 0.0±0.0 | 12.5±0.0 |
| claude / vision_only | 0.0±0.0 | 0.0±0.0 | 13.8±4.0 |
| claude / full_system | 0.0±0.0 | 0.0±0.0 | 12.5±0.0 |
| claude / state_path | 0.0±0.0 | 0.0±0.0 | 12.5±0.0 |
| gpt / no_rag | 2.5±7.9 | 0.0±0.0 | 12.5±0.0 |
| gpt / vanilla_vector | 0.0±0.0 | 0.0±0.0 | 13.8±4.0 |
| gpt / vanilla_budget | 0.0±0.0 | 0.0±0.0 | 12.5±0.0 |
| gpt / graph_only | 0.0±0.0 | 0.0±0.0 | 12.5±0.0 |
| gpt / vision_only | 0.0±0.0 | 0.0±0.0 | 13.8±4.0 |
| gpt / full_system | 7.5±12.1 | 0.0±0.0 | 23.8±4.0 |
| gpt / state_path | 5.0±10.5 | 0.0±0.0 | 12.5±0.0 |

## Goal Comp (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 100.0±0.0 | 10.0±31.6 | 100.0±0.0 |
| gemini / vanilla_vector | 100.0±0.0 | 20.0±42.2 | 100.0±0.0 |
| gemini / vanilla_budget | 100.0±0.0 | 40.0±51.6 | 90.0±31.6 |
| gemini / graph_only | 100.0±0.0 | 50.0±52.7 | 100.0±0.0 |
| gemini / vision_only | 100.0±0.0 | 30.0±48.3 | 100.0±0.0 |
| gemini / full_system | 70.0±48.3 | 90.0±31.6 | 100.0±0.0 |
| gemini / state_path | 20.0±42.2 | 60.0±51.6 | 100.0±0.0 |
| claude / no_rag | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / vanilla_vector | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / vanilla_budget | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / graph_only | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / vision_only | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / full_system | 80.0±42.2 | 100.0±0.0 | 100.0±0.0 |
| claude / state_path | 40.0±51.6 | 100.0±0.0 | 100.0±0.0 |
| gpt / no_rag | 0.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| gpt / vanilla_vector | 0.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| gpt / vanilla_budget | 70.0±48.3 | 100.0±0.0 | 100.0±0.0 |
| gpt / graph_only | 100.0±0.0 | 100.0±0.0 | 90.0±31.6 |
| gpt / vision_only | 100.0±0.0 | 80.0±42.2 | 100.0±0.0 |
| gpt / full_system | 20.0±42.2 | 100.0±0.0 | 0.0±0.0 |
| gpt / state_path | 0.0±0.0 | 90.0±31.6 | 100.0±0.0 |

