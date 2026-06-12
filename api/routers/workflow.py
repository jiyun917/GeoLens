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


@router.get("/api/workflow/auto/{manual_id}")
async def get_auto_workflow(manual_id: str):
    """Return every auto-generated workflow belonging to a manual."""
    wg = get_workflow_graph()
    prefix = f"auto_{manual_id}__"
    workflows = []
    for wid in list(wg.workflows.keys()):
        if wid.startswith(prefix):
            workflows.append({
                **wg.workflows[wid],
                "nodes": wg.get_workflow_nodes(wid),
            })
    return {"manual_id": manual_id, "count": len(workflows), "workflows": workflows}


@router.get("/api/workflow/auto/{manual_id}/quality")
async def get_auto_workflow_quality(manual_id: str):
    """Return quality metrics for auto-generated workflows of a manual."""
    wg = get_workflow_graph()
    prefix = f"auto_{manual_id}__"
    total_nodes = 0
    total_edges = 0
    nodes_with_links = 0
    nodes_with_visual = 0
    nodes_with_params = 0
    per_workflow = []

    for wid in wg.workflows.keys():
        if not wid.startswith(prefix):
            continue
        nodes = wg.get_workflow_nodes(wid)
        edges = [
            (s, t, d) for s, t, d in wg.graph.out_edges(
                [n["id"] for n in nodes], data=True
            )
        ]
        n_linked = sum(1 for n in nodes if n.get("linked_chunks"))
        n_visual = sum(1 for n in nodes if (n.get("visual_signature") or {}).get("expected_ui_elements"))
        n_params = sum(1 for n in nodes if n.get("parameters"))
        total_nodes += len(nodes)
        total_edges += len(edges)
        nodes_with_links += n_linked
        nodes_with_visual += n_visual
        nodes_with_params += n_params
        per_workflow.append({
            "workflow_id": wid,
            "nodes": len(nodes),
            "edges": len(edges),
            "linked_chunks_coverage": (n_linked / len(nodes)) if nodes else 0.0,
            "visual_signature_coverage": (n_visual / len(nodes)) if nodes else 0.0,
            "parameters_coverage": (n_params / len(nodes)) if nodes else 0.0,
        })

    return {
        "manual_id": manual_id,
        "workflow_count": len(per_workflow),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "linked_chunks_coverage": (nodes_with_links / total_nodes) if total_nodes else 0.0,
        "visual_signature_coverage": (nodes_with_visual / total_nodes) if total_nodes else 0.0,
        "parameters_coverage": (nodes_with_params / total_nodes) if total_nodes else 0.0,
        "per_workflow": per_workflow,
    }


class EvalRequest(BaseModel):
    manual_id: str
    manual_graph_path: str  # absolute or relative path to the hand-authored workflow JSON


@router.post("/api/eval/run")
async def run_evaluation(body: EvalRequest):
    """Run the full AutoProcRAG evaluation suite for one manual.

    Reads `data/eval/test_questions.json` and `data/eval/test_screenshots.json`
    (both optional — missing files simply return empty sections).
    """
    from ..services.evaluation import run_full_evaluation
    import os
    path = body.manual_graph_path
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), path)
    return run_full_evaluation(body.manual_id, path)


@router.post("/api/rag/route")
async def route_rag(body: RouteRequest):
    """
    Guide RAG entry point. Returns the guide mode context block for the LLM.
    """
    router_instance = get_rag_router()
    result = router_instance.route(
        user_message=body.message,
        screenshot_b64=body.screenshot,
        session_state=body.session_state or {},
        manual_ids=body.manual_ids,
    )
    return result
