"""Re-index the OpendTect manual using the current parser (pdfplumber).

Existing chromadb collection for the manual is dropped and rebuilt so that
the new parser's chunks fully replace the old ones. Old collection was
backed up separately as `data/chromadb_pymupdf_reference/` before running
this script.

Usage:
    .venv/Scripts/python.exe scripts/reindex_manual.py \\
        --manual-id 645b7cdf2690408da843b9ce63c52d5b \\
        --pdf data/uploads/645b7cdf2690408da843b9ce63c52d5b_Introduction-...
"""

from __future__ import annotations

import argparse
import os
import sys
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
    ap.add_argument("--manual-id", required=True, help="Manual ID (matches ChromaDB collection name suffix)")
    ap.add_argument("--pdf", required=True, help="Path to PDF file")
    ap.add_argument("--skip-ocr", action="store_true",
                    help="Skip Gemini Vision OCR pass (useful for testing without spending)")
    args = ap.parse_args()

    from api.services.parser.pdf_parser import parse_pdf
    from api.services.embedder import embed_and_store
    from api.services import vectorstore

    if args.skip_ocr:
        os.environ.pop("GEMINI_API_KEY", None)

    collection_name = f"manual_{args.manual_id}"

    print(f"[reindex] Manual ID: {args.manual_id}")
    print(f"[reindex] PDF: {args.pdf}")
    print(f"[reindex] Collection: {collection_name}")

    # Drop existing collection so new chunks fully replace old ones
    try:
        client = vectorstore.get_client()
        existing = [c.name for c in client.list_collections()]
        if collection_name in existing:
            print(f"[reindex] Dropping existing collection {collection_name}")
            client.delete_collection(collection_name)
    except Exception as e:
        print(f"[reindex] Warning during drop: {e}")

    # Parse
    print("[reindex] Parsing PDF...")
    pieces = parse_pdf(args.pdf)
    print(f"[reindex] Extracted {len(pieces)} page pieces")

    # Embed + store
    print("[reindex] Embedding + storing...")
    embed_and_store(args.manual_id, pieces, pdf_path=args.pdf)

    # Final count
    client = vectorstore.get_client()
    col = client.get_collection(collection_name)
    print(f"[reindex] Done. Collection now has {col.count()} chunks.")


if __name__ == "__main__":
    main()
