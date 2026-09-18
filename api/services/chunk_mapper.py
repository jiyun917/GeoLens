"""
Chunk Mapper: auto-populate workflow node linked_chunks by semantic similarity.
Matches each workflow node's title+description against ChromaDB chunks and
records the top-k chunk IDs into the workflow JSON file.
"""

import json
import os
import glob
from typing import Dict, List, Optional

from . import vectorstore
from .embedder import get_embeddings
from .workflow_graph import WORKFLOW_DIR


def _collect_chunk_candidates(manual_id: str) -> List[Dict]:
    """Fetch (id, text, metadata) for every chunk in a manual collection."""
    try:
        collection = vectorstore.get_collection(manual_id)
        if collection is None:
            return []
        res = collection.get(include=["documents", "metadatas"])
        if not res or not res.get("ids"):
            return []
        out = []
        for i, cid in enumerate(res["ids"]):
            out.append({
                "id": cid,
                "text": res["documents"][i] if i < len(res["documents"]) else "",
                "metadata": res["metadatas"][i] if i < len(res["metadatas"]) else {},
            })
        return out
    except Exception as e:
        print(f"[ChunkMapper] Failed to fetch chunks for {manual_id}: {e}")
        return []


def _section_candidates(manual_id: str, query_emb: List[float], prefixes: List[str], top_k: int) -> List[tuple]:
    """(chunk_id, distance) for chunks whose section starts with one of the
    prefixes, ranked by embedding distance (v3 section provenance)."""
    try:
        collection = vectorstore.get_collection(manual_id)
        if collection is None:
            return []
        res = collection.get(include=["metadatas", "embeddings"])
    except Exception as e:
        print(f"[ChunkMapper] section fetch failed for {manual_id}: {e}")
        return []
    out = []
    ids = res.get("ids") or []
    metas = res.get("metadatas") or []
    embs = res.get("embeddings")
    if embs is None:
        return []
    for i, cid in enumerate(ids):
        sec = str((metas[i] or {}).get("section", "")) if i < len(metas) else ""
        if not any(sec.startswith(p) for p in prefixes):
            continue
        e = list(embs[i])
        # squared L2 on normalized vectors (= chroma's default distance)
        dist = float(sum((a - b) ** 2 for a, b in zip(query_emb, e)))
        out.append((cid, dist))
    out.sort(key=lambda x: x[1])
    return out[:top_k]


def map_node_to_chunks(
    node: Dict,
    manual_ids: List[str],
    top_k: int = 3,
    max_distance: float = 1.5,
) -> List[str]:
    """
    Use vector similarity to find the top-k chunks best matching this node.
    max_distance: upper bound on cosine/L2 distance (larger = more permissive).
    Returns list of chunk IDs (always up to top_k, even if matches are weak —
    weak matches still provide some context for rare workflow steps).

    v3 — section provenance: when the node carries ``manual_sections`` (a list
    of section-number prefixes the node was authored from, e.g. ["1.3.1a"]),
    candidates are restricted to chunks of those sections (ranked by the same
    embedding distance) and the global top-k only fills remaining slots. The
    auto-generated workflows carry their source chunks by construction; this
    gives hand-authored workflows the same manual provenance.
    """
    title = node.get("title") or ""
    description = node.get("description") or ""
    keywords = " ".join((node.get("visual_signature", {}) or {}).get("screenshot_keywords", []) or [])
    workflow_label = (node.get("workflow_id") or "").replace("_", " ")

    query = f"{workflow_label} {title} {description} {keywords}".strip()
    if not query:
        return []

    try:
        query_emb = get_embeddings([query])[0]
    except Exception as e:
        print(f"[ChunkMapper] Embedding failed: {e}")
        return []

    best_chunks: List[tuple] = []  # (chunk_id, distance)
    prefixes = [str(p) for p in (node.get("manual_sections") or []) if str(p).strip()]
    if prefixes:
        for mid in manual_ids:
            for cid, dist in _section_candidates(mid, query_emb, prefixes, top_k):
                best_chunks.append((cid, -1.0 + dist * 1e-6))   # section chunks rank first, in distance order
    for mid in manual_ids:
        try:
            res = vectorstore.search(mid, query_emb, top_k=top_k)
            if not res or not res.get("ids"):
                continue
            ids = res["ids"][0] if isinstance(res["ids"][0], list) else res["ids"]
            dists = res.get("distances", [[]])[0] if res.get("distances") else []
            for i, cid in enumerate(ids):
                dist = dists[i] if i < len(dists) else 999
                best_chunks.append((cid, dist))
        except Exception as e:
            print(f"[ChunkMapper] Search failed for {mid}: {e}")
            continue

    best_chunks.sort(key=lambda x: x[1])
    # Permissive: take top_k regardless of threshold, since weak matches still help
    # Only filter out genuinely irrelevant ones (very high distance)
    selected_ids = []
    seen = set()
    for cid, dist in best_chunks:
        if len(selected_ids) >= top_k:
            break
        if cid in seen or dist > max_distance:
            continue
        seen.add(cid)
        selected_ids.append(cid)
    return selected_ids


def map_workflow_file(
    workflow_path: str,
    manual_ids: List[str],
    top_k: int = 3,
) -> Dict:
    """
    Process a single workflow JSON file: populate linked_chunks for each node.
    Returns stats.
    """
    try:
        with open(workflow_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load {workflow_path}: {e}"}

    mapped = 0
    total = len(data.get("nodes", []))
    for node in data.get("nodes", []):
        chunk_ids = map_node_to_chunks(node, manual_ids, top_k=top_k)
        node["linked_chunks"] = chunk_ids
        if chunk_ids:
            mapped += 1

    try:
        with open(workflow_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {"error": f"Failed to save {workflow_path}: {e}"}

    return {
        "workflow_id": data.get("workflow_id"),
        "file": os.path.basename(workflow_path),
        "total_nodes": total,
        "mapped_nodes": mapped,
    }


def map_all_workflows(
    manual_ids: List[str],
    workflow_dir: Optional[str] = None,
    top_k: int = 3,
) -> List[Dict]:
    """Map all workflow JSON files in the directory."""
    workflow_dir = workflow_dir or WORKFLOW_DIR
    results = []
    for path in glob.glob(os.path.join(workflow_dir, "*.json")):
        result = map_workflow_file(path, manual_ids, top_k=top_k)
        results.append(result)
        print(
            f"[ChunkMapper] {result.get('file')}: "
            f"{result.get('mapped_nodes', 0)}/{result.get('total_nodes', 0)} nodes mapped"
        )
    return results
