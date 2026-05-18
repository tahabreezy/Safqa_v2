from __future__ import annotations

import uuid
from typing import Any

from repositories.alert_repo import alert_repo


async def get_alerts(user_id: uuid.UUID) -> list[dict[str, Any]]:
    return await alert_repo.get_by_user(user_id)


async def create_alert(
    user_id: uuid.UUID, filters: dict[str, Any], email: str, label: str
) -> dict[str, Any]:
    return await alert_repo.create(user_id, filters, email, label)


async def toggle_alert(alert_id: uuid.UUID, is_active: bool) -> dict[str, Any] | None:
    return await alert_repo.update_active(alert_id, is_active)


async def delete_alert(alert_id: uuid.UUID) -> bool:
    return await alert_repo.delete(alert_id)
