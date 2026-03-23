"""GeoBanana: Geological schematic diagram generation endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.geo_diagram import generate_geo_diagram

router = APIRouter(prefix="/api")


class DiagramRequest(BaseModel):
    report_text: str
    data_type: str = "seismic"
    language: str = "ko"
    capture_image: str | None = None


@router.post("/diagram")
async def generate_diagram(req: DiagramRequest):
    result = await generate_geo_diagram(
        report_text=req.report_text,
        data_type=req.data_type,
        language=req.language,
        capture_image=req.capture_image,
    )
    if not result:
        raise HTTPException(status_code=500, detail="Diagram generation failed")
    return {"image": result["image"], "structures": result.get("structures", []), "success": True}
