from __future__ import annotations

from dataclasses import dataclass

@dataclass
class EnwikiPageviewRecord:
    """Representation of an enwiki pageview record."""

    id: int
    title: str
    en_views: int | None = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "en_views": self.en_views,
        }


__all__ = ["EnwikiPageviewRecord"]
