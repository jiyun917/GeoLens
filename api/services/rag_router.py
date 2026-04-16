"""
GeoLens RAG Router.
Dispatches incoming requests to guide / report / qa pipelines based on
explicit mode selection or auto-detection.
"""

from typing import Dict, List, Optional

from .guide_pipeline import GuideRAGPipeline, get_guide_pipeline
from .report_pipeline import ReportRAGPipeline, get_report_pipeline
from .rag import get_manual_context


class GeoLensRAGRouter:
    """Route requests to the appropriate RAG pipeline."""

    def __init__(
        self,
        guide_pipeline: Optional[GuideRAGPipeline] = None,
        report_pipeline: Optional[ReportRAGPipeline] = None,
    ):
        self.guide_pipeline = guide_pipeline or get_guide_pipeline()
        self.report_pipeline = report_pipeline or get_report_pipeline()

    # ═══════════════════════════════════════════════════════════
    # Mode detection
    # ═══════════════════════════════════════════════════════════

    def detect_mode(
        self,
        user_message: str,
        session_state: Optional[Dict] = None,
        has_screenshot: bool = False,
    ) -> str:
        """
        Returns: 'guide' | 'report' | 'qa'
        Explicit mode in session_state['mode'] overrides auto-detection.
        """
        session_state = session_state or {}
        explicit = session_state.get("mode")
        if explicit in ("guide", "report", "qa"):
            return explicit

        msg = (user_message or "").lower()

        # Report keywords
        report_kw = ["report", "summary", "document", "정리", "보고서", "리포트", "요약", "문서화"]
        if any(k in msg for k in report_kw):
            return "report"

        # Guide keywords (next-step assistance)
        guide_kw = ["next", "then", "how", "what now", "다음", "어떻게", "뭐해", "이제"]
        if has_screenshot and any(k in msg for k in guide_kw):
            return "guide"

        if has_screenshot:
            return "guide"  # Default to guide when screenshot present

        return "qa"

    # ═══════════════════════════════════════════════════════════
    # Main route
    # ═══════════════════════════════════════════════════════════

    def route(
        self,
        user_message: str,
        screenshot_b64: Optional[str] = None,
        session_state: Optional[Dict] = None,
        manual_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Returns a unified response structure:
        {
          "mode": "guide" | "report" | "qa",
          "context_block": "...",  # text to inject into LLM system prompt
          "raw_output": {...}      # mode-specific output for debugging/UI
        }
        """
        session_state = session_state or {}
        has_screenshot = bool(screenshot_b64)
        mode = self.detect_mode(user_message, session_state, has_screenshot)

        if mode == "guide":
            output = self.guide_pipeline.process_guide_request(
                screenshot_b64=screenshot_b64,
                user_message=user_message,
                session_history=session_state,
                manual_ids=manual_ids,
            )
            block = self.guide_pipeline.build_context_block(output)
            return {"mode": "guide", "context_block": block, "raw_output": output}

        if mode == "report":
            output = self.report_pipeline.generate_report_context(
                session_history=session_state,
                report_type=session_state.get("report_type", "interpretation_summary"),
                user_params=session_state.get("parameters"),
                manual_ids=manual_ids,
            )
            block = self.report_pipeline.build_context_block(output)
            return {"mode": "report", "context_block": block, "raw_output": output}

        # qa mode (simple vector search)
        context = get_manual_context(manual_ids or [], user_message, top_k=5) if user_message else None
        block = f"[Manual Context]\n{context}" if context else ""
        return {
            "mode": "qa",
            "context_block": block,
            "raw_output": {"query": user_message, "context": context},
        }


# Singleton
_router_instance: Optional[GeoLensRAGRouter] = None


def get_rag_router() -> GeoLensRAGRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = GeoLensRAGRouter()
    return _router_instance
