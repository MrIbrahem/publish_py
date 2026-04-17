from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _WordRecord(BaseDb):
    __tablename__ = "words"

    w_id = Column(Integer, primary_key=True, autoincrement=True)
    w_title = Column(String(120), unique=True, nullable=False)
    w_lead_words = Column(Integer, nullable=True)
    w_all_words = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "w_id": self.w_id,
            "w_title": self.w_title,
            "w_lead_words": self.w_lead_words,
            "w_all_words": self.w_all_words,
        }


@dataclass
class WordRecord:
    """Representation of a words record."""

    w_id: int
    w_title: str
    w_lead_words: int | None = None
    w_all_words: int | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "w_id": self.w_id,
            "w_title": self.w_title,
            "w_lead_words": self.w_lead_words,
            "w_all_words": self.w_all_words,
        }


__all__ = ["WordRecord"]
