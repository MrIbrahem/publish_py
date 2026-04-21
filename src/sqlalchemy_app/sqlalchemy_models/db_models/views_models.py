"""
Views domain models - Dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EnwikiPageviewRecord:
    """Representation of an enwiki pageview record."""

    id: int
    title: str
    en_views: int | None = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "en_views": self.en_views,
        }


@dataclass
class ViewsNewRecord:
    """Representation of a views_new record."""

    id: int
    target: str
    lang: str
    year: int
    views: int | None = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "lang": self.lang,
            "year": self.year,
            "views": self.views,
        }


@dataclass
class ViewsNewAllRecord:
    """Representation of a views_new_all view record (aggregated views)."""

    target: str
    lang: str
    views: int | None = 0

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "lang": self.lang,
            "views": self.views,
        }


__all__ = [
    "EnwikiPageviewRecord",
    "ViewsNewRecord",
    "ViewsNewAllRecord",
]
