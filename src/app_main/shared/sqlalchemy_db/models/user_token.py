from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Column, Integer, LargeBinary, String, func, DateTime

from ...utils.decode_bytes import coerce_bytes
from ..engine import BaseDb

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

    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    last_used_at = Column(DateTime, nullable=True, server_default=func.current_timestamp())
    rotated_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            # "access_token": self.access_token,
            # "access_secret": self.access_secret,
            "access_token": coerce_bytes(self.access_token),
            "access_secret": coerce_bytes(self.access_secret),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_used_at": self.last_used_at,
            "rotated_at": self.rotated_at,
        }


__all__ = [
    "_UserTokenRecord",
]
