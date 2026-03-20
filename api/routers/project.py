from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import project_store

router = APIRouter()


class ProjectSaveRequest(BaseModel):
    id: str = ""
    topic: str = ""
    captures: list = []
    report_content: str = ""
    manual_ids: list = []


@router.post("/api/project/save")
async def save_project(body: ProjectSaveRequest):
    data = body.model_dump()
    saved = project_store.save_project(data)
    return {"id": saved["id"], "updated_at": saved["updated_at"]}


@router.get("/api/project/list")
async def list_projects():
    return {"projects": project_store.list_projects()}


@router.get("/api/project/{project_id}")
async def get_project(project_id: str):
    data = project_store.load_project(project_id)
    if not data:
        raise HTTPException(status_code=404, detail="Project not found")
    return data


@router.delete("/api/project/{project_id}")
async def delete_project(project_id: str):
    if project_store.delete_project(project_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Project not found")
