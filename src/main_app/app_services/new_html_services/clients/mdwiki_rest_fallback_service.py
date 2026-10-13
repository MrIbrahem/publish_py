import logging
from typing import Any

from ....services.clients import HttpClient

from .local_rest_json_repository import LocalRestJsonRepository

# Assuming these are imported from your custom modules/packages
from .mdwiki_api import MdwikiApi


class MdwikiRestFallbackService:
    """Fetches REST wikitext from MDWiki, falling back to local files when the API fails."""

    def __init__(
        self,
        http_client: HttpClient | None = None,
        mdwiki_api: Any | None = None,
        local: Any | None = None,
    ) -> None:
        """Initialize the fallback service."""
        self.http_client = http_client or HttpClient()
        self.mdwiki_api = mdwiki_api or MdwikiApi(self.http_client)
        self.local = local or LocalRestJsonRepository()

    def get_wikitext(self, title: str) -> dict[str, str]:
        """Fetch wikitext from the REST API, falling back to local storage on failure.

        :param title: The title of the page to fetch
        :return: Dictionary containing source, revid, and error message
        """
        source, revid, error_msg = self.mdwiki_api._fetch_rest(title)

        if error_msg:
            logging.error(
                f"MdwikiRestFallbackService: REST API failed ({error_msg}) for title: {title}, trying local file"
            )

            json_data = self.local.find(title)
            if json_data is not None:
                revid = json_data.get("latest", {}).get("id", "")
                return {
                    "source": json_data.get("source", ""),
                    "revid": str(revid),
                    "error": "",
                }

        return {
            "source": source,
            "revid": str(revid),
            "error": error_msg,
        }
