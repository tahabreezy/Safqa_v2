from unittest.mock import AsyncMock, patch


class TestHealth:
    def test_all_ok(self, client):
        with (
            patch("infrastructure.database.db.fetchrow", AsyncMock(return_value={"ok": 1})),
            patch("infrastructure.redis_client.redis_client.get", AsyncMock(return_value=None)),
            patch("infrastructure.meili_client.meili_client.health", return_value={"status": "available"}),
        ):
            resp = client.get("/v1/health")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["dependencies"]["database"] is True
        assert data["dependencies"]["redis"] is True
        assert data["dependencies"]["meilisearch"] is True

    def test_db_down_returns_503(self, client):
        with (
            patch("infrastructure.database.db.fetchrow", AsyncMock(side_effect=Exception("DB error"))),
            patch("infrastructure.redis_client.redis_client.get", AsyncMock(return_value=None)),
            patch("infrastructure.meili_client.meili_client.health", return_value={"status": "available"}),
        ):
            resp = client.get("/v1/health")

        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["database"] is False
        assert data["dependencies"]["redis"] is True
        assert data["dependencies"]["meilisearch"] is True

    def test_redis_down_returns_503(self, client):
        with (
            patch("infrastructure.database.db.fetchrow", AsyncMock(return_value={"ok": 1})),
            patch("infrastructure.redis_client.redis_client.get", AsyncMock(side_effect=Exception("Redis error"))),
            patch("infrastructure.meili_client.meili_client.health", return_value={"status": "available"}),
        ):
            resp = client.get("/v1/health")

        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["database"] is True
        assert data["dependencies"]["redis"] is False
        assert data["dependencies"]["meilisearch"] is True

    def test_meili_down_returns_503(self, client):
        with (
            patch("infrastructure.database.db.fetchrow", AsyncMock(return_value={"ok": 1})),
            patch("infrastructure.redis_client.redis_client.get", AsyncMock(return_value=None)),
            patch("infrastructure.meili_client.meili_client.health", side_effect=Exception("Meili error")),
        ):
            resp = client.get("/v1/health")

        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["database"] is True
        assert data["dependencies"]["redis"] is True
        assert data["dependencies"]["meilisearch"] is False

    def test_all_down_returns_503(self, client):
        with (
            patch("infrastructure.database.db.fetchrow", AsyncMock(return_value=None)),
            patch("infrastructure.redis_client.redis_client.get", AsyncMock(side_effect=Exception("Redis error"))),
            patch("infrastructure.meili_client.meili_client.health", return_value={"status": "unavailable"}),
        ):
            resp = client.get("/v1/health")

        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["database"] is False
        assert data["dependencies"]["redis"] is False
        assert data["dependencies"]["meilisearch"] is False

    def test_cache_miss_still_ok(self, client):
        with (
            patch("infrastructure.database.db.fetchrow", AsyncMock(return_value={"ok": 1})),
            patch("infrastructure.redis_client.redis_client.get", AsyncMock(return_value=None)),
            patch("infrastructure.meili_client.meili_client.health", return_value={"status": "available"}),
        ):
            resp = client.get("/v1/health")

        assert resp.status_code == 200
