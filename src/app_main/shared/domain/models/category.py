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
    category: str
    campaign: str
    display: str | None = ""
    category2: str | None = ""
    depth: int = 0
    is_default: int = 0

    def to_dict(self) -> dict:
        """Convert the CategoryRecord to a dictionary."""
        return {
            "id": self.id,
            "category": self.category,
            "campaign": self.campaign,
            "display": self.display,
            "category2": self.category2,
            "depth": self.depth,
            "is_default": self.is_default,
        }


__all__ = [
    "CategoryRecord",
]
