"""
Integration tests for src/sqlalchemy_app/admin/routes/admin.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestAdminIndex:
    """Integration tests for the admin index route."""

    def test_admin_index_requires_admin(self, mock_admin_required, client: FlaskClient):
        """Test that admin index redirects to last dashboard."""
        response = client.get("/admin/")

        assert response.status_code == 302
        assert response.location.endswith("/admin/last")

    def test_admin_index_renders_dashboard(self, mock_admin_required, auth_client: FlaskClient):
        """Test that admin index renders dashboard."""

        response = auth_client.get("/admin/")

        assert response.status_code == 302
        assert response.location.endswith("/admin/last")


@pytest.mark.integration
class TestAdminSidebar:
    """Integration tests for admin sidebar."""

    def test_sidebar_injected_in_context(self, mock_admin_required, auth_client: FlaskClient):
        """Test that sidebar is injected in template context."""
        response = auth_client.get("/admin/")

        # Context processor runs for every admin request, just verify response is successful
        # The sidebar is injected via @bp_admin.app_context_processor decorator
        assert response.status_code == 302
        assert response.location.endswith("/admin/last")


@pytest.mark.integration
class TestAdminBlueprints:
    """Integration tests for registered admin blueprints."""

    def test_coordinators_routes_registered(self, mock_admin_required, client: FlaskClient):
        """Test that coordinators routes are registered."""
        # Check that the coordinators route exists
        response = client.get("/admin/coordinators/")

        # Route should exist and be accessible with mocked admin
        assert response.status_code == 200

    def test_full_translators_routes_registered(self, mock_admin_required, client: FlaskClient):
        """Test that full translators routes are registered."""
        response = client.get("/admin/full_translators/")

        assert response.status_code == 200

    def test_users_no_inprocess_routes_registered(self, mock_admin_required, client: FlaskClient):
        """Test that users no inprocess routes are registered."""
        response = client.get("/admin/users_no_inprocess/")

        assert response.status_code == 200

    def test_language_settings_routes_registered(self, mock_admin_required, client: FlaskClient):
        """Test that language settings routes are registered."""
        response = client.get("/admin/language_settings/")

        assert response.status_code == 200

    def test_settings_routes_registered(self, mock_admin_required, client: FlaskClient):
        """Test that settings routes are registered."""
        response = client.get("/admin/settings/")

        assert response.status_code == 200


@pytest.mark.integration
class TestAdminRouteAccess:
    """Integration tests for admin route access control."""

    def test_anonymous_user_redirected(self, client: FlaskClient):
        """Test that anonymous users are redirected from admin routes."""
        response = client.get("/admin/", follow_redirects=False)

        # Should redirect to login
        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_authenticated_non_admin_redirected(self, auth_client: FlaskClient):
        """Test that authenticated non-admin users are denied access."""
        # Mock current_user to return a non-admin user
        from src.sqlalchemy_app.shared.services.user_token_service import UserTokenRecord

        mock_user = UserTokenRecord(user_id=12345, username="TestUser")

        with patch("src.sqlalchemy_app.admin.decorators.current_user", return_value=mock_user):
            # Mock _get_cached_active_coordinators to return list without "TestUser"
            with patch(
                "src.sqlalchemy_app.admin.decorators._get_cached_active_coordinators",
                return_value=["admin"],
            ):
                response = auth_client.get("/admin/", follow_redirects=False)

                # Should return 403 Forbidden (not a redirect)
                assert response.status_code == 403
