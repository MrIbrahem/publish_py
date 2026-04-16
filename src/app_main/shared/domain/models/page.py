from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
