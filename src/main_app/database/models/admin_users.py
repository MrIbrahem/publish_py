from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from ...extensions import db
from .base import TimestampMixin

logger = logging.getLogger(__name__)


class UsersSharedRecord(TimestampMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Modern approach for defining foreign keys
    username: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False
    )

    # Python application default and database-level server default configuration
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True, server_default=text("1"))

    def to_json(self) -> dict[str, Any]:
        """Serializes the pure model instance into a dictionary."""
        data: dict[str, Any] = {}
        table_keys = [
            "id",
            "username",
            "is_active",
            "created_at",
            "updated_at",
        ]
        for column in table_keys:
            value = getattr(self, column)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[column] = value

        return data


class CoordinatorRecord(UsersSharedRecord, db.Model):
    """
    Coordinator role — username references users.username.
    """

    __tablename__ = "coordinators"

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<Coordinator id={self.id} username={self.username!r} is_active={self.is_active}>"


class AdminRecord(UsersSharedRecord, db.Model):
    """
    Admin role — username references users.username.
    """

    __tablename__ = "admins"

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<Admin id={self.id} username={self.username!r} is_active={self.is_active}>"


__all__ = [
    "CoordinatorRecord",
    "AdminRecord",
]
