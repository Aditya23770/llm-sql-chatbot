from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.api.routes import health, query, admin

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ingest schema into ChromaDB on first startup
    try:
        from app.services.schema_ingestion import ingest_schema
        count = await ingest_schema(force=False)
        if count:
            logger.info("ChromaDB ingestion complete (%d documents)", count)
        else:
            logger.info("ChromaDB collection already populated, skipping ingestion")
    except Exception as exc:
        logger.warning("Schema ingestion skipped: %s", exc)
    yield


app = FastAPI(title="LLM SQL Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        # Add Streamlit Cloud URL after deploy
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(query.router)
app.include_router(admin.router)
