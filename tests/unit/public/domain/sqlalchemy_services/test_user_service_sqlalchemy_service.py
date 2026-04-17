"""
TODO: write tests
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.sqlalchemy_services.user_service import (
    add_or_update_user,
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    list_users,
    list_users_by_group,
    update_user,
    user_exists,
)
from src.app_main.shared.sqlalchemy_db.engine import BaseDb, build_engine, init_db
