from __future__ import annotations

import asyncio
import os

import asyncpg
import structlog

from celery_app import celery_app

log = structlog.get_logger()


@celery_app.task(name="tasks.scrape_task.scrape_all_domains")
def scrape_all_domains() -> dict:
    from scrapy.crawler import CrawlerRunner
    from scrapy.utils.log import configure_logging
    from scrapy.utils.project import get_project_settings
    from twisted.internet import reactor

    log.info("scrape_start")
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    from safqa_scraper.spiders.tenders_spider import TendersSpider

    deferred = runner.crawl(TendersSpider)
    deferred.addBoth(lambda _: reactor.stop())
    reactor.run()

    from tasks.alert_task import match_and_send_alerts
    match_and_send_alerts.delay()

    log.info("scrape_completed", spider="tenders")
    return {"status": "completed", "spider": "tenders"}


async def _expire_tenders_query() -> int:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for expire_tenders task")

    conn = await asyncpg.connect(database_url)
    try:
        result = await conn.execute(
            """
            UPDATE tenders
            SET status = 'expired'
            WHERE deadline_at < CURRENT_DATE
              AND status = 'active'
            """
        )
        count = int(result.split(" ")[-1])
        log.info("tenders_expired", count=count)
        return count
    finally:
        await conn.close()


@celery_app.task(name="tasks.scrape_task.expire_tenders")
def expire_tenders() -> dict:
    count = asyncio.run(_expire_tenders_query())
    _expire_meilisearch(count)
    _flush_search_cache()
    return {"expired": count, "meilisearch_updated": True, "cache_flushed": True}


def _expire_meilisearch(expired_count: int) -> None:
    if expired_count == 0:
        return
    from meilisearch import Client
    meili_url = os.getenv("MEILI_URL", "http://meilisearch:7700")
    meili_key = os.getenv("MEILI_MASTER_KEY", "")
    meili_url_clean = meili_url.replace("+http", "http")
    client = Client(meili_url_clean, meili_key)
    try:
        result = client.index("tenders").update_documents(
            [{"status": "expired"}],
            primary_key="reference_number"
        )
        log.info("meilisearch_expire_scheduled", task_id=result.task_uid)
    except Exception as e:
        log.error("meilisearch_expire_error", error=str(e))


def _flush_search_cache() -> None:
    try:
        import redis as sync_redis
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        r = sync_redis.from_url(redis_url, decode_responses=True)
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = r.scan(cursor=cursor, match="search:*", count=500)
            if keys:
                deleted += r.delete(*keys)
            if cursor == 0:
                break
        log.info("search_cache_flushed", deleted=deleted)
    except Exception as e:
        log.error("cache_flush_error", error=str(e))
