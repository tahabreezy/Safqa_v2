import structlog

from fastapi import APIRouter
from infrastructure.database import db
from infrastructure.redis_client import redis_client
from infrastructure.meili_client import meili_client

log = structlog.get_logger()

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    deps = {
        "database": await _check_db(),
        "redis": await _check_redis(),
        "meilisearch": _check_meili(),
    }
    all_ok = all(deps.values())
    status_code = 200 if all_ok else 503

    from fastapi.responses import JSONResponse
    resp = JSONResponse(
        content={"status": "ok" if all_ok else "degraded", "dependencies": deps},
        status_code=status_code,
    )
    log.info("health_check", status="ok" if all_ok else "degraded", dependencies=deps)
    return resp


async def _check_db() -> bool:
    try:
        row = await db.fetchrow("SELECT 1 AS ok")
        return row is not None and row["ok"] == 1
    except Exception:
        return False


async def _check_redis() -> bool:
    try:
        await redis_client.connect()
        val = await redis_client.get("health:ping")
        return val is None or True
    except Exception:
        return False


def _check_meili() -> bool:
    try:
        health = meili_client.health()
        return health.get("status") == "available"
    except Exception:
        return False
