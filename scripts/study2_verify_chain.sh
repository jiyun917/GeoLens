#!/usr/bin/env bash
# Study 2 — pre-registration §1.1 selection run and §2.1 dev-set verification, sequential.
#   1. selection: no_rag x 1 x 3 models on the two candidate test scenarios (drafts dir); step
#      accuracy only (judge off). Responses are used for selection only.
#   2. dev dry-run x5 with the 9-workflow pool (routing only).
#   3. dev full_system benches x1 per model, CONTEXT_ASSEMBLY=v6, RERANK_SESSION_BLOCK=0 and =1.
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
PY=".venv/Scripts/python.exe"
LOG="data/eval/results/study2_verify.log"
DEV_DIR="data/eval/scenarios/.dev_opendtect"
SEL_DIR="data/eval/study2/scenarios_gt_draft"
mkdir -p "$DEV_DIR"
cp data/eval/scenarios/opendtect__survey_setup__01.json data/eval/scenarios/opendtect__3d_visualization__01.json \
   data/eval/scenarios/opendtect__attribute_computation__01.json "$DEV_DIR"/
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study2 verify chain kickoff === git $(git rev-parse --short HEAD); dirty=$(git status --short -- api scripts data/workflows | wc -l)"
  echo "scorer=$GEOLENS_SCORER pool=$(ls data/workflows/*.json | wc -l) workflows"
} | tee -a "$LOG"

echo "$(date -u +%H:%M:%S) === 1. selection: no_rag x1 x3 models on $SEL_DIR ===" | tee -a "$LOG"
for m in gemini claude gpt; do
  ts=$(date -u +%Y%m%dT%H%M%S)
  echo "$(date -u +%H:%M:%S) selection $m" | tee -a "$LOG"
  $PY -u -m api.services.bench_runner --model $m --backends no_rag --scenarios "$SEL_DIR" \
      --out "data/eval/results/run_${m}_study2sel_r1_${ts}.json" 2>&1 | tee -a "$LOG"
done

echo "$(date -u +%H:%M:%S) === 2. dev dry-run x5 (9-workflow pool) ===" | tee -a "$LOG"
$PY -u scripts/routing_dryrun_v3.py --knobs iter2 --reps 5 --tag study2pool 2>&1 | tee -a "$LOG"

echo "$(date -u +%H:%M:%S) === 3. dev full_system benches: v6, session block 0 / 1 ===" | tee -a "$LOG"
for sb in 0 1; do
  for m in gemini claude gpt; do
    ts=$(date -u +%Y%m%dT%H%M%S)
    echo "$(date -u +%H:%M:%S) dev full_system $m CONTEXT_ASSEMBLY=v6 RERANK_SESSION_BLOCK=$sb" | tee -a "$LOG"
    CONTEXT_ASSEMBLY=v6 RERANK_SESSION_BLOCK=$sb $PY -u -m api.services.bench_runner --model $m --backends full_system \
        --scenarios "$DEV_DIR" --out "data/eval/results/run_${m}_study2verify_sb${sb}_r1_${ts}.json" 2>&1 | tee -a "$LOG"
  done
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study2 verify chain complete ===" | tee -a "$LOG"
