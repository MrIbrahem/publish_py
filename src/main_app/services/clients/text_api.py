from __future__ import annotations

import logging
import re

from .http_client import http_client

ALLOWED_WIKI_PROJECT = re.compile(r"^(?:[a-z0-9-]+\.wikipedia\.org|commons\.wikimedia\.org)$", re.IGNORECASE)

logger = logging.getLogger(__name__)


class TextApiClient:
    """Client for fetching raw text from MediaWiki API."""

    @staticmethod
    def get_wikitext(title: str, project: str = "commons.wikimedia.org") -> str:
        """Fetch raw wikitext of a page from Wikimedia projects.

        Args:
            title (str): Page title (e.g. 'Template:OWID/Parkinsons prevalence')
            project (str): Domain of wiki (default: commons.wikimedia.org)

        Returns:
            str: wikitext content or empty string if not found/rejected
        """
        if not ALLOWED_WIKI_PROJECT.fullmatch(project):
            logger.warning("Rejected unsupported wiki project: %s", project)
            return ""

        api_url = f"https://{project}/w/api.php"
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "formatversion": "2",
            "rvslots": "*",
            "titles": title,
        }
        data = {}
        try:
            response = http_client.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Error: get_wikitext : {e}")

        pages = data.get("query", {}).get("pages", [])
        for page in pages:
            revs = page.get("revisions")
            if revs:
                return revs[0].get("slots", {}).get("main", {}).get("content") or ""

        return ""


def get_wikitext(title: str, project: str = "commons.wikimedia.org") -> str:
    return TextApiClient.get_wikitext(title, project)


__all__ = [
    "TextApiClient",
    "get_wikitext",
]
