from functools import lru_cache
from app.clients.database import DatabaseClient
from app.clients.cache import CacheClient
from app.core.config import get_settings


@lru_cache
def get_db_client() -> DatabaseClient:
    return DatabaseClient(get_settings().db_url)


@lru_cache
def get_cache_client() -> CacheClient:
    s = get_settings()
    return CacheClient(s.redis_url, s.redis_default_ttl_seconds)
