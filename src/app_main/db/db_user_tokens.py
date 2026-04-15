"""

"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Any, List

import pymysql

from ..crypto import decrypt_value, encrypt_value

from ..config import DbConfig
from . import Database
from .sql_schema_tables import sql_tables

logger = logging.getLogger(__name__)


def current_ts() -> str:
    # Store in UTC. MySQL DATETIME has no TZ; keep application-level UTC.
    """
    Return the current UTC timestamp formatted for MySQL DATETIME.

    Returns:
        A string of the current UTC time in the format "YYYY-MM-DD HH:MM:SS".
    """
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

        access_key = decrypt_value(self.access_token)
        access_secret = decrypt_value(self.access_secret)
        # mark_token_used(self.user_id)
        return access_key, access_secret

    def __post_init__(self) -> None:
        self.access_token = _coerce_bytes(self.access_token)
        self.access_secret = _coerce_bytes(self.access_secret)


class UserTokenDB:
    """MySQL-backed"""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.db.execute_query_safe(sql_tables.user_tokens)

    def _row_to_record(self, row: dict[str, Any]) -> UserTokenRecord:
        return UserTokenRecord(**row)

    def _fetch_by_id(self, user_id: int) -> UserTokenRecord:
        rows = self.db.fetch_query_safe(
            "SELECT * FROM user_tokens WHERE user_id = %s",
            (user_id,),
        )
        if not rows:
            raise LookupError(f"User user_id {user_id} was not found")
        return self._row_to_record(rows[0])

    def get_user_id(self, username: str) -> int | None:
        rows = self.db.fetch_query_safe(
            "SELECT user_id FROM user_tokens WHERE username = %s",
            (username,),
        )
        if not rows:
            # logger.warning(f"")
            return None

        return rows[0].get("user_id")

    def _fetch_by_username(self, username: str) -> UserTokenRecord:
        rows = self.db.fetch_query_safe(
            "SELECT * FROM user_tokens WHERE username = %s",
            (username,),
        )
        if not rows:
            raise LookupError(f"User {username!r} was not found")
        return self._row_to_record(rows[0])

    def list(self) -> List[UserTokenRecord]:
        rows = self.db.fetch_query_safe("SELECT * FROM user_tokens ORDER BY user_id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, username: str, **kwargs) -> UserTokenRecord:
        username = username.strip()
        if not username:
            raise ValueError("Username is required")

        cols = ["username"] + list(kwargs.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        values = [username] + list(kwargs.values())

        try:
            self.db.execute_query(
                f"INSERT INTO user_tokens ({', '.join(cols)}) VALUES ({placeholders})",
                tuple(values),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"User '{username}' already exists") from None

        return self._fetch_by_username(username)

    def update(self, user_id: int, **kwargs) -> UserTokenRecord:
        _ = self._fetch_by_id(user_id)
        if not kwargs:
            return self._fetch_by_id(user_id)

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        self.db.execute_query_safe(
            f"UPDATE user_tokens SET {set_clause} WHERE user_id = %s",
            tuple(values),
        )
        return self._fetch_by_id(user_id)

    def upsert(self, user_id: int, username: str, access_key: str, access_secret: str) -> None:
        """Insert or update the encrypted OAuth credentials for a user."""

        user_id = int(user_id) if isinstance(user_id, str) else user_id
        now = current_ts()
        encrypted_token = encrypt_value(access_key)
        encrypted_secret = encrypt_value(access_secret)

        return self.db.execute_query_safe(
            """
                INSERT INTO user_tokens (
                    user_id,
                    username,
                    access_token,
                    access_secret,
                    created_at,
                    updated_at,
                    last_used_at,
                    rotated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
                ON DUPLICATE KEY UPDATE
                    username = VALUES(username),
                    access_token = VALUES(access_token),
                    access_secret = VALUES(access_secret),
                    updated_at = VALUES(updated_at),
                    last_used_at = VALUES(last_used_at),
                    rotated_at = CURRENT_TIMESTAMP
                """,
            (
                user_id,
                username,
                encrypted_token,
                encrypted_secret,
                now,
                now,
                now,
            ),
        )

    def delete(self, user_id: int) -> UserTokenRecord:
        record = self._fetch_by_id(user_id)
        self.db.execute_query_safe(
            "DELETE FROM user_tokens WHERE user_id = %s",
            (user_id,),
        )
        return record


__all__ = [
    "current_ts",
    "UserTokenDB",
    "UserTokenRecord",
]
