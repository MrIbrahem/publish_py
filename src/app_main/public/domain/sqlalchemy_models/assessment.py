from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _AssessmentRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS assessments (
        id int unsigned NOT NULL AUTO_INCREMENT,
        title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        importance varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY title (title)
      )
    """

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
