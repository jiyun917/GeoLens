"""QGIS Pilot — monitor Training Manual (1b63832805da...) until ready.

Polls the manual endpoint, records ready-transition time, then queries
metadata, runs QA (10 random chunks), lists auto-workflows, generates
markdown report.

t0 recovery: original upload script t0 lost (script killed). Use
Manual.created_at from API as t0 approximation (accurate to seconds —
upload endpoint sets it at Manual.new() call time, which is the same
POST that would set t0).
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "http://127.0.0.1:8000"
MANUAL_ID = "1b63832805da406bab1e06567cac7c69"
POLL_INTERVAL = 15   # seconds
POLL_TIMEOUT = 45 * 60   # 45 min

PDF_PATH = os.environ.get("QGIS_TRAINING_MANUAL_PDF", "QGIS-3.44-TrainingManual-en.pdf")

OUT_MD = Path(r"./data\eval\results\qgis_pilot_upload_report.md")


def fmt_ts(t):
    if isinstance(t, str):
        return t  # already ISO
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat(timespec="seconds")


def parse_iso(s: str) -> float:
    """Manual.created_at is UTC isoformat without tz, e.g., '2026-08-12T09:38:57.123456'."""
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        return time.time()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def pdf_meta(path: str) -> dict:
    from pypdf import PdfReader
    return {"size_mb": os.path.getsize(path) / 1024 / 1024,
            "page_count": len(PdfReader(path).pages)}


def qa_sample(manual_id: str, k: int = 10):
    import chromadb
    c = chromadb.PersistentClient(path="data/chromadb").get_collection(f"manual_{manual_id}")
    ids = c.get()["ids"]
    if len(ids) < k:
        k = len(ids)
    sample_ids = random.sample(ids, k)
    docs = c.get(ids=sample_ids)["documents"]
    return sample_ids, docs


def list_qgis_workflows(manual_id: str) -> list:
    """Return list of auto workflow file paths matching auto_{manual_id}__*.json."""
    import glob
    pattern = f"data/workflows/auto_{manual_id}__*.json"
    return sorted(glob.glob(pattern))


def main():
    print(f"[MONITOR] manual_id={MANUAL_ID}")
    print(f"[MONITOR] poll every {POLL_INTERVAL}s, timeout {POLL_TIMEOUT}s")

    meta = pdf_meta(PDF_PATH)
    print(f"[META] {os.path.basename(PDF_PATH)}: {meta['size_mb']:.1f}MB, {meta['page_count']} pages")

    # Get t0 from created_at
    r0 = requests.get(f"{BASE}/api/manual/{MANUAL_ID}", timeout=10)
    r0.raise_for_status()
    body0 = r0.json()
    t0_iso = body0["created_at"]
    t0 = parse_iso(t0_iso)
    print(f"[t0] Manual.created_at = {t0_iso}")

    # Poll
    elapsed = 0
    last_status = body0.get("status")
    print(f"[t+{elapsed:4d}s] status={last_status}  chunks={body0.get('chunk_count')}")
    while elapsed < POLL_TIMEOUT:
        r = requests.get(f"{BASE}/api/manual/{MANUAL_ID}", timeout=10)
        body = r.json()
        st = body.get("status")
        if st != last_status:
            print(f"[t+{elapsed:4d}s] status={st}  chunks={body.get('chunk_count')} wf={body.get('workflow_count')}")
            last_status = st
        if st == "ready":
            t1 = time.time()
            dur = t1 - t0
            print(f"[READY] t1={fmt_ts(t1)}  duration={dur:.1f}s ({dur/60:.1f} min)")
            break
        if st == "error":
            print(f"[ERROR] {body.get('error_message')}")
            return
        time.sleep(POLL_INTERVAL); elapsed += POLL_INTERVAL
    else:
        print(f"[TIMEOUT] {POLL_TIMEOUT}s exceeded")
        return

    # Final query
    body = requests.get(f"{BASE}/api/manual/{MANUAL_ID}", timeout=10).json()
    chunk_count = body.get("chunk_count")
    workflow_count = body.get("workflow_count")
    print(f"[FINAL] chunk_count={chunk_count} workflow_count={workflow_count}")

    # QA sample
    print("[QA] sampling 10 chunks...")
    try:
        sample_ids, sample_docs = qa_sample(MANUAL_ID, k=10)
    except Exception as e:
        print(f"[QA] sample failed: {e}")
        sample_ids, sample_docs = [], []

    # List auto workflows
    wf_files = list_qgis_workflows(MANUAL_ID)
    print(f"[WORKFLOWS] {len(wf_files)} auto workflow files")

    # Render report
    md_lines = [
        "# QGIS Pilot — Training Manual 업로드 결과",
        "",
        f"**실행 시각 (UTC)**: {fmt_ts(time.time())}",
        f"**서버**: `{BASE}` (env: GEOLENS_SOFTWARE_ID=qgis)",
        f"**업로드 경로**: POST /api/manual/upload (UI 와 동일 정규 HTTP 엔드포인트)",
        "",
        "**KB 범위**: Training Manual 단독 (Desktop User Guide 제외 — 감사 기록 참조)",
        "",
        "## 이식 비용 표 첫 실측값",
        "",
        "| PDF | 파일 크기 (MB) | 페이지 | 업로드 시작 (UTC) | 완료 (UTC) | 소요 시간 (s) | manual_id | chunk_count | workflow_count |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| {os.path.basename(PDF_PATH)} | {meta['size_mb']:.1f} | {meta['page_count']} | "
        f"{t0_iso} | {fmt_ts(t1)} | {dur:.1f} ({dur/60:.1f} min) | "
        f"`{MANUAL_ID}` | {chunk_count} | {workflow_count} |",
        "",
        "**t0 주석**: Manual.created_at 값 사용. 최초 upload script 가 종료되어 request-fire 시각을 직접 기록하지 못했으나, "
        "Manual.new() 호출은 upload endpoint 진입 직후 발생하므로 실제 request-fire 와 초 단위 차이만 존재.",
        "",
        "## Auto workflow 발견 (hint_workflow_id prefix)",
        "",
        f"**Prefix**: `auto_{MANUAL_ID}__*` (총 {len(wf_files)} 개)",
        "",
    ]
    for wf_file in wf_files[:20]:
        wid = os.path.basename(wf_file).replace(".json", "")
        try:
            wf_data = json.loads(open(wf_file, "r", encoding="utf-8").read())
            title = wf_data.get("name", "?")
            node_count = len(wf_data.get("nodes", []))
        except Exception:
            title = "?"
            node_count = "?"
        md_lines.append(f"- `{wid}` — {title} ({node_count} nodes)")
    if len(wf_files) > 20:
        md_lines.append(f"- ... (+{len(wf_files)-20} 개)")
    md_lines.append("")

    md_lines.append("## QA — 무작위 청크 10개 샘플 검사")
    md_lines.append("")
    md_lines.append(f"Collection: `manual_{MANUAL_ID}` (전체 {chunk_count} chunks, 10개 sample)")
    md_lines.append("")
    for i, (sid, doc) in enumerate(zip(sample_ids, sample_docs)):
        snippet = (doc or "")[:400].replace("\n", " ")
        md_lines.append(f"**Chunk {i+1}** (`{sid[:20]}...`)")
        md_lines.append("")
        md_lines.append(f"> {snippet}...")
        md_lines.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print("\n" + "=" * 70)
    print(f"[SAVED] {OUT_MD}")
    print("=" * 70)


if __name__ == "__main__":
    main()
