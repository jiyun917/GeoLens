# Scenario Schema (v1.1)

Location: `data/eval/scenarios/opendtect__<goal_slug>__<variant>.json`

Excluded / draft scenarios go under `data/eval/scenarios/excluded/`.

## Top-level fields

| field | type | required | meaning |
|---|---|---|---|
| `scenario_id` | string | ✓ | `opendtect__<goal_slug>__<variant>` — must match filename |
| `manual_id` | string | ✓ | ChromaDB collection id for the source manual |
| `manual_name` | string | ✓ | human-readable manual title |
| `manual_reference` | string | ✓ | chapter reference in the manual (e.g. `1.2.2a Survey Setup & Load SEG-Y`) — anchors the scenario to a specific manual section |
| `category` | string | ✓ | `setup` / `import` / `visualization` / `tracking` / `attribute` / `interpretation` / … |
| `difficulty` | string | ✓ | `easy` / `medium` / `hard` |
| `language` | string | ✓ | `ko` / `en` — output language expected from the model |
| `goal` | string | ✓ | user-typed goal text (verbatim as pasted into GeoLens) |
| `initial_state` | object | ✓ | pre-conditions before step 0 — see below |
| `steps` | array | ✓ | ordered steps — see below |
| `completion` | object | ✓ | goal-completion criteria |

## `initial_state`

| field | type | meaning |
|---|---|---|
| `description` | string | prose summary — what OpendTect state must exist before capture starts |
| `must_be_true` | array<string> | machine-readable assertions the capturer verifies before pressing start |

## `steps[i]`

| field | type | meaning |
|---|---|---|
| `step_index` | int | 0-based, matches captured filename `step_<i>.jpg` |
| `screenshot_path` | string | path relative to repo root |
| `visual_state_gt` | object | ground-truth UI extraction expected from the vision recognizer |
| `expected_action_text_pattern` | string | regex (case-insensitive) the AI response should match — anchors scoring |
| `expected_action_keywords` | array<string> | lenient keyword list (used when regex is too strict) |
| `allowed_alternatives` | array<{pattern, note}> | acceptable phrasing variants |
| `expected_workflow_node` | string \| null | workflow node id the localizer SHOULD pick; null = any acceptable |
| `is_error_recovery_test` | bool | true when the step tests wrong-state detection & recovery |
| `trap` | object \| absent | describes a scored trap (`category_vs_child_item`, `post_completion_repeat`, `goal_completion_sentinel`, `prefer_verify_over_skip`) |
| `capture_instructions` | object | tells the human capturer exactly which screen state to show |
| `capture_required` | bool | true = needs a new capture; false/absent = archived screenshot already covers it |
| `source_note` | string | provenance note (mapping origin) |

### `steps[i].capture_instructions`

| field | meaning |
|---|---|
| `screen_state` | one-line description of the frame to capture |
| `user_should_have_just` | user action that produces the state |
| `must_not_show` | array<string> of contents that invalidate the capture |

## `completion`

| field | meaning |
|---|---|
| `final_screenshot_path` | screenshot after goal achieved (may be null if same as last step) |
| `expected_done_sentinel` | true = model should emit `완료`/`Done` after this |
| `known_limitation` | optional string — describes a documented weakness |
| `known_failure` | optional string — for scenarios where completion is known to break |

## Adding a new scenario

1. Write JSON under `data/eval/scenarios/opendtect__<slug>__01.json`
2. Fill top-level metadata + `initial_state` + steps + `completion`
3. Anchor to a manual chapter via `manual_reference`
4. Capture the required screenshots and place under `data/eval/screenshots/<scenario_id>/`
5. Run `python scripts/validate_screenshots.py --scenario <scenario_id>` — every step must return `[OK]` before `bench_runner` is invoked
6. If any step is `[FAIL]`, either recapture the screenshot or refine `expected_action_keywords` — but do NOT relax keywords to match a bad capture; that defeats the metric

## Categories used so far

| category | scenario | manual ref |
|---|---|---|
| setup | `opendtect__survey_setup__01` | 1.2.2a |
| visualization | `opendtect__3d_visualization__01` | 1.3.1a |

Planned expansions (chapter-anchored):
- `random_line` — 1.3.x
- `horizon_tracking` — 1.4.2
- `attribute` — 1.5.x
