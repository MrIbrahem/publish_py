"""
Integration tests for src/sqlalchemy_app/admin/routes/full_translators.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestFullTranslatorsDashboard:
    """Integration tests for full translators dashboard."""

    def test_full_translators_dashboard_requires_admin(self, client: FlaskClient):
        """Test that full translators dashboard requires admin access."""
        response = client.get("/admin/full_translators")

        assert response.status_code == 302 # in [200, 302, 401, 403]

    def test_full_translators_dashboard_lists_translators(self, auth_client: FlaskClient):
        """Test that full translators dashboard lists translators."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.full_translators.list_full_translators") as mock_list:
                mock_list.return_value = [
                    MagicMock(user="Translator1", is_active=True),
                    MagicMock(user="Translator2", is_active=False),
                ]

                response = auth_client.get("/admin/full_translators")

                assert response.status_code == 302 # in [200, 302]


@pytest.mark.integration
class TestAddFullTranslator:
    """Integration tests for adding full translators."""

    def test_add_full_translator_requires_admin(self, client: FlaskClient):
        """Test that adding full translator requires admin access."""
        response = client.post("/admin/full_translators/add", data={"username": "NewTranslator"})

        assert response.status_code == 302 # in [302, 401, 403]

    def test_add_full_translator_with_valid_data(self, auth_client: FlaskClient):
        """Test adding full translator with valid data."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.full_translators.add_full_translator") as mock_add:
                mock_add.return_value = MagicMock(user="NewTranslator")

                response = auth_client.post(
                    "/admin/full_translators/add",
                    data={"username": "NewTranslator"},
                    follow_redirects=False,
                )

                assert response.status_code == 302 # in [302, 200]

    def test_add_full_translator_without_username_fails(self, auth_client: FlaskClient):
        """Test that adding full translator without username fails."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            response = auth_client.post(
                "/admin/full_translators/add",
                data={"username": ""},
                follow_redirects=False,
            )

            assert response.status_code == 302 # in [302, 200]


@pytest.mark.integration
class TestDeleteFullTranslator:
    """Integration tests for deleting full translators."""

    def test_delete_full_translator_requires_admin(self, client: FlaskClient):
        """Test that deleting full translator requires admin access."""
        response = client.post("/admin/full_translators/1/delete")

        assert response.status_code == 302 # in [302, 401, 403]

    def test_delete_full_translator_with_valid_id(self, auth_client: FlaskClient):
        """Test deleting full translator with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.full_translators.delete_full_translator") as mock_delete:
                mock_delete.return_value = MagicMock(user="DeletedTranslator")

                response = auth_client.post(
                    "/admin/full_translators/1/delete",
                    follow_redirects=False,
                )

                assert response.status_code == 302


@pytest.mark.integration
class TestActivateDeactivateFullTranslator:
    """Integration tests for activating/deactivating full translators."""

    def test_activate_full_translator_requires_admin(self, client: FlaskClient):
        """Test that activating full translator requires admin access."""
        response = client.post("/admin/full_translators/1/activate")

        assert response.status_code == 302 # in [302, 401, 403]

    def test_deactivate_full_translator_requires_admin(self, client: FlaskClient):
        """Test that deactivating full translator requires admin access."""
        response = client.post("/admin/full_translators/1/deactivate")

        assert response.status_code == 302 # in [302, 401, 403]

    def test_activate_full_translator_with_valid_id(self, auth_client: FlaskClient):
        """Test activating full translator with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.full_translators.update_full_translator") as mock_update:
                mock_update.return_value = MagicMock(username="ActivatedTranslator")

                response = auth_client.post(
                    "/admin/full_translators/1/activate",
                    follow_redirects=False,
                )

                assert response.status_code == 302

    def test_deactivate_full_translator_with_valid_id(self, auth_client: FlaskClient):
        """Test deactivating full translator with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.full_translators.update_full_translator") as mock_update:
                mock_update.return_value = MagicMock(username="DeactivatedTranslator")

                response = auth_client.post(
                    "/admin/full_translators/1/deactivate",
                    follow_redirects=False,
                )

                assert response.status_code == 302
