#!/usr/bin/env bash
# Study 2 environment = the v3 frozen configuration (scripts/run_v3.sh exports, tag v3-freeze-c01fdda)
# plus the study-2 pre-run fixes (V3-28). Source this before any study-2 command:
#   source scripts/study2_env.sh
# CONTEXT_ASSEMBLY / RERANK_SESSION_BLOCK are left to the caller (verification compares values);
# the confirmatory run script pins them to the values fixed in the signed pre-registration.
export CHROMADB_PATH="${CHROMADB_PATH:-./data/chromadb_v4}"
export EMBED_MODEL="${EMBED_MODEL:-BAAI/bge-m3}"
export GEOLENS_SCORER="${GEOLENS_SCORER:-v4}"            # study 2: scorer v4 (F1)
export RAG_KG_ENABLED="${RAG_KG_ENABLED:-0}"
export RAG_KG_POSITION="${RAG_KG_POSITION:-last}"
export AUX_THINKING_BUDGET="${AUX_THINKING_BUDGET:-0}"
export GEN_TEMPERATURE="${GEN_TEMPERATURE:-0.2}"
export GEN_MAX_TOKENS="${GEN_MAX_TOKENS:-1024}"
export GEMINI_THINKING_BUDGET="${GEMINI_THINKING_BUDGET:-1024}"
export VANILLA_BUDGET_CHARS="${VANILLA_BUDGET_CHARS:-3900}"
export BENCH_SAVE_CONTEXT="${BENCH_SAVE_CONTEXT:-1}"      # keep context blocks for loss analysis
export ROUTER_MATCHER="${ROUTER_MATCHER:-embedding}"
export ROUTER_POOL_K="${ROUTER_POOL_K:-5}"
export ROUTER_GRAPH_PRIOR="${ROUTER_GRAPH_PRIOR:-1}"
export VISION_PROMPT_VERSION="${VISION_PROMPT_VERSION:-v3}"
export RERANK_PROMPT_VERSION="${RERANK_PROMPT_VERSION:-v4}"
export POST_COMPLETION_MODE="${POST_COMPLETION_MODE:-soft}"
export CONFIDENCE_THRESHOLD="${CONFIDENCE_THRESHOLD:-0.7}"
export GOAL_STATE_HINT="${GOAL_STATE_HINT:-1}"
export GOAL_STATE_MARGIN="${GOAL_STATE_MARGIN:-0.02}"
export ROUTER_TIE_PRIOR="${ROUTER_TIE_PRIOR:-1}"
export ROUTER_GROUP_PRIOR="${ROUTER_GROUP_PRIOR:-1}"
export ROUTER_TWO_STAGE="${ROUTER_TWO_STAGE:-0}"
export ROUTER_EVIDENCE_GATE="${ROUTER_EVIDENCE_GATE:-0}"
export RERANK_VOTES="${RERANK_VOTES:-1}"
export GEN_PROMPT_VERSION="${GEN_PROMPT_VERSION:-v2}"
export PARALLEL_RETRIEVAL="${PARALLEL_RETRIEVAL:-1}"
export ROUTED_VECTOR_QUERY="${ROUTED_VECTOR_QUERY:-goal}"
export GRAPH_VECTOR_AUX="${GRAPH_VECTOR_AUX:-0}"
export FALLBACK_CTX_CHARS="${FALLBACK_CTX_CHARS:-3900}"
export VECTOR_CTX_CHARS="${VECTOR_CTX_CHARS:-1500}"
export GRAPH_CTX_CHARS="${GRAPH_CTX_CHARS:-800}"
export GRAPH_CTX_ITEMS="${GRAPH_CTX_ITEMS:-3}"
export PYTHONIOENCODING=utf-8
