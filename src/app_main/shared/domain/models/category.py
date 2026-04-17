from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ...db.engine import BaseDb

logger = logging.getLogger(__name__)


class _CategoryRecord(BaseDb):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(120), unique=True, nullable=False)
    campaign = Column(String(120), nullable=False, default="")
    display = Column(String(120), nullable=False, default="")
    category2 = Column(String(120), nullable=False, default="")
    depth = Column(Integer, nullable=False, default=0)
    is_default = Column(Integer, nullable=False, default=0)

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
