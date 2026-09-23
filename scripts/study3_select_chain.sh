#!/usr/bin/env bash
# Study 3 §1.1 selection run: no_rag x 1 x 3 models on the GT-approved test scenarios, two passes
# (GEOLENS_SOFTWARE_ID per software). Responses are used for selection only. Preflight-gated.
set -u
cd "$(dirname "$0")/.."
source scripts/study2_env.sh
export GEOLENS_SCORER=v5 CONTEXT_ASSEMBLY=v7 ROUTER_SESSION_STICKY=1 ROUTER_HISTORY_ADVANCE=1 RERANK_SESSION_BLOCK=1
PY=".venv/Scripts/python.exe"
LOG="data/eval/results/study3_select.log"
OT_DIR="data/eval/scenarios/.study3_test_opendtect"
QG_DIR="data/eval/scenarios/.study3_test_qgis"
PASSES="${PASSES:-opendtect,qgis}"
for pass in ${PASSES//,/ }; do
  d=$OT_DIR; [ "$pass" = qgis ] && d=$QG_DIR
  $PY scripts/preflight_check.py --scenarios "$d" --expect GEOLENS_SCORER=v5 --allow-dirty || { echo "preflight failed for $d" | tee -a "$LOG"; exit 2; }
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study3 selection kickoff === git $(git rev-parse --short HEAD)" | tee -a "$LOG"
for pass in ${PASSES//,/ }; do
  dir=$OT_DIR; [ "$pass" = qgis ] && dir=$QG_DIR
  for m in gemini claude gpt; do
    ts=$(date -u +%Y%m%dT%H%M%S)
    echo "$(date -u +%H:%M:%S) selection $pass $m" | tee -a "$LOG"
    GEOLENS_SOFTWARE_ID=$pass $PY -u -m api.services.bench_runner --model $m --backends no_rag --scenarios "$dir" \
        --out "data/eval/results/run_${m}_study3sel_${pass}_r1_${ts}.json" 2>&1 | tee -a "$LOG"
  done
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === study3 selection complete ===" | tee -a "$LOG"
