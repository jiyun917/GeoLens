"""Minimal reindex for §-1 equivalence audit only.

Skips AutoProcRAG post-processing (chunk role classification, workflow
graph construction, CLIP image indexing) since the equivalence audit only
compares raw retrieval overlap between two chromadb indexes. Those
post-processing steps are the reproduction-time responsibility of the
`_process_pdf` production path (kept unchanged), not part of the
migration verification.

Executes: parse_pdf (pdfplumber) → split_into_chunks → get_embeddings →
vectorstore.add_chunks. This is a strict subset of production
embed_and_store, ensuring the resulting chunks are byte-identical to what
production would produce.

Usage:
    .venv/Scripts/python.exe scripts/reindex_manual_minimal.py \\
        --manual-id 645b7cdf2690408da843b9ce63c52d5b \\
        --pdf data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-...
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
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual-id", required=True)
    ap.add_argument("--pdf", required=True)
    args = ap.parse_args()

    from api.services.parser.pdf_parser import parse_pdf
    from api.services.embedder import split_into_chunks, get_embeddings, _contextualize_chunk
    from api.services import vectorstore

    collection = f"manual_{args.manual_id}"
    print(f"[reindex-min] Collection: {collection}", flush=True)

    # Clean start: drop existing collection so new chunks fully replace old
    try:
        client = vectorstore.get_client()
        existing = [c.name for c in client.list_collections()]
        if collection in existing:
            print(f"[reindex-min] Dropping existing {collection}", flush=True)
            client.delete_collection(collection)
    except Exception as e:
        print(f"[reindex-min] Drop warning: {e}", flush=True)

    t0 = time.time()

    # 1. Parse
    print(f"[reindex-min] Parsing PDF (pdfplumber + OCR pass)...", flush=True)
    pieces = parse_pdf(args.pdf)
    t_parse = time.time() - t0
    print(f"[reindex-min] Parsed {len(pieces)} page pieces in {t_parse:.1f}s", flush=True)

    # 2. Chunk
    chunk_pairs = split_into_chunks(pieces)
    if not chunk_pairs:
        print("[reindex-min] No chunks produced. Aborting.", flush=True)
        return
    print(f"[reindex-min] Split into {len(chunk_pairs)} chunks", flush=True)

    # 3. Generate IDs and contextualize (mirrors production)
    ids = [uuid.uuid4().hex for _ in chunk_pairs]
    chunk_pairs = [
        (text, {**meta, "chunk_id": cid})
        for (text, meta), cid in zip(chunk_pairs, ids)
    ]

    contextualized = []
    metadatas = []
    for chunk, meta in chunk_pairs:
        contextualized.append(_contextualize_chunk(chunk, meta))
        metadatas.append(meta)

    # 4. Embed
    print(f"[reindex-min] Embedding {len(contextualized)} chunks (batches of 100)...", flush=True)
    t_embed_start = time.time()
    all_embeddings = []
    for i in range(0, len(contextualized), 100):
        batch = contextualized[i : i + 100]
        emb = get_embeddings(batch)
        all_embeddings.extend(emb)
        print(f"[reindex-min]   batch {i//100 + 1}: {len(emb)} embeddings", flush=True)
    print(f"[reindex-min] Embedding done in {time.time() - t_embed_start:.1f}s", flush=True)

    # 5. Store
    vectorstore.add_chunks(
        manual_id=args.manual_id,
        ids=ids,
        documents=contextualized,
        metadatas=metadatas,
        embeddings=all_embeddings,
    )
    print(f"[reindex-min] Stored {len(ids)} chunks in ChromaDB", flush=True)

    # Verify
    client = vectorstore.get_client()
    col = client.get_collection(collection)
    print(f"[reindex-min] Verification: collection has {col.count()} chunks", flush=True)
    print(f"[reindex-min] Total elapsed: {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
