""" """

from __future__ import annotations

import json
import logging
from typing import Any

from ....database.models import PageRecord, UserPageRecord
from ....database.services import CategoryService, PagesService, UserPagesService

logger = logging.getLogger(__name__)


def _find_exists_or_update_page(
    sourcetitle: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    service = PagesService()
    orm_obj: PageRecord | None = service.find_page_record(sourcetitle, lang, user)
    if orm_obj:
        return service.set_target(orm_obj, target)
    return False


def _find_exists_or_update_user_page(
    sourcetitle: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    user_service = UserPagesService()
    orm_obj: UserPageRecord | None = user_service.find_page_record(sourcetitle, lang, user)
    if orm_obj:
        return user_service.set_target(orm_obj, target)
    return False


def add_to_db(
    wd_result: dict[str, Any],
    target: str,
    lang: str,
    user: str,
    campaign: str,
    sourcetitle: str,
    mdwiki_revid: str | int,
    translate_type: str = "lead",
    words: int = 0,
) -> dict[str, Any]:
    """Add page to database.

    Args:
        target: Target page title
        lang: Target language code
        user: Username
        wd_result: Wikidata result
        campaign: Campaign name
        sourcetitle: Source page title
        mdwiki_revid: MDWiki revision ID
        translate_type: Translation type
        words: Article words

    Returns:
        Database operation result
    """
    category_service = CategoryService()
    user_pages_service = UserPagesService()
    pages_service = PagesService()

    # Get category from campaign using database lookup
    # This mirrors the PHP retrieveCampaignCategories() function
    cat_object = category_service.get_campaign_category(campaign)
    cat = cat_object.category if cat_object else ""

    # Check if abuse filter warning was triggered
    to_users_table = "abusefilter-warning-39" in json.dumps(wd_result)

    if not to_users_table:
        user_t = user.replace("User:", "").replace("user:", "")
        if user_t in target:
            to_users_table = True

    # Normalize inputs
    sourcetitle = sourcetitle.replace("_", " ")
    target = target.replace("_", " ")
    user = user.replace("_", " ")

    if isinstance(words, str):
        words = int(words)

    # Validate required fields
    if not user or not sourcetitle or not lang:
        return {
            "use_user_sql": False,
            "to_users_table": to_users_table,
            "one_empty": {"title": sourcetitle, "lang": lang, "user": user},
        }

    result: dict[str, Any] = {
        "use_user_sql": to_users_table,
        "to_users_table": to_users_table,
    }

    # Check if exists and update if needed
    if to_users_table:
        exists = _find_exists_or_update_user_page(sourcetitle, lang, user, target)
    else:
        exists = _find_exists_or_update_page(sourcetitle, lang, user, target)

    if exists:
        result["exists"] = "already_in"
        return result

    md_revid = int(mdwiki_revid) if mdwiki_revid else None

    if to_users_table:
        # Insert new record
        add_done = user_pages_service.insert_page_target(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=md_revid,
            word=words,
        )
    else:
        # Insert new record
        add_done = pages_service.insert_page_target(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=md_revid,
            word=words,
        )

    result["execute_query"] = add_done is True
    return result


def add_to_db_tab(link_to_wd: dict[str, Any], tab: dict[str, Any]) -> dict[str, Any]:

    return add_to_db(
        link_to_wd,
        tab["title"],
        tab["lang"],
        tab["user"],
        tab["campaign"],
        tab["sourcetitle"],
        tab["revid"],
        translate_type=tab["translate_type"],
        words=tab["words"],
    )


__all__ = [
    "add_to_db_tab",
]
