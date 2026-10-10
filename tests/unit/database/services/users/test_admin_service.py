from unittest.mock import patch

import pytest

from src.main_app.database.services.users.coordinator_service import CoordinatorService


class TestSetup:
    def setup_method(self):
        self.service = CoordinatorService()


class TestAddCoordinator(TestSetup):
    def test_empty_username_raises(self):
        with patch("src.main_app.database.services.users.coordinator_service.db"):
            with pytest.raises(ValueError, match="Username is required"):
                self.service.add_coordinator("")
