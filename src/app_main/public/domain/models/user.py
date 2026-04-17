from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String

from ....shared.db.engine import BaseDb


class _UserRecord(BaseDb):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, default="")
    wiki = Column(String(255), nullable=False, default="")
    user_group = Column(String(120), nullable=False, default="Uncategorized")
    reg_date = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "wiki": self.wiki,
            "user_group": self.user_group,
            "reg_date": self.reg_date,
        }


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
