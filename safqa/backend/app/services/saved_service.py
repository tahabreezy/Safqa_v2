from __future__ import annotations

import uuid
from typing import Any

from repositories.saved_repo import saved_repo


async def get_saved(
    user_id: uuid.UUID, page: int = 1, limit: int = 20
) -> tuple[list[dict[str, Any]], int]:
    return await saved_repo.get_by_user(user_id, page=page, limit=limit)


async def save_tender(user_id: uuid.UUID, tender_id: uuid.UUID) -> bool:
    return await saved_repo.save(user_id, tender_id)


async def unsave_tender(user_id: uuid.UUID, tender_id: uuid.UUID) -> bool:
    return await saved_repo.delete(user_id, tender_id)
