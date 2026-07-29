"""
Integration tests for src/main_app/public/routes/api/routes.py module.

These tests use real database operations via services to seed test data.
No database/ORM mocks are used - all tests interact with the real test database.
"""

from __future__ import annotations

import json

import pytest
from flask.testing import FlaskClient

from src.main_app.db.services import (
    CategoryService,
    InProcessService,
    LangService,
    ReportService,
)


@pytest.fixture
def seed_categories():
    """Seed category records into the database."""
    service = CategoryService()
    service.add_category(category="RTT", campaign="RTT", display="RTT")
    service.add_category(category="RTTVideo", campaign="RTTVideo", display="RTT Video")
    return service


@pytest.fixture
def seed_langs():
    """Seed language records into the database."""
    service = LangService()
    service.add_lang(code="en", autonym="English", name="English")
    service.add_lang(code="ar", autonym="العربية", name="Arabic")
    return service


@pytest.fixture
def seed_reports(seed_langs):
    """Seed report records into the database."""
    service = ReportService()
    service.add_report(
        title="Test Article 1",
        user="TestUser",
        lang="en",
        sourcetitle="Source 1",
        result="success",
        data='{"status": "ok"}',
    )
    service.add_report(
        title="Test Article 2",
        user="TestUser",
        lang="ar",
        sourcetitle="Source 2",
        result="error",
        data='{"status": "error"}',
    )
    return service


@pytest.fixture
def seed_in_process(seed_langs, seed_categories):
    """Seed in-process translation records into the database."""
    service = InProcessService()
    service.add_in_process(
        title="In Progress Article",
        user="Translator1",
        lang="en",
        cat="RTT",
        translate_type="lead",
        word=500,
    )
    return service


@pytest.fixture
def seed_pages(seed_categories, seed_langs):
    """Seed page records into the database."""
    from src.main_app.db.models import PageRecord
    from src.main_app.extensions import db

    page1 = PageRecord(
        title="Published Article 1",
        word=1000,
        translate_type="lead",
        cat="RTT",
        lang="en",
        user="Translator1",
        target="Published_Article_1",
        deleted=0,
    )
    page2 = PageRecord(
        title="Published Article 2",
        word=1500,
        translate_type="full",
        cat="RTTVideo",
        lang="ar",
        user="Translator2",
        target="Published_Article_2",
        deleted=0,
    )
    db.session.add(page1)
    db.session.add(page2)
    db.session.commit()
    return [page1, page2]


@pytest.fixture
def seed_user_pages(seed_pages, seed_categories):
    """Seed user page records into the database."""
    from src.main_app.db.models import UserPageRecord
    from src.main_app.extensions import db

    page = UserPageRecord(
        title="User Page Article",
        word=800,
        translate_type="lead",
        cat="RTT",
        lang="en",
        user="Translator1",
        target="User_Page_Article",
        deleted=0,
    )
    db.session.add(page)
    db.session.commit()
    return page


@pytest.fixture
def seed_views(seed_pages):
    """Seed view records into the database."""
    from src.main_app.db.models import ViewsNewRecord
    from src.main_app.extensions import db

    view1 = ViewsNewRecord(
        target="Published_Article_1",
        lang="en",
        year=2024,
        views=150,
    )
    view2 = ViewsNewRecord(
        target="Published_Article_2",
        lang="ar",
        year=2024,
        views=200,
    )
    db.session.add(view1)
    db.session.add(view2)
    db.session.commit()
    return [view1, view2]


@pytest.mark.integration
class TestApiPreflight:
    """Integration tests for API preflight endpoint."""

    def test_api_preflight_returns_cors_headers(self, mock_client: FlaskClient):
        """Test that OPTIONS endpoint returns correct CORS headers."""
        response = mock_client.options("/api/publish_reports")

        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Methods"] == "GET, OPTIONS"
        assert response.headers["Access-Control-Allow-Headers"] == "Content-Type"
        assert response.headers["Access-Control-Max-Age"] == "7200"


