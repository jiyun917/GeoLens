#!/usr/bin/env bash
# Study 4 development/verification environment = study-3 pins + the study-4 mechanism changes.
# Source AFTER scripts/study2_env.sh. Every value here is exported unconditionally (V3-41 lesson).
export GEOLENS_SCORER=v6                 # v5 + tokenizer fix (bracket glued to a Latin run)
export CONTEXT_ASSEMBLY=v8               # chain lookahead (3 edges) + lookbehind (1 edge), screen-judged
export ROUTER_SESSION_STICKY=1           # R1 (study 2)
export ROUTER_HISTORY_ADVANCE=1          # R2'' (study 3) ...
export ROUTER_ADVANCE_MIN_COVERAGE=0.6   # ... with the coverage bar lowered to _edge_covered's 0.6
export ROUTER_SCREEN_ADVANCE=1           # R3 (study 4): screen-delta advance
export ROUTER_SCREEN_ADVANCE_HOPS=3
export ROUTER_SCREEN_ADVANCE_MIN_TOKENS=1
export ROUTER_PRIOR_HOPS=2               # 2-hop successors in the candidate pool
export RERANK_SESSION_BLOCK=1
export GEN_PROMPT_VERSION=v3             # grounded references only (all backends alike)
