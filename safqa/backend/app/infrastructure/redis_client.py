from __future__ import annotations

import os

import redis.asyncio as redis


class RedisClient:
    def __init__(self):
        self.url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = redis.from_url(self.url, decode_responses=True)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

    async def get(self, key: str) -> str | None:
        await self.connect()
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int = 1800) -> None:
        await self.connect()
        await self._client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.connect()
        await self._client.delete(key)

    async def blocklist_token(self, token: str, ttl: int) -> None:
        await self.connect()
        await self._client.set(f"blocklist:{token}", "1", ex=ttl)

    async def is_token_blocklisted(self, token: str) -> bool:
        await self.connect()
        return await self._client.exists(f"blocklist:{token}") > 0


redis_client = RedisClient()
