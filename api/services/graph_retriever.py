"""
Graph Retriever: Hybrid retrieval combining workflow graph traversal
with ChromaDB vector search.
"""

from typing import Dict, List, Optional

from .workflow_graph import WorkflowGraph, get_workflow_graph
from .rag import get_manual_context
from . import vectorstore
from .embedder import get_embeddings


class GraphRetriever:
    """
    Hybrid retriever:
    - Graph-based: fetch chunks linked to a workflow node
    - Vector-based: fallback semantic search via ChromaDB
    - Hybrid: combine both with context-aware query enrichment
    """

    def __init__(self, workflow_graph: Optional[WorkflowGraph] = None):
        self.graph = workflow_graph or get_workflow_graph()

    # ═══════════════════════════════════════════════════════════
    # Graph-based retrieval
    # ═══════════════════════════════════════════════════════════

    def retrieve_by_graph(
        self,
        current_node_id: str,
        intent: str = "next_step",
        manual_ids: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Graph-driven retrieval based on current workflow position.

        intent:
        - 'next_step': get chunks for next nodes in workflow
        - 'current': get chunks for the current node
        - 'explain': get chunks explaining the current step's concepts
        """
        results: List[Dict] = []

        current = self.graph.get_node(current_node_id)
        if not current:
            return results

        if intent == "current":
            nodes = [current]
        elif intent == "next_step":
            nodes = self.graph.get_next_steps(current_node_id) or [current]
        else:  # 'explain'
            nodes = [current]

        # 1. Use linked_chunks if available
        chunk_ids = []
        for n in nodes:
            chunk_ids.extend(n.get("linked_chunks", []) or [])

        if chunk_ids and manual_ids:
            linked_docs = self._fetch_chunks_by_ids(manual_ids, chunk_ids)
            for doc in linked_docs:
                results.append({
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "source_type": "graph_linked",
                    "node_id": doc.get("node_id"),
                })

        # 2. Vector search using node title + description as query
        if manual_ids:
            for n in nodes:
                query = f"{n.get('title', '')} {n.get('description', '')}".strip()
                if query:
                    vector_results = get_manual_context(manual_ids, query, top_k=3)
                    if vector_results:
                        results.append({
                            "text": vector_results,
                            "metadata": {"node_id": n["id"], "title": n.get("title")},
                            "source_type": "graph_vector",
                            "node_id": n["id"],
                        })

        return results

    # ═══════════════════════════════════════════════════════════
    # Vector-based retrieval (fallback / standalone)
    # ═══════════════════════════════════════════════════════════

    def retrieve_by_vector(
        self, query: str, manual_ids: Optional[List[str]] = None, top_k: int = 5
    ) -> Optional[str]:
        """Standard vector search via existing RAG infrastructure."""
        if not manual_ids or not query:
            return None
        return get_manual_context(manual_ids, query, top_k=top_k)

    # ═══════════════════════════════════════════════════════════
    # Hybrid retrieval
    # ═══════════════════════════════════════════════════════════

    def hybrid_retrieve(
        self,
        current_node_id: Optional[str],
        query: str,
        intent: str = "next_step",
        manual_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Combined graph + vector retrieval.
        Returns structured context:
        {
          "graph_context": [...],
          "vector_context": "...",
          "current_node": {...},
          "next_nodes": [...]
        }
        """
        result = {
            "graph_context": [],
            "vector_context": None,
            "current_node": None,
            "next_nodes": [],
        }

        if current_node_id:
            current = self.graph.get_node(current_node_id)
            if current:
                result["current_node"] = current
                result["next_nodes"] = self.graph.get_next_steps(current_node_id)
                # Enrich query with node context
                enriched_query = (
                    f"[{current.get('workflow_id', '')} > {current.get('title', '')}] {query}"
                )
                result["graph_context"] = self.retrieve_by_graph(
                    current_node_id, intent=intent, manual_ids=manual_ids
                )
                # Vector search with enriched query
                result["vector_context"] = self.retrieve_by_vector(
                    enriched_query, manual_ids=manual_ids
                )
                return result

        # No current node → plain vector search
        result["vector_context"] = self.retrieve_by_vector(query, manual_ids=manual_ids)
        return result

    # ═══════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _fetch_chunks_by_ids(manual_ids: List[str], chunk_ids: List[str]) -> List[Dict]:
        """Fetch specific chunks by their IDs from ChromaDB."""
        docs = []
        for manual_id in manual_ids:
            try:
                # ChromaDB get by IDs
                collection = vectorstore.get_collection(manual_id)
                if collection is None:
                    continue
                res = collection.get(ids=chunk_ids, include=["documents", "metadatas"])
                if res and res.get("documents"):
                    for i, doc in enumerate(res["documents"]):
                        meta = res["metadatas"][i] if i < len(res.get("metadatas") or []) else {}
                        docs.append({
                            "text": doc,
                            "metadata": meta,
                            "node_id": meta.get("node_id"),
                        })
            except Exception:
                continue
        return docs


# Singleton
_graph_retriever_instance: Optional[GraphRetriever] = None


def get_graph_retriever() -> GraphRetriever:
    global _graph_retriever_instance
    if _graph_retriever_instance is None:
        _graph_retriever_instance = GraphRetriever()
    return _graph_retriever_instance
