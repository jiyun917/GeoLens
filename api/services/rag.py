"""
Hybrid RAG: Combines vector search (ChromaDB) + graph traversal (NetworkX).
Vector search finds relevant text chunks.
Graph search finds related entities and relationships for deeper context.
"""

import os
import re
from typing import Dict, List, Optional

from .embedder import get_embeddings
from . import vectorstore
from . import graphstore


def _extract_entities_from_query(query: str) -> List[str]:
    """
    Extract potential entity names from the user query.
    Uses simple heuristics: capitalized words, quoted terms, geological terms.
    """
    entities = []

    # Quoted terms
    quoted = re.findall(r'["\']([^"\']+)["\']', query)
    entities.extend(quoted)

    # Capitalized phrases (likely proper nouns: basin names, formation names)
    cap_phrases = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', query)
    entities.extend(cap_phrases)

    # Korean geological terms
    ko_terms = re.findall(r'[가-힣]{2,}', query)
    entities.extend(ko_terms)

    # Common geological English terms in query
    geo_terms = re.findall(
        r'\b(?:fault|graben|rift|basin|fold|anticline|syncline|formation|'
        r'seismic|well|log|horizon|unconformity|thrust|normal fault|'
        r'reverse fault|strike.slip|sediment|reservoir|trap|seal|'
        r'GPR|gravity|magnetic|resistivity)\b',
        query, re.IGNORECASE
    )
    entities.extend(geo_terms)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for e in entities:
        e_lower = e.strip().lower()
        if e_lower and e_lower not in seen:
            seen.add(e_lower)
            unique.append(e.strip())
    return unique


def _format_graph_context(triplets: List[Dict]) -> str:
    """Format graph triplets into a readable context block."""
    if not triplets:
        return ""

    lines = []
    for t in triplets[:20]:  # Limit to top 20 triplets
        lines.append(f"  {t['subject']} --[{t['relation']}]--> {t['object']}")

    return "\n".join(lines)


def get_manual_context(manual_ids: List[str], query: str, top_k: int = 5) -> Optional[str]:
    """
    Hybrid RAG: vector search + graph traversal.
    1. Vector search: find relevant text chunks (if manuals exist)
    2. Graph search: base geoscience graph (always) + manual graphs
    3. Combine both into enriched context
    """
    ids = manual_ids or []

    # === 1. Vector Search ===
    top_vector = []
    if ids:
        query_embedding = get_embeddings([query])[0]
        vector_results = []
        for manual_id in ids:
            try:
                results = vectorstore.search(manual_id, query_embedding, top_k=top_k)
                if results and results["documents"] and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        distance = results["distances"][0][i] if results.get("distances") else 999
                        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                        vector_results.append({
                            "text": doc,
                            "distance": distance,
                            "metadata": metadata,
                            "manual_id": manual_id,
                        })
            except Exception:
                continue

        vector_results.sort(key=lambda x: x["distance"])
        top_vector = vector_results[:top_k]

    # === 2. Graph Search (always runs - includes base graph) ===
    entities = _extract_entities_from_query(query)

    for vr in top_vector[:3]:
        chunk_entities = _extract_entities_from_query(vr["text"][:500])
        entities.extend(chunk_entities)

    seen = set()
    unique_entities = []
    for e in entities:
        el = e.lower()
        if el not in seen:
            seen.add(el)
            unique_entities.append(e)

    print(f"[RAG] Extracted entities: {unique_entities[:15]}")

    try:
        unique_triplets = graphstore.query_subgraph_with_base(ids, unique_entities, max_hops=2)
    except Exception as e:
        print(f"[RAG] Graph search error: {e}")
        unique_triplets = []

    print(f"[RAG] Graph triplets found: {len(unique_triplets)}")
    for t in unique_triplets[:5]:
        print(f"  {t['subject']} --[{t['relation']}]--> {t['object']}")

    # === 3. Combine Context ===
    context_parts = []

    graph_context = _format_graph_context(unique_triplets)
    if graph_context:
        context_parts.append(
            f"[Knowledge Graph - Related Entities & Relationships]\n{graph_context}"
        )

    for r in top_vector:
        source = r["metadata"].get("source", "unknown")
        context_parts.append(f"[Source: {source}]\n{r['text']}")

    if not context_parts:
        return None

    return "\n\n---\n\n".join(context_parts)
