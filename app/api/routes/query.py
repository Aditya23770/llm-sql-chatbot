import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.core.security import verify_api_key
from app.api.deps import get_db_client, get_cache_client
from app.services.query_handler import handle_query

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def process_query(
    request: QueryRequest,
    db=Depends(get_db_client),
    cache=Depends(get_cache_client),
):
    logger.info("Received query: %r provider=%s", request.query, request.provider)
    try:
        return await handle_query(request.query, request.provider, db, cache)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("Unhandled error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
