import os
import structlog

from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from infrastructure.database import db
from infrastructure.redis_client import redis_client
from infrastructure.meili_client import meili_client
from middleware.rate_limit import limiter

log = structlog.get_logger()


def _configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def _init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN", "")
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.1,
        )


def _create_app() -> FastAPI:
    _configure_structlog()
    _init_sentry()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await db.connect()
        await redis_client.connect()
        log.info("startup_complete", database="connected", redis="connected")
        yield
        await redis_client.disconnect()
        await db.disconnect()
        log.info("shutdown_complete")

    app = FastAPI(
        title="Safqa API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    _register_middleware(app)
    _register_routers(app)
    _setup_metrics(app)
    _register_exception_handlers(app)

    return app


def _register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        response = await call_next(request)
        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
        )
        return response


def _register_routers(app: FastAPI) -> None:
    from routers.alerts import router as alerts_router
    from routers.auth import router as auth_router
    from routers.health import router as health_router
    from routers.saved import router as saved_router
    from routers.tenders import router as tenders_router

    prefix = "/v1"
    app.include_router(health_router, prefix=prefix)
    app.include_router(auth_router, prefix=prefix)
    app.include_router(tenders_router, prefix=prefix)
    app.include_router(saved_router, prefix=prefix)
    app.include_router(alerts_router, prefix=prefix)


def _setup_metrics(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app, endpoint="/v1/metrics")


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        log.error("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
        )


app = _create_app()
