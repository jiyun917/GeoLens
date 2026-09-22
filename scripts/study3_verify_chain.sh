#!/usr/bin/env bash
# Study 3 — pre-run verification of R2 (history advance) + scorer v5 on (a) the OpendTect dev set and
# (b) the closed study-2 test set (now used as a dev-like set for the routing-lag defect, V3-34).
# full_system only, 1 run per model, final study-3 configuration. Preflight-gated.
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
export GEOLENS_SCORER=v5 CONTEXT_ASSEMBLY=v7 ROUTER_SESSION_STICKY=1 ROUTER_HISTORY_ADVANCE=1 RERANK_SESSION_BLOCK=1
PY=".venv/Scripts/python.exe"
TAG="${TAG:-study3verify}"
LOG="data/eval/results/${TAG}.log"
DEV_DIR="data/eval/scenarios/.dev_opendtect"
S2_DIR="data/eval/scenarios/.study2_test"
$PY scripts/preflight_check.py --scenarios "$S2_DIR" --expect GEOLENS_SCORER=v5 CONTEXT_ASSEMBLY=v7 ROUTER_SESSION_STICKY=1 ROUTER_HISTORY_ADVANCE=1 --allow-dirty || { echo "preflight failed - verification refused" | tee -a "$LOG"; exit 2; }
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study3 verify kickoff === git $(git rev-parse --short HEAD); pool=$(ls data/workflows/*.json | wc -l)"
  echo "scorer=$GEOLENS_SCORER assembly=$CONTEXT_ASSEMBLY sticky=$ROUTER_SESSION_STICKY advance=$ROUTER_HISTORY_ADVANCE session_block=$RERANK_SESSION_BLOCK"
} | tee -a "$LOG"
for set in dev s2; do
  dir=$DEV_DIR; [ "$set" = s2 ] && dir=$S2_DIR
  for m in gemini claude gpt; do
    ts=$(date -u +%Y%m%dT%H%M%S)
    echo "$(date -u +%H:%M:%S) $set full_system $m" | tee -a "$LOG"
    $PY -u -m api.services.bench_runner --model $m --backends full_system --scenarios "$dir" \
        --out "data/eval/results/run_${m}_${TAG}_${set}_r1_${ts}.json" 2>&1 | tee -a "$LOG"
  done
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study3 verify complete ===" | tee -a "$LOG"
