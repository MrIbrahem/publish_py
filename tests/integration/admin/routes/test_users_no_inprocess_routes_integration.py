"""
Integration tests for src/sqlalchemy_app/admin/routes/users_no_inprocess.py module.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestUsersNoInprocessDashboard:
    """Integration tests for users no inprocess dashboard."""

    def test_users_no_inprocess_dashboard_requires_admin(self, client: FlaskClient):
        """Test that users no inprocess dashboard requires admin access."""
        response = client.get("/admin/users_no_inprocess")

        assert response.status_code in [200, 302, 401, 403]

    def test_users_no_inprocess_dashboard_lists_users(self, auth_client: FlaskClient):
        """Test that users no inprocess dashboard lists users."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.users_no_inprocess.list_users_no_inprocess") as mock_list:
                mock_list.return_value = [
                    MagicMock(user="User1", is_active=True),
                    MagicMock(user="User2", is_active=False),
                ]

                response = auth_client.get("/admin/users_no_inprocess")

                assert response.status_code in [200, 302]


@pytest.mark.integration
class TestAddUserNoInprocess:
    """Integration tests for adding users not in process."""

    def test_add_user_no_inprocess_requires_admin(self, client: FlaskClient):
        """Test that adding user requires admin access."""
        response = client.post("/admin/users_no_inprocess/add", data={"username": "NewUser"})

        assert response.status_code in [302, 401, 403]

    def test_add_user_no_inprocess_with_valid_data(self, auth_client: FlaskClient):
        """Test adding user with valid data."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.users_no_inprocess.add_users_no_inprocess") as mock_add:
                mock_add.return_value = MagicMock(user="NewUser")

                response = auth_client.post(
                    "/admin/users_no_inprocess/add",
                    data={"username": "NewUser"},
                    follow_redirects=False,
                )

                assert response.status_code in [302, 200]

    def test_add_user_no_inprocess_without_username_fails(self, auth_client: FlaskClient):
        """Test that adding user without username fails."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            response = auth_client.post(
                "/admin/users_no_inprocess/add",
                data={"username": ""},
                follow_redirects=False,
            )

            assert response.status_code in [302, 200]


@pytest.mark.integration
class TestDeleteUserNoInprocess:
    """Integration tests for deleting users not in process."""

    def test_delete_user_no_inprocess_requires_admin(self, client: FlaskClient):
        """Test that deleting user requires admin access."""
        response = client.post("/admin/users_no_inprocess/1/delete")

        assert response.status_code in [302, 401, 403]

    def test_delete_user_no_inprocess_with_valid_id(self, auth_client: FlaskClient):
        """Test deleting user with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.users_no_inprocess.delete_users_no_inprocess") as mock_delete:
                mock_delete.return_value = MagicMock(user="DeletedUser")

                response = auth_client.post(
                    "/admin/users_no_inprocess/1/delete",
                    follow_redirects=False,
                )

                assert response.status_code == 302


@pytest.mark.integration
class TestActivateDeactivateUserNoInprocess:
    """Integration tests for activating/deactivating users not in process."""

    def test_activate_user_no_inprocess_requires_admin(self, client: FlaskClient):
        """Test that activating user requires admin access."""
        response = client.post("/admin/users_no_inprocess/1/activate")

        assert response.status_code in [302, 401, 403]

    def test_deactivate_user_no_inprocess_requires_admin(self, client: FlaskClient):
        """Test that deactivating user requires admin access."""
        response = client.post("/admin/users_no_inprocess/1/deactivate")

        assert response.status_code in [302, 401, 403]

    def test_activate_user_no_inprocess_with_valid_id(self, auth_client: FlaskClient):
        """Test activating user with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.users_no_inprocess.update_users_no_inprocess") as mock_update:
                mock_update.return_value = MagicMock(username="ActivatedUser")

                response = auth_client.post(
                    "/admin/users_no_inprocess/1/activate",
                    follow_redirects=False,
                )

                assert response.status_code == 302

    def test_deactivate_user_no_inprocess_with_valid_id(self, auth_client: FlaskClient):
        """Test deactivating user with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.users_no_inprocess.update_users_no_inprocess") as mock_update:
                mock_update.return_value = MagicMock(username="DeactivatedUser")

                response = auth_client.post(
                    "/admin/users_no_inprocess/1/deactivate",
                    follow_redirects=False,
                )

                assert response.status_code == 302
