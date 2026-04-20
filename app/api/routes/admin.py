import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AdminResponse
from app.core.security import verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/admin/reload-schema",
    response_model=AdminResponse,
    dependencies=[Depends(verify_api_key)],
)
async def reload_schema():
    try:
        from app.services.schema_ingestion import ingest_schema
        count = await ingest_schema(force=True)
        return AdminResponse(message="Schema re-ingested successfully", documents_indexed=count)
    except Exception as exc:
        logger.error("Schema reload failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
