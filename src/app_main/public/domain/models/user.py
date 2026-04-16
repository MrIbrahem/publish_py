from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class UserRecord:
    """Representation of a user record."""

    user_id: int
    username: str
    email: str = ""
    wiki: str = ""
    user_group: str = "Uncategorized"
    reg_date: Any | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "wiki": self.wiki,
            "user_group": self.user_group,
            "reg_date": self.reg_date,
        }


__all__ = ["UserRecord"]
