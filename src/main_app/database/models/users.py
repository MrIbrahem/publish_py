from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ...extensions import db
from ...services.core.crypto import decrypt_value
from ...services.utils.decode_bytes import coerce_bytes
from .base import TimestampMixin

logger = logging.getLogger(__name__)


class UserRecord(db.Model):
    """
    Stable user identity — source of truth for user_id and username.
    """

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default=text("''"))
    wiki: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default=text("''"))
    user_group: Mapped[str] = mapped_column(
        String(120), nullable=False, default="Uncategorized", server_default=text("'Uncategorized'")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        default=func.current_timestamp(),
    )

    # One-to-One relationship with UserTokenRecord using the modern SQLAlchemy 2.0 style
    token: Mapped[UserTokenRecord | None] = relationship(back_populates="user", uselist=False)

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.email = kwargs.get("email") or ""
        self.wiki = kwargs.get("wiki") or ""
        self.user_group = kwargs.get("user_group") or "Uncategorized"

    def to_json(self) -> dict[str, Any]:
        """Serializes the pure model instance into a dictionary."""
        data: dict[str, Any] = {}
        table_keys = [
            "user_id",
            "username",
            "email",
            "wiki",
            "user_group",
            "created_at",
        ]
        for column in table_keys:
            value = getattr(self, column)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[column] = value

        return data


class AdminUserRecord(TimestampMixin, db.Model):
    """
    Coordinator/admin role — username references users.username.
    """

    __tablename__ = "coordinators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Modern approach for defining foreign keys
    username: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False
    )

    # Python application default and database-level server default configuration
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True, server_default=text("1"))

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

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

    def __repr__(self) -> str:
        return f"<Coordinator id={self.id} username={self.username!r} is_active={self.is_active}>"


class UserTokenRecord(TimestampMixin, db.Model):
    """
    OAuth credentials — child of users table.
    """

    __tablename__ = "user_tokens"

    # Modern consolidated syntax for a field acting as both a Primary Key and a Foreign Key
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )

    # LargeBinary maps strictly to Python bytes
    access_token: Mapped[bytes] = mapped_column(db.LargeBinary(1024), nullable=False)
    access_secret: Mapped[bytes] = mapped_column(db.LargeBinary(1024), nullable=False)

    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True, server_default=func.current_timestamp())
    rotated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Clean explicit relationship mapping matching SQLAlchemy 2.0 recommendations via back_populates
    user: Mapped[UserRecord] = relationship(back_populates="token")

    @validates("access_token", "access_secret")
    def validate_bytes(self, key, value) -> bytes:
        return coerce_bytes(value)

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_json(self) -> dict[str, Any]:
        """Serializes the pure model instance into a dictionary."""
        data: dict[str, Any] = {}
        table_keys = [
            "user_id",
            # "access_token",
            # "access_secret",
            "created_at",
            "updated_at",
            "last_used_at",
            "rotated_at",
        ]
        for column in table_keys:
            value = getattr(self, column)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[column] = value

        return data

    def decrypted(self) -> tuple[str, str]:
        """Return the decrypted access token and secret."""

        access_key = decrypt_value(self.access_token)
        access_secret = decrypt_value(self.access_secret)
        return access_key, access_secret


class UsersNoInprocessRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS users_no_inprocess (
        id int unsigned NOT NULL AUTO_INCREMENT,
        user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        is_active int NOT NULL DEFAULT '1',
        PRIMARY KEY (id),
        UNIQUE KEY user (user)
    )

    """

    __tablename__ = "users_no_inprocess"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    is_active: Mapped[int] = mapped_column(nullable=False, default=1)

    def __init__(self, **kwargs: Any) -> None:
        # Apply Python-level defaults for fields not provided
        if "is_active" not in kwargs:
            kwargs["is_active"] = 1

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user,
            "is_active": self.is_active,
        }


class FullTranslatorRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS full_translators (
        id int unsigned NOT NULL AUTO_INCREMENT,
        user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        is_active int NOT NULL DEFAULT '1',
        PRIMARY KEY (id),
        UNIQUE KEY user (user)
    )
    """

    __tablename__ = "full_translators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    is_active: Mapped[int] = mapped_column(nullable=False, default=1)

    def __init__(self, **kwargs: Any) -> None:
        # Apply Python-level defaults for fields not provided
        if "is_active" not in kwargs:
            kwargs["is_active"] = 1

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user,
            "is_active": self.is_active,
        }


__all__ = [
    "AdminUserRecord",
    "UserTokenRecord",
    "UserRecord",
    "FullTranslatorRecord",
    "UsersNoInprocessRecord",
]
