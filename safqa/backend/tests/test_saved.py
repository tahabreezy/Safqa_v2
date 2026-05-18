import uuid
from unittest.mock import AsyncMock, patch


def _fake_tender(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "reference_number": "REF-001",
        "title": "Construction Route",
        "authority": "Ministère",
        "city": "Casablanca",
        "domain_code": "1.15",
        "domain_label": "Construction",
        "procedure_type": "AO Ouvert",
        "budget_mad": 1_000_000.0,
        "published_at": "2026-01-01",
        "deadline_at": "2026-02-01",
        "source_url": "https://example.com/tender/1",
        "status": "active",
    }
    defaults.update(overrides)
    return defaults


class TestListSaved:
    ROUTE = "/v1/saved"

    def test_returns_saved(self, client, mock_get_current_user):
        rows = [_fake_tender(), _fake_tender()]
        with patch("routers.saved.get_saved", AsyncMock(return_value=(rows, 2))):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2
        assert data["total"] == 2
        assert data["page"] == 1

    def test_empty(self, client, mock_get_current_user):
        with patch("routers.saved.get_saved", AsyncMock(return_value=([], 0))):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        assert resp.json()["data"] == []
        assert resp.json()["total"] == 0

    def test_pagination(self, client, mock_get_current_user):
        rows = [_fake_tender()]
        with patch("routers.saved.get_saved", AsyncMock(return_value=(rows, 25))):
            resp = client.get(self.ROUTE + "?page=2&limit=5")

        assert resp.status_code == 200
        assert resp.json()["page"] == 2

    def test_requires_auth(self, client):
        resp = client.get(self.ROUTE)
        assert resp.status_code == 401

    def test_passes_user_id(self, client, mock_get_current_user, fake_user):
        with patch("routers.saved.get_saved", AsyncMock(return_value=([], 0))) as mock:
            client.get(self.ROUTE)

        uid = mock.call_args[0][0]
        assert str(uid) == fake_user["id"]


class TestSaveTender:
    ROUTE = "/v1/saved/"

    def test_save_success(self, client, mock_get_current_user):
        tid = uuid.uuid4()
        with patch("routers.saved.save_tender", AsyncMock(return_value=True)):
            resp = client.post(self.ROUTE + str(tid))

        assert resp.status_code == 200
        assert resp.json()["status"] == "saved"

    def test_save_not_found_returns_404(self, client, mock_get_current_user):
        with patch("routers.saved.save_tender", AsyncMock(return_value=False)):
            resp = client.post(self.ROUTE + str(uuid.uuid4()))

        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.post(self.ROUTE + str(uuid.uuid4()))
        assert resp.status_code == 401


class TestUnsaveTender:
    ROUTE = "/v1/saved/"

    def test_unsave_success(self, client, mock_get_current_user):
        tid = uuid.uuid4()
        with patch("routers.saved.unsave_tender", AsyncMock(return_value=True)):
            resp = client.delete(self.ROUTE + str(tid))

        assert resp.status_code == 200
        assert resp.json()["status"] == "removed"

    def test_unsave_not_found_returns_404(self, client, mock_get_current_user):
        with patch("routers.saved.unsave_tender", AsyncMock(return_value=False)):
            resp = client.delete(self.ROUTE + str(uuid.uuid4()))

        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.delete(self.ROUTE + str(uuid.uuid4()))
        assert resp.status_code == 401
