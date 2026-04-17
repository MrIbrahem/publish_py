from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Column, DateTime, Integer, LargeBinary, String

from ....shared.sqlalchemy_db.engine import BaseDb
from ...utils.decode_bytes import coerce_bytes

logger = logging.getLogger(__name__)


class _UserTokenRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS user_tokens (
        user_id int NOT NULL,
        username varchar(255) NOT NULL,
        access_token varbinary(1024) NOT NULL,
        access_secret varbinary(1024) NOT NULL,
        created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        last_used_at datetime DEFAULT NULL,
        rotated_at datetime DEFAULT NULL,
        PRIMARY KEY (user_id),
        UNIQUE KEY uq_user_tokens_username (username)
    )
    """

    __tablename__ = "user_tokens"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    access_token = Column(LargeBinary(1024), nullable=False)
    access_secret = Column(LargeBinary(1024), nullable=False)
    created_at = Column(DateTime, nullable=True, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, nullable=True, server_default="CURRENT_TIMESTAMP")
    last_used_at = Column(DateTime, nullable=True)
    rotated_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "access_token": self.access_token,
            "access_secret": self.access_secret,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_used_at": self.last_used_at,
            "rotated_at": self.rotated_at,
        }


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
        from ...core.crypto import decrypt_value

        access_key = decrypt_value(self.access_token)
        access_secret = decrypt_value(self.access_secret)
        return access_key, access_secret

    def __post_init__(self) -> None:
        self.access_token = coerce_bytes(self.access_token)
        self.access_secret = coerce_bytes(self.access_secret)


__all__ = [
    "UserTokenRecord",
]