@pytest.mark.integration
class TestPublishReports:
    """Integration tests for publish_reports endpoint."""

    def test_publish_reports_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that publish_reports returns empty results when no reports exist."""
        response = mock_client.get("/api/publish_reports?limit=5")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["count"], int)
        assert data["count"] == 0

    def test_publish_reports_returns_seeded_data(self, mock_client: FlaskClient, seed_reports):
        """Test that publish_reports returns seeded report data."""
        response = mock_client.get("/api/publish_reports?limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 2

        titles = [r["title"] for r in data["results"]]
        assert "Test Article 1" in titles
        assert "Test Article 2" in titles

    def test_publish_reports_with_lang_filter(self, mock_client: FlaskClient, seed_reports):
        """Test that publish_reports filters by language."""
        response = mock_client.get("/api/publish_reports?lang=en&limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["count"] == 1
        assert data["results"][0]["lang"] == "en"

    def test_publish_reports_with_user_filter(self, mock_client: FlaskClient, seed_reports):
        """Test that publish_reports filters by user."""
        response = mock_client.get("/api/publish_reports?user=TestUser&limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["count"] == 2

    def test_publish_reports_validation_error(self, mock_client: FlaskClient):
        """Test that publish_reports handles invalid parameters."""
        response = mock_client.get("/api/publish_reports?year=invalid")

        assert response.status_code == 400
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "Validation failed"

    def test_publish_reports_select_fields(self, mock_client: FlaskClient, seed_reports):
        """Test that publish_reports respects select parameter."""
        response = mock_client.get("/api/publish_reports?select=id,title&limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert data["count"] > 0
        for item in data["results"]:
            assert "id" in item
            assert "title" in item


@pytest.mark.integration
class TestPublishReportsStats:
    """Integration tests for publish_reports_stats endpoint."""

    def test_publish_reports_stats_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that stats returns empty when no reports exist."""
        response = mock_client.get("/api/publish_reports/stats")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_publish_reports_stats_returns_seeded_data(self, mock_client: FlaskClient, seed_reports):
        """Test that stats returns correct aggregated data."""
        response = mock_client.get("/api/publish_reports/stats")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 2

        langs = [r["lang"] for r in data["results"]]
        assert "en" in langs
        assert "ar" in langs


@pytest.mark.integration
class TestInProcess:
    """Integration tests for in_process endpoint."""

    def test_in_process_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that in_process returns empty results when no records exist."""
        response = mock_client.get("/api/in_process?limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_in_process_returns_seeded_data(self, mock_client: FlaskClient, seed_in_process):
        """Test that in_process returns seeded translation records."""
        response = mock_client.get("/api/in_process?limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 1

        item = data["results"][0]
        assert item["title"] == "In Progress Article"
        assert item["user"] == "Translator1"
        assert item["lang"] == "en"
        assert item["cat"] == "RTT"

    def test_in_process_with_lang_filter(self, mock_client: FlaskClient, seed_in_process):
        """Test that in_process filters by language."""
        response = mock_client.get("/api/in_process?lang=en&limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["count"] == 1
        assert data["results"][0]["lang"] == "en"

    def test_in_process_with_invalid_lang_returns_empty(self, mock_client: FlaskClient, seed_in_process):
        """Test that in_process returns empty for non-existent language."""
        response = mock_client.get("/api/in_process?lang=fr&limit=5")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["count"] == 0


@pytest.mark.integration
class TestInProcessTotal:
    """Integration tests for in_process_total endpoint."""

    def test_in_process_total_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that in_process_total returns empty when no records exist."""
        response = mock_client.get("/api/in_process_total")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_in_process_total_returns_user_counts(self, mock_client: FlaskClient, seed_in_process):
        """Test that in_process_total returns correct user counts."""
        response = mock_client.get("/api/in_process_total")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 1

        item = data["results"][0]
        assert item["user"] == "Translator1"
        assert item["article_count"] == 1


