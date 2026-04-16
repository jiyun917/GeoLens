"""
Guide Mode State-Aware RAG Pipeline.
Combines:
  - Screenshot visual analysis (Gemini)
  - Workflow graph localization (current node matching)
  - Next-step retrieval (graph + vector)
  - Correction logic (handle skipped steps, wrong workflow)
"""

import json
import os
import re
from typing import Dict, List, Optional, Any

from .workflow_graph import WorkflowGraph, get_workflow_graph
from .graph_retriever import GraphRetriever, get_graph_retriever


VISUAL_STATE_PROMPT = """You are analyzing a screenshot of the OpendTect geophysics software.
Extract the current UI state into JSON:

{
  "current_dialog": "name of the currently visible dialog/window",
  "active_menu": "currently active menu or tab, if visible",
  "visible_elements": ["key UI elements visible on screen"],
  "data_state": "state of data loaded (e.g., '3D seismic loaded', 'none')",
  "current_action": "what action appears to be in progress"
}

Respond with JSON only, no markdown fences, no explanation."""


def _extract_json(text: str) -> Optional[Dict]:
    """Extract JSON object from model response."""
    if not text:
        return None
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None


class GuideRAGPipeline:
    """
    Guide mode pipeline:
      1. Recognize visual state from screenshot (via Gemini)
      2. Match to workflow graph node (localization)
      3. Retrieve next-step context (graph + vector)
      4. Check correction need vs expected position
      5. Build enriched context for guide response
    """

    def __init__(
        self,
        workflow_graph: Optional[WorkflowGraph] = None,
        retriever: Optional[GraphRetriever] = None,
    ):
        self.graph = workflow_graph or get_workflow_graph()
        self.retriever = retriever or get_graph_retriever()

    # ═══════════════════════════════════════════════════════════
    # Step 1: Visual State Recognition
    # ═══════════════════════════════════════════════════════════

    def recognize_visual_state(self, screenshot_b64: str) -> Dict:
        """
        Use Gemini to extract structured UI state from a screenshot.
        screenshot_b64: raw base64 or data URL
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {}

        try:
            from google import genai
            from google.genai import types
            import base64 as b64module

            client = genai.Client(api_key=api_key)

            # Extract base64 payload
            b64_data = screenshot_b64
            mime = "image/jpeg"
            if screenshot_b64.startswith("data:image/"):
                header, b64_data = screenshot_b64.split(",", 1)
                try:
                    mime = header.split(";")[0].split(":")[1]
                except Exception:
                    mime = "image/jpeg"

            image_bytes = b64module.b64decode(b64_data)

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=VISUAL_STATE_PROMPT),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime),
                    ],
                )
            ]
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            )
            response = client.models.generate_content(
                model="gemini-2.5-pro", contents=contents, config=config
            )
            return _extract_json(response.text) or {}
        except Exception as e:
            print(f"[GuidePipeline] Visual state recognition failed: {e}")
            return {}

    # ═══════════════════════════════════════════════════════════
    # Step 2: Graph Localization
    # ═══════════════════════════════════════════════════════════

    def localize_to_graph(
        self, visual_state: Dict, hint_workflow_id: Optional[str] = None
    ) -> Dict:
        """
        Match visual state to a workflow graph node.
        Returns {"node": node_dict or None, "confidence": float}.
        """
        node, score = self.graph.get_current_node(visual_state, hint_workflow_id)
        return {"node": node, "confidence": score}

    # ═══════════════════════════════════════════════════════════
    # Step 3-5: Main processing
    # ═══════════════════════════════════════════════════════════

    def process_guide_request(
        self,
        screenshot_b64: Optional[str],
        user_message: str,
        session_history: Optional[Dict] = None,
        manual_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Main entry point. Returns a structured context dict for the LLM:
        {
          "visual_state": {...},
          "current_node": {...} or None,
          "confidence": 0.0-1.0,
          "next_nodes": [...],
          "graph_context": [...],
          "vector_context": "...",
          "correction": {...} or None,
          "intent": "next_step" | "explain" | "qa",
        }
        """
        session_history = session_history or {}

        # Step 1: Recognize visual state
        visual_state: Dict = {}
        if screenshot_b64:
            visual_state = self.recognize_visual_state(screenshot_b64)

        # Step 2: Detect intent
        intent = self._detect_intent(user_message)

        # Step 3: Localize
        hint = session_history.get("active_workflow_id")
        localization = self.localize_to_graph(visual_state, hint)
        current_node = localization["node"]
        confidence = localization["confidence"]
        current_node_id = current_node["id"] if current_node else None

        # Step 4: Retrieve context
        retrieval = self.retriever.hybrid_retrieve(
            current_node_id=current_node_id,
            query=user_message,
            intent=intent,
            manual_ids=manual_ids,
        )

        # Step 5: Correction check
        correction = None
        expected_node_id = session_history.get("expected_next_node_id")
        if current_node_id and expected_node_id:
            correction = self.graph.analyze_position(current_node_id, expected_node_id)

        return {
            "visual_state": visual_state,
            "current_node": current_node,
            "confidence": confidence,
            "next_nodes": retrieval.get("next_nodes", []),
            "graph_context": retrieval.get("graph_context", []),
            "vector_context": retrieval.get("vector_context"),
            "correction": correction,
            "intent": intent,
        }

    # ═══════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _detect_intent(user_message: str) -> str:
        """Classify user message into intent."""
        if not user_message:
            return "next_step"
        msg = user_message.lower()
        explain_keywords = ["explain", "what is", "meaning", "설명", "뜻", "의미"]
        qa_keywords = ["why", "how does", "difference", "왜", "차이"]
        next_keywords = ["next", "then", "after", "다음", "이제", "어떻게"]

        if any(kw in msg for kw in explain_keywords):
            return "explain"
        if any(kw in msg for kw in qa_keywords):
            return "qa"
        if any(kw in msg for kw in next_keywords):
            return "next_step"
        return "next_step"

    @staticmethod
    def build_context_block(pipeline_output: Dict) -> str:
        """
        Build a text context block to inject into the LLM system prompt.
        """
        parts = []

        current = pipeline_output.get("current_node")
        if current:
            parts.append(
                f"[Current Step] {current.get('workflow_id', '')} > "
                f"Step {current.get('step_number', '?')}: {current.get('title', '')}\n"
                f"Description: {current.get('description', '')}"
            )

        next_nodes = pipeline_output.get("next_nodes") or []
        if next_nodes:
            next_lines = []
            for n in next_nodes:
                cond = f" [if: {n.get('edge_condition')}]" if n.get("edge_condition") else ""
                next_lines.append(
                    f"  - Next ({n.get('edge_type', 'sequential')}){cond}: "
                    f"Step {n.get('step_number', '?')} {n.get('title', '')} — "
                    f"{n.get('edge_instruction') or n.get('description', '')}"
                )
            parts.append("[Possible Next Steps]\n" + "\n".join(next_lines))

        correction = pipeline_output.get("correction")
        if correction and correction.get("case") not in (None, "on_target", "unknown", "no_target"):
            parts.append(f"[Correction Needed] case={correction.get('case')}\n{json.dumps(correction, ensure_ascii=False, indent=2)[:500]}")

        graph_ctx = pipeline_output.get("graph_context") or []
        for g in graph_ctx[:3]:
            if g.get("text"):
                parts.append(f"[Manual Context (graph)]\n{g['text'][:800]}")

        vector_ctx = pipeline_output.get("vector_context")
        if vector_ctx:
            parts.append(f"[Manual Context (vector)]\n{vector_ctx[:1500]}")

        if not parts:
            return ""
        return "\n\n".join(parts)


# Singleton
_guide_pipeline_instance: Optional[GuideRAGPipeline] = None


def get_guide_pipeline() -> GuideRAGPipeline:
    global _guide_pipeline_instance
    if _guide_pipeline_instance is None:
        _guide_pipeline_instance = GuideRAGPipeline()
    return _guide_pipeline_instance
