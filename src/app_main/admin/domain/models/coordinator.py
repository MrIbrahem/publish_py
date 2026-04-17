""" """

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CoordinatorRecord:
    """Representation of a coordinator record."""

    id: int
    username: str
    is_active: int = 1

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
        }


__all__ = [
    "CoordinatorRecord",
]
