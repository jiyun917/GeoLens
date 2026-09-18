"""Re-embed an existing ChromaDB collection with the current EMBED_MODEL,
keeping the same chunk ids / documents / metadatas (so workflow
linked_chunks keep resolving), into a separate ChromaDB directory.

v3 rerun: the unified2/3/4 index was embedded with all-MiniLM-L6-v2 (256
word-piece window, English-centric). This script reads the stored
documents (which already carry the "[Section, Page, Source]" contextual
prefix) and writes bge-m3 vectors to data/chromadb_v3. No PDF parsing and
no Gemini OCR is repeated, so the chunk set is byte-identical to the
pdfplumber index used by unified3/4.

Usage:
    EMBED_MODEL=BAAI/bge-m3 .venv/Scripts/python.exe scripts/reembed_index.py \
        --src data/chromadb --dst data/chromadb_v3 --manual-id 645b7cdf2690408da843b9ce63c52d5b
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="data/chromadb")
    ap.add_argument("--dst", default="data/chromadb_v3")
    ap.add_argument("--manual-id", action="append", required=True)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    import chromadb
    from api.services.embedder import get_embeddings, EMBED_MODEL

    src = chromadb.PersistentClient(path=str(ROOT / args.src))
    dst = chromadb.PersistentClient(path=str(ROOT / args.dst))
    for mid in args.manual_id:
        name = f"manual_{mid}"
        col = src.get_collection(name)
        data = col.get(include=["documents", "metadatas"])
        ids, docs, metas = data["ids"], data["documents"], data["metadatas"]
        print(f"[reembed] {name}: {len(ids)} chunks from {args.src} -> {args.dst} with {EMBED_MODEL}")
        try:
            dst.delete_collection(name)
        except Exception:
            pass
        out = dst.get_or_create_collection(name=name)
        t0 = time.time()
        for i in range(0, len(ids), args.batch):
            emb = get_embeddings(docs[i:i + args.batch])
            out.add(ids=ids[i:i + args.batch], documents=docs[i:i + args.batch],
                    metadatas=metas[i:i + args.batch], embeddings=emb)
            if (i // args.batch) % 5 == 0:
                print(f"  {i + len(emb)}/{len(ids)} ({time.time() - t0:.0f}s)", flush=True)
        print(f"[reembed] done {name}: {out.count()} chunks, dim={len(emb[0])}, {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
