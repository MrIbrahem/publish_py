"""
Service for fetching wikitext from MDWiki.
"""

import logging
from typing import Any

from ..services.http_client import HttpClient

logger = logging.getLogger(__name__)


class MdwikiApiService:
    """
    Fetches page content from MDWiki using the REST API.
    """

    def __init__(self, http_client: HttpClient | None = None):
        self.http = http_client or HttpClient()
        self.base_rest_url = "https://mdwiki.org/w/rest.php/v1"

    def get_wikitext(self, title: str) -> dict[str, Any]:
        """
        Get wikitext and revision ID for a given title.

        Returns:
            {
                "source": str,
                "revid": str | int,
                "error": str,
            }
        """
        # Encode title for URL
        title_encoded = title.replace(" ", "_").replace("/", "%2F")
        url = f"{self.base_rest_url}/page/{title_encoded}"

        response = self.http.request(url, method="GET")

        if response["error"] or not response["output"]:
            logger.error(f"Failed to fetch wikitext for title: {title}")
            return {
                "source": "",
                "revid": "",
                "error": response.get("error") or "Empty response",
            }

        try:
            data = response["output"]
            import json

            json_data = json.loads(data)

            source = json_data.get("source", "")
            revid = json_data.get("latest", {}).get("id", "")

            return {
                "source": source,
                "revid": revid,
                "error": "",
            }
        except Exception as e:
            logger.error(f"Failed to parse MDWiki response for {title}: {e}")
            return {
                "source": "",
                "revid": "",
                "error": str(e),
            }


__all__ = [
    "MdwikiApiService",
]
