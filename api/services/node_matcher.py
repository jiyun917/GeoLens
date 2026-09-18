"""Semantic candidate matcher for workflow-node localization (v3).

v2 scored a node by the fraction of its visual_signature strings
(screenshot_keywords, expected_ui_elements, expected_dialog) that occur
verbatim, as substrings, in the flattened vision output. Routing
diagnosis on the development set (2026-09-18, data/eval/results/
routing_diag_dev_v2.md) showed that every attribute_computation failure
happened at this candidate stage: the expected workflow never entered the
keyword top-3 because its signature phrases are descriptive sentences
("about to choose an Attribute Type", "Input Data = 4 Dip steered median
filter") that a vision model does not emit verbatim, while workflows with
short generic tokens ("Survey", "Add", "Elements") always scored higher.

This module replaces the substring score with cosine similarity between
the vision output and a textual rendering of each node (title,
description, expected dialog, UI elements, keywords) under the same
embedder the retrieval index uses (EMBED_MODEL, bge-m3 by default). No
signature text is modified; only the matching function changes, and it
applies identically to every workflow in the pool.

Select with ROUTER_MATCHER=embedding (v3 default) or ROUTER_MATCHER=substring
(v2 behaviour).
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

_NODE_EMB: Dict[str, List[float]] = {}   # node id -> embedding (per node text hash)
_NODE_TEXT: Dict[str, str] = {}


def matcher_kind() -> str:
    return os.environ.get("ROUTER_MATCHER", "embedding").strip().lower()


def node_text(node: Dict) -> str:
    sig = node.get("visual_signature") or {}
    parts = [
        f"Step: {node.get('title') or ''}",
        f"Description: {node.get('description') or ''}",
    ]
    if sig.get("expected_dialog"):
        parts.append(f"Dialog: {sig['expected_dialog']}")
    ui = [str(e).replace("_", " ") for e in (sig.get("expected_ui_elements") or [])]
    if ui:
        parts.append("Elements: " + ", ".join(ui))
    kws = [str(k) for k in (sig.get("screenshot_keywords") or [])]
    if kws:
        parts.append("Keywords: " + ", ".join(kws))
    return "\n".join(parts)


def visual_state_text(visual_state: Dict) -> str:
    vs = visual_state or {}
    elems = vs.get("visible_elements") or []
    return "\n".join([
        f"Dialog: {vs.get('current_dialog') or ''}",
        f"Menu: {vs.get('active_menu') or ''}",
        "Elements: " + ", ".join(str(e) for e in elems),
        f"Data: {vs.get('data_state') or ''}",
        f"Action: {vs.get('current_action') or ''}",
    ])


def _ensure_node_embeddings(nodes: List[Dict]) -> None:
    from .embedder import get_embeddings
    missing = []
    for n in nodes:
        nid = n.get("id")
        t = node_text(n)
        if nid and (nid not in _NODE_EMB or _NODE_TEXT.get(nid) != t):
            missing.append((nid, t))
    if missing:
        embs = get_embeddings([t for _, t in missing])
        for (nid, t), e in zip(missing, embs):
            _NODE_EMB[nid] = e
            _NODE_TEXT[nid] = t


def _dot(a: List[float], b: List[float]) -> float:
    return float(sum(x * y for x, y in zip(a, b)))


def score_nodes(visual_state: Dict, nodes: List[Dict],
                hint_workflow_id: Optional[str] = None) -> List[Tuple[Dict, float]]:
    """Return [(node, cosine)] for every node (filtered by hint), unsorted."""
    from .embedder import get_embeddings
    if not visual_state or not nodes:
        return []
    cand = [n for n in nodes if not hint_workflow_id or n.get("workflow_id") == hint_workflow_id]
    _ensure_node_embeddings(cand)
    q = get_embeddings([visual_state_text(visual_state)])[0]
    return [(dict(n), _dot(q, _NODE_EMB[n["id"]])) for n in cand if n.get("id") in _NODE_EMB]


def top_k(visual_state: Dict, nodes: List[Dict], k: int = 3,
          hint_workflow_id: Optional[str] = None) -> List[Tuple[Dict, float]]:
    scored = score_nodes(visual_state, nodes, hint_workflow_id)
    scored.sort(key=lambda p: p[1], reverse=True)
    return scored[:k]
