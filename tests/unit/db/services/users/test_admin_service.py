# ruff: noqa: F401
from unittest.mock import patch

import pytest

from src.main_app.db.services.users.admin_service import (
    AdminService,
    add_coordinator,
)


class TestAddCoordinator:
    def test_empty_username_raises(self):
        with patch("src.main_app.db.services.users.admin_service.db"):
            with pytest.raises(ValueError, match="Username is required"):
                add_coordinator("")
