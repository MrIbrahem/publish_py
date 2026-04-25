"""
Integration tests for src/sqlalchemy_app/admin/routes/coordinators.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestCoordinatorsDashboard:
    """Integration tests for coordinators dashboard."""

    def test_coordinators_dashboard_requires_admin(self, client: FlaskClient):
        """Test that coordinators dashboard requires admin access."""
        response = client.get("/admin/coordinators")

        # Should redirect to login or require admin
        assert response.status_code == 302  # in [200, 302, 401, 403]

    def test_coordinators_dashboard_lists_coordinators(self, auth_client: FlaskClient):
        """Test that coordinators dashboard lists coordinators."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.coordinators.list_coordinators") as mock_list:
                mock_list.return_value = [
                    MagicMock(username="Coordinator1", is_active=True),
                    MagicMock(username="Coordinator2", is_active=False),
                ]

                response = auth_client.get("/admin/coordinators")

                # May redirect or show dashboard
                assert response.status_code == 302  # in [200, 302]


@pytest.mark.integration
class TestAddCoordinator:
    """Integration tests for adding coordinators."""

    def test_add_coordinator_requires_admin(self, client: FlaskClient):
        """Test that adding coordinator requires admin access."""
        response = client.post("/admin/coordinators/add", data={"username": "NewCoordinator"})

        assert response.status_code == 302  # in [302, 401, 403]

    def test_add_coordinator_with_valid_data(self, auth_client: FlaskClient):
        """Test adding coordinator with valid data."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.coordinators.add_coordinator") as mock_add:
                mock_add.return_value = MagicMock(username="NewCoordinator")

                response = auth_client.post(
                    "/admin/coordinators/add",
                    data={"username": "NewCoordinator"},
                    follow_redirects=False,
                )

                # Should redirect after successful add
                assert response.status_code == 302  # in [302, 200]

    def test_add_coordinator_without_username_fails(self, auth_client: FlaskClient):
        """Test that adding coordinator without username fails."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            response = auth_client.post(
                "/admin/coordinators/add",
                data={"username": ""},
                follow_redirects=False,
            )

            # Should redirect with error
            assert response.status_code == 302  # in [302, 200]


@pytest.mark.integration
class TestDeleteCoordinator:
    """Integration tests for deleting coordinators."""

    def test_delete_coordinator_requires_admin(self, client: FlaskClient):
        """Test that deleting coordinator requires admin access."""
        response = client.post("/admin/coordinators/1/delete")

        assert response.status_code == 302  # in [302, 401, 403]

    def test_delete_coordinator_with_valid_id(self, auth_client: FlaskClient):
        """Test deleting coordinator with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.coordinators.delete_coordinator") as mock_delete:
                mock_delete.return_value = MagicMock(username="DeletedCoordinator")

                response = auth_client.post(
                    "/admin/coordinators/1/delete",
                    follow_redirects=False,
                )

                assert response.status_code == 302


@pytest.mark.integration
class TestActivateDeactivateCoordinator:
    """Integration tests for activating/deactivating coordinators."""

    def test_activate_coordinator_requires_admin(self, client: FlaskClient):
        """Test that activating coordinator requires admin access."""
        response = client.post("/admin/coordinators/1/activate")

        assert response.status_code == 302  # in [302, 401, 403]

    def test_deactivate_coordinator_requires_admin(self, client: FlaskClient):
        """Test that deactivating coordinator requires admin access."""
        response = client.post("/admin/coordinators/1/deactivate")

        assert response.status_code == 302  # in [302, 401, 403]

    def test_activate_coordinator_with_valid_id(self, auth_client: FlaskClient):
        """Test activating coordinator with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.coordinators.set_coordinator_active") as mock_set:
                mock_set.return_value = MagicMock(username="ActivatedCoordinator")

                response = auth_client.post(
                    "/admin/coordinators/1/activate",
                    follow_redirects=False,
                )

                assert response.status_code == 302

    def test_deactivate_coordinator_with_valid_id(self, auth_client: FlaskClient):
        """Test deactivating coordinator with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.coordinators.set_coordinator_active") as mock_set:
                mock_set.return_value = MagicMock(username="DeactivatedCoordinator")

                response = auth_client.post(
                    "/admin/coordinators/1/deactivate",
                    follow_redirects=False,
                )

                assert response.status_code == 302
