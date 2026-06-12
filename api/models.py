import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Manual(BaseModel):
    id: str
    name: str
    type: str  # "pdf", "url", "github"
    source: str  # file path, URL, or repo URL
    status: str  # "processing", "ready", "error"
    error_message: Optional[str] = None
    chunk_count: int = 0
    workflow_count: int = 0
    created_at: str

    @staticmethod
    def new(name: str, type: str, source: str) -> "Manual":
        return Manual(
            id=uuid.uuid4().hex,
            name=name,
            type=type,
            source=source,
            status="processing",
            chunk_count=0,
            workflow_count=0,
            created_at=datetime.utcnow().isoformat(),
        )


class ManualListResponse(BaseModel):
    manuals: List[Manual]
