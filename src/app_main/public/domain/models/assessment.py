from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.db.engine import BaseDb


class _AssessmentRecord(BaseDb):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), unique=True, nullable=False)
    importance = Column(String(120), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "importance": self.importance,
        }


@dataclass
class AssessmentRecord:
    """Representation of an assessment record."""

    id: int
    title: str
    importance: str | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "importance": self.importance,
        }


__all__ = ["AssessmentRecord"]
