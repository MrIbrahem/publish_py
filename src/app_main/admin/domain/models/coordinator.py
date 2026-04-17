""" """

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb

logger = logging.getLogger(__name__)


class _CoordinatorRecord(BaseDb):
    """
    ORM model for the coordinators table.
    CREATE TABLE IF NOT EXISTS coordinators (
        id int unsigned NOT NULL AUTO_INCREMENT,
        username varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        is_active int NOT NULL DEFAULT '1',
        PRIMARY KEY (id),
        UNIQUE KEY username (username)
      )
    """

    __tablename__ = "coordinators"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(120, collation="utf8mb4_unicode_ci"), unique=True, nullable=False)
    is_active: int = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
        }

    def __repr__(self) -> str:
        return f"<Coordinator id={self.id} username={self.username!r} is_active={self.is_active}>"


@dataclass
class CoordinatorRecord:
    """Representation of a coordinator record."""

    id: int
    username: str
    is_active: int = 1

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
        }


__all__ = [
    # Model
    # "Coordinator",
    "_CoordinatorRecord",
    "CoordinatorRecord",
]
