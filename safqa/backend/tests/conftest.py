import os
import sys
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


@pytest.fixture(autouse=True, scope="session")
def _setup_env():
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("MEILI_URL", "http://localhost:7700")
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
    os.environ.setdefault("RESEND_API_KEY", "test-resend-key")


@pytest.fixture
def fake_user():
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "test@example.com",
        "created_at": "2026-01-01T00:00:00",
    }


@pytest.fixture
def app():
    from unittest.mock import MagicMock
    from app.main import app as _app
    from infrastructure.database import db as _db
    from infrastructure.redis_client import redis_client as _redis

    _db.connect = AsyncMock()
    _db.disconnect = AsyncMock()
    _redis.connect = AsyncMock()
    _redis.disconnect = AsyncMock()
    _redis._client = MagicMock()
    _redis._client.exists = AsyncMock(return_value=False)
    _redis._client.get = AsyncMock(return_value=None)
    _redis._client.set = AsyncMock()
    _redis._client.delete = AsyncMock()
    yield _app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(fake_user):
    from services.auth_service import create_access_token

    token = create_access_token(fake_user["id"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_get_current_user(app, fake_user):
    async def override(user_id=None):
        return fake_user

    from dependencies import get_current_user
    app.dependency_overrides[get_current_user] = override
    yield
    app.dependency_overrides.pop(get_current_user, None)
