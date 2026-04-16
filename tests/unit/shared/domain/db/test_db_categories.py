"""
Tests for db.db_categories module.

TODO: CategoriesDB has major updates, we should rewrite related tests.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.config import DbConfig
from src.app_main.shared.domain.db.db_categories import (
    CategoriesDB,
)


@pytest.fixture
def fixture_for_category_db() -> DbConfig:
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="localhost",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


class TestCategoriesDB:
    """Tests for CategoriesDB class."""
    ...
