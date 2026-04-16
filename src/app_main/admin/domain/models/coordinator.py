from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CoordinatorRecord:
    """Representation of a coordinator record."""

    id: int
    user: str
    active: int = 1

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "user": self.user,
            "active": self.active,
        }


__all__ = ["CoordinatorRecord"]
