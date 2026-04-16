from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CategoryRecord:
    """
    Category records.
    """

    id: int
    category: str | None = None
    category2: str | None = ""
    display: str | None = ""
    campaign: str | None = ""
    depth: int | None = None
    is_default: int = 0

    def to_dict(self) -> dict:
        """Convert the CategoryRecord to a dictionary."""
        return {
            "id": self.id,
            "category": self.category,
            "category2": self.category2,
            "display": self.display,
            "campaign": self.campaign,
            "depth": self.depth,
            "is_default": self.is_default,
        }


__all__ = [
    "CategoryRecord",
]
