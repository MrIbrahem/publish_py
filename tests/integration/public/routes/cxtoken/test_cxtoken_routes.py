"""
Integration tests for src/main_app/public/routes/cxtoken/routes.py module.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from flask.testing import FlaskClient

from src.main_app.db.services import UsersService, UserTokenService


@pytest.mark.integration
class TestCxTokenPreflight:
    """Integration tests for the CORS preflight endpoint."""

    def test_preflight_returns_200(self, mock_client: FlaskClient):
        """Test that OPTIONS request returns 200."""
        response = mock_client.options("/cxtoken/")

        assert response.status_code == 200

    def test_preflight_sets_cors_headers(self, mock_client: FlaskClient):
        """Test that preflight sets CORS headers."""
        response = mock_client.options("/cxtoken/")

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
        assert "Access-Control-Max-Age" in response.headers


@pytest.mark.integration
class TestCxTokenGet:
    """Integration tests for the cxtoken GET endpoint."""

    def test_missing_parameters_returns_400(self, mock_client: FlaskClient):
        """Test that missing wiki/user parameters returns 400."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            response = mock_client.get("/cxtoken/")

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data

    def test_missing_wiki_returns_400(self, mock_client: FlaskClient):
        """Test that missing wiki parameter returns 400."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            response = mock_client.get("/cxtoken/?user=TestUser")

            assert response.status_code == 400

    def test_missing_user_returns_400(self, mock_client: FlaskClient):
        """Test that missing user parameter returns 400."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            response = mock_client.get("/cxtoken/?wiki=en")

            assert response.status_code == 400

    def test_no_user_token_returns_403(self, mock_client: FlaskClient):
        """Test that request without valid user token returns 403."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            response = mock_client.get("/cxtoken/?wiki=en&user=NonExistentUser")

            assert response.status_code == 403
            data = response.get_json()
            assert "error" in data

    def test_valid_request_returns_cxtoken(self, mock_client: FlaskClient):
        """Test that valid request returns cxtoken."""
        users_service = UsersService()
        user = users_service.create_user("TokenUser")

        token_service = UserTokenService()
        encrypted_token = token_service.encrypt_value("test_access_token")
        encrypted_secret = token_service.encrypt_value("test_access_secret")
        token_service.create_user_token(user.user_id, encrypted_token, encrypted_secret)

        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.main_app.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken:
                mock_get_cxtoken.return_value = {"csrftoken": "test_token_123"}

                with patch("src.main_app.public.routes.cxtoken.routes.store_jwt"):
                    response = mock_client.get("/cxtoken/?wiki=en&user=TokenUser")

                    assert response.status_code == 200
                    data = response.get_json()
                    assert "csrftoken" in data


@pytest.mark.integration
class TestCxTokenCache:
    """Integration tests for cxtoken caching."""

    def test_cached_cxtoken_returned_from_cache(self, mock_client: FlaskClient):
        """Test that cached cxtoken is returned from cache."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.main_app.public.routes.cxtoken.routes.get_from_store") as mock_from_store:
                mock_from_store.return_value = {"csrftoken": "cached_token_123"}

                response = mock_client.get("/cxtoken/?wiki=en&user=TestUser")

                assert response.status_code == 200
                data = response.get_json()
                assert data["csrftoken"] == "cached_token_123"


@pytest.mark.integration
class TestCxTokenUserFormatting:
    """Integration tests for user formatting in cxtoken."""

    def test_user_underscores_replaced_with_spaces(self, mock_client: FlaskClient):
        """Test that underscores in username are replaced with spaces."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.main_app.public.routes.cxtoken.routes._format_user") as mock_format:
                mock_format.return_value = "Test User"

                mock_client.get("/cxtoken/?wiki=en&user=Test_User")

                mock_format.assert_called()

    def test_special_users_mapping_applied(self, mock_client: FlaskClient):
        """Test that special user mappings are applied."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f

            with patch("src.main_app.public.routes.cxtoken.routes.settings") as mock_settings:
                mock_settings.users.special_users = {"SpecialUser": "MappedUser"}

                mock_client.get("/cxtoken/?wiki=en&user=SpecialUser")


class TestCxtokenRouteIntegration:
    """Integration tests for cxtoken route."""

    def test_cxtoken_requires_authentication(self, mock_client):
        """Test that cxtoken route requires authentication."""
        response = mock_client.get("/cxtoken?wiki=arwiki")

        assert response.status_code == 400

    def test_cxtoken_rejects_missing_user_param(self, mock_client):
        """Test that cxtoken route rejects requests without user parameter."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f
            response = mock_client.get("/cxtoken/?wiki=arwiki")
            assert response.status_code == 400

    def test_cxtoken_rejects_missing_wiki_param(self, auth_client):
        """Test that cxtoken route rejects requests without wiki parameter."""
        with patch("src.main_app.public.routes.cxtoken.routes.check_cors") as mock_cors:
            mock_cors.return_value = lambda f: f
            response = auth_client.get("/cxtoken/")
            assert response.status_code == 400
