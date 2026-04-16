"""
Report Mode RAG Pipeline.
Backward traversal on workflow graph + contextual vector retrieval
to build a rich context for report generation.
"""

from typing import Dict, List, Optional

from .workflow_graph import WorkflowGraph, get_workflow_graph
from .graph_retriever import GraphRetriever, get_graph_retriever
from .rag import get_manual_context


REPORT_TEMPLATES = {
    "interpretation_summary": {
        "sections": ["목적", "사용 데이터", "해석 방법", "파라미터 설정", "결과", "고찰"],
        "search_focus": "methodology",
    },
    "parameter_justification": {
        "sections": ["파라미터 목록", "각 파라미터의 의미", "설정 근거", "권장 범위"],
        "search_focus": "parameters",
    },
    "workflow_documentation": {
        "sections": ["전체 워크플로우", "각 단계 상세", "소요 시간", "주의사항"],
        "search_focus": "procedure",
    },
}


class ReportRAGPipeline:
    """
    Report mode pipeline:
      - Backward-traverse the workflow graph based on session history
      - For each completed step, retrieve conceptual explanations via vector search
      - Structure into a report-ready context block
    """

    def __init__(
        self,
        workflow_graph: Optional[WorkflowGraph] = None,
        retriever: Optional[GraphRetriever] = None,
    ):
        self.graph = workflow_graph or get_workflow_graph()
        self.retriever = retriever or get_graph_retriever()

    # ═══════════════════════════════════════════════════════════
    # Entry point
    # ═══════════════════════════════════════════════════════════

    def generate_report_context(
        self,
        session_history: Dict,
        report_type: str = "interpretation_summary",
        user_params: Optional[Dict] = None,
        manual_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Main entry. Returns structured context for report generation.

        session_history:
          - visited_node_ids: [str]
          - parameters: { node_id: [{name, value}] }
          - active_workflow_id: str
          - current_node_id: str

        Returns:
        {
          "workflow_path": [...],
          "steps": [{"node": ..., "technique": [...], "parameters": [...]}],
          "report_template": {...}
        }
        """
        session_history = session_history or {}
        user_params = user_params or {}

        # Step 1: Collect path (backward traversal)
        visited_ids = session_history.get("visited_node_ids") or []
        current_id = session_history.get("current_node_id")

        if visited_ids:
            path_nodes = self.graph.get_path_from_history(visited_ids)
        elif current_id:
            path_nodes = self.graph.get_completed_path(current_id)
        else:
            path_nodes = []

        # Step 2: For each step, gather conceptual context via vector search
        steps_context = []
        template = REPORT_TEMPLATES.get(report_type, REPORT_TEMPLATES["interpretation_summary"])

        for node in path_nodes:
            step_params = session_history.get("parameters", {}).get(node["id"], []) or node.get("parameters", [])
            step_ctx = self.collect_step_context(
                node, step_params, manual_ids=manual_ids, focus=template.get("search_focus")
            )
            steps_context.append(step_ctx)

        return {
            "workflow_path": path_nodes,
            "steps": steps_context,
            "report_template": template,
            "report_type": report_type,
        }

    # ═══════════════════════════════════════════════════════════
    # Per-step context collection
    # ═══════════════════════════════════════════════════════════

    def collect_step_context(
        self,
        node: Dict,
        used_parameters: List[Dict],
        manual_ids: Optional[List[str]] = None,
        focus: str = "methodology",
    ) -> Dict:
        """
        Gather context for one workflow step.

        Collects:
          1. Technique explanation (method/principle)
          2. Parameter explanations (meaning, range)
          3. Procedural info (from the graph node)
        """
        technique_ctx = None
        param_ctx: List[Dict] = []

        workflow_label = node.get("workflow_id", "").replace("_", " ")
        title = node.get("title", "")

        if manual_ids:
            # Technique/principle search with Contextual Retrieval style query
            if focus == "parameters":
                tech_query = f"[{workflow_label} > {title}] parameter meaning configuration"
            elif focus == "procedure":
                tech_query = f"[{workflow_label} > {title}] procedure step-by-step workflow"
            else:
                tech_query = f"[{workflow_label} > {title}] principle method explanation theory"

            technique_ctx = get_manual_context(manual_ids, tech_query, top_k=3)

            # Per-parameter search
            for p in used_parameters:
                pname = p.get("name", "")
                pval = p.get("value", p.get("default", ""))
                pquery = f"[{workflow_label} > {title}] {pname} {pval} meaning range recommendation"
                pctx = get_manual_context(manual_ids, pquery, top_k=2)
                if pctx:
                    param_ctx.append({
                        "name": pname,
                        "value": pval,
                        "context": pctx,
                    })

        return {
            "step_info": {
                "id": node.get("id"),
                "workflow_id": node.get("workflow_id"),
                "step_number": node.get("step_number"),
                "title": title,
                "description": node.get("description"),
                "step_type": node.get("step_type"),
            },
            "technique_explanation": technique_ctx,
            "parameter_explanation": param_ctx,
        }

    # ═══════════════════════════════════════════════════════════
    # Context block formatter
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def build_context_block(report_context: Dict) -> str:
        """Flatten report context into a system prompt text block."""
        parts = []

        path = report_context.get("workflow_path") or []
        if path:
            summary = " → ".join(
                [f"{n.get('step_number','?')}.{n.get('title','')}" for n in path]
            )
            parts.append(f"[Workflow Path Summary]\n{summary}")

        steps = report_context.get("steps") or []
        for s in steps:
            info = s.get("step_info", {})
            lines = [
                f"--- Step {info.get('step_number')} · {info.get('title')} ---",
                f"Description: {info.get('description')}",
            ]
            if s.get("technique_explanation"):
                lines.append(f"Technique context:\n{s['technique_explanation'][:800]}")
            if s.get("parameter_explanation"):
                for p in s["parameter_explanation"]:
                    lines.append(
                        f"Parameter `{p['name']}` = {p['value']}\n  Context: {str(p.get('context', ''))[:400]}"
                    )
            parts.append("\n".join(lines))

        if not parts:
            return ""
        return "\n\n".join(parts)


# Singleton
_report_pipeline_instance: Optional[ReportRAGPipeline] = None


def get_report_pipeline() -> ReportRAGPipeline:
    global _report_pipeline_instance
    if _report_pipeline_instance is None:
        _report_pipeline_instance = ReportRAGPipeline()
    return _report_pipeline_instance
