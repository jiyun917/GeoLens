import uuid
from typing import List, Tuple

import tiktoken
from sentence_transformers import SentenceTransformer

from . import vectorstore
from .manual_store import update_manual
from .graph_builder import build_graph_from_chunks

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def split_into_chunks(text: str) -> List[str]:
    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def get_embeddings(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


def embed_and_store(manual_id: str, content_pieces: List[Tuple[str, dict]]):
    """
    Takes a list of (text, metadata) tuples, chunks them, embeds, and stores in ChromaDB.
    Updates the manual's chunk_count and status when done.
    """
    all_chunks = []
    all_metadatas = []

    for text, metadata in content_pieces:
        chunks = split_into_chunks(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append(metadata)

    if not all_chunks:
        update_manual(manual_id, status="ready", chunk_count=0)
        return

    # Embed in batches of 100
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.extend(embeddings)

    ids = [uuid.uuid4().hex for _ in all_chunks]

    vectorstore.add_chunks(
        manual_id=manual_id,
        ids=ids,
        documents=all_chunks,
        metadatas=all_metadatas,
        embeddings=all_embeddings,
    )

    update_manual(manual_id, status="ready", chunk_count=len(all_chunks))
    print(f"[EMBED] Manual {manual_id} ready: {len(all_chunks)} chunks")

    # Build knowledge graph from chunks (Graph RAG) - in separate thread to not block
    import threading
    def _build_graph():
        try:
            chunk_pairs = list(zip(all_chunks, all_metadatas))
            build_graph_from_chunks(manual_id, chunk_pairs)
        except Exception as e:
            print(f"[GRAPH] Graph building failed for {manual_id}: {e}")

    threading.Thread(target=_build_graph, daemon=True).start()
