from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


def coerce_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    raise TypeError("Expected bytes-compatible value for encrypted token")


@dataclass
class UserTokenRecord:
    """Decrypted OAuth credential bundle stored in the database."""

    user_id: int
    username: str
    access_token: bytes
    access_secret: bytes
    created_at: Any | None = None
    updated_at: Any | None = None
    last_used_at: Any | None = None
    rotated_at: Any | None = None

    def decrypted(self) -> tuple[str, str]:
        """Return the decrypted access token and secret."""
        from ..shared.core.crypto import decrypt_value

        access_key = decrypt_value(self.access_token)
        access_secret = decrypt_value(self.access_secret)
        return access_key, access_secret

    def __post_init__(self) -> None:
        self.access_token = coerce_bytes(self.access_token)
        self.access_secret = coerce_bytes(self.access_secret)


@dataclass
class UserRecord:
    """Representation of a user record."""

    user_id: int
    username: str
    email: str = ""
    wiki: str = ""
    user_group: str = "Uncategorized"
    reg_date: Any | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "wiki": self.wiki,
            "user_group": self.user_group,
            "reg_date": self.reg_date,
        }


@dataclass
class UsersNoInprocessRecord:
    """Representation of a users_no_inprocess record."""

    id: int
    user: str
    is_active: int = 1

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "user": self.user,
            "is_active": self.is_active,
        }


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


@dataclass
class FullTranslatorRecord:
    """Representation of a full translator record."""

    id: int
    user: str
    is_active: int = 1

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "user": self.user,
            "is_active": self.is_active,
        }


__all__ = [
    "UserTokenRecord",
    "UserRecord",
    "UsersNoInprocessRecord",
    "CoordinatorRecord",
    "FullTranslatorRecord",
]
