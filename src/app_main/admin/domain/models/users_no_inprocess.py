from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _UsersNoInprocessRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS users_no_inprocess (
        id int unsigned NOT NULL AUTO_INCREMENT,
        user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        active int NOT NULL DEFAULT '1',
        PRIMARY KEY (id),
        UNIQUE KEY user (user)
    )

    """

    __tablename__ = "users_no_inprocess"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(120), unique=True, nullable=False)
    active = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user,
            "active": self.active,
        }


@dataclass
class UsersNoInprocessRecord:
    """Representation of a users_no_inprocess record."""

    id: int
    user: str
    active: int = 1

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "user": self.user,
            "active": self.active,
        }


__all__ = ["UsersNoInprocessRecord"]
