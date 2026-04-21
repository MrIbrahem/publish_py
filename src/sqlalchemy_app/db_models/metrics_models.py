"""
Metrics domain models - Dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AssessmentRecord:
    """Representation of an assessment record."""

    id: int
    title: str
    importance: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "importance": self.importance,
        }


@dataclass
class RefsCountRecord:
    """Representation of a refs_counts record."""

    r_id: int
    r_title: str
    r_lead_refs: int | None = None
    r_all_refs: int | None = None

    def to_dict(self) -> dict:
        return {
            "r_id": self.r_id,
            "r_title": self.r_title,
            "r_lead_refs": self.r_lead_refs,
            "r_all_refs": self.r_all_refs,
        }


@dataclass
class WordRecord:
    """Representation of a words record."""

    w_id: int
    w_title: str
    w_lead_words: int | None = None
    w_all_words: int | None = None

    def to_dict(self) -> dict:
        return {
            "w_id": self.w_id,
            "w_title": self.w_title,
            "w_lead_words": self.w_lead_words,
            "w_all_words": self.w_all_words,
        }


__all__ = [
    "AssessmentRecord",
    "RefsCountRecord",
    "WordRecord",
]
