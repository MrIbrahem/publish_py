from __future__ import annotations

from dataclasses import dataclass


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
