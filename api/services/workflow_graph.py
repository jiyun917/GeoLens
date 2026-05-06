"""
Workflow Graph: Directed Acyclic Graph (DAG) of software workflow steps.
Used by guide mode to locate current step and find next steps,
and by report mode to backtrack completed steps.
"""

import json
import os
import glob
from typing import Dict, List, Optional, Tuple

import networkx as nx

WORKFLOW_DIR = os.environ.get(
    "WORKFLOW_DATA_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "workflows"),
)


class WorkflowGraph:
    """Workflow DAG manager: loads JSON workflows and provides graph traversal."""

    def __init__(self, workflow_dir: Optional[str] = None):
        self.workflow_dir = workflow_dir or WORKFLOW_DIR
        self.graph: nx.DiGraph = nx.DiGraph()
        self.workflows: Dict[str, Dict] = {}  # workflow_id → metadata
        self.build_graph()

    # ═══════════════════════════════════════════════════════════
    # Loading
    # ═══════════════════════════════════════════════════════════

    def build_graph(self):
        """Load all workflow JSON files into a single combined DAG."""
        self.graph = nx.DiGraph()
        self.workflows = {}

        if not os.path.isdir(self.workflow_dir):
            print(f"[WorkflowGraph] Directory not found: {self.workflow_dir}")
            return

        json_files = glob.glob(os.path.join(self.workflow_dir, "*.json"))
        for path in json_files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._load_workflow(data)
            except Exception as e:
                print(f"[WorkflowGraph] Failed to load {path}: {e}")

        print(
            f"[WorkflowGraph] Loaded {len(self.workflows)} workflows, "
            f"{self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges"
        )

    def _load_workflow(self, data: Dict):
        workflow_id = data.get("workflow_id")
        if not workflow_id:
            return

        self.workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "name": data.get("name", workflow_id),
            "description": data.get("description", ""),
        }

        for node in data.get("nodes", []):
            nid = node["id"]
            self.graph.add_node(nid, **node)

        for edge in data.get("edges", []):
            src = edge.get("source")
            tgt = edge.get("target")
            if src and tgt:
                self.graph.add_edge(
                    src,
                    tgt,
                    edge_type=edge.get("edge_type", "sequential"),
                    condition=edge.get("condition"),
                    instruction=edge.get("instruction", ""),
                )

    # ═══════════════════════════════════════════════════════════
    # Node/Edge Access
    # ═══════════════════════════════════════════════════════════

    def get_node(self, node_id: str) -> Optional[Dict]:
        if node_id not in self.graph:
            return None
        return dict(self.graph.nodes[node_id])

    def get_all_nodes(self) -> List[Dict]:
        return [dict(self.graph.nodes[n]) for n in self.graph.nodes]

    def get_workflow_nodes(self, workflow_id: str) -> List[Dict]:
        """All nodes belonging to a specific workflow, ordered by step_number."""
        nodes = [
            dict(self.graph.nodes[n])
            for n in self.graph.nodes
            if self.graph.nodes[n].get("workflow_id") == workflow_id
        ]
        return sorted(nodes, key=lambda n: n.get("step_number", 0))

    def list_workflows(self) -> List[Dict]:
        return list(self.workflows.values())

    # ═══════════════════════════════════════════════════════════
    # Visual State Matching (Current Node Detection)
    # ═══════════════════════════════════════════════════════════

    def get_top_k_nodes(
        self, visual_state: Dict, k: int = 3, hint_workflow_id: Optional[str] = None
    ) -> List[Tuple[Dict, float]]:
        """Return top-k (node, score) matches by visual_signature keyword overlap."""
        vs_text = " ".join(
            [
                str(visual_state.get("current_dialog", "")),
                str(visual_state.get("active_menu", "")),
                " ".join(visual_state.get("visible_elements", []) or []),
                str(visual_state.get("data_state", "")),
                str(visual_state.get("current_action", "")),
            ]
        ).lower()

        scored: List[Tuple[Dict, float]] = []
        for node_id in self.graph.nodes:
            node = self.graph.nodes[node_id]
            if hint_workflow_id and node.get("workflow_id") != hint_workflow_id:
                continue
            score = self._score_node_match(node, vs_text)
            if score > 0:
                scored.append((dict(node), score))
        scored.sort(key=lambda p: p[1], reverse=True)
        return scored[:k]

    def get_current_node(
        self, visual_state: Dict, hint_workflow_id: Optional[str] = None
    ) -> Tuple[Optional[Dict], float]:
        """
        Match a visual state (from screenshot) to a workflow node.
        Returns (node, confidence_score). Score 0.0-1.0.

        visual_state: {
          "current_dialog": "...",
          "active_menu": "...",
          "visible_elements": ["..."],
          "data_state": "...",
          "current_action": "..."
        }
        """
        # Flatten visual_state into a searchable text
        vs_text = " ".join(
            [
                str(visual_state.get("current_dialog", "")),
                str(visual_state.get("active_menu", "")),
                " ".join(visual_state.get("visible_elements", []) or []),
                str(visual_state.get("data_state", "")),
                str(visual_state.get("current_action", "")),
            ]
        ).lower()

        best_node = None
        best_score = 0.0

        for node_id in self.graph.nodes:
            node = self.graph.nodes[node_id]
            if hint_workflow_id and node.get("workflow_id") != hint_workflow_id:
                continue

            score = self._score_node_match(node, vs_text)
            if score > best_score:
                best_score = score
                best_node = node

        return (dict(best_node) if best_node else None, best_score)

    @staticmethod
    def _score_node_match(node: Dict, vs_text: str) -> float:
        """Compute match score between a node's visual_signature and the state text."""
        sig = node.get("visual_signature", {}) or {}
        keywords = sig.get("screenshot_keywords", []) or []
        dialog = (sig.get("expected_dialog") or "").lower()
        ui = sig.get("expected_ui_elements", []) or []

        if not keywords and not dialog and not ui:
            return 0.0

        matches = 0
        total = len(keywords) + len(ui) + (1 if dialog else 0)

        for kw in keywords:
            if kw.lower() in vs_text:
                matches += 1
        for el in ui:
            if el.lower().replace("_", " ") in vs_text:
                matches += 1
        if dialog and dialog in vs_text:
            matches += 1

        return matches / total if total > 0 else 0.0

    # ═══════════════════════════════════════════════════════════
    # Graph Traversal
    # ═══════════════════════════════════════════════════════════

    def get_next_steps(self, current_node_id: str) -> List[Dict]:
        """Get successor nodes (next possible steps)."""
        if current_node_id not in self.graph:
            return []
        next_nodes = []
        for _, tgt, edge_data in self.graph.out_edges(current_node_id, data=True):
            node = dict(self.graph.nodes[tgt])
            node["edge_type"] = edge_data.get("edge_type", "sequential")
            node["edge_instruction"] = edge_data.get("instruction", "")
            node["edge_condition"] = edge_data.get("condition")
            next_nodes.append(node)
        return next_nodes

    def get_previous_steps(self, current_node_id: str) -> List[Dict]:
        """Get predecessor nodes (previous steps)."""
        if current_node_id not in self.graph:
            return []
        prev_nodes = []
        for src, _, edge_data in self.graph.in_edges(current_node_id, data=True):
            node = dict(self.graph.nodes[src])
            node["edge_type"] = edge_data.get("edge_type", "sequential")
            node["edge_instruction"] = edge_data.get("instruction", "")
            prev_nodes.append(node)
        return prev_nodes

    def get_workflow_path(self, start: str, end: str) -> List[Dict]:
        """Shortest path between two nodes (returns node dicts)."""
        if start not in self.graph or end not in self.graph:
            return []
        try:
            path_ids = nx.shortest_path(self.graph, source=start, target=end)
            return [dict(self.graph.nodes[nid]) for nid in path_ids]
        except nx.NetworkXNoPath:
            return []

    def get_completed_path(self, current_node_id: str) -> List[Dict]:
        """
        Get all nodes leading up to the current node within its workflow.
        Used by report mode for backward traversal.
        """
        if current_node_id not in self.graph:
            return []

        current_node = self.graph.nodes[current_node_id]
        workflow_id = current_node.get("workflow_id")
        current_step = current_node.get("step_number", 0)

        if not workflow_id:
            return [dict(current_node)]

        completed = [
            dict(self.graph.nodes[n])
            for n in self.graph.nodes
            if self.graph.nodes[n].get("workflow_id") == workflow_id
            and self.graph.nodes[n].get("step_number", 0) <= current_step
        ]
        return sorted(completed, key=lambda n: n.get("step_number", 0))

    def get_path_from_history(self, node_ids: List[str]) -> List[Dict]:
        """Build a path from a list of visited node IDs (preserves order)."""
        path = []
        seen = set()
        for nid in node_ids:
            if nid in self.graph and nid not in seen:
                path.append(dict(self.graph.nodes[nid]))
                seen.add(nid)
        return path

    # ═══════════════════════════════════════════════════════════
    # Correction Analysis
    # ═══════════════════════════════════════════════════════════

    def analyze_position(
        self, current_node_id: str, expected_node_id: str
    ) -> Dict:
        """
        Compare actual user position to expected position.
        Returns analysis for correction logic in guide pipeline.
        """
        if not current_node_id or current_node_id not in self.graph:
            return {"case": "unknown", "reason": "현재 위치를 파악할 수 없음"}

        if not expected_node_id or expected_node_id not in self.graph:
            return {"case": "no_target", "current": self.get_node(current_node_id)}

        if current_node_id == expected_node_id:
            return {"case": "on_target", "current": self.get_node(current_node_id)}

        current = self.graph.nodes[current_node_id]
        expected = self.graph.nodes[expected_node_id]

        # Different workflows?
        if current.get("workflow_id") != expected.get("workflow_id"):
            return {
                "case": "different_workflow",
                "current_workflow": current.get("workflow_id"),
                "expected_workflow": expected.get("workflow_id"),
                "current": self.get_node(current_node_id),
                "expected": self.get_node(expected_node_id),
            }

        # Check if current is a predecessor of expected
        try:
            path_ids = nx.shortest_path(
                self.graph, source=current_node_id, target=expected_node_id
            )
            missing_nodes = [dict(self.graph.nodes[nid]) for nid in path_ids[1:-1]]
            if not missing_nodes:
                return {
                    "case": "one_step_behind",
                    "current": self.get_node(current_node_id),
                    "expected": self.get_node(expected_node_id),
                }
            return {
                "case": "skipped_steps",
                "current": self.get_node(current_node_id),
                "expected": self.get_node(expected_node_id),
                "missing_steps": missing_nodes,
            }
        except nx.NetworkXNoPath:
            return {
                "case": "divergent",
                "current": self.get_node(current_node_id),
                "expected": self.get_node(expected_node_id),
            }


# Singleton instance (lazy-initialized)
_workflow_graph_instance: Optional[WorkflowGraph] = None


def get_workflow_graph() -> WorkflowGraph:
    global _workflow_graph_instance
    if _workflow_graph_instance is None:
        _workflow_graph_instance = WorkflowGraph()
    return _workflow_graph_instance


def reload_workflow_graph() -> WorkflowGraph:
    """Force-reload workflow JSON files (useful for development)."""
    global _workflow_graph_instance
    _workflow_graph_instance = WorkflowGraph()
    return _workflow_graph_instance
