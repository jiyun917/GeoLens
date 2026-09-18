"""QGIS Pilot upload monitor v2 — with chromadb mtime tracking for diagnostic."""

import os
import sys
import time
from datetime import datetime, timezone

import requests

sys.stdout.reconfigure(encoding="utf-8")

PDF = os.environ.get("QGIS_TRAINING_MANUAL_PDF", "QGIS-3.44-TrainingManual-en.pdf")
BASE = "http://127.0.0.1:8000"


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def chromadb_mtime():
    try:
        latest = max(
            os.path.getmtime(os.path.join(root, f))
            for root, _, files in os.walk("data/chromadb")
            for f in files
        )
        return datetime.fromtimestamp(latest, tz=timezone.utc).isoformat(timespec="seconds")
    except Exception:
        return "?"


def main():
    print(f"[{utc_now_iso()}] upload POST → {PDF}", flush=True)
    with open(PDF, "rb") as f:
        r = requests.post(
            f"{BASE}/api/manual/upload",
            files={"file": (os.path.basename(PDF), f, "application/pdf")},
            timeout=180,
        )
    r.raise_for_status()
    mid = r.json()["id"]
    t0 = time.time()
    print(f"[{utc_now_iso()}] accepted manual_id={mid}", flush=True)
    print(f"[t+   0s] chromadb_mtime={chromadb_mtime()}", flush=True)

    last_status, last_chunks = None, None
    last_mtime_check = time.time()
    for _ in range(360):  # 30 min max at 5s poll
        time.sleep(5)
        b = requests.get(f"{BASE}/api/manual/{mid}", timeout=10).json()
        st, cc = b.get("status"), b.get("chunk_count")
        elapsed = int(time.time() - t0)
        changed = st != last_status or cc != last_chunks
        now = time.time()
        if changed or (now - last_mtime_check > 30):
            print(f"[t+{elapsed:4d}s] status={st} chunks={cc} wf={b.get('workflow_count')} chromadb_mtime={chromadb_mtime()}", flush=True)
            last_mtime_check = now
        if changed:
            last_status, last_chunks = st, cc
        if st in ("ready", "error"):
            print(f"[FINAL] status={st} chunks={cc} wf={b.get('workflow_count')} err={b.get('error_message')}", flush=True)
            return

    print(f"[TIMEOUT] 30 min exceeded, still status={last_status}", flush=True)


if __name__ == "__main__":
    main()
