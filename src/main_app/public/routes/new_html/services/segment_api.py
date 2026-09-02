"""
Service for converting HTML to segmented content.
"""

import json
import logging

from .http_client import HttpClient

logger = logging.getLogger(__name__)


class SegmentApiService:
    """
    Converts HTML to segments using the external HtmltoSegments API.
    """

    def __init__(self, http_client: HttpClient | None = None):
        self.http = http_client or HttpClient()
        # Current production endpoint
        self.api_url = "https://mdwikipy.toolforge.org/HtmltoSegments"

    def convert(self, html: str) -> dict[str, str]:
        """
        Convert HTML to segmented content.

        Returns:
            {"result": str} on success or {"error": str} on failure.
        """
        if not html:
            return {"error": "Empty HTML"}

        response = self.http.request(
            self.api_url,
            method="POST",
            json={"html": html},
        )

        if response["error"] or not response["output"]:
            logger.error("Segment API request failed")
            return {"error": "Could not reach Segment API"}

        try:
            data = json.loads(response["output"])
        except Exception:
            return {"error": "Invalid JSON response from Segment API"}

        if "error" in data:
            return {"error": data["error"]}

        if "result" in data:
            result = data["result"]

            # Filter known empty/error messages
            if result in (
                "Content for translate is not given or is empty",
                "Sectionwrap: Attempting to remove a non-section tag: undefined",
            ):
                return {"result": ""}

            return {"result": result}

        return {"error": "Unexpected response format"}


__all__ = [
    "SegmentApiService",
]
