from __future__ import annotations

import os

import sentry_sdk
import structlog

from celery import Celery
from celery.schedules import crontab
from kombu import Queue

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    cache_logger_on_first_use=True,
)

_sentry_dsn = os.getenv("SENTRY_DSN", "")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        traces_sample_rate=0.1,
    )

broker_url = os.getenv("RABBITMQ_URL", "")
result_backend = os.getenv("REDIS_URL", "")

celery_app = Celery("safqa", broker=broker_url, backend=result_backend)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_queues=(
        Queue("default", routing_key="default"),
        Queue("dlq", routing_key="dlq"),
    ),
    task_default_queue="default",
    task_default_routing_key="default",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "tasks.alert_task.match_and_send_alerts": {"queue": "default"},
        "tasks.scrape_task.scrape_all_domains": {"queue": "default"},
        "tasks.scrape_task.expire_tenders": {"queue": "default"},
    },
)

celery_app.conf.beat_schedule = {
    "scrape-all-domains": {
        "task": "tasks.scrape_task.scrape_all_domains",
        "schedule": crontab(minute=0, hour="*/4"),
    },
    "expire-tenders": {
        "task": "tasks.scrape_task.expire_tenders",
        "schedule": crontab(minute=0, hour=2),
    },
}
