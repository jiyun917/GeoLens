import os
import shutil
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, UploadFile, HTTPException
from pydantic import BaseModel

from ..models import Manual, ManualListResponse
from ..services import manual_store, vectorstore, graphstore
from ..services.embedder import embed_and_store
from ..services.parser.pdf_parser import parse_pdf
from ..services.parser.url_parser import parse_url
from ..services.parser.github_parser import parse_github

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _process_pdf(manual_id: str, file_path: str):
    try:
        content_pieces = parse_pdf(file_path)
        embed_and_store(manual_id, content_pieces, pdf_path=file_path)
    except Exception as e:
        manual_store.update_manual(manual_id, status="error", error_message=str(e))


def _process_url(manual_id: str, url: str):
    try:
        content_pieces = parse_url(url)
        embed_and_store(manual_id, content_pieces)
    except Exception as e:
        manual_store.update_manual(manual_id, status="error", error_message=str(e))


def _process_github(manual_id: str, repo_url: str):
    try:
        content_pieces = parse_github(repo_url)
        embed_and_store(manual_id, content_pieces)
    except Exception as e:
        manual_store.update_manual(manual_id, status="error", error_message=str(e))


@router.post("/api/manual/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), mode: str = "guide"):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    _ensure_upload_dir()
    manual = Manual.new(name=file.filename, type="pdf", source=file.filename, mode=mode)
    file_path = os.path.join(UPLOAD_DIR, f"{manual.id}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    manual.source = file_path
    manual_store.add_manual(manual)
    background_tasks.add_task(_process_pdf, manual.id, file_path)

    return manual.model_dump()


class UrlRequest(BaseModel):
    url: str
    name: Optional[str] = None
    mode: str = "guide"


@router.post("/api/manual/url")
async def add_url(background_tasks: BackgroundTasks, body: UrlRequest):
    name = body.name or body.url
    manual = Manual.new(name=name, type="url", source=body.url, mode=body.mode)
    manual_store.add_manual(manual)
    background_tasks.add_task(_process_url, manual.id, body.url)

    return manual.model_dump()


class GithubRequest(BaseModel):
    url: str
    name: Optional[str] = None
    mode: str = "guide"


@router.post("/api/manual/github")
async def add_github(background_tasks: BackgroundTasks, body: GithubRequest):
    name = body.name or body.url
    manual = Manual.new(name=name, type="github", source=body.url, mode=body.mode)
    manual_store.add_manual(manual)
    background_tasks.add_task(_process_github, manual.id, body.url)

    return manual.model_dump()


@router.get("/api/manual/list")
async def list_manuals(mode: Optional[str] = None):
    manuals = manual_store.load_manuals()
    if mode:
        manuals = [m for m in manuals if getattr(m, "mode", "guide") == mode]
    return ManualListResponse(manuals=manuals).model_dump()


@router.get("/api/manual/{manual_id}")
async def get_manual(manual_id: str):
    manual = manual_store.get_manual(manual_id)
    if not manual:
        raise HTTPException(status_code=404, detail="Manual not found")
    return manual.model_dump()


@router.delete("/api/manual/{manual_id}")
async def delete_manual(manual_id: str):
    manual = manual_store.get_manual(manual_id)
    if not manual:
        raise HTTPException(status_code=404, detail="Manual not found")

    # Delete from ChromaDB (both standard and guide collections) and Graph
    vectorstore.delete_collection(manual_id)
    if hasattr(vectorstore, "delete_guide_collection"):
        vectorstore.delete_guide_collection(manual_id)
    graphstore.delete_graph(manual_id)

    # Delete auto-generated workflow JSONs + reload graph
    try:
        from ..services.auto_graph_builder import delete_auto_workflows
        from ..services.workflow_graph import reload_workflow_graph
        removed = delete_auto_workflows(manual_id)
        if removed:
            reload_workflow_graph()
    except Exception as e:
        print(f"[MANUAL] auto workflow cleanup failed: {e}")

    # Delete extracted manual images + clear CLIP index
    try:
        from ..services.image_extractor import delete_manual_images
        from ..services.visual_matcher import get_visual_matcher
        delete_manual_images(manual_id)
        get_visual_matcher().clear_manual(manual_id)
    except Exception as e:
        print(f"[MANUAL] image cleanup failed: {e}")

    # Delete uploaded file if it's a PDF
    if manual.type == "pdf" and manual.source and os.path.exists(manual.source):
        try:
            os.remove(manual.source)
        except Exception:
            pass

    # Delete from store
    manual_store.delete_manual(manual_id)

    return {"status": "deleted"}


@router.get("/api/manual/{manual_id}/graph")
async def get_manual_graph_stats(manual_id: str):
    manual = manual_store.get_manual(manual_id)
    if not manual:
        raise HTTPException(status_code=404, detail="Manual not found")
    stats = graphstore.get_graph_stats(manual_id)
    return stats
