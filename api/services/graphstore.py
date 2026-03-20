"""
Graph store for Graph RAG.
Stores knowledge graphs per manual using NetworkX + JSON persistence.
Each node is a geological/geophysical entity, each edge is a relationship.
"""

import json
import os
from typing import Dict, List, Optional, Tuple

import networkx as nx

GRAPH_DIR = os.environ.get(
    "GRAPH_DATA_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "graphs"),
)


def _graph_path(manual_id: str) -> str:
    os.makedirs(GRAPH_DIR, exist_ok=True)
    return os.path.join(GRAPH_DIR, f"graph_{manual_id}.json")


def load_graph(manual_id: str) -> nx.DiGraph:
    """Load a manual's knowledge graph from JSON."""
    path = _graph_path(manual_id)
    if not os.path.exists(path):
        return nx.DiGraph()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    for node in data.get("nodes", []):
        G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for edge in data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], **{k: v for k, v in edge.items() if k not in ("source", "target")})
    return G


def save_graph(manual_id: str, G: nx.DiGraph):
    """Save a knowledge graph to JSON."""
    nodes = []
    for node_id, attrs in G.nodes(data=True):
        nodes.append({"id": node_id, **attrs})

    edges = []
    for src, tgt, attrs in G.edges(data=True):
        edges.append({"source": src, "target": tgt, **attrs})

    data = {"nodes": nodes, "edges": edges}

    path = _graph_path(manual_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_graph(manual_id: str):
    """Delete a manual's graph file."""
    path = _graph_path(manual_id)
    if os.path.exists(path):
        os.remove(path)


def add_triplets(manual_id: str, triplets: List[Tuple[str, str, str]], chunk_source: str = ""):
    """
    Add (subject, relation, object) triplets to a manual's graph.
    Nodes get type/description attributes; edges get relation labels.
    """
    G = load_graph(manual_id)

    for subj, rel, obj in triplets:
        subj_norm = subj.strip().lower()
        obj_norm = obj.strip().lower()

        if not subj_norm or not obj_norm or not rel.strip():
            continue

        # Add or update nodes
        if not G.has_node(subj_norm):
            G.add_node(subj_norm, label=subj.strip(), mentions=1, sources=[chunk_source])
        else:
            G.nodes[subj_norm]["mentions"] = G.nodes[subj_norm].get("mentions", 0) + 1
            sources = G.nodes[subj_norm].get("sources", [])
            if chunk_source and chunk_source not in sources:
                sources.append(chunk_source)
                G.nodes[subj_norm]["sources"] = sources

        if not G.has_node(obj_norm):
            G.add_node(obj_norm, label=obj.strip(), mentions=1, sources=[chunk_source])
        else:
            G.nodes[obj_norm]["mentions"] = G.nodes[obj_norm].get("mentions", 0) + 1
            sources = G.nodes[obj_norm].get("sources", [])
            if chunk_source and chunk_source not in sources:
                sources.append(chunk_source)
                G.nodes[obj_norm]["sources"] = sources

        # Add edge (allow multiple relationships via key)
        rel_norm = rel.strip()
        if G.has_edge(subj_norm, obj_norm):
            existing_rel = G.edges[subj_norm, obj_norm].get("relation", "")
            if rel_norm not in existing_rel:
                G.edges[subj_norm, obj_norm]["relation"] = f"{existing_rel}; {rel_norm}"
            G.edges[subj_norm, obj_norm]["weight"] = G.edges[subj_norm, obj_norm].get("weight", 1) + 1
        else:
            G.add_edge(subj_norm, obj_norm, relation=rel_norm, weight=1, source=chunk_source)

    save_graph(manual_id, G)
    return G


def query_subgraph(manual_id: str, entities: List[str], max_hops: int = 2) -> List[Dict]:
    """
    Given seed entities, traverse the graph up to max_hops and return
    relevant triplets as context.
    """
    G = load_graph(manual_id)
    if G.number_of_nodes() == 0:
        return []

    # Normalize and match entities to graph nodes
    seed_nodes = set()
    for entity in entities:
        ent_lower = entity.strip().lower()
        # Exact match
        if G.has_node(ent_lower):
            seed_nodes.add(ent_lower)
            continue
        # Partial match
        for node in G.nodes():
            if ent_lower in node or node in ent_lower:
                seed_nodes.add(node)

    if not seed_nodes:
        return []

    # BFS traversal up to max_hops
    visited = set()
    frontier = seed_nodes.copy()
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            if node in visited:
                continue
            visited.add(node)
            # Outgoing edges
            for _, neighbor, data in G.edges(node, data=True):
                next_frontier.add(neighbor)
            # Incoming edges
            for predecessor, _, data in G.in_edges(node, data=True):
                next_frontier.add(predecessor)
        frontier = next_frontier - visited

    visited.update(frontier)

    # Collect triplets from the subgraph
    triplets = []
    for src, tgt, data in G.edges(data=True):
        if src in visited or tgt in visited:
            src_label = G.nodes[src].get("label", src)
            tgt_label = G.nodes[tgt].get("label", tgt)
            relation = data.get("relation", "related_to")
            triplets.append({
                "subject": src_label,
                "relation": relation,
                "object": tgt_label,
                "weight": data.get("weight", 1),
            })

    # Sort by relevance (weight)
    triplets.sort(key=lambda x: x["weight"], reverse=True)
    return triplets


BASE_GRAPH_PATH = os.path.join(GRAPH_DIR, "base_geoscience.json")

_base_graph_cache: Optional[nx.DiGraph] = None


def load_base_graph() -> nx.DiGraph:
    """Load the pre-built geoscience knowledge graph (cached)."""
    global _base_graph_cache
    if _base_graph_cache is not None:
        return _base_graph_cache

    if not os.path.exists(BASE_GRAPH_PATH):
        _base_graph_cache = nx.DiGraph()
        return _base_graph_cache

    with open(BASE_GRAPH_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    for node in data.get("nodes", []):
        G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for edge in data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], **{k: v for k, v in edge.items() if k not in ("source", "target")})

    _base_graph_cache = G
    return _base_graph_cache


