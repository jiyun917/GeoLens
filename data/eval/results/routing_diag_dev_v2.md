# Routing diagnosis — development set, v2 mechanism (2026-09-18)

**Scope**: development set only (opendtect__survey_setup__01, opendtect__3d_visualization__01, opendtect__attribute_computation__01; 16 steps). QGIS test set not touched.
**Input**: the vision outputs recorded by the thinking-off dry-run of 2026-09-17 (`routing_dryrun_vision_think0.json`, all 7 workflow JSONs loaded = 41 candidate nodes). No new API calls; candidate pools recomputed offline with the v2 substring scorer and CLIP.
**Question**: where does a failed step drop out — at the candidate stage (keyword-substring top-3 ∪ CLIP top-3) or at the LLM rerank?

## Stage attribution (v2 substring matcher + CLIP, rerank thinking off)

| scenario | step | expected wf in candidate pool? | rerank result | stage |
|---|---|---|---|---|
| 3d_visualization | 0 | yes | d3_visualization 0.8 | OK |
| 3d_visualization | 1 | yes | d3_visualization 0.8 | OK |
| 3d_visualization | 2 | yes | d3_visualization 0.8 | OK |
| 3d_visualization | 3 | yes | none | RERANK_NONE |
| attribute_computation | 0–7 | **no (8/8)** | none ×4, horizon_tracking 0.7, d3_visualization 0.8 ×2, auto_bf2804 0.5 | **POOL_MISS ×8** |
| survey_setup | 0–3 | yes | survey_setup 0.8–0.9 | OK ×4 |

Summary: 16 steps = OK 7, POOL_MISS 8, RERANK_NONE 1, RERANK_WRONG 0, LOW_CONF 0.

## Why the pool misses seismic_attribute

Best v2 substring score of any seismic_attribute node vs best other-workflow node, per attribute step: 0.18–0.20 vs 0.47–0.67 (8/8 steps). The vision output does carry the on-screen strings ('Attribute Set 3D', 'Energy dropdown', 'Add as new button', 'Save on Close checkbox', 'Select Layer 2'), but the seismic_attribute signatures are descriptive sentences ("about to choose an Attribute Type", "Input Data = 4 Dip steered median filter", "Time gate populated: -28 to +28") that never occur verbatim, so their substring fraction stays near 0.2, while survey_setup / horizon_tracking / d3_visualization nodes carry short generic tokens ('Survey', 'Add', 'Elements', 'Select') that occur in almost any OpendTect screen and score 0.5–0.7.

CLIP top-3 never contributes a seismic_attribute node either: cosine 0.82–0.91 for d3_visualization / auto_bf2804 (QGIS) nodes on every OpendTect screen — UI chrome dominates, and the page-proximity node mapping is not manual-aware.

## Decision (mechanism, not signatures)

Option (a) — make the vision prompt report on-screen strings verbatim — does not address the failure: the strings are already reported; the signatures are not verbatim strings. Option (b) — replace the substring fraction by embedding similarity between the vision output and the node text (title + description + expected dialog + UI elements + keywords) under the retrieval embedder (bge-m3) — targets the failure directly and treats every workflow identically. No signature text is edited.

Offline check with the same stored vision outputs, embedding matcher top-3: expected workflow in pool **14/16** (v2: 8/16); top-1 correct 11/16. The two remaining misses are attribute steps 5 and 7 (main window with an In-line displayed; d3_visualization nodes are semantically closest — a genuine ambiguity, not a scorer artifact).

Implementation: `api/services/node_matcher.py` (ROUTER_MATCHER=embedding default; `substring` reproduces v2), wired into `WorkflowGraph.get_top_k_nodes` / `get_current_node`. CLIP stage unchanged.
