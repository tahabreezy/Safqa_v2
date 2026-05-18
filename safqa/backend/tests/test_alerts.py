import uuid
from unittest.mock import AsyncMock, patch


def _fake_alert(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "label": "Construction Alerts",
        "filters": {"domain_code": "1.15"},
        "email": "user@example.com",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00",
    }
    defaults.update(overrides)
    return defaults


class TestListAlerts:
    ROUTE = "/v1/alerts"

    def test_returns_alerts(self, client, mock_get_current_user):
        alerts = [_fake_alert(), _fake_alert()]
        with patch("routers.alerts.get_alerts", AsyncMock(return_value=alerts)):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["label"] == "Construction Alerts"

    def test_empty(self, client, mock_get_current_user):
        with patch("routers.alerts.get_alerts", AsyncMock(return_value=[])):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        assert resp.json() == []

    def test_requires_auth(self, client):
        resp = client.get(self.ROUTE)
        assert resp.status_code == 401

    def test_passes_user_id(self, client, mock_get_current_user, fake_user):
        with patch("routers.alerts.get_alerts", AsyncMock(return_value=[])) as mock:
            client.get(self.ROUTE)

        uid = mock.call_args[0][0]
        assert str(uid) == fake_user["id"]


class TestCreateAlert:
    ROUTE = "/v1/alerts"

    def test_creates_alert(self, client, mock_get_current_user):
        alert = _fake_alert(label="My Alert")
        with patch("routers.alerts.create_alert", AsyncMock(return_value=alert)):
            resp = client.post(
                self.ROUTE,
                json={
                    "filters": {"domain_code": "1.15"},
                    "email": "me@example.com",
                    "label": "My Alert",
                },
            )

        assert resp.status_code == 201
        assert resp.json()["label"] == "My Alert"

    def test_requires_auth(self, client):
        resp = client.post(
            self.ROUTE,
            json={"filters": {}, "email": "me@example.com", "label": "Test"},
        )
        assert resp.status_code == 401

    def test_validates_email(self, client, mock_get_current_user):
        resp = client.post(
            self.ROUTE,
            json={"filters": {}, "email": "bad-email", "label": "Test"},
        )
        assert resp.status_code == 422


class TestToggleAlert:
    ROUTE = "/v1/alerts/"

    def test_toggle_active(self, client, mock_get_current_user):
        aid = uuid.uuid4()
        alert = _fake_alert(id=str(aid), is_active=False)
        with patch("routers.alerts.toggle_alert", AsyncMock(return_value=alert)):
            resp = client.patch(self.ROUTE + str(aid), json={"is_active": False})

        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_toggle_not_found_returns_404(self, client, mock_get_current_user):
        with patch("routers.alerts.toggle_alert", AsyncMock(return_value=None)):
            resp = client.patch(self.ROUTE + str(uuid.uuid4()), json={"is_active": True})

        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.patch(self.ROUTE + str(uuid.uuid4()), json={"is_active": True})
        assert resp.status_code == 401


class TestDeleteAlert:
    ROUTE = "/v1/alerts/"

    def test_delete_success(self, client, mock_get_current_user):
        with patch("routers.alerts.delete_alert", AsyncMock(return_value=True)):
            resp = client.delete(self.ROUTE + str(uuid.uuid4()))

        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

    def test_delete_not_found_returns_404(self, client, mock_get_current_user):
        with patch("routers.alerts.delete_alert", AsyncMock(return_value=False)):
            resp = client.delete(self.ROUTE + str(uuid.uuid4()))

        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.delete(self.ROUTE + str(uuid.uuid4()))
        assert resp.status_code == 401
