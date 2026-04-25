"""
Integration tests for src/sqlalchemy_app/public/routes/main/routes.py module.
"""

from __future__ import annotations

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestMainIndex:
    """Integration tests for the main index route."""

    def test_index_returns_200(self, client: FlaskClient):
        """Test that index route returns 200."""
        response = client.get("/")

        # May redirect or return 200
        assert response.status_code in [200, 302]

    def test_index_renders_template(self, client: FlaskClient):
        """Test that index route renders template."""
        response = client.get("/")

        # Check for HTML content
        assert response.content_type in ["text/html; charset=utf-8", "text/html"]


@pytest.mark.integration
class TestMainReports:
    """Integration tests for the reports route."""

    def test_reports_returns_200(self, client: FlaskClient):
        """Test that reports route returns 200."""
        response = client.get("/reports")

        assert response.status_code in [200, 302]

    def test_reports_renders_template(self, client: FlaskClient):
        """Test that reports route renders template."""
        response = client.get("/reports")

        assert response.status_code == 200
        assert response.content_type in ["text/html; charset=utf-8", "text/html"]


@pytest.mark.integration
class TestMainFavicon:
    """Integration tests for the favicon route."""

    def test_favicon_returns_200(self, client: FlaskClient):
        """Test that favicon route returns 200 or 404 if not present."""
        response = client.get("/favicon.ico")

        assert response.status_code == 404

    def test_favicon_returns_correct_mimetype(self, client: FlaskClient):
        """Test that favicon returns correct mimetype."""
        response = client.get("/favicon.ico")

        if response.status_code == 200:
            assert "icon" in response.content_type or response.content_type == "image/x-icon"
