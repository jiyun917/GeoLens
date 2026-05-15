"""
Procedural State-Path Retrieval (PSPR) — the paper's novel contribution.

Traditional RAG returns an unordered top-K chunk bag. PSPR instead walks the
auto-generated workflow DAG starting from the user's *currently localized*
node and returns a **structured procedural sub-path**:

    StepPath = {
       prev:    Optional[StepCard]    # the step just completed (from visited)
       current: StepCard              # the anchor node (where the user is now)
       next:    List[StepCard]        # 1..N successor steps
       siblings:List[StepCard]        # workflow-internal branches
       trace:   List[str]             # linearized [prev → current → next]
    }

    StepCard = {
       node:    workflow node dict
       chunks:  List[Dict]            # the linked_chunks contents
       role:    "prev" | "current" | "next" | "sibling"
       confidence: float              # only meaningful for `current`
    }

The downstream context-block formatter emits:

    [██ PROCEDURAL PATH (state-aware) ██]
    Just completed: Step 3 — Enter survey root path
    You are at:     Step 4 — Click OK in Survey Setup dialog   ← current
    Coming next:    Step 5 — Click Yes to confirm
                    Step 6 — Click OK on Survey Information

    [Step 4 manual text]
    ...
    [Step 5 manual text]
    ...

The Claude generator now has explicit temporal grounding instead of having
to *infer* "where the user is in the procedure" from an unordered chunk bag.

Compared to existing retrieval modes:

  - vanilla_vector   — top-K by cosine similarity to query
  - graph_only       — anchor node + linked_chunks (no path expansion)
  - GraphRAG-style   — entity-relation sub-graph (orthogonal axis)
  - PSPR (this)      — procedural state-conditioned DAG sub-path

The state-conditioning is the key novel bit: `visited_node_ids` is used to
decide what counts as "prev" (the last visited node that's a predecessor of
the anchor), preventing the "click Next again" repetition class of bug.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ────────────────────────────────────────────────────────────────────
# Data structures
# ────────────────────────────────────────────────────────────────────

@dataclass
class StepCard:
    node: Dict
    role: str                            # "prev" | "current" | "next" | "sibling"
    chunks: List[Dict] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def id(self) -> str:
        return self.node.get("id", "")

    @property
    def title(self) -> str:
        return self.node.get("title", "")

    @property
    def description(self) -> str:
        return self.node.get("description", "")

    @property
    def step_number(self):
        return self.node.get("step_number")


@dataclass
class StepPath:
    current: Optional[StepCard]
    prev: Optional[StepCard] = None
    next: List[StepCard] = field(default_factory=list)
    siblings: List[StepCard] = field(default_factory=list)

    @property
    def trace(self) -> List[str]:
        out: List[str] = []
        if self.prev:
            out.append(f"[prev] {self.prev.title}")
        if self.current:
            out.append(f"[current] {self.current.title}")
        for n in self.next:
            out.append(f"[next] {n.title}")
        return out


# ────────────────────────────────────────────────────────────────────
# Retriever
# ────────────────────────────────────────────────────────────────────

class StatePathRetriever:
    """Expand a procedural sub-path around the anchor node, conditioned on
    visited history. Pure DAG walk + chunk materialization — no LLM calls."""

    def __init__(self, workflow_graph, next_horizon: int = 2,
                 chunks_per_step: int = 3, max_siblings: int = 2):
        self.graph = workflow_graph
        self.next_horizon = next_horizon
        self.chunks_per_step = chunks_per_step
        self.max_siblings = max_siblings

    def retrieve(self, anchor_node_id: Optional[str], manual_id: str,
                 visited_node_ids: Optional[List[str]] = None,
                 confidence: float = 0.0) -> StepPath:
        if not anchor_node_id:
            return StepPath(current=None)
        anchor = self.graph.get_node(anchor_node_id)
        if not anchor:
            return StepPath(current=None)

        visited = list(visited_node_ids or [])

        current = StepCard(node=anchor, role="current", confidence=confidence)
        current.chunks = self._fetch_chunks_for_node(anchor, manual_id)

        # PREV — pick the most recently visited node that is a predecessor of
        # the anchor (within the same workflow). Falls back to most-recent
        # visited node if no graph predecessor matches.
        prev_card = self._find_prev(anchor, visited, manual_id)

        # NEXT — successors in the DAG, ordered by step_number, taking up to
        # next_horizon. Skip ones in visited (those are already done).
        next_cards = self._find_next(anchor, visited, manual_id)

        # SIBLINGS — other nodes in the same workflow neither prev nor next,
        # useful when the user might have branched.
        siblings = self._find_siblings(anchor, visited, prev_card, next_cards, manual_id)

        return StepPath(
            current=current,
            prev=prev_card,
            next=next_cards,
            siblings=siblings,
        )

    # ────────────────────────────────────────────────────────────────

    def _find_prev(self, anchor: Dict, visited: List[str], manual_id: str) -> Optional[StepCard]:
        anchor_id = anchor.get("id")
        wf_id = anchor.get("workflow_id")
        # Try most-recent visited that is a graph predecessor of anchor in same workflow
        for vid in reversed(visited):
            if vid == anchor_id:
                continue
            vnode = self.graph.get_node(vid)
            if not vnode or vnode.get("workflow_id") != wf_id:
                continue
            # Predecessor check: vnode.step_number < anchor.step_number, and an
            # in-edge exists from vnode (loose check via successor relation)
            if (vnode.get("step_number") or 0) < (anchor.get("step_number") or 0):
                card = StepCard(node=vnode, role="prev")
                card.chunks = self._fetch_chunks_for_node(vnode, manual_id)
                return card
        return None

    def _find_next(self, anchor: Dict, visited: List[str], manual_id: str) -> List[StepCard]:
        # Use the WorkflowGraph successor API
        successors = self.graph.get_next_steps(anchor.get("id"))
        out: List[StepCard] = []
        for nxt in successors:
            if nxt.get("id") in visited:
                continue
            card = StepCard(node=nxt, role="next")
            card.chunks = self._fetch_chunks_for_node(nxt, manual_id)
            out.append(card)
            if len(out) >= self.next_horizon:
                break

        # If get_next_steps returned nothing (e.g. anchor is terminal), also
        # try same-workflow nodes with step_number > anchor.step_number as
        # fallback.
        if not out:
            wf_id = anchor.get("workflow_id")
            anchor_step = anchor.get("step_number") or 0
            wf_nodes = sorted(
                [n for n in self.graph.get_workflow_nodes(wf_id)
                 if (n.get("step_number") or 0) > anchor_step
                 and n.get("id") not in visited],
                key=lambda n: n.get("step_number") or 0,
            )
            for nxt in wf_nodes[: self.next_horizon]:
                card = StepCard(node=nxt, role="next")
                card.chunks = self._fetch_chunks_for_node(nxt, manual_id)
                out.append(card)

        return out

    def _find_siblings(self, anchor: Dict, visited: List[str],
                       prev_card: Optional[StepCard], next_cards: List[StepCard],
                       manual_id: str) -> List[StepCard]:
        wf_id = anchor.get("workflow_id")
        excluded = {anchor.get("id"), prev_card.id if prev_card else None,
                    *[c.id for c in next_cards], *visited}
        out: List[StepCard] = []
        for n in self.graph.get_workflow_nodes(wf_id):
            if n.get("id") in excluded:
                continue
            # Take only nodes adjacent in step_number (anchor_step ±1) — likely
            # to be alternates or just-skipped branches.
            diff = abs((n.get("step_number") or 0) - (anchor.get("step_number") or 0))
            if diff <= 1:
                card = StepCard(node=n, role="sibling")
                card.chunks = self._fetch_chunks_for_node(n, manual_id, limit=1)
                out.append(card)
                if len(out) >= self.max_siblings:
                    break
        return out

    # ────────────────────────────────────────────────────────────────

    def _fetch_chunks_for_node(self, node: Dict, manual_id: str,
                               limit: Optional[int] = None) -> List[Dict]:
        ids = (node.get("linked_chunks") or [])[: (limit or self.chunks_per_step)]
        if not ids:
            return []
        try:
            from . import vectorstore
            result = vectorstore.get_chunks_by_ids(manual_id, ids)
        except Exception:
            return []
        docs = result.get("documents") or []
        metas = result.get("metadatas") or []
        out = []
        for d, m in zip(docs, metas):
            out.append({"text": d, "metadata": m})
        return out


# ────────────────────────────────────────────────────────────────────
# Context block formatter
# ────────────────────────────────────────────────────────────────────

def format_step_path(path: StepPath, max_chars_per_chunk: int = 600) -> str:
    """Render a StepPath into a system-prompt-ready context block. Designed
    to make procedural state EXPLICIT to the generator LLM."""
    if path.current is None:
        return ""

    parts: List[str] = ["[██ PROCEDURAL PATH (state-aware) ██]"]

    # Header trace
    header = []
    if path.prev:
        sn = path.prev.step_number
        header.append(f"Just completed:  Step {sn} — {path.prev.title}")
    sn_c = path.current.step_number
    conf = path.current.confidence
    header.append(f"You are at:      Step {sn_c} — {path.current.title}   "
                  f"(localization confidence: {conf:.2f})")
    for n in path.next:
        header.append(f"Coming next:     Step {n.step_number} — {n.title}")
    if path.siblings:
        for s in path.siblings:
            header.append(f"Workflow branch: Step {s.step_number} — {s.title}")
    parts.append("\n".join(header))

    # Bodies — current is most detailed, next is short, prev is one-liner
    if path.current.description:
        parts.append(f"\n[Current step description]\n{path.current.description}")

    if path.current.chunks:
        body = []
        for c in path.current.chunks:
            t = (c.get("text") or "")[:max_chars_per_chunk]
            body.append(t)
        parts.append("[Current step — manual snippets]\n" + "\n---\n".join(body))

    if path.next:
        next_lines = []
        for n in path.next:
            line = f"[next: Step {n.step_number} — {n.title}] {n.description[:200]}"
            if n.chunks:
                line += "\n  " + (n.chunks[0].get("text") or "")[: max_chars_per_chunk // 2]
            next_lines.append(line)
        parts.append("[Expected next steps]\n" + "\n".join(next_lines))

    # Trailing instruction so the LLM uses the structure
    parts.append(
        "Use this PATH to:\n"
        "  - issue the action belonging to the CURRENT step;\n"
        "  - NOT to re-issue the prev step (already done);\n"
        "  - to anticipate the next step's dialog so you can recognize a "
        "post-completion residual (current dialog still showing after action "
        "completed) and instruct dismissal instead."
    )

    return "\n\n".join(parts)


# Convenience singleton — uses the production WorkflowGraph
_singleton: Optional[StatePathRetriever] = None


def get_state_path_retriever() -> StatePathRetriever:
    global _singleton
    if _singleton is None:
        from .workflow_graph import get_workflow_graph
        _singleton = StatePathRetriever(get_workflow_graph())
    return _singleton
