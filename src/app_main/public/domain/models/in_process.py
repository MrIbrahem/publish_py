from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass
class InProcessRecord:
    """Representation of an in_process record."""

    id: int
    title: str
    user: str
    lang: str
    cat: str | None = "RTT"
    translate_type: str | None = "lead"
    word: int | None = 0
    add_date: Any | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "cat": self.cat,
            "translate_type": self.translate_type,
            "word": self.word,
            "add_date": self.add_date,
        }


__all__ = ["InProcessRecord"]
