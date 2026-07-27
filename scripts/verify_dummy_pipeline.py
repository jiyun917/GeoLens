"""End-to-end reproducibility check for the guide pipeline using the
synthetic manual corpus at data/eval/dummy_manuals/.

Reviewers without access to the copyrighted OpenDtect manual can run
this to confirm the paper's core pipeline works on their machine.

Steps:
  1. Ingest three synthetic manual markdown files as a single manual
     (bypasses the PDF parser since the source is plain markdown; the
     PDF parser itself is exercised by the OpenDtect reindex path and
     validated in data/eval/results/pypdf_migration_audit.md).
  2. Chunk + embed + persist to a scratch ChromaDB collection.
  3. Retrieve top-5 chunks for three sample queries via the same
     get_manual_context() helper the vanilla_vector backend uses.
  4. If a GEMINI_API_KEY is present, generate a one-step response with
     the full_system backend to prove the LLM path is wired.

Exit code:
  0 — every step succeeded
  1 — an ingest / retrieval / generation step failed (details on stderr)

Usage:
    .venv/Scripts/python.exe scripts/verify_dummy_pipeline.py
    .venv/Scripts/python.exe scripts/verify_dummy_pipeline.py --skip-generate
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
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


DUMMY_DIR = ROOT / "data" / "eval" / "dummy_manuals"
SAMPLE_QUERIES = [
    ("terminology",   "What does the term inline mean in seismic data?"),
    ("workflow",      "How do I define the grid when creating a new survey?"),
    ("visualization", "What are the three orthogonal displays a standard 3D Scene should contain?"),
]


def log(msg: str, *, err: bool = False) -> None:
    stream = sys.stderr if err else sys.stdout
    print(msg, file=stream, flush=True)


def load_dummy_pieces() -> list[tuple[str, dict]]:
    """Read every .md file in DUMMY_DIR as a (text, metadata) pair. The
    text is the whole file; downstream split_into_chunks handles size."""
    if not DUMMY_DIR.exists():
        raise FileNotFoundError(f"dummy manuals dir missing: {DUMMY_DIR}")
    files = sorted(DUMMY_DIR.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"no .md files in {DUMMY_DIR}")
    pieces: list[tuple[str, dict]] = []
    for i, f in enumerate(files):
        text = f.read_text(encoding="utf-8")
        # Section title = the first "# ..." line, fallback to filename stem.
        title = f.stem
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        pieces.append((text, {
            "source":  str(f.relative_to(ROOT)),
            "page":    i + 1,
            "section": title,
            "type":    "markdown",
        }))
    return pieces


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-generate", action="store_true",
                    help="Retrieval only; skip the LLM generation step. "
                         "Use when no GEMINI_API_KEY is set.")
    ap.add_argument("--keep-index", action="store_true",
                    help="Keep the scratch ChromaDB index after the run "
                         "(default: delete).")
    args = ap.parse_args()

    log("=== dummy pipeline verification ===")

    manual_id = f"dummy_{uuid.uuid4().hex[:8]}"
    scratch_dir = Path(tempfile.mkdtemp(prefix="geolens_verify_"))
    os.environ["CHROMADB_PATH"] = str(scratch_dir)
    log(f"scratch chromadb: {scratch_dir}")
    log(f"manual_id:        {manual_id}")

    try:
        from api.services.embedder import split_into_chunks, get_embeddings, _contextualize_chunk
        from api.services import vectorstore
        from api.services.rag import get_manual_context

        # 1. Ingest
        log("\n[1/4] loading synthetic manual…")
        pieces = load_dummy_pieces()
        log(f"      loaded {len(pieces)} source documents")

        # 2. Chunk + embed
        log("[2/4] chunk + embed…")
        chunk_pairs = split_into_chunks(pieces)
        if not chunk_pairs:
            log("      no chunks produced", err=True)
            return 1
        log(f"      {len(chunk_pairs)} chunks produced")

        ids = [uuid.uuid4().hex for _ in chunk_pairs]
        chunk_pairs = [
            (t, {**m, "chunk_id": cid})
            for (t, m), cid in zip(chunk_pairs, ids)
        ]
        contextualized = [_contextualize_chunk(t, m) for (t, m) in chunk_pairs]
        metadatas = [m for (_, m) in chunk_pairs]

        try:
            embeddings = get_embeddings(contextualized)
        except Exception as e:
            log(f"      embedding failed: {e}", err=True)
            log("      → check that OPENAI_API_KEY is set for the embedder", err=True)
            return 1
        log(f"      {len(embeddings)} embeddings computed")

        vectorstore.add_chunks(
            manual_id=manual_id, ids=ids,
            documents=contextualized, metadatas=metadatas, embeddings=embeddings,
        )
        log("      chunks stored in ChromaDB")

        # 3. Retrieval
        log("[3/4] retrieving top-5 for 3 sample queries…")
        retrieval_ok = True
        for label, query in SAMPLE_QUERIES:
            context = get_manual_context(manual_ids=[manual_id], query=query, top_k=5)
            if not context or len(context.strip()) < 20:
                log(f"      [{label}] EMPTY retrieval for query: {query}", err=True)
                retrieval_ok = False
                continue
            first_line = context.strip().splitlines()[0][:80]
            log(f"      [{label}] OK  ({len(context)} chars, first line: '{first_line}…')")
        if not retrieval_ok:
            return 1

        # 4. Generation (optional)
        if args.skip_generate:
            log("[4/4] generation SKIPPED (--skip-generate)")
        elif not os.environ.get("GEMINI_API_KEY"):
            log("[4/4] generation SKIPPED (no GEMINI_API_KEY in env)")
        else:
            log("[4/4] generating one step response via Gemini + retrieval context…")
            try:
                from api.services.rag import get_manual_context
                from api.services.bench_backends import _record_usage, _reset_usage
                from google import genai
                from google.genai import types as genai_types

                query = SAMPLE_QUERIES[1][1]
                context = get_manual_context(manual_ids=[manual_id], query=query, top_k=5)
                prompt = (
                    "You are a step-by-step software guide. Given the manual "
                    "excerpt below and the user's question, respond with a "
                    "single actionable next step (one sentence).\n\n"
                    f"### Manual excerpt\n{context}\n\n### Question\n{query}"
                )
                client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
                _reset_usage()
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[genai_types.Part.from_text(text=prompt)],
                )
                text = (resp.text or "").strip()
                if not text:
                    log("      empty response from Gemini", err=True)
                    return 1
                log(f"      response ({len(text)} chars): {text[:200]}"
                    + ("…" if len(text) > 200 else ""))
            except Exception as e:
                log(f"      generation failed: {e}", err=True)
                return 1

        log("\n✓ dummy pipeline verification PASSED")
        return 0

    finally:
        if not args.keep_index:
            shutil.rmtree(scratch_dir, ignore_errors=True)
            log(f"cleaned up scratch dir: {scratch_dir}")
        else:
            log(f"scratch dir kept: {scratch_dir}")


if __name__ == "__main__":
    sys.exit(main())
