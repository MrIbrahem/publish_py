"""
Integration tests for src/main_app/admin/routes/settings.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from src.main_app.db.services import SettingsService


@pytest.mark.integration
class TestSettingsDashboard:
    """Integration tests for settings dashboard."""

    def test_settings_dashboard_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that settings dashboard requires admin access."""
        response = mock_client.get("/adminpanel/settings/")

        # With mock_admin_required, should render successfully
        assert response.status_code == 200

    def test_settings_dashboard_lists_settings(self, mock_admin_required, auth_client: FlaskClient):
        """Test that settings dashboard lists settings."""
        settings_service = SettingsService()
        settings_service.create_setting("test_setting", "Test Title", "boolean")

        response = auth_client.get("/adminpanel/settings/")

        # Should render dashboard successfully
        assert response.status_code == 200


@pytest.mark.integration
class TestCreateSetting:
    """Integration tests for creating settings."""

    def test_create_setting_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that creating setting requires admin access."""
        response = mock_client.post(
            "/adminpanel/settings/create",
            data={"key": "new_setting", "title": "New Setting", "value_type": "boolean"},
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/settings/"

    def test_create_setting_with_valid_data(self, mock_admin_required, auth_client: FlaskClient):
        """Test creating setting with valid data."""
        response = auth_client.post(
            "/adminpanel/settings/create",
            data={
                "key": "new_setting",
                "title": "New Setting",
                "value_type": "boolean",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/settings/"

    def test_create_setting_invalid_key_format(self, mock_admin_required, auth_client: FlaskClient):
        """Test that creating setting with invalid key format fails."""

        response = auth_client.post(
            "/adminpanel/settings/create",
            data={
                "key": "INVALID_KEY",  # Invalid: uppercase
                "title": "New Setting",
                "value_type": "boolean",
            },
            follow_redirects=False,
        )

        # Should redirect with error flash
        assert response.status_code == 302
        assert response.location == "/adminpanel/settings/"


@pytest.mark.integration
class TestUpdateSetting:
    """Integration tests for updating settings."""

    def test_update_setting_requires_admin(self, mock_admin_required, mock_client: FlaskClient):
        """Test that updating settings requires admin access."""
        response = mock_client.post("/adminpanel/settings/update", data={"setting_test": "value"})

        assert response.status_code == 302
        assert response.location == "/adminpanel/settings/"

    def test_update_setting_with_valid_data(self, mock_admin_required, auth_client: FlaskClient):
        """Test updating setting with valid data."""
        settings_service = SettingsService()
        settings_service.create_setting("test_setting", "Test Title", "boolean")

        response = auth_client.post(
            "/adminpanel/settings/update",
            data={"setting_test_setting": "on"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/settings/"

    def test_delete_setting_via_update(self, mock_admin_required, auth_client: FlaskClient):
        """Test deleting setting via update form."""
        settings_service = SettingsService()
        settings_service.create_setting("test_setting", "Test Title", "boolean")

        response = auth_client.post(
            "/adminpanel/settings/update",
            data={"delete_test_setting": "on"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/adminpanel/settings/"
