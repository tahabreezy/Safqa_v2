from __future__ import annotations

import uuid
from typing import Any

from infrastructure.database import db


class UserRepo:
    async def create(self, email: str, password_hash: str) -> dict[str, Any]:
        row = await db.fetchrow(
            """
            INSERT INTO users (email, password_hash)
            VALUES ($1, $2)
            RETURNING id, email, created_at
            """,
            email,
            password_hash,
        )
        return dict(row) if row else {}

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        row = await db.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email,
        )
        return dict(row) if row else None

    async def get_by_id(self, user_id: uuid.UUID) -> dict[str, Any] | None:
        row = await db.fetchrow(
            "SELECT id, email, created_at FROM users WHERE id = $1",
            user_id,
        )
        return dict(row) if row else None


user_repo = UserRepo()
