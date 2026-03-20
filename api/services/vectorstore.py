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


def delete_collection(manual_id: str):
    client = get_client()
    try:
        client.delete_collection(name=f"manual_{manual_id}")
    except Exception:
        pass
