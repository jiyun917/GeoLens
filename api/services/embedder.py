import uuid
from typing import List, Optional, Tuple

import tiktoken
from sentence_transformers import SentenceTransformer

from . import vectorstore
from .manual_store import update_manual
from .graph_builder import build_graph_from_chunks
from .chunk_classifier import ChunkClassifier

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _chunk_single_text(text: str) -> List[str]:
    """Split a single text into token-based chunks with overlap."""
    enc = tiktoken.encoding_for_model("gpt-4o")
    # Pre-split very large texts to avoid tiktoken stack overflow
    MAX_CHARS = 50000
    if len(text) > MAX_CHARS:
        sub_texts = [text[i:i + MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
        all_tokens = []
        for sub in sub_texts:
            all_tokens.extend(enc.encode(sub))
        tokens = all_tokens
    else:
        tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def split_into_chunks(content_pieces: List[Tuple[str, dict]]) -> List[Tuple[str, dict]]:
    """
    Split content pieces into chunks, respecting section boundaries.
    Each (text, metadata) pair is chunked independently so chunks never cross sections.
    Returns list of (chunk_text, metadata_with_chunk_index) tuples.
    """
    all_chunks = []
    # Track chunk_index per section
    section_counters = {}

    for text, metadata in content_pieces:
        section = metadata.get("section", "unknown")
        if section not in section_counters:
            section_counters[section] = 0

        chunks = _chunk_single_text(text)
        for chunk in chunks:
            chunk_meta = {
                **metadata,
                "section": section,
                "chunk_index": section_counters[section],
            }
            all_chunks.append((chunk, chunk_meta))
            section_counters[section] += 1

    return all_chunks


def _contextualize_chunk(chunk: str, metadata: dict) -> str:
    """
    Prepend contextual information to a chunk (Contextual Retrieval).
    This helps the embedding model and LLM understand where the chunk comes from.
    """
    section = metadata.get("section", "unknown")
    page = metadata.get("page", "?")
    source = metadata.get("source", "unknown")
    return f"[Section: {section}, Page: {page}, Source: {source}]\n{chunk}"


def get_embeddings(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


def embed_and_store(
    manual_id: str,
    content_pieces: List[Tuple[str, dict]],
    pdf_path: Optional[str] = None,
):
    """
    Takes a list of (text, metadata) tuples, chunks them within section boundaries,
    applies contextual retrieval (prepends section/page/source info),
    embeds, and stores in ChromaDB.

    Also triggers AutoProcRAG post-processing:
      - chunk role classification (procedural / parameter / concept / …)
      - automatic Workflow Graph construction from classified chunks
      - (if pdf_path) manual image extraction + CLIP indexing for visual matching

    Updates the manual's chunk_count, workflow_count, and status when done.
    """
    # Split into chunks respecting section boundaries
    chunk_pairs = split_into_chunks(content_pieces)

    if not chunk_pairs:
        update_manual(manual_id, status="ready", chunk_count=0, workflow_count=0)
        return

    # Classify each chunk's procedural role (procedural_step / parameter_desc /
    # concept_explanation / transition_cue / ui_description / general).
    # Adds chunk_role + extracted fields to each chunk's metadata.
    try:
        chunk_pairs = ChunkClassifier().classify_batch(chunk_pairs)
    except Exception as e:
        print(f"[EMBED] chunk classification failed ({e}); continuing without roles")

    # Generate ChromaDB IDs up front and bake them into metadata so the auto
    # graph builder can reference chunks by their stored id.
    ids = [uuid.uuid4().hex for _ in chunk_pairs]
    chunk_pairs = [
        (text, {**meta, "chunk_id": cid})
        for (text, meta), cid in zip(chunk_pairs, ids)
    ]

    # Apply contextual retrieval: prepend metadata context to each chunk
    contextualized_chunks = []
    chunk_metadatas = []
    raw_chunks = []  # For graph building (without context prefix)

    for chunk, metadata in chunk_pairs:
        contextualized = _contextualize_chunk(chunk, metadata)
        contextualized_chunks.append(contextualized)
        chunk_metadatas.append(metadata)
        raw_chunks.append(chunk)

    # Embed contextualized chunks in batches of 100
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(contextualized_chunks), batch_size):
        batch = contextualized_chunks[i : i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.extend(embeddings)

    vectorstore.add_chunks(
        manual_id=manual_id,
        ids=ids,
        documents=contextualized_chunks,
        metadatas=chunk_metadatas,
        embeddings=all_embeddings,
    )

    print(f"[EMBED] Manual {manual_id} ready: {len(contextualized_chunks)} contextualized chunks")

    # ─── AutoProcRAG post-processing ──────────────────────
    workflow_count = _build_auto_workflows(manual_id, chunk_pairs)
    if pdf_path:
        _index_manual_images(manual_id, pdf_path)

    update_manual(
        manual_id,
        status="ready",
        chunk_count=len(contextualized_chunks),
        workflow_count=workflow_count,
    )

    # Build knowledge graph from raw chunks (without context prefix)
    import threading
    def _build_graph():
        try:
            graph_pairs = list(zip(raw_chunks, chunk_metadatas))
            build_graph_from_chunks(manual_id, graph_pairs)
        except Exception as e:
            print(f"[GRAPH] Graph building failed for {manual_id}: {e}")

    threading.Thread(target=_build_graph, daemon=True).start()


def _build_auto_workflows(manual_id: str, classified_chunks: List[Tuple[str, dict]]) -> int:
    """Build and save auto workflow JSONs. Returns the number of workflows created."""
    try:
        from .auto_graph_builder import AutoGraphBuilder, save_workflows
        workflows = AutoGraphBuilder().build_workflow_from_chunks(manual_id, classified_chunks)
        if not workflows:
            print(f"[AUTO_GRAPH] no qualifying sections for manual={manual_id}")
            return 0
        paths = save_workflows(workflows)
        print(f"[AUTO_GRAPH] saved {len(paths)} workflow JSON(s) for manual={manual_id}")
        try:
            from .workflow_graph import reload_workflow_graph
            reload_workflow_graph()
        except Exception as e:
            print(f"[AUTO_GRAPH] reload failed: {e}")
        return len(workflows)
    except Exception as e:
        print(f"[AUTO_GRAPH] build failed for manual={manual_id}: {e}")
        return 0


def _index_manual_images(manual_id: str, pdf_path: str) -> int:
    """Extract manual images from the PDF and index them for visual matching."""
    try:
        from .image_extractor import ManualImageExtractor
        from .visual_matcher import get_visual_matcher
        extractor = ManualImageExtractor()
        images = extractor.extract_images(pdf_path)
        if not images:
            return 0
        extractor.save_images(manual_id, images)
        matcher = get_visual_matcher()
        if not matcher.available():
            print(f"[VISUAL_MATCH] skipped CLIP indexing for manual={manual_id} (CLIP unavailable)")
            return 0
        return matcher.index_manual_images(manual_id, images)
    except Exception as e:
        print(f"[VISUAL_MATCH] image indexing failed for manual={manual_id}: {e}")
        return 0
