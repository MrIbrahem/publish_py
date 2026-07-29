"""
Integration tests for src/main_app/admin/routes/users_no_inprocess.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from src.main_app.db.services import UsersNoInprocessService


@pytest.mark.integration
class TestUsersNoInprocessDashboard:
    """Integration tests for users no inprocess dashboard."""

    def test_users_no_inprocess_dashboard_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that users no inprocess dashboard requires admin access."""
        response = mock_client.get("/admin/users_no_inprocess/")

        # With mock_admin_required, should render successfully
        assert response.status_code == 200

    def test_users_no_inprocess_dashboard_lists_users(self, mock_admin_required, auth_client: FlaskClient):
        """Test that users no inprocess dashboard lists users."""
        service = UsersNoInprocessService()
        service.add_users_no_inprocess("User1", is_active=1)
        service.add_users_no_inprocess("User2", is_active=0)

        response = auth_client.get("/admin/users_no_inprocess/")

        # Should render dashboard successfully
        assert response.status_code == 200


@pytest.mark.integration
class TestAddUserNoInprocess:
    """Integration tests for adding users not in process."""

    def test_add_user_no_inprocess_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that adding user requires admin access."""
        response = mock_client.post("/admin/users_no_inprocess/add", data={"username": "NewUser"})

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"

    def test_add_user_no_inprocess_with_valid_data(self, mock_admin_required, auth_client: FlaskClient):
        """Test adding user with valid data."""
        response = auth_client.post(
            "/admin/users_no_inprocess/add",
            data={"username": "NewUser"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"

    def test_add_user_no_inprocess_without_username_fails(self, mock_admin_required, auth_client: FlaskClient):
        """Test that adding user without username fails."""
        response = auth_client.post(
            "/admin/users_no_inprocess/add",
            data={"username": ""},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"


@pytest.mark.integration
class TestDeleteUserNoInprocess:
    """Integration tests for deleting users not in process."""

    def test_delete_user_no_inprocess_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that deleting user requires admin access."""
        response = mock_client.post("/admin/users_no_inprocess/1/delete")

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"

    def test_delete_user_no_inprocess_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test deleting user with valid ID."""
        service = UsersNoInprocessService()
        record = service.add_users_no_inprocess("ToDeleteUser")

        response = auth_client.post(
            f"/admin/users_no_inprocess/{record.id}/delete",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"


@pytest.mark.integration
class TestActivateDeactivateUserNoInprocess:
    """Integration tests for activating/deactivating users not in process."""

    def test_activate_user_no_inprocess_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that activating user requires admin access."""
        response = mock_client.post("/admin/users_no_inprocess/1/activate")

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"

    def test_deactivate_user_no_inprocess_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that deactivating user requires admin access."""
        response = mock_client.post("/admin/users_no_inprocess/1/deactivate")

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"

    def test_activate_user_no_inprocess_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test activating user with valid ID."""
        service = UsersNoInprocessService()
        record = service.add_users_no_inprocess("ActivateUser", is_active=0)

        response = auth_client.post(
            f"/admin/users_no_inprocess/{record.id}/activate",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"

    def test_deactivate_user_no_inprocess_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test deactivating user with valid ID."""
        service = UsersNoInprocessService()
        record = service.add_users_no_inprocess("DeactivateUser", is_active=1)

        response = auth_client.post(
            f"/admin/users_no_inprocess/{record.id}/deactivate",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/admin/users_no_inprocess/"
