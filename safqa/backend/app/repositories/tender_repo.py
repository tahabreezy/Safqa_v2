from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from infrastructure.database import db


class TenderRepo:
    async def get_by_ids(self, ids: list[str]) -> list[dict[str, Any]]:
        rows = await db.fetch(
            "SELECT * FROM tenders WHERE id = ANY($1::uuid[])",
            ids,
        )
        return [dict(r) for r in rows]

    async def get_by_id(self, tender_id: uuid.UUID) -> dict[str, Any] | None:
        row = await db.fetchrow(
            "SELECT * FROM tenders WHERE id = $1",
            tender_id,
        )
        return dict(row) if row else None

    async def get_by_ref(self, ref: str) -> dict[str, Any] | None:
        row = await db.fetchrow(
            "SELECT * FROM tenders WHERE reference_number = $1",
            ref,
        )
        return dict(row) if row else None

    async def get_stats(self) -> dict[str, Any]:
        row = await db.fetchrow(
            """
            SELECT
                COUNT(*) FILTER (WHERE status = 'active') AS active,
                COUNT(*) FILTER (WHERE status = 'active' AND deadline_at - CURRENT_DATE <= 14) AS urgent,
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - 7) AS new_this_week,
                COUNT(*) AS total
            FROM tenders
            """
        )
        return dict(row) if row else {"active": 0, "urgent": 0, "new_this_week": 0, "total": 0}

    async def get_domains(self) -> list[dict[str, Any]]:
        rows = await db.fetch(
            """
            SELECT domain_code, domain_label, COUNT(*) AS count
            FROM tenders
            WHERE status = 'active'
            GROUP BY domain_code, domain_label
            ORDER BY domain_code
            """
        )
        return [dict(r) for r in rows]


tender_repo = TenderRepo()
