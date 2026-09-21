#!/usr/bin/env bash
# Study 2 confirmatory run — signed pre-registration data/eval/study2/study2_pre_registration_DRAFT.md.
# Matrix: MODELS x {no_rag, vanilla_budget, vanilla_vector, full_system} x adopted test scenarios x REPS.
# Everything is the v3 frozen configuration (scripts/study2_env.sh) plus the study-2 fixes fixed
# BEFORE the run: scorer v4, context assembly v6, RERANK_SESSION_BLOCK as pinned below.
#
# Usage: bash scripts/run_study2.sh            # 3 models x 10 replicates
#        MODELS=gemini REPS=1 bash scripts/run_study2.sh   # smoke
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
# Pinned by the signed pre-registration (§2 F2/F3/F5, V3-31): assembly v7, session block kept, session-sticky router rule.
export CONTEXT_ASSEMBLY="${CONTEXT_ASSEMBLY:-v7}"
export RERANK_SESSION_BLOCK="${RERANK_SESSION_BLOCK:-1}"
export ROUTER_SESSION_STICKY="${ROUTER_SESSION_STICKY:-1}"
TAG="${TAG:-study2}"
REPS="${REPS:-10}"
MODELS="${MODELS:-gemini,claude,gpt}"
TEST_DIR="${TEST_DIR:-data/eval/scenarios/.study2_test}"   # adopted, GT-approved test scenarios only
PY=".venv/Scripts/python.exe"
LOG="data/eval/results/${TAG}_bench.log"
if ! git tag --list | grep -q "^study2-prereg-signed$"; then echo "pre-registration not signed (tag study2-prereg-signed missing)"; exit 2; fi
if [ ! -d "$TEST_DIR" ] || [ -z "$(ls "$TEST_DIR"/*.json 2>/dev/null)" ]; then echo "no adopted test scenarios in $TEST_DIR"; exit 2; fi
# Hard gate (V3-32): pool/scenarios/knobs must pass the preflight.
$PY scripts/preflight_check.py --scenarios "$TEST_DIR" --expect CONTEXT_ASSEMBLY="$CONTEXT_ASSEMBLY" ROUTER_SESSION_STICKY="$ROUTER_SESSION_STICKY" RERANK_SESSION_BLOCK="$RERANK_SESSION_BLOCK" GEOLENS_SCORER="$GEOLENS_SCORER" CHROMADB_PATH="$CHROMADB_PATH" || { echo "preflight failed - run refused"; exit 2; }
START_REP="${START_REP:-1}"   # resume after an interruption (§6.4: the interrupted replicate is discarded and re-run)
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench kickoff ==="
  echo "models=${MODELS} reps=${REPS} start=${START_REP} scenarios=$(ls "$TEST_DIR"/*.json | xargs -n1 basename | tr '\n' ' ')"
  echo "scorer=${GEOLENS_SCORER} assembly=${CONTEXT_ASSEMBLY} rerank_session_block=${RERANK_SESSION_BLOCK} sticky=${ROUTER_SESSION_STICKY} pool=$(ls data/workflows/*.json | wc -l) workflows"
  echo "git: $(git rev-parse --short HEAD) $(git branch --show-current); dirty=$(git status --short -- api scripts data/workflows data/eval/scenarios | wc -l) files"
} | tee -a "$LOG"
$PY -u scripts/run_all_models.py --models "$MODELS" --repeats "$REPS" --start "$START_REP" --judge consensus --tag "$TAG" \
    --backends no_rag vanilla_budget vanilla_vector full_system --scenarios "$TEST_DIR" 2>&1 | tee -a "$LOG"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench complete ===" | tee -a "$LOG"
