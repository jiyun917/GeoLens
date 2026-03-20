"""
Project store: Save/load interpretation projects as JSON files.
Each project includes topic, captures (metadata only, images stored separately),
report content, and reference manual IDs.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "projects")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _project_path(project_id: str) -> str:
    return os.path.join(DATA_DIR, f"{project_id}.json")


def save_project(data: Dict) -> Dict:
    """Save a project. If no id, create one."""
    _ensure_dir()

    if not data.get("id"):
        data["id"] = uuid.uuid4().hex[:12]
    if not data.get("created_at"):
        data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()

    path = _project_path(data["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def load_project(project_id: str) -> Optional[Dict]:
    """Load a single project."""
    path = _project_path(project_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_projects() -> List[Dict]:
    """List all projects (metadata only, no captures/report)."""
    _ensure_dir()
    projects = []
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            projects.append({
                "id": data.get("id"),
                "topic": data.get("topic", ""),
                "capture_count": len(data.get("captures", [])),
                "data_types": list(set(c.get("dataType", "other") for c in data.get("captures", []))),
                "has_report": bool(data.get("report_content")),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
            })
        except Exception:
            continue

    projects.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return projects


def delete_project(project_id: str) -> bool:
    """Delete a project."""
    path = _project_path(project_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
