from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AssessmentRecord:
    """Representation of an assessment record."""

    id: int
    title: str
    importance: str | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "importance": self.importance,
        }


__all__ = ["AssessmentRecord"]
