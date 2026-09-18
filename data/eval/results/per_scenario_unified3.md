# Per-scenario breakdown — unified3

Cells report mean ± sample SD over n=5 replicates. Each scenario value is the mean over that scenario's steps.

## Step Acc (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 75.0±0.0 | 20.0±27.4 | 72.5±5.6 |
| gemini / vanilla_vector | 85.0±13.7 | 60.0±13.7 | 57.5±6.8 |
| gemini / graph_only | 80.0±11.2 | 30.0±44.7 | 80.0±14.3 |
| gemini / vision_only | 80.0±11.2 | 35.0±13.7 | 75.0±15.3 |
| gemini / full_system | 90.0±13.7 | 55.0±11.2 | 77.5±13.7 |
| gemini / state_path | 80.0±20.9 | 55.0±11.2 | 85.0±10.5 |
| claude / no_rag | 100.0±0.0 | 100.0±0.0 | 57.5±6.8 |
| claude / vanilla_vector | 100.0±0.0 | 100.0±0.0 | 50.0±0.0 |
| claude / graph_only | 90.0±13.7 | 100.0±0.0 | 50.0±0.0 |
| claude / vision_only | 100.0±0.0 | 100.0±0.0 | 50.0±0.0 |
| claude / full_system | 100.0±0.0 | 100.0±0.0 | 52.5±5.6 |
| claude / state_path | 100.0±0.0 | 100.0±0.0 | 50.0±0.0 |
| gpt / no_rag | 35.0±13.7 | 60.0±37.9 | 75.0±12.5 |
| gpt / vanilla_vector | 25.0±17.7 | 60.0±22.4 | 97.5±5.6 |
| gpt / graph_only | 45.0±11.2 | 75.0±17.7 | 77.5±5.6 |
| gpt / vision_only | 65.0±13.7 | 75.0±17.7 | 75.0±15.3 |
| gpt / full_system | 60.0±13.7 | 60.0±22.4 | 72.5±10.5 |
| gpt / state_path | 70.0±11.2 | 95.0±11.2 | 65.0±13.7 |
| qwen / no_rag | 25.0±17.7 | 80.0±32.6 | 25.0±8.8 |
| qwen / vanilla_vector | 25.0±17.7 | 60.0±22.4 | 40.0±16.3 |
| qwen / graph_only | 55.0±11.2 | 60.0±13.7 | 27.5±13.7 |
| qwen / vision_only | 40.0±33.5 | 70.0±11.2 | 32.5±6.8 |
| qwen / full_system | 70.0±20.9 | 75.0±17.7 | 37.5±12.5 |
| qwen / state_path | 55.0±27.4 | 80.0±11.2 | 50.0±17.7 |

## Hall Rate (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 0.0±0.0 | 0.0±0.0 | 0.0±0.0 |
| gemini / vanilla_vector | 5.0±11.2 | 5.0±11.2 | 5.0±11.2 |
| gemini / graph_only | 0.0±0.0 | 0.0±0.0 | 7.5±16.8 |
| gemini / vision_only | 5.0±11.2 | 5.0±11.2 | 2.5±5.6 |
| gemini / full_system | 0.0±0.0 | 5.0±11.2 | 0.0±0.0 |
| gemini / state_path | 0.0±0.0 | 0.0±0.0 | 10.0±10.5 |
| claude / no_rag | 40.0±13.7 | 0.0±0.0 | 37.5±8.8 |
| claude / vanilla_vector | 40.0±13.7 | 0.0±0.0 | 50.0±12.5 |
| claude / graph_only | 20.0±11.2 | 0.0±0.0 | 42.5±11.2 |
| claude / vision_only | 30.0±11.2 | 0.0±0.0 | 45.0±11.2 |
| claude / full_system | 25.0±0.0 | 0.0±0.0 | 50.0±12.5 |
| claude / state_path | 20.0±11.2 | 0.0±0.0 | 57.5±11.2 |
| gpt / no_rag | 30.0±11.2 | 45.0±32.6 | 25.0±12.5 |
| gpt / vanilla_vector | 25.0±0.0 | 70.0±11.2 | 25.0±0.0 |
| gpt / graph_only | 35.0±13.7 | 55.0±32.6 | 17.5±6.8 |
| gpt / vision_only | 25.0±0.0 | 55.0±32.6 | 12.5±0.0 |
| gpt / full_system | 20.0±11.2 | 60.0±33.5 | 17.5±11.2 |
| gpt / state_path | 25.0±0.0 | 10.0±22.4 | 15.0±5.6 |
| qwen / no_rag | 40.0±13.7 | 80.0±32.6 | 10.0±5.6 |
| qwen / vanilla_vector | 60.0±45.4 | 75.0±17.7 | 30.0±20.9 |
| qwen / graph_only | 55.0±20.9 | 90.0±22.4 | 35.0±18.5 |
| qwen / vision_only | 65.0±28.5 | 85.0±13.7 | 32.5±6.8 |
| qwen / full_system | 45.0±11.2 | 85.0±13.7 | 52.5±18.5 |
| qwen / state_path | 35.0±33.5 | 85.0±13.7 | 60.0±22.4 |

## Goal Comp (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 100.0±0.0 | 40.0±54.8 | 100.0±0.0 |
| gemini / vanilla_vector | 100.0±0.0 | 40.0±54.8 | 100.0±0.0 |
| gemini / graph_only | 100.0±0.0 | 40.0±54.8 | 100.0±0.0 |
| gemini / vision_only | 100.0±0.0 | 20.0±44.7 | 100.0±0.0 |
| gemini / full_system | 80.0±44.7 | 60.0±54.8 | 100.0±0.0 |
| gemini / state_path | 60.0±54.8 | 80.0±44.7 | 80.0±44.7 |
| claude / no_rag | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / vanilla_vector | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / graph_only | 80.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| claude / vision_only | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / full_system | 100.0±0.0 | 80.0±44.7 | 100.0±0.0 |
| claude / state_path | 80.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| gpt / no_rag | 20.0±44.7 | 80.0±44.7 | 100.0±0.0 |
| gpt / vanilla_vector | 40.0±54.8 | 100.0±0.0 | 100.0±0.0 |
| gpt / graph_only | 80.0±44.7 | 80.0±44.7 | 100.0±0.0 |
| gpt / vision_only | 100.0±0.0 | 80.0±44.7 | 100.0±0.0 |
| gpt / full_system | 20.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| gpt / state_path | 20.0±44.7 | 80.0±44.7 | 100.0±0.0 |
| qwen / no_rag | 20.0±44.7 | 40.0±54.8 | 80.0±44.7 |
| qwen / vanilla_vector | 0.0±0.0 | 40.0±54.8 | 20.0±44.7 |
| qwen / graph_only | 60.0±54.8 | 40.0±54.8 | 20.0±44.7 |
| qwen / vision_only | 20.0±44.7 | 60.0±54.8 | 40.0±54.8 |
| qwen / full_system | 20.0±44.7 | 40.0±54.8 | 0.0±0.0 |
| qwen / state_path | 20.0±44.7 | 60.0±54.8 | 20.0±44.7 |

