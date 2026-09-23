#!/usr/bin/env bash
# Study 3 confirmatory run — signed pre-registration data/eval/study3/study3_pre_registration_DRAFT.md.
# Two passes because the vision-prompt profile / completion patterns are selected per process by
# GEOLENS_SOFTWARE_ID: (1) OpendTect test scenarios, (2) QGIS test scenarios. Same pool, same knobs.
# Matrix per pass: MODELS x {no_rag, vanilla_budget, vanilla_vector, full_system} x scenarios x REPS.
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
# Pinned by the signed pre-registration (tag study3-prereg-signed, sections 2/6) and NOT overridable from the
# environment. V3-41: the previous ':-v5' fallback let study2_env.sh's GEOLENS_SCORER=v4 default through
# (kickoff 2026-09-23T04:49:41Z logged scorer=v4; aborted before any result file); the preflight expectation
# below is therefore given as literals, not as the same variables.
export GEOLENS_SCORER=v5            # F1' hall definition v5 fixed BEFORE the run
export CONTEXT_ASSEMBLY=v7
export ROUTER_SESSION_STICKY=1      # R1
export ROUTER_HISTORY_ADVANCE=1     # R2''
export RERANK_SESSION_BLOCK=1
TAG="${TAG:-study3}"
REPS="${REPS:-10}"
MODELS="${MODELS:-gemini,claude,gpt}"
OT_DIR="${OT_DIR:-data/eval/scenarios/.study3_test_opendtect}"
QG_DIR="${QG_DIR:-data/eval/scenarios/.study3_test_qgis}"
PASSES="${PASSES:-opendtect,qgis}"
START_REP="${START_REP:-1}"
PY=".venv/Scripts/python.exe"
LOG="data/eval/results/${TAG}_bench.log"
if ! git tag --list | grep -q "^study3-prereg-signed$"; then echo "pre-registration not signed (tag study3-prereg-signed missing)"; exit 2; fi
for d in "$OT_DIR" "$QG_DIR"; do
  $PY scripts/preflight_check.py --scenarios "$d" --expect GEOLENS_SCORER=v5 CONTEXT_ASSEMBLY=v7 ROUTER_SESSION_STICKY=1 ROUTER_HISTORY_ADVANCE=1 RERANK_SESSION_BLOCK=1 CHROMADB_PATH=./data/chromadb_v4 EMBED_MODEL=BAAI/bge-m3 || { echo "preflight failed for $d - run refused"; exit 2; }
done
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench kickoff === passes=${PASSES} models=${MODELS} reps=${REPS} start=${START_REP}"
  echo "scorer=${GEOLENS_SCORER} assembly=${CONTEXT_ASSEMBLY} sticky=${ROUTER_SESSION_STICKY} advance=${ROUTER_HISTORY_ADVANCE} session_block=${RERANK_SESSION_BLOCK} pool=$(ls data/workflows/*.json | wc -l)"
  echo "git: $(git rev-parse --short HEAD); dirty=$(git status --short -- api scripts data/workflows data/eval/scenarios | wc -l) files"
} | tee -a "$LOG"
for pass in ${PASSES//,/ }; do
  dir=$OT_DIR; sid=opendtect; [ "$pass" = qgis ] && { dir=$QG_DIR; sid=qgis; }
  echo "$(date -u +%H:%M:%S) === pass ${pass} (GEOLENS_SOFTWARE_ID=${sid}, $(ls "$dir"/*.json | xargs -n1 basename | tr '\n' ' ')) ===" | tee -a "$LOG"
  GEOLENS_SOFTWARE_ID=$sid $PY -u scripts/run_all_models.py --models "$MODELS" --repeats "$REPS" --start "$START_REP" --judge consensus --tag "${TAG}_${pass}" \
      --backends no_rag vanilla_budget vanilla_vector full_system --scenarios "$dir" 2>&1 | tee -a "$LOG"
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench complete ===" | tee -a "$LOG"
