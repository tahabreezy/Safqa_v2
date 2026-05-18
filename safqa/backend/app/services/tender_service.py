from __future__ import annotations

import uuid
from typing import Any

from repositories.tender_repo import tender_repo


async def get_tender(tender_id: uuid.UUID) -> dict[str, Any] | None:
    return await tender_repo.get_by_id(tender_id)


async def get_tender_by_ref(ref: str) -> dict[str, Any] | None:
    return await tender_repo.get_by_ref(ref)


async def get_stats() -> dict[str, Any]:
    return await tender_repo.get_stats()


async def get_domains() -> list[dict[str, Any]]:
    return await tender_repo.get_domains()
