from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, UniqueConstraint

from ....shared.db.engine import BaseDb


class _ViewsNewRecord(BaseDb):
    __tablename__ = "views_new"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String(120), nullable=False)
    lang = Column(String(30), nullable=False)
    year = Column(Integer, nullable=False)
    views = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("target", "lang", "year", name="target_lang_year"),)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "lang": self.lang,
            "year": self.year,
            "views": self.views,
        }


@dataclass
class ViewsNewRecord:
    """Representation of a views_new record."""

    id: int
    target: str
    lang: str
    year: int
    views: int | None = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "target": self.target,
            "lang": self.lang,
            "year": self.year,
            "views": self.views,
        }


__all__ = ["ViewsNewRecord"]