@pytest.mark.integration
class TestPagesUsers:
    """Integration tests for pages_users endpoint."""

    def test_pages_users_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that pages_users returns empty when no records exist."""
        response = mock_client.get("/api/pages_users")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_pages_users_returns_seeded_data(self, mock_client: FlaskClient, seed_user_pages):
        """Test that pages_users returns seeded page records."""
        response = mock_client.get("/api/pages_users")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 1

        item = data["results"][0]
        assert item["title"] == "User Page Article"
        assert item["target"] == "User_Page_Article"


@pytest.mark.integration
class TestPagesWithViews:
    """Integration tests for pages_with_views endpoint."""

    def test_pages_with_views_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that pages_with_views returns empty when no records exist."""
        response = mock_client.get("/api/pages_with_views")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_pages_with_views_returns_seeded_data(self, mock_client: FlaskClient, seed_views):
        """Test that pages_with_views returns pages with view counts."""
        response = mock_client.get("/api/pages_with_views")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 2

        for item in data["results"]:
            assert "views" in item


@pytest.mark.integration
class TestCategories:
    """Integration tests for categories endpoint."""

    def test_categories_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that categories returns empty when no records exist."""
        response = mock_client.get("/api/categories")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_categories_returns_seeded_data(self, mock_client: FlaskClient, seed_categories):
        """Test that categories returns seeded category records."""
        response = mock_client.get("/api/categories")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 2

        category_names = [c["category"] for c in data["results"]]
        assert "RTT" in category_names
        assert "RTTVideo" in category_names


@pytest.mark.integration
class TestLangs:
    """Integration tests for langs endpoint."""

    def test_langs_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that langs returns empty when no records exist."""
        response = mock_client.get("/api/langs")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_langs_returns_seeded_data(self, mock_client: FlaskClient, seed_langs):
        """Test that langs returns seeded language records."""
        response = mock_client.get("/api/langs")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 2

        codes = [lang["code"] for lang in data["results"]]
        assert "en" in codes
        assert "ar" in codes


@pytest.mark.integration
class TestUsersByTranslationsCount:
    """Integration tests for users_by_translations_count endpoint."""

    def test_users_by_translations_count_returns_empty_when_no_data(self, mock_client: FlaskClient):
        """Test that users_by_translations_count returns empty when no records exist."""
        response = mock_client.get("/api/users_by_translations_count")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 0

    def test_users_by_translations_count_returns_sorted_data(self, mock_client: FlaskClient, seed_pages):
        """Test that users_by_translations_count returns sorted counts."""
        response = mock_client.get("/api/users_by_translations_count")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "results" in data
        assert "count" in data
        assert data["count"] == 2

        values = list(data["results"].values())
        assert values == sorted(values, reverse=True)


@pytest.mark.integration
class TestTopLangs:
    """Integration tests for top_langs endpoint."""

    def test_top_langs_returns_200(self, mock_client: FlaskClient):
        """Test that top_langs route is properly registered."""
        response = mock_client.get("/api/top_langs")

        assert response.status_code == 200
        assert response.content_type == "application/json"


@pytest.mark.integration
class TestTopUsers:
    """Integration tests for top_users endpoint."""

    def test_top_users_returns_200(self, mock_client: FlaskClient):
        """Test that top_users route is properly registered."""
        response = mock_client.get("/api/top_users")

        assert response.status_code == 200
        assert response.content_type == "application/json"


@pytest.mark.integration
class TestCorsHeaders:
    """Integration tests for CORS headers on API responses."""

    def test_cors_headers_present_on_get(self, mock_client: FlaskClient):
        """Test that CORS headers are present on GET API responses."""
        response = mock_client.get("/api/publish_reports?limit=1")

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    def test_cors_headers_present_on_options(self, mock_client: FlaskClient):
        """Test that CORS headers are present on OPTIONS responses."""
        response = mock_client.options("/api/publish_reports")

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
        assert "Access-Control-Max-Age" in response.headers
