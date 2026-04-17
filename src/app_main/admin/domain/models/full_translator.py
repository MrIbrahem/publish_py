from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.db.engine import BaseDb


class _FullTranslatorRecord(BaseDb):
    __tablename__ = "full_translators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(120), unique=True, nullable=False)
    active = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user,
            "active": self.active,
        }


@dataclass
class FullTranslatorRecord:
    """Representation of a full translator record."""

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


__all__ = ["FullTranslatorRecord"]
