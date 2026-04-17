from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text

from ...db.engine import BaseDb


class _ReportRecord(BaseDb):
    __tablename__ = "publish_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")
    title = Column(String(255), nullable=False)
    user = Column(String(255), nullable=False)
    lang = Column(String(255), nullable=False)
    sourcetitle = Column(String(255), nullable=False)
    result = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date.isoformat() if hasattr(self.date, "isoformat") else str(self.date),
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


@dataclass
class ReportRecord:
    """Representation of a report record."""

    id: int
    date: Any
    title: str
    user: str
    lang: str
    sourcetitle: str
    result: str
    data: str

    def to_dict(self) -> dict[str, Any]:
        """Convert a ReportRecord to a dictionary."""
        # Handle date conversion with None safety
        if self.date is None:
            date_str = ""
        elif hasattr(self.date, "isoformat"):
            date_str = self.date.isoformat()
        else:
            date_str = str(self.date)

        return {
            "id": self.id,
            "date": date_str,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


__all__ = ["ReportRecord"]
