from __future__ import annotations

from dataclasses import dataclass


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
