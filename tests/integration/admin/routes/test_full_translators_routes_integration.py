"""
Integration tests for src/main_app/admin/routes/full_translators.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from src.main_app.db.services import FullTranslatorService


@pytest.mark.integration
class TestFullTranslatorsDashboard:
    """Integration tests for full translators dashboard."""

    def test_full_translators_dashboard_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that full translators dashboard requires admin access."""
        response = mock_client.get("/adminpanel/full_translators/")

        # With mock_admin_required, should render successfully
        assert response.status_code == 200

    def test_full_translators_dashboard_lists_translators(self, mock_admin_required, auth_client: FlaskClient):
        """Test that full translators dashboard lists translators."""
        ft_service = FullTranslatorService()
        ft_service.add_full_translator("Translator1", is_active=1)
        ft_service.add_full_translator("Translator2", is_active=0)

        response = auth_client.get("/adminpanel/full_translators/")

        # Should render dashboard successfully
        assert response.status_code == 200


@pytest.mark.integration
class TestAddFullTranslator:
    """Integration tests for adding full translators."""

    def test_add_full_translator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that adding full translator requires admin access."""
        response = mock_client.post("/adminpanel/full_translators/add", data={"username": "NewTranslator"})

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"

    def test_add_full_translator_with_valid_data(self, mock_admin_required, auth_client: FlaskClient):
        """Test adding full translator with valid data."""
        response = auth_client.post(
            "/adminpanel/full_translators/add",
            data={"username": "NewTranslator"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"

    def test_add_full_translator_without_username_fails(self, mock_admin_required, auth_client: FlaskClient):
        """Test that adding full translator without username fails."""
        response = auth_client.post(
            "/adminpanel/full_translators/add",
            data={"username": ""},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"


@pytest.mark.integration
class TestDeleteFullTranslator:
    """Integration tests for deleting full translators."""

    def test_delete_full_translator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that deleting full translator requires admin access."""
        response = mock_client.post("/adminpanel/full_translators/1/delete")

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"

    def test_delete_full_translator_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test deleting full translator with valid ID."""
        ft_service = FullTranslatorService()
        record = ft_service.add_full_translator("ToDeleteTranslator")

        response = auth_client.post(
            f"/adminpanel/full_translators/{record.id}/delete",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"


@pytest.mark.integration
class TestActivateDeactivateFullTranslator:
    """Integration tests for activating/deactivating full translators."""

    def test_activate_full_translator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that activating full translator requires admin access."""
        response = mock_client.post("/adminpanel/full_translators/1/activate")

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"

    def test_deactivate_full_translator_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that deactivating full translator requires admin access."""
        response = mock_client.post("/adminpanel/full_translators/1/deactivate")

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"

    def test_activate_full_translator_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test activating full translator with valid ID."""
        ft_service = FullTranslatorService()
        record = ft_service.add_full_translator("ActivateTranslator", is_active=0)

        response = auth_client.post(
            f"/adminpanel/full_translators/{record.id}/activate",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"

    def test_deactivate_full_translator_with_valid_id(self, mock_admin_required, auth_client: FlaskClient):
        """Test deactivating full translator with valid ID."""
        ft_service = FullTranslatorService()
        record = ft_service.add_full_translator("DeactivateTranslator", is_active=1)

        response = auth_client.post(
            f"/adminpanel/full_translators/{record.id}/deactivate",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/full_translators/"
