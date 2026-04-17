from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
