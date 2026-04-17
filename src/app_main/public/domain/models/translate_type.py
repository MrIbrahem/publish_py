from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TranslateTypeRecord:
    """Representation of a translate_type record."""

    tt_id: int
    tt_title: str
    tt_lead: int = 1
    tt_full: int = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "tt_id": self.tt_id,
            "tt_title": self.tt_title,
            "tt_lead": self.tt_lead,
            "tt_full": self.tt_full,
        }


__all__ = ["TranslateTypeRecord"]
