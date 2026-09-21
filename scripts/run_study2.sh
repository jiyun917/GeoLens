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
export CONTEXT_ASSEMBLY="${CONTEXT_ASSEMBLY:-v6}"
export RERANK_SESSION_BLOCK="${RERANK_SESSION_BLOCK:-__PIN_AT_SIGNING__}"   # pinned in the signed pre-registration (§2 F3)
TAG="${TAG:-study2}"
REPS="${REPS:-10}"
MODELS="${MODELS:-gemini,claude,gpt}"
TEST_DIR="${TEST_DIR:-data/eval/scenarios/.study2_test}"   # adopted, GT-approved test scenarios only
PY=".venv/Scripts/python.exe"
LOG="data/eval/results/${TAG}_bench.log"
if [ "$RERANK_SESSION_BLOCK" = "__PIN_AT_SIGNING__" ]; then echo "RERANK_SESSION_BLOCK not pinned — sign the pre-registration first"; exit 2; fi
if [ ! -d "$TEST_DIR" ] || [ -z "$(ls "$TEST_DIR"/*.json 2>/dev/null)" ]; then echo "no adopted test scenarios in $TEST_DIR"; exit 2; fi
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench kickoff ==="
  echo "models=${MODELS} reps=${REPS} scenarios=$(ls "$TEST_DIR"/*.json | xargs -n1 basename | tr '\n' ' ')"
  echo "scorer=${GEOLENS_SCORER} assembly=${CONTEXT_ASSEMBLY} rerank_session_block=${RERANK_SESSION_BLOCK} pool=$(ls data/workflows/*.json | wc -l) workflows"
  echo "git: $(git rev-parse --short HEAD) $(git branch --show-current); dirty=$(git status --short -- api scripts data/workflows data/eval/scenarios | wc -l) files"
} | tee -a "$LOG"
$PY -u scripts/run_all_models.py --models "$MODELS" --repeats "$REPS" --judge consensus --tag "$TAG" \
    --backends no_rag vanilla_budget vanilla_vector full_system --scenarios "$TEST_DIR" 2>&1 | tee -a "$LOG"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench complete ===" | tee -a "$LOG"
