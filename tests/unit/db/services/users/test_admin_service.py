from unittest.mock import patch

import pytest

from src.main_app.db.services.users.admin_service import AdminService


class TestSetup:
    def setup_method(self):
        self.service = AdminService()


class TestAddCoordinator(TestSetup):
    def test_empty_username_raises(self):
        with patch("src.main_app.db.services.users.admin_service.db"):
            with pytest.raises(ValueError, match="Username is required"):
                self.service.add_coordinator("")
