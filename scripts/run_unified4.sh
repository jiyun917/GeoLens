#!/bin/bash
# unified4 bench runner — signature refinement re-execution.
#
# Combines the two verified wrappers from unified3:
#   - run_unified3.sh (Qwen availability probe → skip-if-down)
#   - run_unified3_recovery.sh (credit-probe + inter-replicate sleep +
#     rc=4 immediate abort on credit depletion)
#
# The "safety belt is worn when it looks unnecessary" principle: even
# though unified3 recovery uncovered credit depletion only after a
# specific spend chain, unified4 also runs ~$40 including longctx, so
# the same protections stay on.
#
# Behavior:
#   1. Log Qwen curl probe result as the first substantive line
#   2. Main matrix: 4-model (or 3-model if Qwen down) × 6 backends × 5 rep × 3 scenarios
#   3. Long_context: Gemini × 5 rep with credit-depletion aware probe
#      + 60s inter-replicate sleep
#   4. Post-run empty-response audit
#
# Usage:  bash scripts/run_unified4.sh
# Log:    data/eval/results/unified4_bench.log
#
# Stop rule (pre-registered): unified5 does not exist. This is the last
# iteration for the paper regardless of outcome.

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.." || exit 1
mkdir -p data/eval/results

LOG="data/eval/results/unified4_bench.log"
STATUS_FILE="data/eval/results/unified4_status.log"
QWEN_URL="${QWEN_URL:-http://localhost:28000/v1/models}"
INTER_SLEEP=60          # seconds between long_context replicates
PROBE_WAIT_MAX=1800     # max seconds to wait on Gemini probe
PROBE_WAIT_INTERVAL=60

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === unified4 bench kickoff ===" | tee -a "$LOG"

# ─── Qwen availability probe (log first substantive line) ─────────
echo "$(date -u +%H:%M:%S) probing Qwen endpoint: $QWEN_URL" | tee -a "$LOG"
QWEN_HTTP=$(curl -s --max-time 5 -o /dev/null -w "%{http_code}" "$QWEN_URL" 2>/dev/null)
if [ "$QWEN_HTTP" = "200" ]; then
    QWEN_UP=1
    MODELS="gemini,claude,gpt,qwen"
    echo "$(date -u +%H:%M:%S) Qwen probe: HTTP $QWEN_HTTP (UP). Running full 4-model matrix." | tee -a "$LOG"
    echo "qwen: UP (HTTP $QWEN_HTTP) at $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS_FILE"
else
    QWEN_UP=0
    MODELS="gemini,claude,gpt"
    echo "$(date -u +%H:%M:%S) Qwen probe: HTTP $QWEN_HTTP (DOWN). Skipping qwen — run separately later:" | tee -a "$LOG"
    echo "  .venv/Scripts/python.exe scripts/run_all_models.py --models qwen --repeats 5 --tag unified4 \\" | tee -a "$LOG"
    echo "      --backends no_rag vanilla_vector graph_only vision_only full_system state_path" | tee -a "$LOG"
    echo "qwen: DOWN (HTTP $QWEN_HTTP) at $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS_FILE"
fi

# ─── Gemini quota probe helper (from unified3 recovery) ──────────
gemini_quota_probe() {
    # Exit codes: 0=OK, 1=throttled, 2=no key, 3=other, 4=CREDIT_DEPLETED
    .venv/Scripts/python.exe - <<'PYEOF'
import os, sys
try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if os.path.exists(p):
            load_dotenv(p)
except ImportError:
    pass
key = os.environ.get("GEMINI_API_KEY")
if not key:
    sys.exit(2)
try:
    from google import genai
    from google.genai import types as t
    client = genai.Client(api_key=key)
    r = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[t.Part.from_text(text="ok")],
        config=t.GenerateContentConfig(temperature=0, max_output_tokens=5),
    )
    print("OK", (r.text or "").strip()[:20])
    sys.exit(0)
except Exception as e:
    msg = str(e)
    if "prepayment credits are depleted" in msg or "credits are depleted" in msg.lower():
        print("CREDIT_DEPLETED", msg[:300])
        sys.exit(4)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "rate limit" in msg.lower():
        print("THROTTLED", msg[:200])
        sys.exit(1)
    print("OTHER_ERROR", msg[:200])
    sys.exit(3)
PYEOF
}

