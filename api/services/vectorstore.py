import os
import chromadb

CHROMA_DIR = os.environ.get(
    "CHROMADB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chromadb"),
)


def get_client() -> chromadb.ClientAPI:
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection(manual_id: str):
    client = get_client()
    return client.get_or_create_collection(name=f"manual_{manual_id}")


def add_chunks(manual_id: str, ids: list, documents: list, metadatas: list, embeddings: list):
    collection = get_collection(manual_id)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )


def search(manual_id: str, query_embedding: list, top_k: int = 5):
    collection = get_collection(manual_id)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    return results


def search_by_section(manual_id: str, section: str, chunk_indices: list[int]) -> dict:
    """
    Retrieve specific chunks by section name and chunk_index values.
    Used for neighbor chunk expansion in LightRAG dual-level retrieval.
    """
    collection = get_collection(manual_id)
    try:
        # Query chunks matching the section and specific chunk indices
        all_docs = []
        all_metas = []
        for idx in chunk_indices:
            results = collection.get(
                where={"$and": [{"section": section}, {"chunk_index": idx}]},
                include=["documents", "metadatas"],
            )
            if results and results["documents"]:
                all_docs.extend(results["documents"])
                all_metas.extend(results["metadatas"])
        return {"documents": all_docs, "metadatas": all_metas}
    except Exception:
        return {"documents": [], "metadatas": []}


def get_chunks_by_ids(manual_id: str, ids: list) -> dict:
    """Fetch chunks by their ChromaDB document ids. Used by the procedural
    state-path retriever to materialize workflow-node linked_chunks. Returns
    {"documents": [...], "metadatas": [...]} ordered to match the input ids
    (missing ids drop out)."""
    if not ids:
        return {"documents": [], "metadatas": []}
    collection = get_collection(manual_id)
    try:
        result = collection.get(ids=list(ids), include=["documents", "metadatas"])
        # Re-order to match input order so callers can preserve their step order
        id_to_idx = {cid: i for i, cid in enumerate(result.get("ids", []) or [])}
        docs, metas = [], []
        for cid in ids:
            if cid in id_to_idx:
                docs.append(result["documents"][id_to_idx[cid]])
                metas.append(result["metadatas"][id_to_idx[cid]])
        return {"documents": docs, "metadatas": metas}
    except Exception:
        return {"documents": [], "metadatas": []}


def delete_collection(manual_id: str):
    client = get_client()
    try:
        client.delete_collection(name=f"manual_{manual_id}")
    except Exception:
        pass
