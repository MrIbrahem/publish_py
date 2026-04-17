from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _CoordinatorRecord(BaseDb):
    __tablename__ = "coordinators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(120), unique=True, nullable=False)
    is_active = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
        }


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


__all__ = ["CoordinatorRecord"]
