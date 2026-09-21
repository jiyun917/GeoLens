#!/usr/bin/env bash
# Study 2 — dev-set verification, round 2, on the FINAL configuration:
#   pool = 7 workflows (generic duplicates moved out), CONTEXT_ASSEMBLY=v7, ROUTER_SESSION_STICKY=1,
#   RERANK_SESSION_BLOCK=1, scorer v4.
#   1. dev dry-run x5 (routing; exercises R1 through last_confirmed → session workflow)
#   2. dev full_system benches x1 per model (exercises v7 history rule + R1 in bench mode)
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
export CONTEXT_ASSEMBLY=v7 ROUTER_SESSION_STICKY=1 RERANK_SESSION_BLOCK=1
PY=".venv/Scripts/python.exe"
LOG="data/eval/results/study2_verify2.log"
DEV_DIR="data/eval/scenarios/.dev_opendtect"
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study2 verify2 kickoff === git $(git rev-parse --short HEAD); dirty=$(git status --short -- api scripts data/workflows data/eval/scenarios | wc -l)"
  echo "scorer=$GEOLENS_SCORER assembly=$CONTEXT_ASSEMBLY sticky=$ROUTER_SESSION_STICKY session_block=$RERANK_SESSION_BLOCK pool=$(ls data/workflows/*.json | wc -l)"
} | tee -a "$LOG"
echo "$(date -u +%H:%M:%S) === 1. dev dry-run x5 (final pool, sticky) ===" | tee -a "$LOG"
$PY -u scripts/routing_dryrun_v3.py --knobs iter2 --reps 5 --tag study2pool_final 2>&1 | tee -a "$LOG"
echo "$(date -u +%H:%M:%S) === 2. dev full_system benches (v7, sticky, sb1) ===" | tee -a "$LOG"
for m in gemini claude gpt; do
  ts=$(date -u +%Y%m%dT%H%M%S)
  echo "$(date -u +%H:%M:%S) dev full_system $m" | tee -a "$LOG"
  $PY -u -m api.services.bench_runner --model $m --backends full_system --scenarios "$DEV_DIR" \
      --out "data/eval/results/run_${m}_study2verify2_r1_${ts}.json" 2>&1 | tee -a "$LOG"
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study2 verify2 complete ===" | tee -a "$LOG"