def query_subgraph_with_base(manual_ids: List[str], entities: List[str], max_hops: int = 2) -> List[Dict]:
    """
    Query both the base geoscience graph and manual-specific graphs.
    Returns combined, deduplicated triplets sorted by weight.
    """
    all_triplets = []

    # 1. Base geoscience graph (always queried)
    base_G = load_base_graph()
    if base_G.number_of_nodes() > 0:
        base_triplets = _query_graph(base_G, entities, max_hops)
        for t in base_triplets:
            t["source_type"] = "base_knowledge"
        all_triplets.extend(base_triplets)

    # 2. Manual-specific graphs
    for manual_id in manual_ids:
        G = load_graph(manual_id)
        if G.number_of_nodes() > 0:
            manual_triplets = _query_graph(G, entities, max_hops)
            for t in manual_triplets:
                t["source_type"] = "manual"
            all_triplets.extend(manual_triplets)

    # Deduplicate
    seen = set()
    unique = []
    for t in sorted(all_triplets, key=lambda x: x["weight"], reverse=True):
        key = (t["subject"].lower(), t["relation"].lower(), t["object"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(t)

    # (1) Filter: base_knowledge always passes, manual triplets need weight >= 2
    filtered = [t for t in unique if t.get("source_type") == "base_knowledge" or t.get("weight", 1) >= 2]

    # (2) Contradiction detection: remove conflicting triplets for the same (subject, relation_type)
    CONTRADICTION_RELATIONS = {"type_of", "has_lithology", "has_age", "interpreted_as", "formed_by"}
    subject_rel_map: Dict[tuple, list] = {}
    for t in filtered:
        rel_base = t["relation"].split(";")[0].strip().lower()
        if rel_base in CONTRADICTION_RELATIONS:
            key = (t["subject"].lower(), rel_base)
            subject_rel_map.setdefault(key, []).append(t)

    contradicted = set()
    for key, triplets_group in subject_rel_map.items():
        if len(triplets_group) > 1:
            objects = set(t["object"].lower() for t in triplets_group)
            if len(objects) > 1:
                # Multiple different values for the same (subject, relation) — keep highest weight only
                triplets_group.sort(key=lambda x: x.get("weight", 1), reverse=True)
                for t in triplets_group[1:]:
                    contradicted.add((t["subject"].lower(), t["relation"].lower(), t["object"].lower()))

    # (3) Remove contradicted triplets + deduplicate by normalized key
    final_seen = set()
    final = []
    for t in filtered:
        norm_key = (t["subject"].lower(), t["relation"].lower(), t["object"].lower())
        if norm_key in contradicted:
            continue
        if norm_key in final_seen:
            continue
        final_seen.add(norm_key)
        final.append(t)

    return final


def _query_graph(G: nx.DiGraph, entities: List[str], max_hops: int = 2) -> List[Dict]:
    """Traverse a graph from seed entities and return triplets."""
    seed_nodes = set()
    for entity in entities:
        ent_lower = entity.strip().lower()
        if G.has_node(ent_lower):
            seed_nodes.add(ent_lower)
            continue
        for node in G.nodes():
            if ent_lower in node or node in ent_lower:
                seed_nodes.add(node)

    if not seed_nodes:
        return []

    visited = set()
    frontier = seed_nodes.copy()
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            if node in visited:
                continue
            visited.add(node)
            for _, neighbor in G.edges(node):
                next_frontier.add(neighbor)
            for predecessor, _ in G.in_edges(node):
                next_frontier.add(predecessor)
        frontier = next_frontier - visited

    visited.update(frontier)

    triplets = []
    for src, tgt, data in G.edges(data=True):
        if src in visited or tgt in visited:
            src_label = G.nodes[src].get("label", src)
            tgt_label = G.nodes[tgt].get("label", tgt)
            relation = data.get("relation", "related_to")
            triplets.append({
                "subject": src_label,
                "relation": relation,
                "object": tgt_label,
                "weight": data.get("weight", 1),
            })

    return triplets


def get_graph_stats(manual_id: str) -> Dict:
    """Get basic stats about a manual's knowledge graph."""
    G = load_graph(manual_id)
    base_G = load_base_graph()
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "base_nodes": base_G.number_of_nodes(),
        "base_edges": base_G.number_of_edges(),
    }
