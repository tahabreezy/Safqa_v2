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


def _search_result(hits, total, page=1, limit=20):
    from infrastructure.meili_client import SearchResult
    return SearchResult(hits=hits, total=total, page=page, limit=limit)


class TestListTenders:
    ROUTE = "/v1/tenders"

    def test_empty_search(self, client):
        result = _search_result([], 0)
        with patch("routers.tenders.search_tenders", AsyncMock(return_value=result)):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        data = resp.json()
        assert data["data"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["total_pages"] == 1

    def test_with_results(self, client):
        hits = [_fake_tender(reference_number="REF-001"), _fake_tender(reference_number="REF-002")]
        result = _search_result(hits, 2)
        with patch("routers.tenders.search_tenders", AsyncMock(return_value=result)):
            resp = client.get(self.ROUTE + "?q=construction")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2
        assert data["total"] == 2
        assert data["total_pages"] == 1

    def test_pagination(self, client):
        hits = [_fake_tender() for _ in range(5)]
        result = _search_result(hits, 25, page=2, limit=5)
        with patch("routers.tenders.search_tenders", AsyncMock(return_value=result)):
            resp = client.get(self.ROUTE + "?page=2&limit=5")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 5
        assert data["total"] == 25
        assert data["page"] == 2
        assert data["total_pages"] == 5

    def test_with_filters(self, client):
        hits = [_fake_tender(domain_code="1.15")]
        result = _search_result(hits, 1)
        with patch("routers.tenders.search_tenders", AsyncMock(return_value=result)) as mock:
            resp = client.get(self.ROUTE + "?domain=1.15&city=Casablanca&type=AO+Ouvert&status=active")

        assert resp.status_code == 200
        mock.assert_called_once()
        kwargs = mock.call_args[1]
        assert kwargs["domain"] == "1.15"
        assert kwargs["city"] == "Casablanca"
        assert kwargs["type"] == "AO Ouvert"
        assert kwargs["status"] == "active"

    def test_urgent_computed(self, client):
        from datetime import date, timedelta
        near = date.today() + timedelta(days=3)
        hits = [_fake_tender(deadline_at=near.isoformat())]
        result = _search_result(hits, 1)
        with patch("routers.tenders.search_tenders", AsyncMock(return_value=result)):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        assert resp.json()["data"][0]["is_urgent"] is True

    def test_not_urgent(self, client):
        from datetime import date, timedelta
        far = date.today() + timedelta(days=30)
        hits = [_fake_tender(deadline_at=far.isoformat())]
        result = _search_result(hits, 1)
        with patch("routers.tenders.search_tenders", AsyncMock(return_value=result)):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        assert resp.json()["data"][0]["is_urgent"] is False

    def test_validation_page_ge_1(self, client):
        resp = client.get(self.ROUTE + "?page=0")
        assert resp.status_code == 422

    def test_validation_limit_le_100(self, client):
        resp = client.get(self.ROUTE + "?limit=200")
        assert resp.status_code == 422


class TestTendersStats:
    ROUTE = "/v1/tenders/stats"

    def test_returns_stats(self, client):
        stats = {"active": 100, "urgent": 10, "new_this_week": 5, "total": 500}
        with patch("routers.tenders.get_stats", AsyncMock(return_value=stats)):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        assert resp.json() == stats


class TestTendersDomains:
    ROUTE = "/v1/tenders/domains"

    def test_returns_domains(self, client):
        domains = [
            {"domain_code": "1.15", "domain_label": "Construction", "count": 10},
            {"domain_code": "2.10", "domain_label": "IT", "count": 5},
        ]
        with patch("routers.tenders.get_domains", AsyncMock(return_value=domains)):
            resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        assert len(resp.json()) == 2
        assert resp.json()[0]["domain_code"] == "1.15"


class TestTendersByRef:
    ROUTE = "/v1/tenders/ref/"

    def test_found(self, client):
        tender = _fake_tender()
        with patch("routers.tenders.get_tender_by_ref", AsyncMock(return_value=tender)):
            resp = client.get(self.ROUTE + "REF-001")

        assert resp.status_code == 200
        assert resp.json()["reference_number"] == "REF-001"

    def test_not_found_returns_404(self, client):
        with patch("routers.tenders.get_tender_by_ref", AsyncMock(return_value=None)):
            resp = client.get(self.ROUTE + "INVALID")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Tender not found"


class TestTendersDetail:
    ROUTE = "/v1/tenders/"

    def test_found(self, client):
        tid = uuid.uuid4()
        tender = _fake_tender(id=str(tid))
        with patch("routers.tenders.get_tender", AsyncMock(return_value=tender)):
            resp = client.get(self.ROUTE + str(tid))

        assert resp.status_code == 200
        assert resp.json()["id"] == str(tid)

    def test_not_found_returns_404(self, client):
        with patch("routers.tenders.get_tender", AsyncMock(return_value=None)):
            resp = client.get(self.ROUTE + "550e8400-e29b-41d4-a716-446655440000")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Tender not found"

    def test_invalid_uuid_returns_422(self, client):
        resp = client.get(self.ROUTE + "not-a-uuid")
        assert resp.status_code == 422
