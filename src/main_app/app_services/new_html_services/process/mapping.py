from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PageRequest:
    """Typed, validated representation of an incoming request.

    Request parameters:
    - title:      page title (already normalized by the controller)
    - new:        force regeneration of cached content
    - all:        use the 'all' data file
    - printetxt: output format (wikitext|html|seg), alias: print
    """

    FORMAT_JSON = "json"
    FORMAT_WIKITEXT = "wikitext"
    FORMAT_HTML = "html"
    FORMAT_SEG = "seg"

    VALID_FORMATS = [
        FORMAT_WIKITEXT,
        FORMAT_HTML,
        FORMAT_SEG,
    ]

    title: str
    format: str
    all: bool
    new: bool

    @classmethod
    def from_array(cls, get_request: Mapping[str, Any], title: str) -> PageRequest:
        """Create a PageRequest instance from a request parameters dictionary and title.

        :param get_request: Usually equivalent to $_GET parameters
        :param title: The page title
        :return: PageRequest instance
        """
        format_val = str(get_request.get("printetxt") or get_request.get("print") or "")
        if format_val not in cls.VALID_FORMATS:
            format_val = cls.FORMAT_JSON

        all_flag = bool(get_request.get("all", ""))

        # Video pages always use the 'all' data file
        if title.startswith("Video"):
            all_flag = True

        force_new = "new" in get_request

        return cls(
            title=title,
            format=format_val,
            all=all_flag,
            new=force_new,
        )


@dataclass(frozen=True)
class PageResult:
    """Result of processing a page.

    Contains no output side effects: the controller decides how to send it.
    """

    status: int
    format: str
    body: str | dict[str, Any] | list[Any]

    @classmethod
    def json(cls, status: int, data: dict[str, Any]) -> PageResult:
        """Create a JSON page result."""
        return cls(status=status, format=PageRequest.FORMAT_JSON, body=data)

    @classmethod
    def text(cls, format: str, body: str, status: int = 200) -> PageResult:
        """Create a text page result (wikitext, html, or seg)."""
        return cls(status=status, format=format, body=body)
