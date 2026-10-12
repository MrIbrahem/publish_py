"""
WikidataLinker    : links the new page to Wikidata (with fallback user)
"""

from __future__ import annotations

import logging
from typing import Any

from ....config import app_settings
from ....database.services import (
    UserTokenService,
)
from ....services.clients import (
    MediaWikiApiClient,
    WikidataClient,
)
from .error_resolver import ErrorFileResolver
from .report_recorder import ReportRecorder

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Wikidata
# --------------------------------------------------------------------------- #
class WikidataLinker:
    """Links a published page to Wikidata, retrying with a fallback user."""

    def __init__(
        self,
        recorder: ReportRecorder,
        token_service: UserTokenService | None = None,
    ) -> None:
        self.recorder = recorder
        self.token_service = token_service or UserTokenService()

    @staticmethod
    def _should_link(lang: str, title: str) -> bool:
        """Return False if the page is missing or is a user page (ns 2)."""
        page_information = MediaWikiApiClient.get_title_info(title, lang)
        if not page_information:
            return False

        # skip link to wd for user pages
        return page_information.get("ns", None) != 2

    def _retry_with_fallback_user(
        self,
        sourcetitle: str,
        lang: str,
        title: str,
        user: str,
    ) -> dict[str, Any]:
        """Retry Wikidata linking with fallback user credentials."""
        fallback_user = app_settings.users.fallback_user
        logger.debug(f"get_csrftoken failed for user: {user}, retrying with {fallback_user}")

        # Retry with fallback user credentials
        fallback_token = self.token_service.get_user_token_by_username(fallback_user)

        if fallback_token is None:
            return {}

        fallback_access_key, fallback_access_secret = fallback_token.decrypted()
        link_result = WikidataClient.link_to_wikidata(
            sourcetitle,
            lang,
            fallback_user,
            title,
            fallback_access_key,
            fallback_access_secret,
        )

        if "error" not in link_result:
            link_result["fallback_user"] = fallback_user
            link_result["original_user"] = user
            logger.debug(f"Successfully linked using {fallback_user} fallback credentials")
        return link_result

    def _record_error(
        self,
        link_result: dict[str, Any],
        sourcetitle: str,
        lang: str,
        user: str,
        title: str,
    ) -> None:
        tab3 = {
            "error": link_result["error"],
            "qid": link_result.get("qid", ""),
            "title": title,
            "sourcetitle": sourcetitle,
            "fallback": link_result.get("fallback", ""),
            "lang": lang,
            "username": user,
        }
        file_name = ErrorFileResolver.resolve(link_result.get("error", {}), "wd_errors")

        # Insert to reports
        self.recorder.record(
            tab3,
            file_name,
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
        )

    def link(
        self,
        sourcetitle: str,
        lang: str,
        user: str,
        title: str,
        access_key: str,
        access_secret: str,
    ) -> dict[str, Any]:
        """
        Run the post-edit Wikidata linking and record any error.

        Args:
            sourcetitle: Source page title
            lang: Target language code
            user: Username
            title: Target page title
            access_key: OAuth access key
            access_secret: OAuth access secret

        Returns:
            Wikidata link result
        """
        if not self._should_link(lang, title):
            # skip link to wd for user pages
            return {"error": "skip link to wd for user pages"}

        link_result = WikidataClient.link_to_wikidata(sourcetitle, lang, user, title, access_key, access_secret)

        # Check if the error is get_csrftoken failure and user is not already the fallback user
        fallback_user = app_settings.users.fallback_user
        if link_result.get("error") == "get_csrftoken failed" and user != fallback_user:
            link_result["fallback"] = self._retry_with_fallback_user(sourcetitle, lang, title, user)

        if "error" in link_result:
            self._record_error(link_result, sourcetitle, lang, user, title)

        return link_result


__all__ = [
    "WikidataLinker",
]
