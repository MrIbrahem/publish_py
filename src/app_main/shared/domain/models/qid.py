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
        ...


__all__ = [
    "QidRecord",
]
