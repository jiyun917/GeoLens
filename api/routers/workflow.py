"""
Workflow and RAG router API endpoints.
"""

from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter

from ..services.workflow_graph import get_workflow_graph, reload_workflow_graph
from ..services.rag_router import get_rag_router

router = APIRouter()


class RouteRequest(BaseModel):
    message: str = ""
    screenshot: Optional[str] = None  # base64 data URL or raw
    session_state: Optional[dict] = None
    manual_ids: Optional[List[str]] = None


@router.get("/api/workflow/list")
async def list_workflows():
    """List all loaded workflows with metadata."""
    wg = get_workflow_graph()
    return {
        "workflows": wg.list_workflows(),
        "node_count": wg.graph.number_of_nodes(),
        "edge_count": wg.graph.number_of_edges(),
    }


@router.get("/api/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get all nodes of a specific workflow."""
    wg = get_workflow_graph()
    return {"workflow_id": workflow_id, "nodes": wg.get_workflow_nodes(workflow_id)}


@router.post("/api/workflow/reload")
async def reload_workflow():
    """Force reload workflow JSONs from disk."""
    wg = reload_workflow_graph()
    return {
        "status": "reloaded",
        "workflows": wg.list_workflows(),
        "node_count": wg.graph.number_of_nodes(),
        "edge_count": wg.graph.number_of_edges(),
    }


@router.post("/api/rag/route")
async def route_rag(body: RouteRequest):
    """
    Unified RAG entry point.
    Returns mode (guide/report/qa) and corresponding context block for LLM.
    """
    router_instance = get_rag_router()
    result = router_instance.route(
        user_message=body.message,
        screenshot_b64=body.screenshot,
        session_state=body.session_state or {},
        manual_ids=body.manual_ids,
    )
    return result
