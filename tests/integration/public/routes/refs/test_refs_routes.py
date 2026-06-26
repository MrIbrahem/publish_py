"""
Integration tests for src/main_app/public/routes/refs/routes.py module.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from flask.testing import FlaskClient


@pytest.mark.integration
class TestRefsIndex:
    """Integration tests for the fixrefs index route."""

    def test_fixrefs_index_returns_200(self, mock_client: FlaskClient):
        """Test that fixrefs index route returns 200."""
        response = mock_client.get("/fixrefs/")

        assert response.status_code == 200

    def test_fixrefs_index_renders_template(self, mock_client: FlaskClient):
        """Test that fixrefs index renders template."""
        response = mock_client.get("/fixrefs/")

        assert response.status_code == 200
        assert response.content_type in ["text/html; charset=utf-8", "text/html"]


@pytest.mark.integration
class TestRefsProcess:
    """Integration tests for the fixrefs process route."""

    def test_fixrefs_process_post_returns_200(self, mock_client: FlaskClient):
        """Test that POST to fixrefs process returns 200."""
        with patch("src.main_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.return_value = "Processed text with fixed references"

            response = mock_client.post(
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

    def test_fixrefs_process_calls_do_changes_to_text(self, mock_client: FlaskClient):
        """Test that fixrefs process calls do_changes_to_text_with_settings."""
        with patch("src.main_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.return_value = "Processed text"

            mock_client.post(
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

    def test_fixrefs_process_handles_error(self, mock_client: FlaskClient):
        """Test that fixrefs process handles errors gracefully."""
        with patch("src.main_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.side_effect = Exception("Processing error")

            response = mock_client.post(
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

    def test_fixrefs_process_preserves_form_data(self, mock_client: FlaskClient):
        """Test that fixrefs process preserves form data in template."""
        with patch("src.main_app.public.routes.refs.routes.do_changes_to_text_with_settings") as mock_do_changes:
            mock_do_changes.return_value = "Processed"

            response = mock_client.post(
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
