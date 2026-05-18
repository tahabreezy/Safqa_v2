from __future__ import annotations

import uuid
from typing import Any

from infrastructure.database import db


class SavedRepo:
    async def get_by_user(
        self, user_id: uuid.UUID, page: int = 1, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        offset = (page - 1) * limit
        rows = await db.fetch(
            """
            SELECT t.*
            FROM saved_tenders st
            JOIN tenders t ON t.id = st.tender_id
            WHERE st.user_id = $1
            ORDER BY st.saved_at DESC
            LIMIT $2 OFFSET $3
            """,
            user_id,
            limit,
            offset,
        )
        count_row = await db.fetchrow(
            "SELECT COUNT(*) AS total FROM saved_tenders WHERE user_id = $1",
            user_id,
        )
        total = count_row["total"] if count_row else 0
        return [dict(r) for r in rows], total

    async def save(self, user_id: uuid.UUID, tender_id: uuid.UUID) -> bool:
        try:
            await db.execute(
                """
                INSERT INTO saved_tenders (user_id, tender_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
                """,
                user_id,
                tender_id,
            )
            return True
        except Exception:
            return False

    async def delete(self, user_id: uuid.UUID, tender_id: uuid.UUID) -> bool:
        result = await db.execute(
            "DELETE FROM saved_tenders WHERE user_id = $1 AND tender_id = $2",
            user_id,
            tender_id,
        )
        return "DELETE 1" in result

    async def is_saved(self, user_id: uuid.UUID, tender_id: uuid.UUID) -> bool:
        row = await db.fetchrow(
            "SELECT 1 FROM saved_tenders WHERE user_id = $1 AND tender_id = $2",
            user_id,
            tender_id,
        )
        return row is not None


saved_repo = SavedRepo()
