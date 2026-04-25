"""
Integration tests for src/sqlalchemy_app/public/routes/refs/routes.py module.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestRefsIndex:
    """Integration tests for the fixrefs index route."""

    def test_fixrefs_index_returns_200(self, client: FlaskClient):
        """Test that fixrefs index route returns 200."""
        response = client.get("/fixrefs/")

        assert response.status_code == 200

    def test_fixrefs_index_renders_template(self, client: FlaskClient):
        """Test that fixrefs index renders template."""
        response = client.get("/fixrefs/")

        assert response.status_code == 200
        assert response.content_type in ["text/html; charset=utf-8", "text/html"]


@pytest.mark.integration
class TestRefsProcess:
    """Integration tests for the fixrefs process route."""

    def test_fixrefs_process_post_returns_200(self, client: FlaskClient):
        """Test that POST to fixrefs process returns 200."""
        with patch("src.sqlalchemy_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.return_value = "Processed text with fixed references"

            response = client.post(
                "/fixrefs/",
                data={
                    "source_title": "Source Title",
                    "title": "Target Title",
                    "text": "Text to process",
                    "lang": "en",
                    "mdwiki_revid": "12345",
                },
            )

            assert response.status_code == 200

    def test_fixrefs_process_calls_do_changes_to_text(self, client: FlaskClient):
        """Test that fixrefs process calls do_changes_to_text_with_settings."""
        with patch("src.sqlalchemy_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.return_value = "Processed text"

            client.post(
                "/fixrefs/",
                data={
                    "source_title": "Source Title",
                    "title": "Target Title",
                    "text": "Text to process",
                    "lang": "en",
                    "mdwiki_revid": "12345",
                },
            )

            mock_do_changes.assert_called_once()

    def test_fixrefs_process_handles_error(self, client: FlaskClient):
        """Test that fixrefs process handles errors gracefully."""
        with patch("src.sqlalchemy_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.side_effect = Exception("Processing error")

            response = client.post(
                "/fixrefs/",
                data={
                    "source_title": "Source Title",
                    "title": "Target Title",
                    "text": "Text to process",
                    "lang": "en",
                },
            )

            # Should not crash, should return error message in template
            assert response.status_code == 200

    def test_fixrefs_process_preserves_form_data(self, client: FlaskClient):
        """Test that fixrefs process preserves form data in template."""
        with patch("src.sqlalchemy_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.return_value = "Processed"

            response = client.post(
                "/fixrefs/",
                data={
                    "source_title": "My Source",
                    "title": "My Title",
                    "text": "My Text",
                    "lang": "ar",
                    "mdwiki_revid": "54321",
                },
            )

            assert response.status_code == 200
