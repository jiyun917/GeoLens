#!/bin/bash
# Re-run only longctx r4 and r5 (r1-r3 already valid from previous recovery).
# Uses the same probe + inter-replicate sleep logic as run_unified3_recovery.sh
# but with credit-depletion detection (rc=4 → immediate abort, no retry).

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.." || exit 1
mkdir -p data/eval/results

LOG="data/eval/results/unified3_r4r5_recovery.log"
INTER_SLEEP=60
PROBE_WAIT_MAX=1800
PROBE_WAIT_INTERVAL=60

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) === longctx r4+r5 recovery kickoff ===" | tee -a "$LOG"

gemini_quota_probe() {
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
            echo "$(date -u +%H:%M:%S) probe OK — proceed" | tee -a "$LOG"
            return 0
        fi
        if [ $rc -eq 4 ]; then
            echo "$(date -u +%H:%M:%S) probe CREDIT DEPLETED — ABORT (recharge needed)" | tee -a "$LOG"
            echo "$(date -u +%H:%M:%S) $result" | tee -a "$LOG"
            return 2
        fi
        echo "$(date -u +%H:%M:%S) probe rc=$rc — wait ${PROBE_WAIT_INTERVAL}s" | tee -a "$LOG"
        sleep $PROBE_WAIT_INTERVAL
        elapsed=$((elapsed + PROBE_WAIT_INTERVAL))
    done
    echo "$(date -u +%H:%M:%S) probe timeout — abort this replicate" | tee -a "$LOG"
    return 1
}

# Post-replicate credit-depletion check on the log
check_depletion_in_log() {
    local n=$(tail -100 "$LOG" 2>/dev/null | grep -c "credits are depleted")
    if [ "$n" -gt 0 ]; then
        echo "$(date -u +%H:%M:%S) DETECTED credit depletion in replicate log — ABORT remaining" | tee -a "$LOG"
        return 1
    fi
    return 0
}

for r in 4 5; do
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

    # Post-run depletion check — if depletion appeared during replicate, abort remaining
    if ! check_depletion_in_log; then
        echo "$(date -u +%H:%M:%S) File $OUT likely corrupt — will need discard + rerun after recharge" | tee -a "$LOG"
        break
    fi

    if [ $r -lt 5 ]; then
        echo "$(date -u +%H:%M:%S) inter-replicate cooldown ${INTER_SLEEP}s..." | tee -a "$LOG"
        sleep $INTER_SLEEP
    fi
done

echo "$(date -u +%H:%M:%S) === r4+r5 recovery complete ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "empty-response audit:" | tee -a "$LOG"
.venv/Scripts/python.exe scripts/_check_empty.py >> "$LOG" 2>&1
tail -25 "$LOG"
