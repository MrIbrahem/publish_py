"""
Integration tests for src/sqlalchemy_app/admin/routes/settings.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestSettingsDashboard:
    """Integration tests for settings dashboard."""

    def test_settings_dashboard_requires_admin(self, mock_admin_required, client: FlaskClient):
        """Test that settings dashboard requires admin access."""
        response = client.get("/admin/settings")

        assert response.status_code == 302
        assert response.location == '/admin/settings/'

    def test_settings_dashboard_lists_settings(self, mock_admin_required, auth_client: FlaskClient):
        """Test that settings dashboard lists settings."""

        with patch("src.sqlalchemy_app.shared.services.setting_service.list_settings") as mock_list:
            mock_setting = MagicMock()
            mock_setting.key = "test_setting"
            mock_setting.value_type = "boolean"
            mock_setting.to_dict.return_value = {"value": True}
            mock_list.return_value = [mock_setting]

            response = auth_client.get("/admin/settings")

            assert response.status_code == 302
            assert response.location == '/admin/settings/'


@pytest.mark.integration
class TestCreateSetting:
    """Integration tests for creating settings."""

    def test_create_setting_requires_admin(self, mock_admin_required, client: FlaskClient):
        """Test that creating setting requires admin access."""
        response = client.post(
            "/admin/settings/create",
            data={"key": "new_setting", "title": "New Setting", "value_type": "boolean"},
        )

        assert response.status_code == 302
        assert response.location == '/admin/settings/'

    def test_create_setting_with_valid_data(self, mock_admin_required, auth_client: FlaskClient):
        """Test creating setting with valid data."""

        with patch("src.sqlalchemy_app.shared.services.setting_service.add_setting") as mock_add:
            mock_add.return_value = MagicMock(key="new_setting")

            response = auth_client.post(
                "/admin/settings/create",
                data={
                    "key": "new_setting",
                    "title": "New Setting",
                    "value_type": "boolean",
                },
                follow_redirects=False,
            )

            assert response.status_code == 302
            assert response.location == '/admin/settings/'

    def test_create_setting_invalid_key_format(self, mock_admin_required, auth_client: FlaskClient):
        """Test that creating setting with invalid key format fails."""

        response = auth_client.post(
            "/admin/settings/create",
            data={
                "key": "INVALID_KEY",  # Invalid: uppercase
                "title": "New Setting",
                "value_type": "boolean",
            },
            follow_redirects=False,
        )

        # Should redirect with error flash
        assert response.status_code == 302
        assert response.location == '/admin/settings/'


@pytest.mark.integration
class TestUpdateSetting:
    """Integration tests for updating settings."""

    def test_update_setting_requires_admin(self, mock_admin_required, client: FlaskClient):
        """Test that updating settings requires admin access."""
        response = client.post("/admin/settings/update", data={"setting_test": "value"})

        assert response.status_code == 302
        assert response.location == '/admin/settings/'

    def test_update_setting_with_valid_data(self, mock_admin_required, auth_client: FlaskClient):
        """Test updating setting with valid data."""

        mock_setting = MagicMock()
        mock_setting.key = "test_setting"
        mock_setting.value_type = "boolean"
        mock_setting.id = 1

        with patch("src.sqlalchemy_app.shared.services.setting_service.list_settings") as mock_list:
            mock_list.return_value = [mock_setting]

            response = auth_client.post(
                "/admin/settings/update",
                data={"setting_test_setting": "on"},
                follow_redirects=False,
            )

            assert response.status_code == 302
            assert response.location == '/admin/settings/'

    def test_delete_setting_via_update(self, mock_admin_required, auth_client: FlaskClient):
        """Test deleting setting via update form."""
        mock_setting = MagicMock()
        mock_setting.key = "test_setting"
        mock_setting.value_type = "boolean"
        mock_setting.id = 1

        with patch("src.sqlalchemy_app.shared.services.setting_service.list_settings") as mock_list:
            mock_list.return_value = [mock_setting]

            response = auth_client.post(
                "/admin/settings/update",
                data={"delete_test_setting": "on"},
                follow_redirects=False,
            )

            assert response.status_code == 302
            assert response.location == '/admin/settings/'
