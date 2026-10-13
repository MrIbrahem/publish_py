"""
External API clients for the new_html module.
- MdwikiApi: fetch wikitext + revision id
"""

from __future__ import annotations

import json
import logging
import re

from ....services.clients.http_client import HttpClient

logger = logging.getLogger(__name__)

def normalize_title_for_url(title: str) -> str:
    """
    doesn't normalize the title. Here the title is only replace("/", "%2F"), whereas MdwikiApi.get_wikitext
    also replaces spaces with underscores. Multi-word titles will build a malformed REST URL and the
    transform will fail. Reuse the same encoding as the fetch path.
    """
    title = title.replace(" ", "_")
    title = title.replace("/", "%2F")
    return title


class MdwikiApi:
    """
    MDWiki API services.

    Provides functions for fetching wikitext content from MDWiki
    using both the API and REST API endpoints.

    https://mdwiki.org/w/rest.php/v1/page/Sympathetic_crashing_acute_pulmonary_edema/html
    https://mdwiki.org/w/rest.php/v1/revision/1420795/html

    """

    REST_BASE = "https://mdwiki.org/w/rest.php/v1"
    API_BASE = "https://mdwiki.org/w/api.php"

    def __init__(
        self,
        http_client: HttpClient | None = None,
    ) -> None:
        """Initialize the checker with an HTTP client instance."""
        self.http_client = http_client or HttpClient()

        # Fallback to Action API
        self.fallback_to_action_api = False

    def _fetch_action_api(self, title: str) -> tuple[str, str, str]:
        """
        Get wikitext content from MDWiki API.
        """
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": title,
            "utf8": 1,
            "formatversion": "2",
            "rvprop": "content|ids",
        }

        response_array = self.http_client.safe_request(self.API_BASE, method="GET", params=params)

        output = response_array.get("output")
        error = response_array.get("error")

        if error or not output:
            logger.error("MdwikiApi: Failed to fetch data from MDWiki API for title: %s", title)
            return "", "", error or "Empty response"

        try:
            json_data = json.loads(output)
            pages = json_data.get("query", {}).get("pages", [])
            if not pages:
                return "", "", "No pages found"

            revisions = pages[0].get("revisions", [])
            if not revisions:
                return "", "", "No revisions found"

            source = revisions[0].get("content", "")
            revid = revisions[0].get("revid", "")
            return source, str(revid), ""

        except (json.JSONDecodeError, IndexError, TypeError) as exc:
            logging.error(f"MdwikiApi: No revision data found for title: {title}")
            return "", "", str(exc)
        except Exception as exc:
            logger.error("Failed to parse MDWiki Action API response: %s", exc)
            return "", "", str(exc)

    def _fetch_rest(self, title: str) -> tuple[str, str, str]:
        """Get wikitext content from MDWiki REST API."""
        title_encoded = normalize_title_for_url(title)
        url = f"{self.REST_BASE}/page/{title_encoded}"

        response = self.http_client.safe_request(
            url=url,
            method="GET",
            timeout=3,
        )
        error = response.get("error")
        output = response.get("output") or ""

        if error or not output:
            logger.error("MdwikiApi: Failed to fetch data from MDWiki REST API for title: %s", title)
            # Fallback to Action API
            if self.fallback_to_action_api:
                return self._fetch_action_api(title)

            return "", "", error or "Empty response"

        try:
            json_data = json.loads(output)
            source = json_data.get("source", "")
            revid = json_data.get("latest", {}).get("id", "")
            return source, str(revid), ""

        except (Exception, json.JSONDecodeError) as exc:
            logger.error("Failed to parse MDWiki REST response: %s", exc)
            if self.fallback_to_action_api:
                return self._fetch_action_api(title)

            return "", "", error or "Empty response"

    def get_wikitext(self, title: str) -> tuple[str, str, str]:
        """
        Return (source, revid, error).
        Follows #REDIRECT if present.
        """
        source, revid, error = self._fetch_rest(title)

        # Follow redirect
        if source:
            match = re.search(r"#REDIRECT\s*\[\[(.*?)\]\]", source, re.IGNORECASE)
            if match:
                redirect_title = match.group(1).strip()
                logger.info("Redirecting to: %s", redirect_title)
                source, revid, error = self._fetch_rest(redirect_title)

        if not source:
            logger.error("WikitextHandler: wikitext empty for title: %s", title)

        return source, str(revid) if revid else "", error

__all__ = [
    "MdwikiApi",
]
