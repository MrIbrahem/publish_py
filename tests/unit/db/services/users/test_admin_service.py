# ruff: noqa: F401
from unittest.mock import MagicMock, patch
import pytest

from src.main_app.db.exceptions import DuplicateUserError
from src.main_app.db.models import AdminUserRecord
from src.main_app.db.services.users.admin_service import (
    active_coordinators,
    add_coordinator,
    delete_coordinator,
    get_coordinator_by_id,
    is_active_coordinator,
    list_coordinators,
    set_coordinator_active,
)


class TestAddCoordinator:
    def test_empty_username_raises(self):
        with patch("src.main_app.db.services.users.admin_service.db"):
            with pytest.raises(ValueError, match="Username is required"):
                add_coordinator("")


class TestGetCoordinatorById:
    def test_not_found_raises(self):
        mock_db = MagicMock()
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        with patch("src.main_app.db.services.users.admin_service.db", mock_db):
            assert get_coordinator_by_id(999) is not None
