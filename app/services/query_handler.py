import logging
from app.clients.database import DatabaseClient
from app.clients.cache import CacheClient
from app.clients.llm.factory import get_llm_client
from app.models.schemas import QueryResponse
from app.prompts.sql_generation import SQL_GENERATION_PROMPT, FULL_SCHEMA
from app.services.sql_extractor import extract_sql

logger = logging.getLogger(__name__)


async def handle_query(
    query: str,
    provider: str,
    db: DatabaseClient,
    cache: CacheClient,
) -> QueryResponse:
    cache_key = CacheClient.make_key(query, provider)

    try:
        cached = await cache.get(cache_key)
        if cached:
            logger.info("Cache hit for query: %r", query)
            return QueryResponse(**cached, cached=True, provider=provider)
    except Exception as exc:
        logger.warning("Cache read failed (skipping): %s", exc)

    # RAG column retrieval — imported lazily so Phase 4 works without ChromaDB
    try:
        from app.services.rag_retriever import retrieve_columns
        rag_columns = await retrieve_columns(query)
    except Exception:
        rag_columns = "All columns: customer_id, name, gender, location"

    system_prompt = SQL_GENERATION_PROMPT.format(
        full_schema=FULL_SCHEMA,
        rag_columns=rag_columns,
        user_query=query,
    )

    llm = get_llm_client(provider)
    llm_response = await llm.complete(system_prompt, query)
    logger.info("LLM raw response: %s", llm_response.content)

    sql_query = extract_sql(llm_response.content)
    logger.info("Extracted SQL: %s", sql_query)

    results = await db.get(sql_query)

    try:
        await cache.set(cache_key, {"sql_query": sql_query, "results": results})
    except Exception as exc:
        logger.warning("Cache write failed (skipping): %s", exc)

    return QueryResponse(sql_query=sql_query, results=results, cached=False, provider=provider)
