"""
Shared db services, used in both admin and public blueprints
"""

from ..db_service import (
    close_cached_db,
    fetch_query_safe,
    get_db,
    has_db_config,
)
from .pages_service import (
    find_exists_or_update,
    insert_page_target,
    list_pages,
)
from .pages_users_service import (
    list_user_pages,
    add_or_update_user_page,
    add_user_page,
    update_user_page,
    delete_user_page,
    find_exists_or_update_user_page,
    insert_user_page_target,
)

from .users_services import (
    get_user_token_by_username,
    upsert_user_token,
    get_user_token,
    delete_user_token,
    delete_user_token_by_username,
)

from .publish_reports_service import (
    add_report,
    delete_report,
    list_publish_reports,
)

__all__ = [
    # db_service
    "close_cached_db",
    "fetch_query_safe",
    "get_db",
    "has_db_config",

    # pages_service
    "find_exists_or_update",
    "insert_page_target",
    "list_pages",

    # users_services
    "upsert_user_token",
    "get_user_token",
    "delete_user_token",
    "get_user_token_by_username",
    "delete_user_token_by_username",

    # publish_reports_service
    "add_report",
    "delete_report",
    "list_publish_reports",

    # pages_users_service
    "list_user_pages",
    "add_or_update_user_page",
    "add_user_page",
    "update_user_page",
    "delete_user_page",
    "find_exists_or_update_user_page",
    "insert_user_page_target",
]
