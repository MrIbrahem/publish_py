from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


def current_ts() -> str:
    """Return the current UTC timestamp formatted for MySQL DATETIME."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _coerce_bytes(value: Any) -> bytes:
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
        from ...core.crypto import decrypt_value

        access_key = decrypt_value(self.access_token)
        access_secret = decrypt_value(self.access_secret)
        return access_key, access_secret

    def __post_init__(self) -> None:
        self.access_token = _coerce_bytes(self.access_token)
        self.access_secret = _coerce_bytes(self.access_secret)


__all__ = [
    "UserTokenRecord",
    "current_ts",
]
