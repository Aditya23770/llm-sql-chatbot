from typing import Any
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class DatabaseClient:
    def __init__(self, db_url: str) -> None:
        # Accepts postgresql+asyncpg:// URLs
        self._engine: AsyncEngine = create_async_engine(db_url, pool_size=5, max_overflow=10)

    async def get(self, sql: str, params: dict | None = None) -> list[dict[str, Any]]:
        """Execute a SELECT query and return rows as dicts."""
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("get() only accepts SELECT queries")
        async with self._engine.connect() as conn:
            result = await conn.execute(sqlalchemy.text(sql), params or {})
            return [dict(row) for row in result.mappings()]

    async def set(self, sql: str, params: dict | None = None) -> int:
        """Execute a write statement and return affected row count."""
        async with self._engine.begin() as conn:
            result = await conn.execute(sqlalchemy.text(sql), params or {})
            return result.rowcount

    async def close(self) -> None:
        await self._engine.dispose()
