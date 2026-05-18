from __future__ import annotations

import os

import asyncpg


class DatabasePool:
    def __init__(self):
        raw = os.getenv("DATABASE_URL", "")
        self.dsn = raw.replace("postgresql+asyncpg://", "postgresql://").replace("postgres+asyncpg://", "postgres://")
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=2,
                max_size=10,
            )

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args) -> str:
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


db = DatabasePool()
