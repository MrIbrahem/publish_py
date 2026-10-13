"""
- TransformApiService: wikitext → HTML
"""

from __future__ import annotations
import logging

from ....config.main_settings import app_settings
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


class TransformApiService:
    """
    Wikipedia transform API services.

    Provides functions for converting wikitext to HTML using the
    Wikipedia REST API transform endpoint.
    """

    def __init__(
        self,
        http_client: HttpClient | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the checker with an HTTP client instance."""
        self.http_client = http_client or HttpClient()
        self.base_url = base_url or app_settings.new_html.transform_base_url

    def convert(self, wikitext: str, title: str) -> dict[str, str]:
        """
        Convert wikitext to HTML using the Wikipedia REST API.

        :param text: The wikitext to convert
        :param title: The title of the page (used for context in conversion)
        :return: dictionary with 'result' key on success or 'error' key on failure
        """
        if not wikitext:
            return {"error": "Empty wikitext"}

        title_encoded = normalize_title_for_url(title)
        url = f"{self.base_url}/transform/wikitext/to/html/{title_encoded}"

        response_array = self.http_client.safe_request(
            url,
            method="POST",
            data={"wikitext": wikitext},
            timeout=30.0,
        )

        response_output = response_array.get("output") or ""

        # Handle the response from the API
        if not response_output:
            logger.error("API request failed for title: %s", title)
            error_msg = response_array.get("error")
            error_code = response_array.get("error_code")
            if error_msg:
                logger.error("Error details: %s (%s)", error_msg, error_code)

            logger.debug("API request failed.")
            return {"error": error_msg or "Error: Could not reach API."}

        # Check if response contains an error
        if ">Wikimedia Error" in response_output:
            logger.error("API returned error for title: %s", title)
            return {"error": "Error: Wikipedia API returned an error."}

        # Check if response is valid HTML
        if "<html" not in response_output.lower():
            logger.error("API returned invalid HTML for title: $title")
            return {"error": "Error: Wikipedia API returned invalid HTML."}

        return {"result": response_output}


__all__ = [
    "TransformApiService",
]
