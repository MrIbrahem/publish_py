"""
Save a published page to the database (pages / user pages tables).

Structure:
    UsersTableResolver : decides whether the record goes to the users table
    PageDataSaver      : normalizes the data and inserts / updates the record

The only public entry point is `PageDataSaver.save_from_tab`.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ....database.services import CategoryService, PagesService, UserPagesService

logger = logging.getLogger(__name__)


class UsersTableResolver:
    """Decides if the page must be stored in the users table."""

    ABUSE_FILTER_WARNING = "abusefilter-warning-39"

    @classmethod
    def should_use(cls, wd_result: dict[str, Any], user: str, target: str) -> bool:
        # Abuse filter warning was triggered
        if cls.ABUSE_FILTER_WARNING in json.dumps(wd_result):
            return True

        # The target page is inside the user's own space
        user_t = user.replace("User:", "").replace("user:", "")
        return user_t in target


class PageDataSaver:
    """Normalizes page data and saves it to the right table."""

    def __init__(
        self,
        category_service: CategoryService | None = None,
        pages_service: PagesService | None = None,
        user_pages_service: UserPagesService | None = None,
    ) -> None:
        self.category_service = category_service or CategoryService()
        self.pages_service = pages_service or PagesService()
        self.user_pages_service = user_pages_service or UserPagesService()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _get_category(self, campaign: str) -> str:
        """Get category from campaign (mirrors PHP retrieveCampaignCategories())."""
        cat_object = self.category_service.get_campaign_category(campaign)
        return cat_object.category if cat_object else ""

    def _select_service(self, to_users_table: bool) -> PagesService | UserPagesService:
        """Both services share find_page_record / set_target / insert_page_target."""
        return self.user_pages_service if to_users_table else self.pages_service

    @staticmethod
    def _update_if_exists(
        service: PagesService | UserPagesService,
        sourcetitle: str,
        lang: str,
        user: str,
        target: str,
    ) -> bool:
        orm_obj = service.find_page_record(sourcetitle, lang, user)
        if orm_obj:
            return service.set_target(orm_obj, target)
        return False

    # ------------------------------------------------------------------ #
    # Main operation
    # ------------------------------------------------------------------ #
    def save(
        self,
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
            wd_result: Wikidata result
            target: Target page title
            lang: Target language code
            user: Username
            campaign: Campaign name
            sourcetitle: Source page title
            mdwiki_revid: MDWiki revision ID
            translate_type: Translation type
            words: Article words

        Returns:
            Database operation result
        """
        cat = self._get_category(campaign)

        to_users_table = UsersTableResolver.should_use(wd_result, user, target)

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

        service = self._select_service(to_users_table)

        # Check if exists and update if needed
        if self._update_if_exists(service, sourcetitle, lang, user, target):
            result["exists"] = "already_in"
            return result

        md_revid = int(mdwiki_revid) if mdwiki_revid else None

        # Insert new record
        add_done = service.insert_page_target(
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

    def save_from_tab(self, link_to_wd: dict[str, Any], tab: dict[str, Any]) -> dict[str, Any]:
        """Save using the operation metadata dict built by the publish worker."""
        return self.save(
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
    "PageDataSaver",
]
