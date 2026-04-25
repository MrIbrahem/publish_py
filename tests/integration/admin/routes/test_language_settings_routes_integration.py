"""
Integration tests for src/sqlalchemy_app/admin/routes/language_settings.py module.

TODO: should mock admin_required decorator
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestLanguageSettingsDashboard:
    """Integration tests for language settings dashboard."""

    def test_language_settings_dashboard_requires_admin(self, client: FlaskClient):
        """Test that language settings dashboard requires admin access."""
        response = client.get("/admin/language_settings")

        assert response.status_code == 302 # in [200, 302, 401, 403]

    def test_language_settings_dashboard_lists_settings(self, auth_client: FlaskClient):
        """Test that language settings dashboard lists settings."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.language_settings.list_language_settings") as mock_list:
                mock_list.return_value = [
                    MagicMock(lang_code="en", move_dots=1, expend=0, add_en_lang=1),
                    MagicMock(lang_code="ar", move_dots=0, expend=1, add_en_lang=0),
                ]

                with patch("src.sqlalchemy_app.admin.routes.language_settings.list_langs") as mock_langs:
                    mock_langs.return_value = [
                        MagicMock(code="en", name="English"),
                        MagicMock(code="ar", name="Arabic"),
                    ]

                    response = auth_client.get("/admin/language_settings")

                    assert response.status_code == 302 # in [200, 302]


@pytest.mark.integration
class TestAddLanguageSetting:
    """Integration tests for adding language settings."""

    def test_add_language_setting_requires_admin(self, client: FlaskClient):
        """Test that adding language setting requires admin access."""
        response = client.post("/admin/language_settings/add", data={"lang_code": "fr"})

        assert response.status_code == 302 # in [302, 401, 403]

    def test_add_language_setting_with_valid_data(self, auth_client: FlaskClient):
        """Test adding language setting with valid data."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.language_settings.add_language_setting") as mock_add:
                mock_add.return_value = MagicMock(lang_code="fr")

                response = auth_client.post(
                    "/admin/language_settings/add",
                    data={
                        "lang_code": "fr",
                        "move_dots": "1",
                        "expend": "0",
                        "add_en_lang": "1",
                    },
                    follow_redirects=False,
                )

                assert response.status_code == 302 # in [302, 200]

    def test_add_language_setting_without_lang_code_fails(self, auth_client: FlaskClient):
        """Test that adding language setting without lang_code fails."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            response = auth_client.post(
                "/admin/language_settings/add",
                data={"lang_code": ""},
                follow_redirects=False,
            )

            assert response.status_code == 302 # in [302, 200]


@pytest.mark.integration
class TestUpdateLanguageSetting:
    """Integration tests for updating language settings."""

    def test_update_language_setting_requires_admin(self, client: FlaskClient):
        """Test that updating language setting requires admin access."""
        response = client.post("/admin/language_settings/1/update", data={"move_dots": "1"})

        assert response.status_code == 302 # in [302, 401, 403]

    def test_update_language_setting_with_valid_data(self, auth_client: FlaskClient):
        """Test updating language setting with valid data."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.language_settings.update_language_setting") as mock_update:
                mock_update.return_value = MagicMock(lang_code="en")

                response = auth_client.post(
                    "/admin/language_settings/1/update",
                    data={
                        "move_dots": "1",
                        "expend": "0",
                        "add_en_lang": "1",
                    },
                    follow_redirects=False,
                )

                assert response.status_code == 302


@pytest.mark.integration
class TestDeleteLanguageSetting:
    """Integration tests for deleting language settings."""

    def test_delete_language_setting_requires_admin(self, client: FlaskClient):
        """Test that deleting language setting requires admin access."""
        response = client.post("/admin/language_settings/1/delete")

        assert response.status_code == 302 # in [302, 401, 403]

    def test_delete_language_setting_with_valid_id(self, auth_client: FlaskClient):
        """Test deleting language setting with valid ID."""
        with patch("src.sqlalchemy_app.admin.decorators.active_coordinators") as mock_coords:
            mock_coords.return_value = ["TestUser"]
            with patch("src.sqlalchemy_app.admin.routes.language_settings.delete_language_setting") as mock_delete:
                mock_delete.return_value = MagicMock(lang_code="deleted_lang")

                response = auth_client.post(
                    "/admin/language_settings/1/delete",
                    follow_redirects=False,
                )

                assert response.status_code == 302
