import logging
from typing import Optional
import chromadb
from chromadb.api import ClientAPI
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_chroma_client: Optional[ClientAPI] = None


def _get_client() -> ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        s = get_settings()
        _chroma_client = chromadb.PersistentClient(path=s.chroma_persist_dir)
    return _chroma_client


async def retrieve_columns(query: str) -> str:
    """Return a formatted string of top-k relevant column descriptions for the given query."""
    s = get_settings()
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = _get_client().get_or_create_collection(
        name=s.chroma_collection_name, embedding_function=ef
    )

    results = collection.query(query_texts=[query], n_results=min(s.rag_top_k, collection.count()))
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    lines = []
    for doc, meta in zip(docs, metas):
        lines.append(f"- {meta['table']}.{meta['column']} ({meta['type']}): {doc}")

    retrieved = "\n".join(lines) if lines else "No specific columns matched."
    logger.info("RAG retrieved %d columns for query: %r", len(lines), query)
    return retrieved
