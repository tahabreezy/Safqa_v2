from __future__ import annotations

import os
import time
from typing import Any

import asyncpg

from safqa_scraper.items import TenderItem


class PostgresPipeline:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "")
        self.conn: asyncpg.Connection | None = None
        self.stats: dict[str, dict[str, Any]] = {}

    def open_spider(self, spider) -> None:
        self.conn = None

    def _get_loop(self):
        import asyncio
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None

    async def _ensure_conn(self) -> asyncpg.Connection:
        if self.conn is None or self.conn.is_closed():
            self.conn = await asyncpg.connect(self.database_url)
        return self.conn

    async def process_item(self, item: TenderItem, spider) -> TenderItem:
        domain_code = item.get("domain_code", "unknown")
        if domain_code not in self.stats:
            self.stats[domain_code] = {
                "count_scraped": 0,
                "count_upserted": 0,
                "errors": [],
                "start_time": time.time(),
            }
        self.stats[domain_code]["count_scraped"] += 1

        conn = await self._ensure_conn()

        try:
            result = await conn.execute(
                """
                INSERT INTO tenders (
                    reference_number, title, authority, city,
                    domain_code, domain_label, procedure_type,
                    budget_raw, budget_mad,
                    published_at, deadline_at, source_url,
                    status, scraped_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'active', now())
                ON CONFLICT (reference_number)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    authority = EXCLUDED.authority,
                    city = EXCLUDED.city,
                    domain_label = EXCLUDED.domain_label,
                    procedure_type = EXCLUDED.procedure_type,
                    budget_raw = EXCLUDED.budget_raw,
                    budget_mad = EXCLUDED.budget_mad,
                    published_at = EXCLUDED.published_at,
                    deadline_at = EXCLUDED.deadline_at,
                    source_url = EXCLUDED.source_url,
                    status = EXCLUDED.status,
                    scraped_at = now()
                WHERE tenders.title IS DISTINCT FROM EXCLUDED.title
                   OR tenders.deadline_at IS DISTINCT FROM EXCLUDED.deadline_at
                """,
                item.get("reference_number"),
                item.get("title"),
                item.get("authority"),
                item.get("city"),
                item.get("domain_code"),
                item.get("domain_label"),
                item.get("procedure_type"),
                item.get("budget_raw"),
                item.get("budget_mad"),
                item.get("published_at"),
                item.get("deadline_at"),
                item.get("source_url"),
            )

            if "INSERT" in result:
                self.stats[domain_code]["count_upserted"] += 1
        except Exception as e:
            self.stats[domain_code]["errors"].append(
                {"url": item.get("source_url", ""), "error_message": str(e)}
            )
            spider.logger.error("PostgresPipeline error for %s: %s",
                                item.get("reference_number"), e)

        return item

    def close_spider(self, spider) -> None:
        import asyncio

        async def _close():
            for domain_code, s in self.stats.items():
                duration_ms = int((time.time() - s["start_time"]) * 1000)
                try:
                    await self._write_scrape_log(
                        domain_code, s["count_scraped"], s["count_upserted"],
                        duration_ms, s["errors"],
                    )
                except Exception as e:
                    spider.logger.error("Failed to write scrape_log for %s: %s",
                                        domain_code, e)
            if self.conn and not self.conn.is_closed():
                await self.conn.close()

        loop = self._get_loop()
        if loop and loop.is_running():
            asyncio.ensure_future(_close())
        else:
            asyncio.run(_close())

    async def _write_scrape_log(
        self, domain_code: str, count_scraped: int, count_upserted: int,
        duration_ms: int, errors: list[dict],
    ) -> None:
        conn = await self._ensure_conn()
        await conn.execute(
            """
            INSERT INTO scrape_logs (domain_code, count_scraped, count_upserted, duration_ms, errors)
            VALUES ($1, $2, $3, $4, $5::jsonb)
            """,
            domain_code, count_scraped, count_upserted, duration_ms,
            errors if errors else [],
        )
