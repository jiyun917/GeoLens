#!/usr/bin/env bash
# v3 rerun wrapper — main matrix (OpendTect dev set, reported as dev-set
# performance) + long_context + QGIS test set (confirmatory).
#
# Fixed BEFORE the run and applied to every backend (see
# data/eval/results/v3_pre_registration.md and methodology_audit_trail.md
# V3-0 … V3-9):
#   scorer v3 (ASCII word boundary, quote-independent hallucination, <think> drop,
#     <3-char GT entries exact match only)
#   knowledge base v4: figure-area OCR rule on both manuals, BAAI/bge-m3, data/chromadb_v4;
#     OpendTect linked_chunks re-linked on v4 (scripts/relink_chunks_v4.py)
#   geology KG block excluded for every backend; vanilla_budget backend (3,900 chars)
#   shared generation settings (temperature 0.2, 1024 answer tokens, Gemini +1024 thinking)
#   auxiliary Flash calls logged + thinking off; vision cache replays tokens AND latency
#   routing mechanism as frozen at the end of the dev loop (knobs below — values are
#     the frozen ones; the freeze commit hash is recorded in the pre-registration)
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

# ── knowledge base / scorer / generation (Task A) ──
export CHROMADB_PATH="${CHROMADB_PATH:-./data/chromadb_v4}"
export EMBED_MODEL="${EMBED_MODEL:-BAAI/bge-m3}"
export GEOLENS_SCORER="${GEOLENS_SCORER:-v3}"
export RAG_KG_ENABLED="${RAG_KG_ENABLED:-0}"
export RAG_KG_POSITION="${RAG_KG_POSITION:-last}"
export AUX_THINKING_BUDGET="${AUX_THINKING_BUDGET:-0}"
export GEN_TEMPERATURE="${GEN_TEMPERATURE:-0.2}"
export GEN_MAX_TOKENS="${GEN_MAX_TOKENS:-1024}"
export GEMINI_THINKING_BUDGET="${GEMINI_THINKING_BUDGET:-1024}"
export VANILLA_BUDGET_CHARS="${VANILLA_BUDGET_CHARS:-3900}"
export BENCH_SAVE_CONTEXT="${BENCH_SAVE_CONTEXT:-0}"
# ── routing / context mechanism (frozen at the end of the dev loop; V3-9) ──
export ROUTER_MATCHER="${ROUTER_MATCHER:-embedding}"
export ROUTER_POOL_K="${ROUTER_POOL_K:-5}"
export ROUTER_GRAPH_PRIOR="${ROUTER_GRAPH_PRIOR:-1}"
export VISION_PROMPT_VERSION="${VISION_PROMPT_VERSION:-v3}"
export RERANK_PROMPT_VERSION="${RERANK_PROMPT_VERSION:-v4}"
export POST_COMPLETION_MODE="${POST_COMPLETION_MODE:-soft}"
export CONFIDENCE_THRESHOLD="${CONFIDENCE_THRESHOLD:-0.7}"
export PARALLEL_RETRIEVAL="${PARALLEL_RETRIEVAL:-1}"
export ROUTED_VECTOR_QUERY="${ROUTED_VECTOR_QUERY:-goal}"
export GRAPH_VECTOR_AUX="${GRAPH_VECTOR_AUX:-0}"
export FALLBACK_CTX_CHARS="${FALLBACK_CTX_CHARS:-3900}"
export VECTOR_CTX_CHARS="${VECTOR_CTX_CHARS:-1500}"
export GRAPH_CTX_CHARS="${GRAPH_CTX_CHARS:-800}"
export GRAPH_CTX_ITEMS="${GRAPH_CTX_ITEMS:-3}"
export PYTHONIOENCODING=utf-8

# OpendTect-only scenario directory for the main matrix and long_context so the
# QGIS test scenario is executed only by run_qgis_pilot.py (its own directory).
DEV_DIR="data/eval/scenarios/.dev_opendtect"
rm -rf "$DEV_DIR"; mkdir -p "$DEV_DIR"
cp data/eval/scenarios/opendtect__survey_setup__01.json \
   data/eval/scenarios/opendtect__3d_visualization__01.json \
   data/eval/scenarios/opendtect__attribute_computation__01.json "$DEV_DIR"/

mkdir -p data/eval/results
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench kickoff ==="
  echo "models=${MODELS} reps=${REPS} chromadb=${CHROMADB_PATH} embed=${EMBED_MODEL} scorer=${GEOLENS_SCORER}"
  echo "kg_enabled=${RAG_KG_ENABLED} aux_think=${AUX_THINKING_BUDGET} temp=${GEN_TEMPERATURE} max_tokens=${GEN_MAX_TOKENS} gemini_think=${GEMINI_THINKING_BUDGET} vanilla_budget=${VANILLA_BUDGET_CHARS}"
  echo "router: matcher=${ROUTER_MATCHER} pool=${ROUTER_POOL_K} prior=${ROUTER_GRAPH_PRIOR} vision=${VISION_PROMPT_VERSION} rerank=${RERANK_PROMPT_VERSION} post_completion=${POST_COMPLETION_MODE} thr=${CONFIDENCE_THRESHOLD}"
  echo "context: parallel=${PARALLEL_RETRIEVAL} routed_query=${ROUTED_VECTOR_QUERY} graph_vector_aux=${GRAPH_VECTOR_AUX} fallback=${FALLBACK_CTX_CHARS} vector=${VECTOR_CTX_CHARS} graph=${GRAPH_CTX_ITEMS}x${GRAPH_CTX_CHARS}"
  echo "git: $(git rev-parse --short HEAD) $(git branch --show-current); dirty=$(git status --short | wc -l) files"
} | tee -a "$LOG"

echo "$(date -u +%H:%M:%S) === main matrix (models=${MODELS}, OpendTect dev set) ===" | tee -a "$LOG"
$PY -u scripts/run_all_models.py --models "$MODELS" --repeats "$REPS" --judge consensus --tag "$TAG" \
    --scenarios "$DEV_DIR" 2>&1 | tee -a "$LOG"

echo "$(date -u +%H:%M:%S) === long_context (gemini x ${REPS}, OpendTect dev set) ===" | tee -a "$LOG"
for r in $(seq 1 "$REPS"); do
  ts=$(date -u +%Y%m%dT%H%M%S)
  $PY -u -m api.services.bench_runner --model gemini --backends long_context --judge consensus \
      --scenarios "$DEV_DIR" \
      --out "data/eval/results/run_gemini_${TAG}longctx_r${r}_${ts}.json" 2>&1 | tee -a "$LOG"
  sleep 60
done

echo "$(date -u +%H:%M:%S) === QGIS test set (models=${MODELS} x ${REPS}, no isolation: 7 workflows loaded) ===" | tee -a "$LOG"
GEOLENS_SOFTWARE_ID=qgis $PY -u scripts/run_qgis_pilot.py --reps "$REPS" --models "$MODELS" --tag "${TAG}_qgis" 2>&1 | tee -a "$LOG"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === ${TAG} bench complete ===" | tee -a "$LOG"
