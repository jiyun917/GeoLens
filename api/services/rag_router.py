"""
GeoLens RAG Router (guide-only).
Routes all requests to the guide pipeline.
"""

from typing import Dict, List, Optional

from .guide_pipeline import GuideRAGPipeline, get_guide_pipeline


class GeoLensRAGRouter:
    """Route requests to the guide RAG pipeline."""

    def __init__(self, guide_pipeline: Optional[GuideRAGPipeline] = None):
        self.guide_pipeline = guide_pipeline or get_guide_pipeline()

    def route(
        self,
        user_message: str,
        screenshot_b64: Optional[str] = None,
        session_state: Optional[Dict] = None,
        manual_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Returns:
        {
          "mode": "guide",
          "context_block": "...",   # text to inject into LLM system prompt
          "raw_output": {...}       # pipeline output for debugging/UI
        }
        """
        session_state = session_state or {}
        output = self.guide_pipeline.process_guide_request(
            screenshot_b64=screenshot_b64,
            user_message=user_message,
            session_history=session_state,
            manual_ids=manual_ids,
        )
        block = self.guide_pipeline.build_context_block(output)
        return {"mode": "guide", "context_block": block, "raw_output": output}


_router_instance: Optional[GeoLensRAGRouter] = None


def get_rag_router() -> GeoLensRAGRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = GeoLensRAGRouter()
    return _router_instance
