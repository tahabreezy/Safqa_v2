from safqa_scraper.filters import apply_filters, matches_tender, build_html_list


def _make_tender(**overrides) -> dict:
    defaults = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "reference_number": "REF-001",
        "title": "Test Tender",
        "authority": "Test Authority",
        "city": "Casablanca",
        "domain_code": "1.15",
        "domain_label": "Construction",
        "procedure_type": "AO Ouvert",
        "budget_mad": 1000000.0,
        "published_at": "2026-01-01",
        "deadline_at": "2026-02-01",
        "source_url": "https://example.com/tender/1",
        "status": "active",
    }
    defaults.update(overrides)
    return defaults


class TestMatchesTender:
    def test_all_filters_match(self):
        tender = _make_tender(domain_code="1.15", city="Casablanca")
        filters = {"domain_code": "1.15", "city": "Casablanca"}
        assert matches_tender(tender, filters) is True

    def test_partial_match_returns_false(self):
        tender = _make_tender(city="Rabat")
        filters = {"domain_code": "1.15", "city": "Casablanca"}
        assert matches_tender(tender, filters) is False

    def test_no_match(self):
        tender = _make_tender(domain_code="2.10")
        filters = {"domain_code": "1.15"}
        assert matches_tender(tender, filters) is False

    def test_empty_filters_returns_true(self):
        assert matches_tender(_make_tender(), {}) is True

    def test_none_field_returns_false(self):
        tender = _make_tender(procedure_type=None)
        assert matches_tender(tender, {"procedure_type": "AO Ouvert"}) is False


class TestApplyFilters:
    def test_all_filters_match_returns_all(self):
        tenders = [
            _make_tender(domain_code="1.15", city="Casablanca"),
            _make_tender(domain_code="1.15", city="Rabat"),
        ]
        result = apply_filters(tenders, {"domain_code": "1.15"})
        assert len(result) == 2

    def test_partial_match_returns_subset(self):
        tenders = [
            _make_tender(domain_code="1.15", city="Casablanca"),
            _make_tender(domain_code="2.10", city="Rabat"),
        ]
        result = apply_filters(tenders, {"city": "Rabat"})
        assert len(result) == 1
        assert result[0]["city"] == "Rabat"

    def test_no_match_returns_empty(self):
        tenders = [_make_tender(domain_code="1.15"), _make_tender(domain_code="2.10")]
        result = apply_filters(tenders, {"domain_code": "3.99"})
        assert result == []

    def test_empty_filters_returns_all(self):
        result = apply_filters([_make_tender(), _make_tender()], {})
        assert len(result) == 2

    def test_empty_tenders_list(self):
        assert apply_filters([], {"domain_code": "1.15"}) == []

    def test_multiple_filters_match(self):
        tenders = [
            _make_tender(domain_code="1.15", city="Casablanca", procedure_type="AO Ouvert"),
            _make_tender(domain_code="1.15", city="Casablanca", procedure_type="AO Restreint"),
        ]
        result = apply_filters(tenders, {"domain_code": "1.15", "city": "Casablanca"})
        assert len(result) == 2

    def test_multiple_filters_partial_match(self):
        tenders = [
            _make_tender(domain_code="1.15", city="Casablanca", procedure_type="AO Ouvert"),
            _make_tender(domain_code="1.15", city="Rabat", procedure_type="AO Ouvert"),
        ]
        result = apply_filters(tenders, {"city": "Casablanca", "procedure_type": "AO Ouvert"})
        assert len(result) == 1
        assert result[0]["city"] == "Casablanca"


class TestBuildHtmlList:
    def test_single_tender(self):
        tenders = [_make_tender(title="Test", authority="Auth")]
        html = build_html_list(tenders)
        assert "<strong>Test</strong>" in html
        assert "Auth" in html
        assert "<ul>" in html
        assert "</ul>" in html

    def test_multiple_tenders(self):
        tenders = [
            _make_tender(title="Tender A"),
            _make_tender(title="Tender B"),
        ]
        html = build_html_list(tenders)
        assert html.count("<li>") == 2

    def test_empty_list(self):
        assert build_html_list([]) == "<ul></ul>"
