"""
Shared db services, used in both admin and public blueprints

"""

from .wikidata.allqid_service import list_targets_by_lang
from .content.category_service import (
    add_category,
    delete_category,
    get_camp_to_cats,
    get_campaign_category,
    list_categories,
    update_category,
)
from .pages.in_process_service import (
    add_in_process,
    delete_in_process,
    delete_in_process_by_title_user_lang,
    get_in_process,
    get_in_process_by_title_user_lang,
    get_in_process_counts_by_user,
    is_in_process,
    list_in_process,
    list_in_process_by_lang,
    list_in_process_by_user,
    update_in_process,
)
from .content.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    list_langs,
)
from .pages.page_service import (
    add_page,
    delete_page,
    find_exists_or_update_page,
    insert_page_target,
    list_of_users_by_translations_count,
    list_pages,
    list_pages_by_lang_cat,
    update_page,
)
from .wikidata.qid_service import list_qids
from .reports.report_service import (
    add_report,
    delete_report,
    list_reports,
    query_reports_with_filters,
)
from .pages.user_page_service import (
    add_user_page,
    delete_user_page,
    find_exists_or_update_user_page,
    insert_user_page_target,
    list_user_pages,
    update_user_page,
)
from .users.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)

__all__ = [
    "list_in_process",
    "list_in_process_by_user",
    "list_in_process_by_lang",
    "get_in_process",
    "get_in_process_by_title_user_lang",
    "add_in_process",
    "update_in_process",
    "delete_in_process",
    "delete_in_process_by_title_user_lang",
    "is_in_process",
    "get_in_process_counts_by_user",
    "add_category",
    "update_category",
    "delete_category",
    "get_campaign_category",
    "list_categories",
    "get_camp_to_cats",
    # page_service
    "list_pages",
    "list_pages_by_lang_cat",
    "add_page",
    "update_page",
    "delete_page",
    "find_exists_or_update_page",
    "insert_page_target",
    "list_of_users_by_translations_count",
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
    "list_reports",
    "add_report",
    "delete_report",
    "query_reports_with_filters",
    # user_page_service
    "list_user_pages",
    "add_user_page",
    "update_user_page",
    "delete_user_page",
    "find_exists_or_update_user_page",
    "insert_user_page_target",
    "list_langs",
    "get_lang",
    "get_lang_by_code",
    "add_lang",
    "add_or_update_lang",
    "delete_lang",
]
