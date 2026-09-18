#!/usr/bin/env bash
# v3 rerun wrapper — main matrix + long_context + QGIS pilot.
#
# Fixed BEFORE the run and applied to every backend (see
# data/eval/results/v3_pre_registration.md):
#   scorer v3 (ASCII word boundary, quote-independent hallucination, <think> drop)
#   embedder BAAI/bge-m3 on data/chromadb_v3 (same chunk ids as data/chromadb)
#   KG triplet block last in retrieved context; vanilla_budget backend added
#   shared generation settings (temperature 0.2, 1024 answer tokens, Gemini +1024 thinking)
#   auxiliary Flash calls logged + thinking off; session-carried visited (no O(N^2))
#   Qwen excluded from v3 (no VL serving); matrix = Gemini 2.5 Pro, Claude Sonnet 4.6, GPT-4o
#
# Usage:
#   bash scripts/run_v3.sh                       # 3 models x 10 replicates
#   MODELS=gemini REPS=1 bash scripts/run_v3.sh  # smoke run
set -u
cd "$(dirname "$0")/.."

TAG="${TAG:-v3}"
REPS="${REPS:-10}"
MODELS="${MODELS:-gemini,claude,gpt}"   # v3: Qwen excluded (Qwen3-VL serving unavailable; text-only Qwen cannot match the input condition)
LOG="data/eval/results/${TAG}_bench.log"
PY=".venv/Scripts/python.exe"

export CHROMADB_PATH="${CHROMADB_PATH:-./data/chromadb_v3}"
export EMBED_MODEL="${EMBED_MODEL:-BAAI/bge-m3}"
export GEOLENS_SCORER="${GEOLENS_SCORER:-v3}"
export RAG_KG_POSITION="${RAG_KG_POSITION:-last}"
export AUX_THINKING_BUDGET="${AUX_THINKING_BUDGET:-0}"
export GEN_TEMPERATURE="${GEN_TEMPERATURE:-0.2}"
export GEN_MAX_TOKENS="${GEN_MAX_TOKENS:-1024}"
export GEMINI_THINKING_BUDGET="${GEMINI_THINKING_BUDGET:-1024}"
export VANILLA_BUDGET_CHARS="${VANILLA_BUDGET_CHARS:-3900}"
export PYTHONIOENCODING=utf-8

mkdir -p data/eval/results
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench kickoff ==="
  echo "models=${MODELS} reps=${REPS} chromadb=${CHROMADB_PATH} embed=${EMBED_MODEL} scorer=${GEOLENS_SCORER}"
  echo "kg=${RAG_KG_POSITION} aux_think=${AUX_THINKING_BUDGET} temp=${GEN_TEMPERATURE} max_tokens=${GEN_MAX_TOKENS} gemini_think=${GEMINI_THINKING_BUDGET} vanilla_budget=${VANILLA_BUDGET_CHARS}"
  echo "git: $(git rev-parse --short HEAD) $(git branch --show-current); dirty=$(git status --short | wc -l) files"
} | tee -a "$LOG"

echo "$(date -u +%H:%M:%S) === main matrix (models=${MODELS}) ===" | tee -a "$LOG"
$PY -u scripts/run_all_models.py --models "$MODELS" --repeats "$REPS" --judge consensus --tag "$TAG" 2>&1 | tee -a "$LOG"

echo "$(date -u +%H:%M:%S) === long_context (gemini x ${REPS}) ===" | tee -a "$LOG"
for r in $(seq 1 "$REPS"); do
  ts=$(date -u +%Y%m%dT%H%M%S)
  $PY -u -m api.services.bench_runner --model gemini --backends long_context --judge consensus \
      --out "data/eval/results/run_gemini_${TAG}longctx_r${r}_${ts}.json" 2>&1 | tee -a "$LOG"
  sleep 60
done

echo "$(date -u +%H:%M:%S) === QGIS pilot (gemini x ${REPS}, no isolation) ===" | tee -a "$LOG"
GEOLENS_SOFTWARE_ID=qgis $PY -u scripts/run_qgis_pilot.py --reps "$REPS" --tag "${TAG}_qgis" 2>&1 | tee -a "$LOG"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench complete ===" | tee -a "$LOG"