wait_for_quota() {
    local elapsed=0
    while [ $elapsed -lt $PROBE_WAIT_MAX ]; do
        result=$(gemini_quota_probe 2>&1)
        rc=$?
        if [ $rc -eq 0 ]; then
            echo "$(date -u +%H:%M:%S) Gemini probe OK — proceed" | tee -a "$LOG"
            return 0
        fi
        if [ $rc -eq 4 ]; then
            echo "$(date -u +%H:%M:%S) Gemini probe CREDIT DEPLETED — ABORT (recharge needed)" | tee -a "$LOG"
            echo "$(date -u +%H:%M:%S) $result" | tee -a "$LOG"
            return 2
        fi
        echo "$(date -u +%H:%M:%S) Gemini probe rc=$rc — wait ${PROBE_WAIT_INTERVAL}s" | tee -a "$LOG"
        sleep $PROBE_WAIT_INTERVAL
        elapsed=$((elapsed + PROBE_WAIT_INTERVAL))
    done
    echo "$(date -u +%H:%M:%S) Gemini probe timeout — abort this replicate" | tee -a "$LOG"
    return 1
}

check_depletion_in_log() {
    local n=$(tail -100 "$LOG" 2>/dev/null | grep -c "credits are depleted")
    if [ "$n" -gt 0 ]; then
        echo "$(date -u +%H:%M:%S) DETECTED credit depletion in replicate log — ABORT remaining" | tee -a "$LOG"
        return 1
    fi
    return 0
}

# ─── Phase B-3: main matrix ────────────────────────────────────────
echo "$(date -u +%H:%M:%S) === Phase B-3: main matrix (models=$MODELS) ===" | tee -a "$LOG"

.venv/Scripts/python.exe scripts/run_all_models.py \
    --models "$MODELS" \
    --repeats 5 \
    --tag unified4 \
    --backends no_rag vanilla_vector graph_only vision_only full_system state_path \
    >> "$LOG" 2>&1

MAIN_EXIT=$?
echo "$(date -u +%H:%M:%S) main matrix exit=$MAIN_EXIT" | tee -a "$LOG"

# ─── Phase B-4: long_context (Gemini × 5, with credit-probe + sleep) ─
echo "$(date -u +%H:%M:%S) === Phase B-4: Gemini longctx × 5 with quota probe ===" | tee -a "$LOG"

for r in 1 2 3 4 5; do
    echo "$(date -u +%H:%M:%S) --- longctx r${r} pre-run probe ---" | tee -a "$LOG"

    if ! wait_for_quota; then
        rc=$?
        if [ $rc -eq 2 ]; then
            echo "$(date -u +%H:%M:%S) longctx r${r} ABORT (credit depletion) — recharge and retry" | tee -a "$LOG"
        else
            echo "$(date -u +%H:%M:%S) longctx r${r} ABORT (probe timeout)" | tee -a "$LOG"
        fi
        break
    fi

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

    if ! check_depletion_in_log; then
        echo "$(date -u +%H:%M:%S) File $OUT likely corrupt — will need discard + rerun after recharge" | tee -a "$LOG"
        break
    fi

    if [ $r -lt 5 ]; then
        echo "$(date -u +%H:%M:%S) inter-replicate cooldown ${INTER_SLEEP}s..." | tee -a "$LOG"
        sleep $INTER_SLEEP
    fi
done

# ─── Summary ───────────────────────────────────────────────────────
echo "$(date -u +%H:%M:%S) === unified4 bench complete ===" | tee -a "$LOG"
echo "main matrix runs saved:" | tee -a "$LOG"
ls -1 data/eval/results/run_*_unified4_r*_*.json 2>/dev/null | wc -l | tee -a "$LOG"
echo "longctx runs saved (this session — filter by kickoff timestamp for exact count):" | tee -a "$LOG"
ls -1 data/eval/results/run_gemini_longctx_r*_*.json 2>/dev/null | wc -l | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "empty-response audit:" | tee -a "$LOG"
.venv/Scripts/python.exe scripts/_check_empty.py >> "$LOG" 2>&1

if [ $QWEN_UP -eq 0 ]; then
    echo "" | tee -a "$LOG"
    echo "REMINDER: Qwen was skipped. Run separately:" | tee -a "$LOG"
    echo "  .venv/Scripts/python.exe scripts/run_all_models.py --models qwen --repeats 5 --tag unified4 \\" | tee -a "$LOG"
    echo "      --backends no_rag vanilla_vector graph_only vision_only full_system state_path" | tee -a "$LOG"
fi

tail -30 "$LOG"
