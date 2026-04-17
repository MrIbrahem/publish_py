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

    def __post_init__(self) -> None:
        # Validate that required fields are not empty
        if not self.category:
            raise ValueError("Category name cannot be empty")

        if not self.campaign:
            raise ValueError("Campaign name cannot be empty")

        self.depth = int(self.depth) or 0
        self.is_default = int(self.is_default) or 0


__all__ = [
    "CategoryRecord",
]
