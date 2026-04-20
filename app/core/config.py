from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "groq"  # "groq" | "openai" | "anthropic"
    llm_model: str = ""         # override per-provider default when set

    # Database
    db_url: str = ""            # postgresql+asyncpg://...

    # Redis
    redis_url: str = ""         # rediss://... (Upstash) or redis://... (local)
    redis_default_ttl_seconds: int = 3600

    # Security
    api_key: str = ""

    # RAG / ChromaDB
    chroma_persist_dir: str = "./rag/chroma_db"
    chroma_collection_name: str = "schema_columns"
    rag_top_k: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
