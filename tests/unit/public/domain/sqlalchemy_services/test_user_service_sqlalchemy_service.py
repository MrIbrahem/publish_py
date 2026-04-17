"""
TODO: write tests
"""

import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.sqlalchemy_db.engine import init_db, build_engine, BaseDb
from src.app_main.public.domain.sqlalchemy_services.user_service import (
    list_users,
    list_users_by_group,
    get_user,
    get_user_by_username,
    add_user,
    add_or_update_user,
    update_user,
    delete_user,
    user_exists,
)
