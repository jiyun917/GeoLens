"""QGIS Pilot — automated PDF upload via regular HTTP endpoint.

Same path as UI's Submit button (POST /api/manual/upload). No direct
internal-function calls. Instruments t0/t1, polls /api/manual/{id} until
ready, collects manual_id/chunk_count/workflow_count, runs QA (10 random
chunk sample), outputs markdown result table.

Usage:
    .venv/Scripts/python.exe scripts/qgis_pilot_upload.py

Prereqs:
    - FastAPI running on http://127.0.0.1:8000 with GEOLENS_SOFTWARE_ID=qgis
    - Both PDFs at hard-coded paths (edit PDFS list if different)
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "http://127.0.0.1:8000"
POLL_INTERVAL = 5           # seconds between status polls
POLL_TIMEOUT = 30 * 60      # 30 min hard timeout per PDF

PDFS = [
    os.environ.get("QGIS_TRAINING_MANUAL_PDF", "QGIS-3.44-TrainingManual-en.pdf"),
    os.environ.get("QGIS_USER_GUIDE_PDF", "QGIS-3.44-DesktopUserGuide-en.pdf"),
]

OUT_MD = Path(r"./data\eval\results\qgis_pilot_upload_report.md")


def fmt_ts(t: float) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat(timespec="seconds")


def pdf_meta(path: str) -> dict:
    """Return {size_mb, page_count}. Uses pypdf (already in venv)."""
    from pypdf import PdfReader
    size = os.path.getsize(path)
    r = PdfReader(path)
    return {
        "size_mb": size / 1024 / 1024,
        "page_count": len(r.pages),
    }


def upload_pdf(path: str) -> tuple[str, float]:
    """POST /api/manual/upload — returns (manual_id, t0)."""
    fname = os.path.basename(path)
    print(f"[UPLOAD] firing POST {BASE}/api/manual/upload  file={fname}")
    with open(path, "rb") as fh:
        files = {"file": (fname, fh, "application/pdf")}
        t0 = time.time()
        r = requests.post(f"{BASE}/api/manual/upload", files=files, timeout=120)
    r.raise_for_status()
    body = r.json()
    mid = body["id"]
    print(f"[UPLOAD] accepted manual_id={mid}  t0={fmt_ts(t0)}")
    return mid, t0


def poll_until_ready(manual_id: str, t0: float) -> tuple[str, float, Optional[str]]:
    """Poll /api/manual/{id} until status in {ready, error}. Returns (status, t1, error_message)."""
    print(f"[POLL] every {POLL_INTERVAL}s until status=ready|error (timeout {POLL_TIMEOUT}s)")
    elapsed = 0
    last_status = None
    while elapsed < POLL_TIMEOUT:
        r = requests.get(f"{BASE}/api/manual/{manual_id}", timeout=15)
        if r.status_code != 200:
            print(f"[POLL] {r.status_code}: {r.text[:200]}")
            time.sleep(POLL_INTERVAL); elapsed += POLL_INTERVAL; continue
        body = r.json()
        status = body.get("status")
        if status != last_status:
            print(f"[POLL] t+{elapsed:4d}s  status={status}  chunk_count={body.get('chunk_count')} workflow_count={body.get('workflow_count')}")
            last_status = status
        if status == "ready":
            t1 = time.time()
            return "ready", t1, None
        if status == "error":
            t1 = time.time()
            return "error", t1, body.get("error_message")
        time.sleep(POLL_INTERVAL); elapsed += POLL_INTERVAL
    return "timeout", time.time(), f"exceeded {POLL_TIMEOUT}s"


def query_manual(manual_id: str) -> dict:
    r = requests.get(f"{BASE}/api/manual/{manual_id}", timeout=15)
    r.raise_for_status()
    return r.json()


def qa_sample(manual_id: str, k: int = 10) -> tuple[list[str], list[str]]:
    """Return (sampled_ids, sampled_docs[:400]) from ChromaDB collection."""
    import chromadb
    c = chromadb.PersistentClient(path="data/chromadb").get_collection(f"manual_{manual_id}")
    all_ids = c.get()["ids"]
    if len(all_ids) < k:
        k = len(all_ids)
    sample_ids = random.sample(all_ids, k)
    docs = c.get(ids=sample_ids)["documents"]
    return sample_ids, docs


def render_report(results: list[dict]) -> str:
    lines = [
        "# QGIS Pilot — PDF 업로드 결과 (자동화 실행)",
        "",
        f"**실행 시각 (UTC)**: {fmt_ts(time.time())}",
        f"**서버**: `{BASE}` (env: GEOLENS_SOFTWARE_ID=qgis)",
        f"**업로드 경로**: POST /api/manual/upload (UI 와 동일 정규 HTTP 엔드포인트)",
        "",
        "## 이식 비용 표 첫 실측값",
        "",
        "| PDF | 파일 크기 (MB) | 페이지 | 업로드 시작 (UTC) | 완료 (UTC) | 소요 시간 (s) | manual_id | chunk_count | workflow_count | status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        dur = r["t1"] - r["t0"] if r.get("t1") else None
        dur_str = f"{dur:.1f}" if dur else "—"
        lines.append(
            f"| {r['pdf_name']} | {r['size_mb']:.1f} | {r['page_count']} | "
            f"{fmt_ts(r['t0'])} | {fmt_ts(r['t1']) if r.get('t1') else '—'} | "
            f"{dur_str} | `{r.get('manual_id','—')}` | {r.get('chunk_count','—')} | "
            f"{r.get('workflow_count','—')} | {r['status']} |"
        )
    lines.append("")
    lines.append("## QA — 무작위 청크 10개 샘플 검사")
    lines.append("")
    for r in results:
        if r["status"] != "ready" or "qa_docs" not in r:
            continue
        lines.append(f"### {r['pdf_name']}")
        lines.append("")
        lines.append(f"Collection: `manual_{r['manual_id']}` (전체 {r['chunk_count']} chunks, 10개 sample)")
        lines.append("")
        for i, (sid, doc) in enumerate(zip(r["qa_ids"], r["qa_docs"])):
            snippet = (doc or "")[:400].replace("\n", " ")
            lines.append(f"**Chunk {i+1}** (`{sid[:16]}...`)")
            lines.append("")
            lines.append(f"> {snippet}...")
            lines.append("")
    lines.append("## Auto workflow 발견 (hint_workflow_id 용 prefix)")
    lines.append("")
    for r in results:
        if r["status"] != "ready":
            continue
        prefix = f"auto_{r['manual_id']}__"
        lines.append(f"- **{r['pdf_name']}**: `{prefix}*` (workflow_count={r['workflow_count']})")
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    results = []
    for path in PDFS:
        pdf_name = os.path.basename(path)
        print("\n" + "=" * 70)
        print(f"[START] {pdf_name}")
        print("=" * 70)
        if not os.path.exists(path):
            print(f"[SKIP] not found: {path}")
            results.append({"pdf_name": pdf_name, "status": "not_found", "t0": time.time()})
            continue
        meta = pdf_meta(path)
        print(f"[META] size={meta['size_mb']:.1f}MB  pages={meta['page_count']}")
        try:
            mid, t0 = upload_pdf(path)
        except Exception as e:
            print(f"[ERROR] upload failed: {e}")
            results.append({"pdf_name": pdf_name, "status": "upload_error", "t0": time.time(),
                            "size_mb": meta["size_mb"], "page_count": meta["page_count"],
                            "error": str(e)})
            continue

        status, t1, err = poll_until_ready(mid, t0)
        dur = t1 - t0
        print(f"[DONE] status={status}  duration={dur:.1f}s")

        entry = {
            "pdf_name": pdf_name,
            "size_mb": meta["size_mb"],
            "page_count": meta["page_count"],
            "manual_id": mid,
            "t0": t0,
            "t1": t1,
            "status": status,
        }
        if err:
            entry["error"] = err
            print(f"[ERROR] {err}")

        if status == "ready":
            body = query_manual(mid)
            entry["chunk_count"] = body.get("chunk_count")
            entry["workflow_count"] = body.get("workflow_count")
            print(f"[META] chunk_count={entry['chunk_count']}  workflow_count={entry['workflow_count']}")
            try:
                sample_ids, sample_docs = qa_sample(mid, k=10)
                entry["qa_ids"] = sample_ids
                entry["qa_docs"] = sample_docs
                print(f"[QA] sampled {len(sample_ids)} chunks")
            except Exception as e:
                print(f"[QA] sample failed: {e}")
                entry["qa_error"] = str(e)
        results.append(entry)

    md = render_report(results)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8")
    print("\n" + "=" * 70)
    print(f"[SAVED] {OUT_MD}")
    print("=" * 70)
    print(md)


if __name__ == "__main__":
    main()
