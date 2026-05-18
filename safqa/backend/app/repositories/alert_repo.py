from __future__ import annotations

import json
import uuid
from typing import Any

from infrastructure.database import db


def _row_to_dict(row) -> dict[str, Any]:
    d = dict(row)
    if isinstance(d.get("filters"), str):
        d["filters"] = json.loads(d["filters"])
    return d

class AlertRepo:
    async def get_by_user(self, user_id: uuid.UUID) -> list[dict[str, Any]]:
        rows = await db.fetch(
            "SELECT * FROM saved_searches WHERE user_id = $1 ORDER BY created_at DESC",
            user_id,
        )
        return [_row_to_dict(r) for r in rows]

    async def create(
        self, user_id: uuid.UUID, filters: dict[str, Any], email: str, label: str
    ) -> dict[str, Any]:
        row = await db.fetchrow(
            """
            INSERT INTO saved_searches (user_id, label, filters, email)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            user_id,
            label,
            json.dumps(filters),
            email,
        )
        return _row_to_dict(row) if row else {}

    async def update_active(self, alert_id: uuid.UUID, is_active: bool) -> dict[str, Any] | None:
        row = await db.fetchrow(
            "UPDATE saved_searches SET is_active = $1 WHERE id = $2 RETURNING *",
            is_active,
            alert_id,
        )
        return _row_to_dict(row) if row else None

    async def delete(self, alert_id: uuid.UUID) -> bool:
        result = await db.execute(
            "DELETE FROM saved_searches WHERE id = $1",
            alert_id,
        )
        return "DELETE 1" in result

    async def get_active_alerts(self) -> list[dict[str, Any]]:
        rows = await db.fetch(
            "SELECT * FROM saved_searches WHERE is_active = true"
        )
        return [_row_to_dict(r) for r in rows]

    async def filter_unseen(
        self, alert_id: uuid.UUID, tender_ids: list[str]
    ) -> list[str]:
        if not tender_ids:
            return []
        rows = await db.fetch(
            """
            SELECT tender_id FROM alert_notifications
            WHERE saved_search_id = $1 AND tender_id = ANY($2::uuid[])
            """,
            alert_id,
            tender_ids,
        )
        seen = {str(r["tender_id"]) for r in rows}
        return [tid for tid in tender_ids if tid not in seen]

    async def record_notifications(
        self, alert_id: uuid.UUID, tender_ids: list[str]
    ) -> None:
        if not tender_ids:
            return
        for tid in tender_ids:
            try:
                await db.execute(
                    """
                    INSERT INTO alert_notifications (saved_search_id, tender_id)
                    VALUES ($1, $2)
                    ON CONFLICT DO NOTHING
                    """,
                    alert_id,
                    tid,
                )
            except Exception:
                pass


alert_repo = AlertRepo()
