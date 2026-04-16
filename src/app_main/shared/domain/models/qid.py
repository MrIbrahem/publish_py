from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QidRecord:
    """
    QID records.
    add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    """

    id: int
    title: str
    qid: str
    add_date: str

    def to_dict(self) -> dict:
        """Convert the QidRecord to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "qid": self.qid,
            "add_date": self.add_date,
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
