"""
Workflow and RAG router API endpoints.
"""

from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter

from ..services.workflow_graph import get_workflow_graph, reload_workflow_graph
from ..services.rag_router import get_rag_router
from ..services.chunk_mapper import map_all_workflows

router = APIRouter()


class RouteRequest(BaseModel):
    message: str = ""
    screenshot: Optional[str] = None  # base64 data URL or raw
    session_state: Optional[dict] = None
    manual_ids: Optional[List[str]] = None


class MapChunksRequest(BaseModel):
    manual_ids: List[str]
    top_k: int = 3


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


@router.post("/api/workflow/map-chunks")
async def map_chunks(body: MapChunksRequest):
    """
    Auto-populate linked_chunks for all workflow nodes by semantic similarity
    against the specified ChromaDB manuals. Updates JSON files in place.
    """
    results = map_all_workflows(body.manual_ids, top_k=body.top_k)
    # Reload workflow graph to pick up new linked_chunks
    reload_workflow_graph()
    return {"status": "ok", "results": results}


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
