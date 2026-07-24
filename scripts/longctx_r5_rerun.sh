#!/bin/bash
# Long_context r5 rerun script.
# Prerequisites: user has raised Gemini spending cap in AI Studio.
# Cost estimate: ~$2.30 (8 steps × $0.283).
# Duration estimate: ~10 minutes.

cd /c/Users/user/Downloads/GeoLens-paper || exit 1
TS=$(date -u +%Y%m%dT%H%M%S)
OUT="data/eval/results/run_gemini_longctx_r5_${TS}.json"
LOG="data/eval/results/long_context_gemini_r5_rerun.log"

echo "Kicking off long_context r5 rerun"
echo "  output: $OUT"
echo "  log:    $LOG"

PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m api.services.bench_runner \
    --model gemini \
    --out "$OUT" \
    --judge consensus \
    --backends long_context \
    > "$LOG" 2>&1 &

echo "  PID: $!"
echo ""
echo "Poll with:"
echo "  until [ -f '$OUT' ]; do sleep 30; done && echo 'r5 rerun done'"
