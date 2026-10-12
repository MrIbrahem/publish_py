"""HTTP client service for unified web requests."""

from __future__ import annotations

import logging
from typing import Any

import requests

from ...config import app_settings

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client wrapper providing standardized methods for HTTP requests."""

    def __init__(self, default_timeout: float = 30.0, user_agent: str | None = None) -> None:
        self.default_timeout = default_timeout
        self._user_agent = user_agent

    @property
    def user_agent(self) -> str:
        if self._user_agent is not None:
            return self._user_agent
        try:
            return app_settings.other.user_agent
        except Exception:
            return "MDWikiCX/1.0"

    def _prepare_headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        req_headers = dict(headers) if headers is not None else {}
        if "User-Agent" not in req_headers and "user-agent" not in req_headers:
            req_headers["User-Agent"] = self.user_agent
        return req_headers

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        auth: Any = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Perform an HTTP GET request."""
        req_headers = self._prepare_headers(headers)
        req_timeout = timeout if timeout is not None else self.default_timeout
        return requests.get(
            url,
            params=params,
            headers=req_headers,
            auth=auth,
            timeout=req_timeout,
            **kwargs,
        )

    def post(
        self,
        url: str,
        data: Any = None,
        json: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        auth: Any = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Perform an HTTP POST request."""
        req_headers = self._prepare_headers(headers)
        req_timeout = timeout if timeout is not None else self.default_timeout
        return requests.post(
            url,
            data=data,
            json=json,
            params=params,
            headers=req_headers,
            auth=auth,
            timeout=req_timeout,
            **kwargs,
        )

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        auth: Any = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Perform a generic HTTP request."""
        req_headers = self._prepare_headers(headers)
        req_timeout = timeout if timeout is not None else self.default_timeout
        return requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=req_headers,
            auth=auth,
            timeout=req_timeout,
            **kwargs,
        )


http_client = HttpClient()

__all__ = ["HttpClient", "http_client"]
