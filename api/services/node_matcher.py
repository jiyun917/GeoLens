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


def _lst(vs: Dict, key: str) -> List[str]:
    v = vs.get(key) or []
    if isinstance(v, str):
        v = [v]
    return [str(x) for x in v if str(x).strip()]


def visual_state_text(visual_state: Dict) -> str:
    """Text rendering of the vision output used for embedding similarity.
    v3 vision output adds verbatim window_titles / menu_items / buttons /
    labels; they are included when present."""
    vs = visual_state or {}
    lines = [f"Dialog: {vs.get('current_dialog') or ''}"]
    if _lst(vs, "window_titles"):
        lines.append("Windows: " + ", ".join(_lst(vs, "window_titles")))
    lines.append(f"Menu: {vs.get('active_menu') or ''}")
    if _lst(vs, "menu_items"):
        lines.append("Menu items: " + ", ".join(_lst(vs, "menu_items")))
    if _lst(vs, "buttons"):
        lines.append("Buttons: " + ", ".join(_lst(vs, "buttons")))
    if _lst(vs, "labels"):
        lines.append("Labels: " + ", ".join(_lst(vs, "labels")))
    if _lst(vs, "field_values"):
        lines.append("Field values: " + ", ".join(_lst(vs, "field_values")))
    lines.append("Elements: " + ", ".join(_lst(vs, "visible_elements")))
    lines.append(f"Data: {vs.get('data_state') or ''}")
    lines.append(f"Action: {vs.get('current_action') or ''}")
    return "\n".join(lines)


def flatten_visual_state(visual_state: Dict) -> str:
    """Lower-cased flat string of every vision field (substring scorer)."""
    vs = visual_state or {}
    parts = [str(vs.get("current_dialog") or ""), str(vs.get("active_menu") or ""),
             str(vs.get("data_state") or ""), str(vs.get("current_action") or "")]
    for k in ("window_titles", "menu_items", "buttons", "labels", "field_values", "visible_elements"):
        parts += _lst(vs, k)
    return " ".join(parts).lower()


_WF_EMB: Dict[str, List[float]] = {}
_WF_TEXT: Dict[str, str] = {}
_GOAL_EMB: Dict[str, List[float]] = {}


def workflow_text(workflow: Dict, nodes: List[Dict]) -> str:
    """Workflow rendering for the two-stage router: name + description + node titles."""
    titles = [str(n.get("title") or "") for n in sorted(nodes, key=lambda n: n.get("step_number", 0))]
    return "\n".join([f"Workflow: {workflow.get('name') or workflow.get('workflow_id')}",
                      f"Description: {workflow.get('description') or ''}",
                      "Steps: " + " / ".join(t for t in titles if t)])


def workflow_scores(user_goal: str, workflows: List[Dict], nodes: List[Dict]) -> List[Tuple[str, float]]:
    """[(workflow_id, cosine(goal, workflow text))] sorted desc (v3 two-stage routing, stage i)."""
    from .embedder import get_embeddings
    goal = (user_goal or "").strip()
    if not goal or not workflows:
        return []
    by_wf: Dict[str, List[Dict]] = {}
    for n in nodes:
        by_wf.setdefault(n.get("workflow_id"), []).append(n)
    missing = []
    for wf in workflows:
        wid = wf.get("workflow_id")
        t = workflow_text(wf, by_wf.get(wid, []))
        if wid and (wid not in _WF_EMB or _WF_TEXT.get(wid) != t):
            missing.append((wid, t))
    if missing:
        for (wid, t), e in zip(missing, get_embeddings([t for _, t in missing])):
            _WF_EMB[wid] = e
            _WF_TEXT[wid] = t
    if goal not in _GOAL_EMB:
        _GOAL_EMB[goal] = get_embeddings([goal])[0]
    g = _GOAL_EMB[goal]
    out = [(wf["workflow_id"], _dot(g, _WF_EMB[wf["workflow_id"]])) for wf in workflows if wf.get("workflow_id") in _WF_EMB]
    out.sort(key=lambda p: p[1], reverse=True)
    return out


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
