"""MediaWiki API client for edit operations.

Mirrors: php_src/bots/api/do_edit.php
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .http_client import HttpClient
from .oauth_client import OAuthClient

logger = logging.getLogger(__name__)


class MediaWikiApiClient:
    """Client for MediaWiki API operations."""

    def __init__(
        self,
        http_client: HttpClient | None = None,
    ) -> None:
        """Initialize the checker with an HTTP client instance."""
        self.http_client = http_client or HttpClient()

    def get_title_info(self, targettitle: str, lang: str) -> dict[str, Any] | None:
        """Get page information from Wikipedia API.

        Args:
            targettitle: Target page title
            lang: Language code

        Returns:
            Page info dictionary or None if not found
        """
        params = {
            "action": "query",
            "format": "json",
            "titles": targettitle,
            "utf8": 1,
            "formatversion": "2",
        }
        url = f"https://{lang}.wikipedia.org/w/api.php"

        try:
            response = self.http_client.get(url, params=params, timeout=30)
            result = response.json()
            logger.debug(f"GetTitleInfo result: {result}")
            pages = result.get("query", {}).get("pages", [])
            if pages:
                return pages[0]
        except Exception as e:
            logger.error(f"GetTitleInfo error: {e}")

        return None

    def publish_do_edit(
        self,
        api_params: dict[str, Any],
        wiki: str,
        access_key: str,
        access_secret: str,
    ) -> dict[str, Any]:
        """Publish an edit to MediaWiki.

        Args:
            api_params: API parameters for the edit
            wiki: Wiki language code
            access_key: OAuth access key
            access_secret: OAuth access secret

        Returns:
            Edit result as dictionary
        """
        https_domain = f"https://{wiki}.wikipedia.org"
        response = OAuthClient().post_params(api_params, https_domain, access_key, access_secret)

        try:
            result = json.loads(response) if response else {}
        except json.JSONDecodeError:
            logger.error(f"Failed to parse edit response: {response}")
            result = {"error": "Failed to parse response"}

        return result


def get_title_info(targettitle: str, lang: str) -> dict[str, Any] | None:
    return MediaWikiApiClient().get_title_info(targettitle, lang)


def publish_do_edit(
    api_params: dict[str, Any],
    wiki: str,
    access_key: str,
    access_secret: str,
) -> dict[str, Any]:
    return MediaWikiApiClient().publish_do_edit(
        api_params,
        wiki,
        access_key,
        access_secret,
    )


__all__ = [
    "MediaWikiApiClient",
    "get_title_info",
    "publish_do_edit",
]
