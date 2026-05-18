from __future__ import annotations

import asyncio
import os
from typing import Any

import asyncpg
import httpx
import structlog

from celery_app import celery_app
from safqa_scraper.filters import apply_filters, build_html_list

log = structlog.get_logger()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.alert_task.match_and_send_alerts",
)
def match_and_send_alerts(self) -> dict:
    return asyncio.run(_run_alert_matching())


async def _run_alert_matching() -> dict:
    database_url = os.getenv("DATABASE_URL")
    resend_api_key = os.getenv("RESEND_API_KEY")
    from_email = "noreply@safqa.ma"

    if not database_url:
        raise RuntimeError("DATABASE_URL is required for alert matching")

    log.info("alert_matching_start")
    conn = await asyncpg.connect(database_url)
    try:
        new_tenders = await conn.fetch(
            """
            SELECT id, reference_number, title, authority, city,
                   domain_code, domain_label, procedure_type,
                   budget_mad, published_at, deadline_at, source_url, status
            FROM tenders
            WHERE scraped_at > NOW() - INTERVAL '4 hours'
            """
        )

        if not new_tenders:
            log.info("alert_matching_no_new_tenders")
            return {"status": "no_new_tenders", "alerts_sent": 0}

        tender_data: list[dict[str, Any]] = [dict(t) for t in new_tenders]
        log.info("alert_matching_tenders_found", count=len(tender_data))

        alerts = await conn.fetch(
            "SELECT * FROM saved_searches WHERE is_active = true"
        )

        total_sent = 0
        for alert in alerts:
            alert_dict = dict(alert)
            alert_filters = alert_dict.get("filters", {})
            if not isinstance(alert_filters, dict):
                continue

            matching = apply_filters(tender_data, alert_filters)
            if not matching:
                continue

            matching_ids = [str(t["id"]) for t in matching]
            unseen = await _filter_unseen(conn, alert_dict["id"], matching_ids)
            if not unseen:
                continue

            unseen_tenders = [t for t in matching if str(t["id"]) in unseen]
            await _send_alert_email(
                resend_api_key, from_email, alert_dict, unseen_tenders
            )
            await _record_notifications(conn, alert_dict["id"], unseen)
            total_sent += 1
            log.info(
                "alert_sent",
                alert_id=str(alert_dict["id"]),
                tender_count=len(unseen),
            )

        log.info("alert_matching_completed", alerts_sent=total_sent)
        return {"status": "completed", "alerts_sent": total_sent}
    finally:
        await conn.close()


async def _filter_unseen(
    conn: asyncpg.Connection, alert_id: str, tender_ids: list[str]
) -> list[str]:
    if not tender_ids:
        return []
    rows = await conn.fetch(
        """
        SELECT tender_id FROM alert_notifications
        WHERE saved_search_id = $1::uuid AND tender_id = ANY($2::uuid[])
        """,
        alert_id,
        tender_ids,
    )
    seen = {str(r["tender_id"]) for r in rows}
    return [tid for tid in tender_ids if tid not in seen]


async def _record_notifications(
    conn: asyncpg.Connection, alert_id: str, tender_ids: list[str]
) -> None:
    if not tender_ids:
        return
    for tid in tender_ids:
        try:
            await conn.execute(
                """
                INSERT INTO alert_notifications (saved_search_id, tender_id)
                VALUES ($1::uuid, $2::uuid)
                ON CONFLICT DO NOTHING
                """,
                alert_id,
                tid,
            )
        except Exception:
            pass


async def _send_alert_email(
    api_key: str | None,
    from_email: str,
    alert: dict[str, Any],
    tenders: list[dict[str, Any]],
) -> None:
    if not api_key:
        return

    max_tenders = 10
    count = len(tenders)
    subject = (
        f"[Safqa Alert] {alert['label']} — {count} nouveau(x) appel(s) d'offres"
    )

    if count <= max_tenders:
        html = build_html_list(tenders)
    else:
        html = (
            f"<p>{count} nouveaux appels d'offres correspondent à votre alerte.</p>"
        )

    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.resend.com/email",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_email,
                "to": [alert["email"]],
                "subject": subject,
                "html": html,
            },
        )
