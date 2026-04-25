"""
Integration tests for src/sqlalchemy_app/public/routes/api/routes.py module.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient

from src.sqlalchemy_app.shared.schemas import PublishReportsQuerySchema


@pytest.mark.integration
class TestApiRoutes:
    """Integration tests for API routes."""

    def test_publish_reports_preflight(self, client: FlaskClient):
        """Test that publish_reports OPTIONS endpoint returns correct CORS headers."""
        response = client.options("/api/publish_reports")

        # Should return 200 with CORS headers
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Methods"] == "GET, OPTIONS"
        assert response.headers["Access-Control-Allow-Headers"] == "Content-Type"
        assert response.headers["Access-Control-Max-Age"] == "7200"

    def test_publish_reports_success(self, client: FlaskClient):
        """Test that publish_reports GET endpoint returns successful response."""
        response = client.get("/api/publish_reports?limit=5")

        # Should return JSON response
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["count"], int)

    def test_publish_reports_with_filters(self, client: FlaskClient):
        """Test that publish_reports accepts various filter parameters."""
        response = client.get("/api/publish_reports?year=2023&month=1&lang=en&limit=10")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data

    def test_publish_reports_validation_error(self, client: FlaskClient):
        """Test that publish_reports handles invalid parameters."""
        # Invalid year (non-numeric)
        response = client.get("/api/publish_reports?year=invalid")

        assert response.status_code == 400
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "Validation failed"

    def test_publish_reports_select_fields(self, client: FlaskClient):
        """Test that publish_reports respects select parameter."""
        response = client.get("/api/publish_reports?select=id,title&limit=5")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        # Check that only selected fields are present (if any results)
        if data["results"]:
            for item in data["results"]:
                # Should only have id and title fields (plus potentially others from to_dict)
                assert "id" in item
                assert "title" in item

    def test_publish_reports_stats_success(self, client: FlaskClient):
        """Test that publish_reports_stats endpoint returns stats."""
        response = client.get("/api/publish_reports_stats")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)

    def test_in_process_success(self, client: FlaskClient):
        """Test that in_process endpoint returns in-process translations."""
        response = client.get("/api/in_process?limit=5")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)

        # Check structure of returned items
        if data["results"]:
            item = data["results"][0]
            expected_fields = {
                "id", "title", "user", "lang", "cat", "translate_type",
                "word", "add_date", "campaign", "autonym"
            }
            assert set(item.keys()) >= expected_fields

    def test_in_process_with_lang_filter(self, client: FlaskClient):
        """Test that in_process endpoint filters by language."""
        response = client.get("/api/in_process?lang=en&limit=5")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data

    def test_in_process_total_success(self, client: FlaskClient):
        """Test that in_process_total endpoint returns user counts."""
        response = client.get("/api/in_process_total")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)

        # Check structure if results exist
        if data["results"]:
            item = data["results"][0]
            assert "user" in item
            assert "article_count" in item

    def test_pages_users_success(self, client: FlaskClient):
        """Test that pages_users endpoint returns pages with users."""
        response = client.get("/api/pages_users")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)
        assert data["count"] <= 100  # Default limit

    def test_pages_with_views_success(self, client: FlaskClient):
        """Test that pages_with_views endpoint returns pages with view counts."""
        response = client.get("/api/pages_with_views")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)

        # Check that views field is present if results exist
        if data["results"]:
            item = data["results"][0]
            assert "views" in item

    def test_categories_success(self, client: FlaskClient):
        """Test that categories endpoint returns category records."""
        response = client.get("/api/categories")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)

    def test_users_by_translations_count_success(self, client: FlaskClient):
        """Test that users_by_translations_count endpoint returns sorted counts."""
        response = client.get("/api/users_by_translations_count")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], dict)  # This endpoint returns a dict

        # Check that results are sorted by value descending
        if data["results"]:
            values = list(data["results"].values())
            assert values == sorted(values, reverse=True)

    def test_langs_success(self, client: FlaskClient):
        """Test that langs endpoint returns language records."""
        response = client.get("/api/langs")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)

    def test_top_langs_route(self, client: FlaskClient):
        """Test that top_langs route is properly registered."""
        response = client.get("/api/top_langs")

        # Should return 200 or handle gracefully if no data
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_top_users_route(self, client: FlaskClient):
        """Test that top_users route is properly registered."""
        response = client.get("/api/top_users")

        # Should return 200 or handle gracefully if no data
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_publish_reports_internal_error_handling(self, client: FlaskClient):
        """Test that publish_reports handles internal errors gracefully."""
        with patch('src.sqlalchemy_app.public.routes.api.routes.query_reports_with_filters') as mock_query:
            mock_query.side_effect = Exception("Database error")

            response = client.get("/api/publish_reports?limit=5")

            assert response.status_code == 500
            assert response.content_type == "application/json"

            data = json.loads(response.data)
            assert "error" in data
            assert "internal error" in data["error"].lower()

    def test_in_process_internal_error_handling(self, client: FlaskClient):
        """Test that in_process handles internal errors gracefully."""
        with patch('src.sqlalchemy_app.public.routes.api.routes.get_session') as mock_session:
            mock_session.side_effect = Exception("Database error")

            response = client.get("/api/in_process?limit=5")

            assert response.status_code == 500
            assert response.content_type == "application/json"

            data = json.loads(response.data)
            assert "error" in data
            assert "internal error" in data["error"].lower()

    def test_cors_headers_present(self, client: FlaskClient):
        """Test that CORS headers are present on API responses."""
        response = client.get("/api/publish_reports?limit=1")

        assert response.status_code == 200
        # Check that CORS headers are present (added by @check_cors decorator)
        assert "Access-Control-Allow-Origin" in response.headers

    def test_empty_results_handling(self, client: FlaskClient):
        """Test that endpoints handle empty results correctly."""
        # Use a valid year that's unlikely to have data
        response = client.get("/api/publish_reports?year=2000&limit=5")

        # This might return 200 (if no data) or 400 (if validation fails for other reasons)
        # Either way, we should get a JSON response
        assert response.content_type == "application/json"

        data = json.loads(response.data)
        # If successful, check for expected structure
        assert response.status_code == 200
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)
        assert data["count"] >= 0  # Should be 0 or more
        # If validation error, that's also acceptable for this test
        # elif response.status_code == 400:
        #     assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__])
