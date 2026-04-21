"""
Shared domain models - Dataclasses.

Note: Several models have been moved to specialized modules:
- pages_models.py: PageRecord, UserPageRecord
- qid_models.py: QidRecord
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CategoryRecord:
    """
    Category records.
    """

    id: int
    category: str
    campaign: str
    display: str | None = ""
    category2: str | None = ""
    depth: int = 0
    is_default: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "campaign": self.campaign,
            "display": self.display,
            "category2": self.category2,
            "depth": self.depth,
            "is_default": self.is_default,
        }

    def __post_init__(self) -> None:
        # Validate that required fields are not empty
        if not self.category:
            raise ValueError("Category name cannot be empty")

        if not self.campaign:
            raise ValueError("Campaign name cannot be empty")

        self.depth = int(self.depth) or 0
        self.is_default = int(self.is_default) or 0


@dataclass
class ReportRecord:
    """Representation of a report record."""

    id: int
    date: Any
    title: str
    user: str
    lang: str
    sourcetitle: str
    result: str
    data: str

    def to_dict(self) -> dict[str, Any]:
        """Convert a ReportRecord to a dictionary."""
        # Handle date conversion with None safety
        if self.date is None:
            date_str = ""
        elif hasattr(self.date, "isoformat"):
            date_str = self.date.isoformat()
        else:
            date_str = str(self.date)

        return {
            "id": self.id,
            "date": date_str,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


__all__ = [
    "ReportRecord",
    "CategoryRecord",
]
