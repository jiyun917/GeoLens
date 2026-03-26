"""
Hybrid RAG with LightRAG Dual-Level Retrieval:
1. Specific Retrieval — vector similarity search for exact matches
2. Neighbor Expansion — same-section adjacent chunks for broader context
3. Abstract Retrieval — graph traversal for conceptual/relational context
4. Merge — deduplicated combination of all three
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


# ═══════════════════════════════════════════════════════════
# LightRAG Dual-Level Retrieval
# ═══════════════════════════════════════════════════════════

def _specific_search(manual_ids: List[str], query: str, top_k: int = 5) -> List[Dict]:
    """
    Specific Retrieval: vector similarity search for concrete matches.
    Finds chunks most similar to the user's exact query.
    """
    if not manual_ids:
        return []

    query_embedding = get_embeddings([query])[0]
    vector_results = []

    for manual_id in manual_ids:
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
                        "source_type": "specific",
                    })
        except Exception:
            continue

    vector_results.sort(key=lambda x: x["distance"])
    top_results = vector_results[:top_k]

    print(f"[RAG] Specific search: {len(top_results)} chunks found")
    return top_results


def _expand_neighbors(manual_ids: List[str], specific_results: List[Dict]) -> List[Dict]:
    """
    Neighbor Chunk Expansion: for each specific result, fetch adjacent chunks
    from the same section (chunk_index ± 1) to provide broader context.
    """
    if not specific_results:
        return []

    neighbor_results = []
    seen_keys = set()

    # Track already-seen chunks from specific results
    for r in specific_results:
        section = r["metadata"].get("section", "")
        idx = r["metadata"].get("chunk_index", -1)
        seen_keys.add(f"{r['manual_id']}:{section}:{idx}")

    for r in specific_results:
        section = r["metadata"].get("section", "")
        chunk_index = r["metadata"].get("chunk_index", -1)
        manual_id = r["manual_id"]

        if not section or chunk_index < 0:
            continue

        # Fetch previous and next chunk in same section
        neighbor_indices = []
        if chunk_index > 0:
            neighbor_indices.append(chunk_index - 1)
        neighbor_indices.append(chunk_index + 1)

        try:
            results = vectorstore.search_by_section(manual_id, section, neighbor_indices)
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    meta = results["metadatas"][i] if i < len(results["metadatas"]) else {}
                    n_idx = meta.get("chunk_index", -1)
                    key = f"{manual_id}:{section}:{n_idx}"

                    if key not in seen_keys:
                        seen_keys.add(key)
                        neighbor_results.append({
                            "text": doc,
                            "distance": 999,  # No distance for neighbors
                            "metadata": meta,
                            "manual_id": manual_id,
                            "source_type": "neighbor",
                        })
        except Exception:
            continue

    print(f"[RAG] Neighbor expansion: {len(neighbor_results)} additional chunks")
    return neighbor_results


def _abstract_search(manual_ids: List[str], query: str, specific_results: List[Dict] = None) -> List[Dict]:
    """
    Abstract Retrieval: graph-based conceptual search.
    Finds related entities and relationships for deeper understanding.
    """
    entities = _extract_entities_from_query(query)

    # Also extract entities from top specific results for richer graph traversal
    if specific_results:
        for vr in specific_results[:3]:
            chunk_entities = _extract_entities_from_query(vr["text"][:500])
            entities.extend(chunk_entities)

    # Deduplicate
    seen = set()
    unique_entities = []
    for e in entities:
        el = e.lower()
        if el not in seen:
            seen.add(el)
            unique_entities.append(e)

    print(f"[RAG] Extracted entities: {unique_entities[:15]}")

    try:
        unique_triplets = graphstore.query_subgraph_with_base(manual_ids, unique_entities, max_hops=2)
    except Exception as e:
        print(f"[RAG] Graph search error: {e}")
        unique_triplets = []

    print(f"[RAG] Graph triplets found: {len(unique_triplets)}")
    for t in unique_triplets[:5]:
        print(f"  {t['subject']} --[{t['relation']}]--> {t['object']}")

    return unique_triplets


def _merge_contexts(
    specific_results: List[Dict],
    neighbor_results: List[Dict],
    graph_triplets: List[Dict],
) -> Optional[str]:
    """
    Merge all retrieval results into a single context string.
    Deduplicates by text content. Orders: graph context first, then specific, then neighbors.
    """
    context_parts = []

    # 1. Graph context (abstract/relational)
    graph_context = _format_graph_context(graph_triplets)
    if graph_context:
        context_parts.append(
            f"[Knowledge Graph - Related Entities & Relationships]\n{graph_context}"
        )

    # 2. Specific + Neighbor chunks (deduplicated by text)
    seen_texts = set()
    all_chunks = []

    # Specific results first (higher relevance)
    for r in specific_results:
        text_key = r["text"][:200]  # Use first 200 chars as dedup key
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            all_chunks.append(r)

    # Then neighbor results
    for r in neighbor_results:
        text_key = r["text"][:200]
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            all_chunks.append(r)

    # Sort: specific first, neighbors after, by chunk_index within same section
    for r in all_chunks:
        source = r["metadata"].get("source", "unknown")
        section = r["metadata"].get("section", "")
        tag = f"[Source: {source}]"
        if section:
            tag = f"[Source: {source}, Section: {section}]"
        if r["source_type"] == "neighbor":
            tag += " (adjacent context)"
        context_parts.append(f"{tag}\n{r['text']}")

    if not context_parts:
        return None

    return "\n\n---\n\n".join(context_parts)


# ═══════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════

def get_manual_context(manual_ids: List[str], query: str, top_k: int = 5) -> Optional[str]:
    """
    LightRAG Dual-Level Retrieval:
    1. Specific search: vector similarity for exact matches
    2. Neighbor expansion: same-section adjacent chunks
    3. Abstract search: graph traversal for conceptual context
    4. Merge: deduplicated combination
    """
    ids = manual_ids or []

    print(f"[RAG] Query: {query[:100]}")

    # 1. Specific Retrieval
    specific_results = _specific_search(ids, query, top_k)

    # 2. Neighbor Expansion
    neighbor_results = _expand_neighbors(ids, specific_results)

    # 3. Abstract Retrieval (graph search — always runs, includes base graph)
    graph_triplets = _abstract_search(ids, query, specific_results)

    # 4. Merge all contexts
    return _merge_contexts(specific_results, neighbor_results, graph_triplets)
