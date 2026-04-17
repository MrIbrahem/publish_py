from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PagesUsersToMainRecord:
    """Representation of a pages_users_to_main record."""

    id: int
    new_target: str = ""
    new_user: str = ""
    new_qid: str = ""

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "new_target": self.new_target,
            "new_user": self.new_user,
            "new_qid": self.new_qid,
        }


__all__ = ["PagesUsersToMainRecord"]
