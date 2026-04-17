from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UsersNoInprocessRecord:
    """Representation of a users_no_inprocess record."""

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


__all__ = ["UsersNoInprocessRecord"]
