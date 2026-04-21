"""
QID domain models - Dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QidRecord:
    """
    QID records.
    add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    """

    id: int
    qid: str
    title: str
    add_date: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "qid": self.qid,
            "title": self.title,
            "add_date": str(self.add_date) if self.add_date else self.add_date,
        }

    def __post_init__(self) -> None:
        # Validate that required fields are not empty
        if not self.title:
            raise ValueError("Title cannot be empty")

        if not self.qid:
            raise ValueError("QID cannot be empty")

        # Validate QID format (should start with Q followed by digits)
        if not self.qid.startswith("Q") or not self.qid[1:].isdigit():
            raise ValueError(f"Invalid QID format: {self.qid}. QID should start with 'Q' followed by digits.")


__all__ = [
    "QidRecord",
]
