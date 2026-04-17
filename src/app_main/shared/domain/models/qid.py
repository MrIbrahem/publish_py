from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import Column, DateTime, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb

logger = logging.getLogger(__name__)


class _QidRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS qids (
        id int unsigned NOT NULL AUTO_INCREMENT,
        qid varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        UNIQUE KEY title (title),
        KEY qid (qid)
    )
    """

    __tablename__ = "qids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qid = Column(String(20), nullable=False)
    title = Column(String(255), unique=True, nullable=False)
    add_date = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "qid": self.qid,
            "title": self.title,
            "add_date": self.add_date,
        }


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
        """Convert the QidRecord to a dictionary."""
        return {
            "id": self.id,
            "qid": self.qid,
            "title": self.title,
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
