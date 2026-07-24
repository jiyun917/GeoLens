"""Run bench_runner sequentially for each model, N times per model.

Each run produces run_<model>_r<replicate>_<timestamp>.json. Replicate runs
are used to compute mean ± std (paper reports variance).

Usage:
    .venv/Scripts/python.exe scripts/run_all_models.py \\
        [--models gemini,claude,qwen,gpt] [--repeats 3] [--judge consensus]
"""

from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 stdout so em-dash / other Unicode punctuation don't crash the
# wrapper on Windows cp949. Without this, the very first print() containing
# an em-dash raises UnicodeEncodeError and the wrapper dies before spawning
# replicate 2 — which is exactly the bug we saw.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def run_one(model: str, replicate: int, judge: str | None, backends: list[str] | None = None,
            tag: str | None = None) -> tuple[int, str]:
    """Invoke bench_runner once. Returns (exit_code, out_path)."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    suffix = f"_{tag}" if tag else ""
    out_path = ROOT / "data" / "eval" / "results" / f"run_{model}{suffix}_r{replicate}_{ts}.json"
    cmd = [
        str(PYTHON),
        "-m", "api.services.bench_runner",
        "--model", model,
        "--out", str(out_path),
    ]
    if judge:
        cmd += ["--judge", judge]
    if backends:
        cmd += ["--backends", *backends]
    print(f"\n{'=' * 70}")
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting {model.upper()} replicate {replicate}")
    print(f"{'=' * 70}")
    print(f"  cmd: {' '.join(cmd)}")
    print(f"  out: {out_path}")
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode, str(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="gemini,claude,qwen,gpt",
                    help="Comma-separated model names to run (default: all 4)")
    ap.add_argument("--repeats", type=int, default=3,
                    help="Number of replicate runs per model (default: 3)")
    ap.add_argument("--judge", default="consensus",
                    help="LLM-as-judge mode (default: consensus)")
    ap.add_argument("--backends", nargs="*", default=None,
                    help="Subset of backends to run (default: all). Pass e.g. --backends no_rag")
    ap.add_argument("--tag", default=None,
                    help="Optional suffix included in output filename to distinguish partial runs")
    args = ap.parse_args()

    models = [m.strip().lower() for m in args.models.split(",") if m.strip()]
    print(f"Running models in sequence: {models}  ×  {args.repeats} replicates each")
    if args.backends:
        print(f"Backends subset: {args.backends}")
    if args.tag:
        print(f"Filename tag: {args.tag}")
    print(f"Total planned runs: {len(models) * args.repeats}")

    summary: list[tuple[str, int, int, str]] = []
    for m in models:
        for r in range(1, args.repeats + 1):
            code, out = run_one(m, r, args.judge, backends=args.backends, tag=args.tag)
            summary.append((m, r, code, out))
            if code != 0:
                print(f"\n[WARN] {m} replicate {r} exited with code {code} — continuing.")
            time.sleep(2)  # small breather between runs

    print("\n\n=== SUMMARY ===")
    for m, r, code, out in summary:
        status = "OK  " if code == 0 else "FAIL"
        print(f"  [{status}] {m:<8} r{r} → {out}")


if __name__ == "__main__":
    main()
