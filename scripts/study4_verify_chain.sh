#!/usr/bin/env bash
# Study 4 - development verification on the development sets (study-2 + study-3 test sets, now dev data, and
# the v3 QGIS test scenario): all four backends, 3 models, 1 replicate, study-4 configuration. Preflight-gated
# (dirty tree allowed: development). Two passes because GEOLENS_SOFTWARE_ID is per process.
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
source scripts/study4_env.sh
PY=".venv/Scripts/python.exe"
TAG="${TAG:-study4ver}"
MODELS="${MODELS:-gemini,claude,gpt}"
BACKENDS="${BACKENDS:-no_rag vanilla_budget vanilla_vector full_system}"
PASSES="${PASSES:-opendtect,qgis}"
LOG="data/eval/results/${TAG}.log"
OT_DIR="data/eval/scenarios/.study4_dev_opendtect"; QG_DIR="data/eval/scenarios/.study4_dev_qgis"
for d in "$OT_DIR" "$QG_DIR"; do
  $PY scripts/preflight_check.py --scenarios "$d" --expect GEOLENS_SCORER=v6 CONTEXT_ASSEMBLY=v8 ROUTER_SESSION_STICKY=1 ROUTER_HISTORY_ADVANCE=1 ROUTER_SCREEN_ADVANCE=1 ROUTER_PRIOR_HOPS=2 GEN_PROMPT_VERSION=v3 CHROMADB_PATH=./data/chromadb_v4 --allow-dirty || { echo "preflight failed for $d" | tee -a "$LOG"; exit 2; }
done
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} kickoff === git $(git rev-parse --short HEAD) dirty=$(git status --short -- api scripts data/workflows | wc -l); pool=$(ls data/workflows/*.json | wc -l)"
  echo "scorer=$GEOLENS_SCORER assembly=$CONTEXT_ASSEMBLY sticky=$ROUTER_SESSION_STICKY advance=$ROUTER_HISTORY_ADVANCE/$ROUTER_ADVANCE_MIN_COVERAGE screen_advance=$ROUTER_SCREEN_ADVANCE/$ROUTER_SCREEN_ADVANCE_HOPS prior_hops=$ROUTER_PRIOR_HOPS session_block=$RERANK_SESSION_BLOCK gen_prompt=$GEN_PROMPT_VERSION"
} | tee -a "$LOG"
for pass in ${PASSES//,/ }; do
  dir=$OT_DIR; sid=opendtect; [ "$pass" = qgis ] && { dir=$QG_DIR; sid=qgis; }
  echo "$(date -u +%H:%M:%S) === pass ${pass} ($(ls "$dir"/*.json | xargs -n1 basename | tr '\n' ' ')) ===" | tee -a "$LOG"
  GEOLENS_SOFTWARE_ID=$sid $PY -u scripts/run_all_models.py --models "$MODELS" --repeats 1 --judge consensus --tag "${TAG}_${pass}" \
      --backends $BACKENDS --scenarios "$dir" 2>&1 | tee -a "$LOG"
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} complete ===" | tee -a "$LOG"
