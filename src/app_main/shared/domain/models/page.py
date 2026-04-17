from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, func, text

from ...db.engine import BaseDb


class _PageRecord(BaseDb):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    word = Column(Integer, nullable=True)
    translate_type = Column(String(20), nullable=True)
    cat = Column(String(120), nullable=True)
    lang = Column(String(30), nullable=True)
    user = Column(String(120), nullable=True)
    target = Column(String(120), nullable=True)
    date = Column(DateTime, nullable=True)
    pupdate = Column(String(120), nullable=True)
    add_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    deleted = Column(Integer, default=0)
    mdwiki_revid = Column(Integer, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "word": self.word,
            "translate_type": self.translate_type,
            "cat": self.cat,
            "lang": self.lang,
            "user": self.user,
            "target": self.target,
            "date": self.date,
            "pupdate": self.pupdate,
            "add_date": self.add_date,
            "deleted": self.deleted,
            "mdwiki_revid": self.mdwiki_revid,
        }


@dataclass
class PageRecord:
    """Representation of a page."""

    id: int
    title: str
    word: int | None = None
    translate_type: str | None = None
    cat: str | None = None
    lang: str | None = None
    user: str | None = None
    target: str | None = None
    date: Any | None = None
    pupdate: str | None = None
    add_date: Any | None = None
    deleted: int = 0
    mdwiki_revid: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "word": self.word,
            "translate_type": self.translate_type,
            "cat": self.cat,
            "lang": self.lang,
            "user": self.user,
            "target": self.target,
            "date": self.date,
            "pupdate": self.pupdate,
            "add_date": self.add_date,
            "deleted": self.deleted,
            "mdwiki_revid": self.mdwiki_revid,
        }


__all__ = ["PageRecord"]
