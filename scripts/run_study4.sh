#!/usr/bin/env bash
# Study 4 confirmatory run - signed pre-registration data/eval/study4/study4_pre_registration_DRAFT.md.
# Two passes (GEOLENS_SOFTWARE_ID per process): (1) OpendTect test scenarios, (2) QGIS test scenarios.
# Matrix per pass: MODELS x {no_rag, vanilla_budget, vanilla_vector, full_system} x scenarios x REPS.
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
source scripts/study4_env.sh            # every study-4 pin exported unconditionally (V3-41 lesson)
TAG="${TAG:-study4}"
REPS="${REPS:-10}"
MODELS="${MODELS:-gemini,claude,gpt}"
OT_DIR="${OT_DIR:-data/eval/scenarios/.study4_test_opendtect}"
QG_DIR="${QG_DIR:-data/eval/scenarios/.study4_test_qgis}"
PASSES="${PASSES:-opendtect,qgis}"
START_REP="${START_REP:-1}"
PY=".venv/Scripts/python.exe"
LOG="data/eval/results/${TAG}_bench.log"
if ! git tag --list | grep -q "^study4-prereg-signed$"; then echo "pre-registration not signed (tag study4-prereg-signed missing)"; exit 2; fi
for d in "$OT_DIR" "$QG_DIR"; do
  $PY scripts/preflight_check.py --scenarios "$d" --expect GEOLENS_SCORER=v6 CONTEXT_ASSEMBLY=v8 ROUTER_SESSION_STICKY=1 ROUTER_HISTORY_ADVANCE=1 ROUTER_ADVANCE_MIN_COVERAGE=0.6 ROUTER_SCREEN_ADVANCE=1 ROUTER_SCREEN_ADVANCE_HOPS=3 ROUTER_PRIOR_HOPS=2 RERANK_SESSION_BLOCK=1 GEN_PROMPT_VERSION=v3 CHROMADB_PATH=./data/chromadb_v4 EMBED_MODEL=BAAI/bge-m3 || { echo "preflight failed for $d - run refused"; exit 2; }
done
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench kickoff === passes=${PASSES} models=${MODELS} reps=${REPS} start=${START_REP}"
  echo "scorer=${GEOLENS_SCORER} assembly=${CONTEXT_ASSEMBLY} sticky=${ROUTER_SESSION_STICKY} advance=${ROUTER_HISTORY_ADVANCE}/${ROUTER_ADVANCE_MIN_COVERAGE} screen_advance=${ROUTER_SCREEN_ADVANCE}/${ROUTER_SCREEN_ADVANCE_HOPS} prior_hops=${ROUTER_PRIOR_HOPS} session_block=${RERANK_SESSION_BLOCK} gen_prompt=${GEN_PROMPT_VERSION} pool=$(ls data/workflows/*.json | wc -l)"
  echo "git: $(git rev-parse --short HEAD); dirty=$(git status --short -- api scripts data/workflows data/eval/scenarios | wc -l) files"
} | tee -a "$LOG"
for pass in ${PASSES//,/ }; do
  dir=$OT_DIR; sid=opendtect; [ "$pass" = qgis ] && { dir=$QG_DIR; sid=qgis; }
  echo "$(date -u +%H:%M:%S) === pass ${pass} (GEOLENS_SOFTWARE_ID=${sid}, $(ls "$dir"/*.json | xargs -n1 basename | tr '\n' ' ')) ===" | tee -a "$LOG"
  GEOLENS_SOFTWARE_ID=$sid $PY -u scripts/run_all_models.py --models "$MODELS" --repeats "$REPS" --start "$START_REP" --judge consensus --tag "${TAG}_${pass}" \
      --backends no_rag vanilla_budget vanilla_vector full_system --scenarios "$dir" 2>&1 | tee -a "$LOG"
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench complete ===" | tee -a "$LOG"
