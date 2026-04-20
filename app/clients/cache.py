import json
import hashlib
import redis.asyncio as aioredis


class CacheClient:
    def __init__(self, redis_url: str, default_ttl: int = 3600) -> None:
        self._client = aioredis.from_url(redis_url, decode_responses=True)
        self._ttl = default_ttl

    @staticmethod
    def make_key(query: str, provider: str) -> str:
        normalized = query.strip().lower()
        raw = f"{provider}:{normalized}"
        return "sqlchat:" + hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, key: str) -> dict | None:
        val = await self._client.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: dict, ttl: int | None = None) -> None:
        await self._client.setex(key, ttl or self._ttl, json.dumps(value))

    async def invalidate(self, key: str) -> None:
        await self._client.delete(key)

    async def close(self) -> None:
        await self._client.aclose()
