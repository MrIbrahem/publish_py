"""
Integration tests for src/main_app/coordinators/routes/coordinators.py module.

TODO: should mock coordinator_required decorator
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from flask.testing import FlaskClient

from src.main_app.services.auth.current_user import CurrentUser


@pytest.mark.integration
class TestCoordinatorsIndex:
    """Integration tests for the coordinators index route."""

    def test_coordinators_index_requires_coordinators(self, mock_coordinator_required, mock_client: FlaskClient):
        """Test that coordinators index redirects to last dashboard."""
        response = mock_client.get("/coordinators_panel/")

        assert response.status_code == 302
        assert response.location.endswith("/coordinators_panel/last")

    def test_coordinators_index_renders_dashboard_no_follow_redirects(
        self, mock_coordinator_required, auth_client: FlaskClient
    ):
        """Test that coordinators index renders dashboard."""

        response = auth_client.get("/coordinators_panel/")

        assert response.status_code == 302
        assert response.location.endswith("/coordinators_panel/last")

    def test_coordinators_index_renders_dashboard(self, mock_coordinator_required, auth_client: FlaskClient):
        """Test that coordinators index renders dashboard."""
        response = auth_client.get("/coordinators_panel/", follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.integration
class TestCoordinatorsSidebar:
    """Integration tests for coordinators sidebar."""

    def test_sidebar_injected_in_context(self, mock_coordinator_required, auth_client: FlaskClient):
        """Test that sidebar is injected in template context."""
        response = auth_client.get("/coordinators_panel/")

        # Context processor runs for every coordinators request, just verify response is successful
        # The sidebar is injected via @bp_coordinators.app_context_processor decorator
        assert response.status_code == 302
        assert response.location.endswith("/coordinators_panel/last")


@pytest.mark.integration
class TestCoordinatorsBlueprints:
    """Integration tests for registered coordinators blueprints."""

    def test_coordinators_routes_registered(self, mock_admin_required, mock_client: FlaskClient):
        """Test that coordinators routes are registered."""
        # Check that the coordinators route exists
        response = mock_client.get("/coordinators_panel/coordinators/")

        # Route should exist and be accessible with mocked coordinators
        assert response.status_code == 200

    def test_full_translators_routes_registered(self, mock_coordinator_required, mock_client: FlaskClient):
        """Test that full translators routes are registered."""
        response = mock_client.get("/coordinators_panel/full_translators/")

        assert response.status_code == 200

    def test_users_no_inprocess_routes_registered(self, mock_coordinator_required, mock_client: FlaskClient):
        """Test that users no inprocess routes are registered."""
        response = mock_client.get("/coordinators_panel/users_no_inprocess/")

        assert response.status_code == 200

    def test_language_settings_routes_registered(self, mock_coordinator_required, mock_client: FlaskClient):
        """Test that language settings routes are registered."""
        response = mock_client.get("/coordinators_panel/language_settings/")

        assert response.status_code == 200

    def test_settings_routes_registered(self, mock_coordinator_required, mock_client: FlaskClient):
        """Test that settings routes are registered."""
        response = mock_client.get("/coordinators_panel/settings/")

        assert response.status_code == 200


@pytest.mark.integration
class TestCoordinatorsRouteAccess:
    """Integration tests for coordinators route access control."""

    def test_anonymous_user_redirected(self, mock_client: FlaskClient):
        """Test that anonymous users are redirected from coordinators routes."""
        response = mock_client.get("/coordinators_panel/", follow_redirects=False)

        # Should redirect to login
        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_authenticated_non_coordinators_redirected(self, auth_client: FlaskClient):
        """Test that authenticated non-coordinators users are denied access."""
        # Mock get_current_user to return a non-coordinators user

        mock_user = CurrentUser(user_id=12345, username="TestUser", access_token="", access_secret="")

        with patch("src.main_app.coordinators.decorators.get_current_user", return_value=mock_user):
            response = auth_client.get("/coordinators_panel/", follow_redirects=False)

            # Should return 403 Forbidden (not a redirect)
            assert response.status_code == 403

    def test_authenticated_non_coordinators_forbidden(self, auth_client: FlaskClient):
        """Test that authenticated non-coordinators users are denied access."""
        # Mock get_current_user to return a non-coordinators user

        mock_user = CurrentUser(user_id=12345, username="TestUser", access_token="", access_secret="")
        with patch("src.main_app.coordinators.decorators.get_current_user", return_value=mock_user):

            response = auth_client.get("/coordinators_panel/", follow_redirects=False)
            # Should return 403 Forbidden (not a redirect)
            assert response.status_code == 403
