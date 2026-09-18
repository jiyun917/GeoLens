#!/bin/bash
# unified3 recovery run — reruns only what was discarded:
#   - Gemini long_context × 5 (all 5 originals had ≥12.5% empty responses)
#   - Qwen × 1 replicate (r1 had 1 empty response, transient <think>-only pattern)
#
# Two hardening measures over the original wrapper:
#   1. **Per-replicate quota probe** — before each longctx replicate, issue a
#      tiny Gemini request to verify quota is available. If 429, wait and retry
#      the probe up to 5 minutes before starting the actual replicate. This
#      prevents "start a fresh long-context call while still throttled" which
#      is what caused r4/r5 to hit 100% empty last time.
#   2. **Inter-replicate sleep** (default 60s) between long_context replicates
#      so the per-minute quota (2M input tokens/min) has time to recover
#      after each 226K-token step.
#
# Usage:
#   bash scripts/run_unified3_recovery.sh
#
# Prerequisites:
#   - Wait at least 1 hour after the failed run so spend-based rate limit
#     resets. The script will refuse to start if the first probe fails.

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.." || exit 1
mkdir -p data/eval/results

LOG="data/eval/results/unified3_recovery.log"
INTER_SLEEP=60          # seconds between long_context replicates
PROBE_WAIT_MAX=1800     # max seconds to wait on probe (30 min per replicate)
PROBE_WAIT_INTERVAL=60  # seconds between probe retries

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === unified3 recovery kickoff ===" | tee -a "$LOG"

# ─── Quota probe helper ─────────────────────────────────────────────
gemini_quota_probe() {
    # Tiny request. Exit codes:
    #   0 = OK (proceed)
    #   1 = rate-limit throttle (transient, retry)
    #   2 = no API key
    #   3 = unclassified error
    #   4 = CREDIT DEPLETION (fatal, do not retry)
    .venv/Scripts/python.exe - <<'PYEOF'
import os, sys, json
sys.path.insert(0, ".")
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
    # Credit depletion is a distinct failure mode — retry is futile.
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
            echo "$(date -u +%H:%M:%S) quota probe: OK — proceed" | tee -a "$LOG"
            return 0
        fi
        if [ $rc -eq 4 ]; then
            # Credit depletion — retry cannot help, abort immediately.
            echo "$(date -u +%H:%M:%S) quota probe: CREDIT DEPLETED — cannot retry. ABORT." | tee -a "$LOG"
            echo "$(date -u +%H:%M:%S) $result" | tee -a "$LOG"
            echo "$(date -u +%H:%M:%S) → Recharge Gemini credits at https://ai.studio/projects then re-run this script." | tee -a "$LOG"
            return 2
        fi
        echo "$(date -u +%H:%M:%S) quota probe: rc=$rc ($result) — wait ${PROBE_WAIT_INTERVAL}s" | tee -a "$LOG"
        sleep $PROBE_WAIT_INTERVAL
        elapsed=$((elapsed + PROBE_WAIT_INTERVAL))
    done
    echo "$(date -u +%H:%M:%S) quota probe: exhausted ${PROBE_WAIT_MAX}s wait, aborting this replicate" | tee -a "$LOG"
    return 1
}

# ─── Phase R-1: Qwen r1 rerun (1 replicate) ─────────────────────────
echo "$(date -u +%H:%M:%S) === Phase R-1: Qwen r1 rerun ===" | tee -a "$LOG"
TS=$(date -u +%Y%m%dT%H%M%S)
OUT_QWEN="data/eval/results/run_qwen_unified3_r1_${TS}.json"

.venv/Scripts/python.exe -m api.services.bench_runner \
    --model qwen \
    --out "$OUT_QWEN" \
    --backends no_rag vanilla_vector graph_only vision_only full_system state_path \
    >> "$LOG" 2>&1

QW_EXIT=$?
echo "$(date -u +%H:%M:%S) Qwen r1 exit=$QW_EXIT ($OUT_QWEN)" | tee -a "$LOG"

# ─── Phase R-2: Gemini long_context × 5 with pre-run probe ─────────
echo "$(date -u +%H:%M:%S) === Phase R-2: Gemini longctx × 5 with quota probe ===" | tee -a "$LOG"

for r in 1 2 3 4 5; do
    echo "$(date -u +%H:%M:%S) --- longctx r${r} pre-run probe ---" | tee -a "$LOG"

    if ! wait_for_quota; then
        echo "$(date -u +%H:%M:%S) longctx r${r} ABORT — quota probe failed after ${PROBE_WAIT_MAX}s (30 min)." | tee -a "$LOG"
        echo "$(date -u +%H:%M:%S) Aborting entire longctx loop to avoid producing partial data. Retry later." | tee -a "$LOG"
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

    # Inter-replicate cooldown to let per-minute quota recover
    if [ $r -lt 5 ]; then
        echo "$(date -u +%H:%M:%S) inter-replicate cooldown ${INTER_SLEEP}s..." | tee -a "$LOG"
        sleep $INTER_SLEEP
    fi
done

# ─── Post-run empty-response audit ─────────────────────────────────
echo "$(date -u +%H:%M:%S) === unified3 recovery complete ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "empty-response audit:" | tee -a "$LOG"
.venv/Scripts/python.exe scripts/_check_empty.py >> "$LOG" 2>&1
tail -20 "$LOG"
