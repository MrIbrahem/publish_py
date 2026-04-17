"""
Shared db services, used in both admin and public blueprints
"""

from .db_service import (
    close_cached_db,
    fetch_query_safe,
    get_db,
    has_db_config,
)
from .pages_service import (
    find_exists_or_update,
    get_pages_db,
    insert_page_target,
    list_pages,
)
from .pages_users_service import (
    insert_user_page_target,
)
from .users_services import (
    get_user_token_by_username,
)

__all__ = [
    "close_cached_db",
    "fetch_query_safe",
    "get_db",
    "has_db_config",
    "find_exists_or_update",
    "get_pages_db",
    "insert_page_target",
    "insert_user_page_target",
    "list_pages",
    "get_user_token_by_username",
]
