"""v3 KB re-ingest: parse with the general figure-OCR rule, chunk, contextualise,
embed with EMBED_MODEL (bge-m3) and store into a NEW ChromaDB directory.

Deliberately does NOT run the chunk classifier, auto workflow builder,
knowledge-graph builder or CLIP re-index (embed_and_store does). Those
would change the candidate pool / KG; the KG block is excluded from guide
context in v3 anyway and the CLIP image cache is page based and unchanged.

Usage:
    CHROMADB_PATH=./data/chromadb_v4 EMBED_MODEL=BAAI/bge-m3 OCR_FIGURES=1 \
      .venv/Scripts/python.exe scripts/reindex_v4.py --manual-id <id> --pdf <path>
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p, override=False)
except ImportError:
    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual-id", required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()
    from api.services.parser.pdf_parser import parse_pdf, OCR_FIGURES, OCR_FIGURE_AREA_MIN
    from api.services.embedder import split_into_chunks, _contextualize_chunk, get_embeddings, EMBED_MODEL
    from api.services import vectorstore
    print(f"[reindex_v4] manual={args.manual_id} pdf={args.pdf} chroma={vectorstore.CHROMA_DIR} embed={EMBED_MODEL} "
          f"figure_ocr={OCR_FIGURES} area_min={OCR_FIGURE_AREA_MIN}", flush=True)
    t0 = time.time()
    pieces = parse_pdf(args.pdf)
    print(f"[reindex_v4] parsed {len(pieces)} page pieces in {time.time() - t0:.0f}s; "
          f"figure-OCR blocks on {sum(1 for t, _ in pieces if '[Figure OCR' in t)} pages", flush=True)
    chunks = split_into_chunks(pieces)
    print(f"[reindex_v4] {len(chunks)} chunks", flush=True)
    ids = [uuid.uuid4().hex for _ in chunks]
    docs = [_contextualize_chunk(c, {**m}) for c, m in chunks]
    metas = [{**m, "chunk_id": cid} for (_, m), cid in zip(chunks, ids)]
    client = vectorstore.get_client()
    name = f"manual_{args.manual_id}"
    try:
        client.delete_collection(name)
    except Exception:
        pass
    col = client.get_or_create_collection(name=name)
    t1 = time.time()
    for i in range(0, len(ids), args.batch):
        emb = get_embeddings(docs[i:i + args.batch])
        col.add(ids=ids[i:i + args.batch], documents=docs[i:i + args.batch], metadatas=metas[i:i + args.batch], embeddings=emb)
        if (i // args.batch) % 10 == 0:
            print(f"  embedded {i + len(emb)}/{len(ids)} ({time.time() - t1:.0f}s)", flush=True)
    print(f"[reindex_v4] done: {col.count()} chunks in {name} ({time.time() - t0:.0f}s total)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
