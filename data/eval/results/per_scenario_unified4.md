# Per-scenario breakdown — unified3

Cells report mean ± sample SD over n=5 replicates. Each scenario value is the mean over that scenario's steps.

## Step Acc (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 85.0±13.7 | 55.0±44.7 | 60.0±16.3 |
| gemini / vanilla_vector | 90.0±13.7 | 80.0±27.4 | 55.0±6.8 |
| gemini / graph_only | 80.0±11.2 | 55.0±27.4 | 75.0±8.8 |
| gemini / vision_only | 90.0±13.7 | 65.0±22.4 | 77.5±16.3 |
| gemini / full_system | 75.0±0.0 | 60.0±28.5 | 82.5±6.8 |
| gemini / state_path | 85.0±13.7 | 65.0±13.7 | 80.0±6.8 |
| claude / no_rag | 100.0±0.0 | 100.0±0.0 | 55.0±6.8 |
| claude / vanilla_vector | 100.0±0.0 | 100.0±0.0 | 52.5±5.6 |
| claude / graph_only | 90.0±13.7 | 100.0±0.0 | 50.0±0.0 |
| claude / vision_only | 100.0±0.0 | 100.0±0.0 | 50.0±0.0 |
| claude / full_system | 100.0±0.0 | 100.0±0.0 | 55.0±6.8 |
| claude / state_path | 100.0±0.0 | 100.0±0.0 | 50.0±0.0 |
| gpt / no_rag | 35.0±13.7 | 40.0±37.9 | 77.5±5.6 |
| gpt / vanilla_vector | 30.0±20.9 | 65.0±13.7 | 85.0±10.5 |
| gpt / graph_only | 60.0±22.4 | 70.0±11.2 | 72.5±5.6 |
| gpt / vision_only | 50.0±25.0 | 55.0±20.9 | 57.5±24.4 |
| gpt / full_system | 65.0±13.7 | 65.0±13.7 | 77.5±5.6 |
| gpt / state_path | 50.0±17.7 | 90.0±13.7 | 77.5±16.3 |
| qwen / no_rag | 50.0±25.0 | 60.0±13.7 | 37.5±15.3 |
| qwen / vanilla_vector | 40.0±13.7 | 95.0±11.2 | 30.0±6.8 |
| qwen / graph_only | 50.0±25.0 | 70.0±11.2 | 27.5±24.0 |
| qwen / vision_only | 65.0±28.5 | 80.0±11.2 | 42.5±20.9 |
| qwen / full_system | 75.0±17.7 | 75.0±0.0 | 20.0±11.2 |
| qwen / state_path | 40.0±13.7 | 80.0±11.2 | 45.0±14.3 |

## Hall Rate (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 0.0±0.0 | 0.0±0.0 | 2.5±5.6 |
| gemini / vanilla_vector | 10.0±13.7 | 0.0±0.0 | 12.5±17.7 |
| gemini / graph_only | 5.0±11.2 | 15.0±22.4 | 7.5±16.8 |
| gemini / vision_only | 0.0±0.0 | 10.0±22.4 | 2.5±5.6 |
| gemini / full_system | 10.0±13.7 | 0.0±0.0 | 12.5±12.5 |
| gemini / state_path | 0.0±0.0 | 0.0±0.0 | 5.0±11.2 |
| claude / no_rag | 35.0±13.7 | 0.0±0.0 | 40.0±16.3 |
| claude / vanilla_vector | 30.0±11.2 | 0.0±0.0 | 42.5±6.8 |
| claude / graph_only | 25.0±0.0 | 0.0±0.0 | 45.0±11.2 |
| claude / vision_only | 40.0±13.7 | 0.0±0.0 | 40.0±5.6 |
| claude / full_system | 20.0±11.2 | 0.0±0.0 | 47.5±13.7 |
| claude / state_path | 15.0±13.7 | 0.0±0.0 | 42.5±14.3 |
| gpt / no_rag | 30.0±11.2 | 40.0±37.9 | 22.5±10.5 |
| gpt / vanilla_vector | 30.0±20.9 | 60.0±22.4 | 20.0±6.8 |
| gpt / graph_only | 25.0±0.0 | 70.0±11.2 | 10.0±5.6 |
| gpt / vision_only | 30.0±11.2 | 60.0±37.9 | 20.0±6.8 |
| gpt / full_system | 25.0±0.0 | 55.0±20.9 | 12.5±0.0 |
| gpt / state_path | 25.0±0.0 | 20.0±20.9 | 17.5±6.8 |
| qwen / no_rag | 50.0±17.7 | 40.0±22.4 | 30.0±19.0 |
| qwen / vanilla_vector | 75.0±30.6 | 85.0±13.7 | 25.0±8.8 |
| qwen / graph_only | 75.0±25.0 | 90.0±13.7 | 37.5±19.8 |
| qwen / vision_only | 55.0±20.9 | 75.0±25.0 | 32.5±31.4 |
| qwen / full_system | 50.0±25.0 | 85.0±22.4 | 15.0±10.5 |
| qwen / state_path | 45.0±11.2 | 80.0±11.2 | 45.0±14.3 |

## Goal Comp (%) by scenario

| Model / Backend | survey_setup (Low, 4st) | 3d_visualization (Low, 4st) | attribute_computation (**High**, 8st) |
|---|---|---|---|
| gemini / no_rag | 100.0±0.0 | 40.0±54.8 | 100.0±0.0 |
| gemini / vanilla_vector | 100.0±0.0 | 80.0±44.7 | 100.0±0.0 |
| gemini / graph_only | 100.0±0.0 | 40.0±54.8 | 100.0±0.0 |
| gemini / vision_only | 100.0±0.0 | 40.0±54.8 | 100.0±0.0 |
| gemini / full_system | 40.0±54.8 | 100.0±0.0 | 100.0±0.0 |
| gemini / state_path | 80.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| claude / no_rag | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / vanilla_vector | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / graph_only | 80.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| claude / vision_only | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / full_system | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| claude / state_path | 40.0±54.8 | 100.0±0.0 | 100.0±0.0 |
| gpt / no_rag | 20.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| gpt / vanilla_vector | 20.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| gpt / graph_only | 100.0±0.0 | 100.0±0.0 | 100.0±0.0 |
| gpt / vision_only | 80.0±44.7 | 80.0±44.7 | 100.0±0.0 |
| gpt / full_system | 80.0±44.7 | 100.0±0.0 | 100.0±0.0 |
| gpt / state_path | 80.0±44.7 | 80.0±44.7 | 100.0±0.0 |
| qwen / no_rag | 60.0±54.8 | 40.0±54.8 | 60.0±54.8 |
| qwen / vanilla_vector | 0.0±0.0 | 20.0±44.7 | 100.0±0.0 |
| qwen / graph_only | 20.0±44.7 | 40.0±54.8 | 0.0±0.0 |
| qwen / vision_only | 0.0±0.0 | 40.0±54.8 | 0.0±0.0 |
| qwen / full_system | 0.0±0.0 | 60.0±54.8 | 60.0±54.8 |
| qwen / state_path | 0.0±0.0 | 80.0±44.7 | 40.0±54.8 |

