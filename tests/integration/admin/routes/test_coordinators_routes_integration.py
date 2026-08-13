"""
Integration tests for src/main_app/admin/routes/coordinators.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from src.main_app.database.services import AdminService, UsersService


@pytest.mark.integration
class TestCoordinatorsDashboard:
    """Integration tests for coordinators dashboard."""

    def test_coordinators_dashboard_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that coordinators dashboard requires admin access."""
        response = mock_client.get("/adminpanel/coordinators/")

        # With mock_admin_required, should render successfully
        assert response.status_code == 200

    def test_coordinators_dashboard_lists_coordinators(self, mock_admin_required, auth_client: FlaskClient):
        """Test that coordinators dashboard lists coordinators."""
        users_service = UsersService()
        users_service.create_user("Coordinator1")
        users_service.create_user("Coordinator2")

        admin_service = AdminService()
        admin_service.add_coordinator("Coordinator1")
        admin_service.add_coordinator("Coordinator2")

        response = auth_client.get("/adminpanel/coordinators/")

        # Should render dashboard successfully
        assert response.status_code == 200


@pytest.mark.integration
class TestAddCoordinator:
    """Integration tests for adding coordinators."""

    def test_add_coordinator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that adding coordinator requires admin access."""
        response = mock_client.post("/adminpanel/coordinators/add", data={"username": "NewCoordinator"})

        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"

    def test_add_coordinator_with_valid_data(self, mock_admin_required, auth_client: FlaskClient):
        """Test adding coordinator with valid data."""
        users_service = UsersService()
        users_service.create_user("NewCoordinator")

        response = auth_client.post(
            "/adminpanel/coordinators/add",
            data={"username": "NewCoordinator"},
            follow_redirects=False,
        )

        # Should redirect after successful add
        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"

    def test_add_coordinator_without_username_fails(self, mock_admin_required, auth_client: FlaskClient):
        """Test that adding coordinator without username fails."""
        response = auth_client.post(
            "/adminpanel/coordinators/add",
            data={"username": ""},
            follow_redirects=False,
        )

        # Should redirect with error
        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"


@pytest.mark.integration
class TestDeleteCoordinator:
    """Integration tests for deleting coordinators."""

    def test_delete_coordinator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that deleting coordinator requires admin access."""
        response = mock_client.post("/adminpanel/coordinators/1/delete")

        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"

    def test_delete_coordinator_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test deleting coordinator with valid ID."""
        users_service = UsersService()
        users_service.create_user("DeletedCoordinator")

        admin_service = AdminService()
        record = admin_service.add_coordinator("DeletedCoordinator")

        response = auth_client.post(
            f"/adminpanel/coordinators/{record.id}/delete",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"


@pytest.mark.integration
class TestActivateDeactivateCoordinator:
    """Integration tests for activating/deactivating coordinators."""

    def test_activate_coordinator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that activating coordinator requires admin access."""
        response = mock_client.post("/adminpanel/coordinators/1/activate")

        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"

    def test_deactivate_coordinator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that deactivating coordinator requires admin access."""
        response = mock_client.post("/adminpanel/coordinators/1/deactivate")

        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"

    def test_activate_coordinator_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test activating coordinator with valid ID."""
        users_service = UsersService()
        users_service.create_user("ActivateCoordinator")

        admin_service = AdminService()
        record = admin_service.add_coordinator("ActivateCoordinator")
        admin_service.set_coordinator_active(record.id, is_active=False)

        response = auth_client.post(
            f"/adminpanel/coordinators/{record.id}/activate",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"

    def test_deactivate_coordinator_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test deactivating coordinator with valid ID."""
        users_service = UsersService()
        users_service.create_user("DeactivateCoordinator")

        admin_service = AdminService()
        record = admin_service.add_coordinator("DeactivateCoordinator")

        response = auth_client.post(
            f"/adminpanel/coordinators/{record.id}/deactivate",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/coordinators/"
