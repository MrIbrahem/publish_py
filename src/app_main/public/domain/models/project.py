from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.db.engine import BaseDb


class _ProjectRecord(BaseDb):
    __tablename__ = "projects"

    g_id = Column(Integer, primary_key=True, autoincrement=True)
    g_title = Column(String(120), unique=True, nullable=False)

    def to_dict(self) -> dict:
        return {
            "g_id": self.g_id,
            "g_title": self.g_title,
        }


@dataclass
class ProjectRecord:
    """Representation of a project record."""

    g_id: int
    g_title: str

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "g_id": self.g_id,
            "g_title": self.g_title,
        }


__all__ = ["ProjectRecord"]
