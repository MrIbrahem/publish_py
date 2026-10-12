"""
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from ...services.clients.http_client import http_client

logger = logging.getLogger(__name__)

class HttpClientService:

    @staticmethod
    def request(
        url: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        timeout: float = 15.0,
    ) -> dict[str, Any]:
        """
        Low-level HTTP helper.

        Returns a normalized dict:
        {
            "output": str,
            "error": str,
            "error_code": str,
            "http_code": int,
        }
        """
        result = {
            "output": "",
            "error": "",
            "error_code": "",
            "http_code": 0,
        }

        try:
            response = http_client.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout,
            )
        except requests.Timeout:
            result["error"] = "Request timed out"
            result["error_code"] = "TIMEOUT"
            logger.error("Timeout while requesting: %s", url)
            return result
        except Exception as exc:
            result["error"] = str(exc)
            result["error_code"] = "REQUEST_ERROR"
            logger.error("Request failed for %s: %s", url, exc)
            return result

        output = response.text
        result["output"] = output
        result["http_code"] = response.status_code

        if response.status_code != 200:
            logging.error("HttpClientService: API returned HTTP %s", response.status_code)
            result["error"] = "HTTP_ERROR"
            result["error_code"] = str(response.status_code)

            # check Cloudflare protection
            if isinstance(output, str) and "Just a moment..." in output:
                logging.error("HttpClientService: Cloudflare protection detected")
                logger.error("Cloudflare protection detected: 'Just a moment...' page returned")
                result["error"] = "CLOUDFLARE_PROTECTION"

            else:
                logger.error(repr(output))

            result["output"] = ""
            return result

        return result


__all__ = [
    "HttpClientService",
]
