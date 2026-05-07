"""
Shared db services, used in both admin and public blueprints
"""

from .page_service import (
    find_exists_or_update_page,
    insert_page_target,
    list_pages,
    list_pages_by_lang_cat,
)
from .allqid_service import list_targets_by_lang
from .qid_service import list_qids
from .report_service import (
    add_report,
    delete_report,
    list_reports,
    query_reports_with_filters,
)
from .user_page_service import (
    add_user_page,
    delete_user_page,
    find_exists_or_update_user_page,
    insert_user_page_target,
    list_user_pages,
    update_user_page,
)
from .user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)

__all__ = [
    # page_service
    "find_exists_or_update_page",
    "insert_page_target",
    "list_pages",
    "list_pages_by_lang_cat",
    # qid_service
    "list_targets_by_lang",
    "list_qids",
    # user_token_service
    "upsert_user_token",
    "get_user_token",
    "delete_user_token",
    "get_user_token_by_username",
    "delete_user_token_by_username",
    # report_service
    "add_report",
    "delete_report",
    "list_reports",
    "query_reports_with_filters",
    # user_page_service
    "list_user_pages",
    "add_user_page",
    "update_user_page",
    "delete_user_page",
    "find_exists_or_update_user_page",
    "insert_user_page_target",
]
