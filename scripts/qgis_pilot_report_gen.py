"""Generate QGIS Pilot upload report from completed manual."""

import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

MANUAL_ID = "bf2804feea57434bb79b749134ed1df0"
PDF = os.environ.get("QGIS_TRAINING_MANUAL_PDF", "QGIS-3.44-TrainingManual-en.pdf")
BASE = "http://127.0.0.1:8000"
OUT = Path(r"./data\eval\results\qgis_pilot_upload_report.md")

import requests
import chromadb
from pypdf import PdfReader


def utc_iso(t):
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat(timespec="seconds")


def parse_iso(s):
    if s.endswith("Z"): s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def main():
    # Manual metadata
    body = requests.get(f"{BASE}/api/manual/{MANUAL_ID}", timeout=10).json()
    t0 = parse_iso(body["created_at"])
    chunk_count = body["chunk_count"]
    workflow_count = body["workflow_count"]

    # t1: from chromadb mtime (last write of embedding batch) + workflow file mtime as approximation
    cdb_mt = max(os.path.getmtime(os.path.join(r, f))
                 for r, _, fs in os.walk("data/chromadb") for f in fs)
    wf_files = sorted(Path("data/workflows").glob(f"auto_{MANUAL_ID}__*.json"))
    wf_mt = max(f.stat().st_mtime for f in wf_files) if wf_files else cdb_mt
    t1 = max(cdb_mt, wf_mt)
    duration = t1 - t0

    # PDF meta
    size_mb = os.path.getsize(PDF) / 1024 / 1024
    page_count = len(PdfReader(PDF).pages)

    # QA sample
    coll = chromadb.PersistentClient(path="data/chromadb").get_collection(f"manual_{MANUAL_ID}")
    all_ids = coll.get()["ids"]
    sample_ids = random.sample(all_ids, min(10, len(all_ids)))
    sample = coll.get(ids=sample_ids)
    docs = sample["documents"]
    metas = sample["metadatas"]

    # Workflow inspection
    wf_data = []
    for f in wf_files:
        w = json.loads(f.read_text(encoding="utf-8"))
        wf_data.append({
            "file": f.name,
            "workflow_id": w["workflow_id"],
            "name": w.get("name", ""),
            "nodes": len(w.get("nodes", [])),
            "edges": len(w.get("edges", [])),
        })

    # Render
    lines = [
        "# QGIS Pilot — Training Manual 업로드 결과",
        "",
        f"**실행 완료 (UTC)**: {utc_iso(t1)}",
        f"**서버**: `{BASE}` (env: GEOLENS_SOFTWARE_ID=qgis)",
        "**업로드 경로**: `POST /api/manual/upload` (UI 와 동일 정규 HTTP 엔드포인트)",
        "**KB 범위**: Training Manual 단독 (Desktop User Guide 제외 — 감사 기록 참조)",
        "",
        "## 이식 비용 표 — 첫 실측값",
        "",
        "| PDF | 크기 (MB) | 페이지 | 업로드 (UTC) | 완료 (UTC) | 소요 | manual_id | chunks | auto wf |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| QGIS-3.44-TrainingManual-en.pdf | {size_mb:.1f} | {page_count} | "
        f"{utc_iso(t0)} | {utc_iso(t1)} | {duration/60:.1f} min | `{MANUAL_ID}` | {chunk_count} | {workflow_count} |",
        "",
        "**t1 주석**: ChromaDB 최종 write 시각과 auto workflow 파일 mtime 중 최댓값. `status=ready` 전환은 두 write 이후 발생하므로 실제 완료 시각과 초 단위 차이만 존재.",
        "",
        f"**참조 조건 (OpendTect unified4)**: Training Manual 454p, chunk_count 486, workflow_count 2 (hand-authored + 2 auto). 이식 비용 표에 나란히 배치하면 페이지 대비 ~1.5× 크기 문서에 대해 인제스트 처리량이 실측됨.",
        "",
        "## Auto Workflow 발견",
        "",
        f"**Prefix (hint_workflow_id 용)**: `auto_{MANUAL_ID}__*`",
        f"**개수**: {len(wf_data)}",
        "",
    ]
    for w in wf_data:
        lines.append(f"### `{w['workflow_id']}`")
        lines.append("")
        lines.append(f"- **이름**: {w['name']}")
        lines.append(f"- **노드 수**: {w['nodes']}")
        lines.append(f"- **에지 수**: {w['edges']}")
        lines.append(f"- **파일**: `data/workflows/{w['file']}`")
        lines.append("")
    lines.append("**관찰**: AutoGraphBuilder 가 QGIS Training Manual 에서 1 개 workflow 만 추출. OpendTect Training Manual (454p) 은 2 개 auto workflow. QGIS 매뉴얼이 절차형 튜토리얼 (Follow Along 섹션) 이 특정 스타일로 구성되어 있어 auto-extraction 이 특정 섹션만 잡은 것으로 보임. Pilot 시나리오는 이 auto workflow 를 사용하거나, 필요 시 hand-author 추가 (OpendTect 의 seismic_attribute 와 동일 방식).")
    lines.append("")
    lines.append("## QA — 무작위 청크 10개 샘플")
    lines.append("")
    lines.append(f"Collection: `manual_{MANUAL_ID}` (전체 {chunk_count} chunks, 10개 sample)")
    lines.append("")
    for i, (sid, doc, meta) in enumerate(zip(sample_ids, docs, metas)):
        snippet = (doc or "")[:400].replace("\n", " ")
        section = meta.get("section", "?") if meta else "?"
        page = meta.get("page", "?") if meta else "?"
        lines.append(f"**Chunk {i+1}** — Section: `{section[:60]}` / Page: {page} / id: `{sid[:16]}...`")
        lines.append("")
        lines.append(f"> {snippet}...")
        lines.append("")

    lines.append("## 다음 단계 (P-2 시나리오 정의)")
    lines.append("")
    lines.append("이식 비용 표 첫 실측값 확보 완료. P-2 시나리오 정의 단계 진입:")
    lines.append("")
    lines.append("- 후보 워크플로우 선정 (auto workflow 활용 or hand-author)")
    lines.append("- QGIS-Training-Data 샘플 데이터로 수행 가능한 6~8 스텝 시나리오")
    lines.append("- 시나리오 정의 후 라우팅 dry-run + 매뉴얼 스텝↔시나리오 스텝 대조표 (체크포인트 8, 9 — 사용자 응답 대기)")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[SAVED] {OUT}")
    print()
    print("\n".join(lines[:20]))


if __name__ == "__main__":
    main()
