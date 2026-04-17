from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _MdwikiRevidRecord(BaseDb):
    __tablename__ = "mdwiki_revids"

    title = Column(String(255), primary_key=True)
    revid = Column(Integer, nullable=False)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "revid": self.revid,
        }


@dataclass
class MdwikiRevidRecord:
    """Representation of an mdwiki_revids record."""

    title: str
    revid: int

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "title": self.title,
            "revid": self.revid,
        }


__all__ = ["MdwikiRevidRecord"]
