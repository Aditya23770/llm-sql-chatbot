import json
import logging
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_SCHEMA_FILE = Path(__file__).parent.parent.parent / "rag" / "schema_definitions.json"


def _get_collection(client: chromadb.PersistentClient, name: str):
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return client.get_or_create_collection(name=name, embedding_function=ef)


async def ingest_schema(force: bool = False) -> int:
    """
    Ingest column metadata into ChromaDB.
    Returns number of documents indexed (0 if skipped because already populated).
    """
    s = get_settings()
    chroma = chromadb.PersistentClient(path=s.chroma_persist_dir)
    collection = _get_collection(chroma, s.chroma_collection_name)

    if not force and collection.count() > 0:
        return 0

    if force:
        chroma.delete_collection(s.chroma_collection_name)
        collection = _get_collection(chroma, s.chroma_collection_name)

    definitions = json.loads(_SCHEMA_FILE.read_text())

    ids, documents, metadatas = [], [], []
    for col in definitions:
        embed_text = (
            f"{col['column']}: {col['description']}. "
            f"Type: {col['type']}. "
            f"Examples: {', '.join(col['example_values'])}"
        )
        ids.append(col["column_id"])
        documents.append(embed_text)
        metadatas.append({"table": col["table"], "column": col["column"], "type": col["type"]})

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    logger.info("Ingested %d column definitions into ChromaDB", len(ids))
    return len(ids)
