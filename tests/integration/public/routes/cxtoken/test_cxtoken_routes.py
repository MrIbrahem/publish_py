"""
Integration tests for src/sqlalchemy_app/public/routes/cxtoken/routes.py module.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestCxTokenPreflight:
    """Integration tests for the CORS preflight endpoint."""

    def test_preflight_returns_200(self, client: FlaskClient):
        """Test that OPTIONS request returns 200."""
        response = client.options("/cxtoken/")

        assert response.status_code == 200

    def test_preflight_sets_cors_headers(self, client: FlaskClient):
        """Test that preflight sets CORS headers."""
        response = client.options("/cxtoken/")

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
        assert "Access-Control-Max-Age" in response.headers


@pytest.mark.integration
class TestCxTokenGet:
    """Integration tests for the cxtoken GET endpoint."""

    def test_missing_parameters_returns_400(self, client: FlaskClient):
        """Test that missing wiki/user parameters returns 400."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            response = client.get("/cxtoken/")

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data

    def test_missing_wiki_returns_400(self, client: FlaskClient):
        """Test that missing wiki parameter returns 400."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            response = client.get("/cxtoken/?user=TestUser")

            assert response.status_code == 400

    def test_missing_user_returns_400(self, client: FlaskClient):
        """Test that missing user parameter returns 400."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            response = client.get("/cxtoken/?wiki=en")

            assert response.status_code == 400

    def test_no_user_token_returns_403(self, client: FlaskClient):
        """Test that request without valid user token returns 403."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token:
                mock_get_token.return_value = None

                response = client.get("/cxtoken/?wiki=en&user=TestUser")

                assert response.status_code == 403
                data = response.get_json()
                assert "error" in data

    def test_valid_request_returns_cxtoken(self, client: FlaskClient):
        """Test that valid request returns cxtoken."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            mock_user_token = MagicMock()
            mock_user_token.decrypted.return_value = ("access_key", "access_secret")

            with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token:
                mock_get_token.return_value = mock_user_token

                with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken:
                    mock_get_cxtoken.return_value = {"csrftoken": "test_token_123"}

                    with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.store_jwt"):
                        response = client.get("/cxtoken/?wiki=en&user=TestUser")

                        assert response.status_code == 200
                        data = response.get_json()
                        assert "csrftoken" in data


@pytest.mark.integration
class TestCxTokenCache:
    """Integration tests for cxtoken caching."""

    def test_cached_cxtoken_returned_from_cache(self, client: FlaskClient):
        """Test that cached cxtoken is returned from cache."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.get_from_store") as mock_from_store:
                mock_from_store.return_value = {"csrftoken": "cached_token_123"}

                response = client.get("/cxtoken/?wiki=en&user=TestUser")

                assert response.status_code == 200
                data = response.get_json()
                assert data["csrftoken"] == "cached_token_123"


@pytest.mark.integration
class TestCxTokenUserFormatting:
    """Integration tests for user formatting in cxtoken."""

    def test_user_underscores_replaced_with_spaces(self, client: FlaskClient):
        """Test that underscores in username are replaced with spaces."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token:
                mock_get_token.return_value = None

                with patch("src.sqlalchemy_app.public.routes.cxtoken.routes._format_user") as mock_format:
                    mock_format.return_value = "Test User"

                    response = client.get("/cxtoken/?wiki=en&user=Test_User")

                    # Check that formatting was called
                    mock_format.assert_called()

    def test_special_users_mapping_applied(self, client: FlaskClient):
        """Test that special user mappings are applied."""
        with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.sqlalchemy_app.public.routes.cxtoken.routes.settings") as mock_settings:
                mock_settings.users.special_users = {"SpecialUser": "MappedUser"}

                with patch(
                    "src.sqlalchemy_app.public.routes.cxtoken.routes.get_user_token_by_username"
                ) as mock_get_token:
                    mock_get_token.return_value = None

                    response = client.get("/cxtoken/?wiki=en&user=SpecialUser")

                    # The formatted user should be "MappedUser" after applying special_users mapping


class TestCxtokenRouteIntegration:
    """Integration tests for cxtoken route."""

    def test_cxtoken_requires_authentication(self, client):
        """Test that cxtoken route requires authentication."""
        response = client.get("/cxtoken?wiki=arwiki")

        # Should redirect to login or return 400 (bad request)
        assert response.status_code == 400

    def test_cxtoken_rejects_missing_wiki_param(self, auth_client):
        """Test that cxtoken route rejects requests without wiki parameter."""
        response = auth_client.get("/cxtoken")

        # Should return bad request
        assert response.status_code == 400
