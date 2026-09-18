#!/bin/bash
# unified3 bench runner with Qwen availability branching.
#
# Behavior:
#   1. Pre-check Qwen endpoint. If up, include qwen in --models list.
#      If down, skip qwen (run gemini/claude/gpt only) and log a note
#      so the user can run qwen separately later.
#   2. Run main matrix (6 backends × N models × 5 replicates).
#   3. Run Gemini long_context 5 replicates sequentially.
#   4. Report progress + final file counts to a log.
#
# All output goes to data/eval/results/unified3_bench.log — long-running,
# safe to leave overnight.

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.." || exit 1
mkdir -p data/eval/results

LOG="data/eval/results/unified3_bench.log"
STATUS_FILE="data/eval/results/unified3_status.log"
QWEN_URL="${QWEN_URL:-http://localhost:28000/v1/models}"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === unified3 bench kickoff ===" | tee -a "$LOG"

# ─── Qwen availability probe ──────────────────────────────────────
echo "$(date -u +%H:%M:%S) probing Qwen endpoint..." | tee -a "$LOG"
if curl -s --max-time 5 -o /dev/null -w "%{http_code}" "$QWEN_URL" 2>/dev/null | grep -q "200"; then
    QWEN_UP=1
    MODELS="gemini,claude,gpt,qwen"
    echo "$(date -u +%H:%M:%S) Qwen endpoint UP. Running full 4-model matrix." | tee -a "$LOG"
    echo "qwen: UP" > "$STATUS_FILE"
else
    QWEN_UP=0
    MODELS="gemini,claude,gpt"
    echo "$(date -u +%H:%M:%S) Qwen endpoint DOWN. Skipping qwen — run separately when server is up:" | tee -a "$LOG"
    echo "  .venv/Scripts/python.exe scripts/run_all_models.py --models qwen --repeats 5 --tag unified3 \\" | tee -a "$LOG"
    echo "      --backends no_rag vanilla_vector graph_only vision_only full_system state_path" | tee -a "$LOG"
    echo "qwen: DOWN (deferred)" > "$STATUS_FILE"
fi

# ─── Phase B-3: main matrix ────────────────────────────────────────
echo "$(date -u +%H:%M:%S) === Phase B-3: main matrix (models=$MODELS) ===" | tee -a "$LOG"

.venv/Scripts/python.exe scripts/run_all_models.py \
    --models "$MODELS" \
    --repeats 5 \
    --tag unified3 \
    --backends no_rag vanilla_vector graph_only vision_only full_system state_path \
    >> "$LOG" 2>&1

MAIN_EXIT=$?
echo "$(date -u +%H:%M:%S) main matrix exit=$MAIN_EXIT" | tee -a "$LOG"

# ─── Phase B-4: long_context (Gemini × 5 reps, sequential) ───────
echo "$(date -u +%H:%M:%S) === Phase B-4: long_context Gemini × 5 ===" | tee -a "$LOG"

for r in 1 2 3 4 5; do
    TS=$(date -u +%Y%m%dT%H%M%S)
    OUT="data/eval/results/run_gemini_longctx_r${r}_${TS}.json"
    echo "$(date -u +%H:%M:%S) longctx r${r} starting → $OUT" | tee -a "$LOG"

    .venv/Scripts/python.exe -m api.services.bench_runner \
        --model gemini \
        --out "$OUT" \
        --backends long_context \
        >> "$LOG" 2>&1

    LC_EXIT=$?
    echo "$(date -u +%H:%M:%S) longctx r${r} exit=$LC_EXIT" | tee -a "$LOG"

    if [ $LC_EXIT -ne 0 ]; then
        echo "$(date -u +%H:%M:%S) WARN: longctx r${r} failed — leaving partial file, continuing" | tee -a "$LOG"
    fi
done

# ─── Summary ───────────────────────────────────────────────────────
echo "$(date -u +%H:%M:%S) === unified3 bench complete ===" | tee -a "$LOG"
echo "main matrix runs saved:" | tee -a "$LOG"
ls -1 data/eval/results/run_*_unified3_r*_*.json 2>/dev/null | wc -l | tee -a "$LOG"
echo "longctx runs saved:" | tee -a "$LOG"
ls -1 data/eval/results/run_gemini_longctx_r*_*.json 2>/dev/null | wc -l | tee -a "$LOG"

if [ $QWEN_UP -eq 0 ]; then
    echo "" | tee -a "$LOG"
    echo "REMINDER: Qwen was skipped. Run separately:" | tee -a "$LOG"
    echo "  .venv/Scripts/python.exe scripts/run_all_models.py --models qwen --repeats 5 --tag unified3 \\" | tee -a "$LOG"
    echo "      --backends no_rag vanilla_vector graph_only vision_only full_system state_path" | tee -a "$LOG"
fi
