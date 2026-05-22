"""
SQLAlchemy-based service for managing user tokens.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....shared.core.crypto import encrypt_value
from ....shared.core.extensions import db
from ...models import UserTokenRecord

logger = logging.getLogger(__name__)


def upsert_user_token(*, user_id: int, username: str, access_key: str, access_secret: str) -> None:
    """Insert or update the encrypted OAuth credentials for a user."""
    username = username.strip()
    if not username:
        raise ValueError("Username is required")

    encrypted_token = encrypt_value(access_key)
    encrypted_secret = encrypt_value(access_secret)
    now = func.current_timestamp()

    # orm_obj = db.session.query(UserTokenRecord).filter(UserTokenRecord.user_id == user_id).first()
    # # user_id is the primary key for UserTokenRecord
    orm_obj = db.session.get(UserTokenRecord, user_id)
    if orm_obj:
        orm_obj.username = username
        orm_obj.access_token = encrypted_token
        orm_obj.access_secret = encrypted_secret
        orm_obj.updated_at = now
        orm_obj.last_used_at = now
        orm_obj.rotated_at = now
    else:
        orm_obj = UserTokenRecord(
            user_id=user_id,
            username=username,
            access_token=encrypted_token,
            access_secret=encrypted_secret,
            created_at=now,
            updated_at=now,
            last_used_at=now,
        )
        db.session.add(orm_obj)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def get_user_token(user_id: str | int) -> Optional[UserTokenRecord]:
    """Fetch the encrypted OAuth credentials for a user."""
    if not user_id:
        return None

    user_id = int(user_id)
    # orm_obj = db.session.query(UserTokenRecord).filter(UserTokenRecord.user_id == user_id).first()

    # # user_id is the primary key for UserTokenRecord
    orm_obj = db.session.get(UserTokenRecord, user_id)
    if not orm_obj:
        return None
    return orm_obj


def delete_user_token(user_id: int) -> bool:
    """Remove the stored OAuth credentials for the given user id.

    Returns ``True`` if a row was deleted, ``False`` if no row existed
    for ``user_id`` (mirroring :func:`delete_user_token_by_username`).
    """
    if not user_id:
        return False

    # # user_id is the primary key for UserTokenRecord
    orm_obj = db.session.get(UserTokenRecord, user_id)
    if not orm_obj:
        return False

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(UserTokenRecord, user_id)
    return deleted is None


def get_user_token_by_username(username: str) -> Optional[UserTokenRecord]:
    """Fetch the encrypted OAuth credentials for a user by username."""
    username = username.strip()
    if not username:
        return None

    orm_obj = db.session.query(UserTokenRecord).filter(UserTokenRecord.username == username).first()
    if not orm_obj:
        return None
    return orm_obj


def delete_user_token_by_username(username: str) -> bool:
    """Remove the stored OAuth credentials for the given username."""
    username = username.strip()
    if not username:
        return False
    orm_obj = get_user_token_by_username(username)
    if not orm_obj:
        return False
    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = get_user_token_by_username(username)
    return deleted is None


__all__ = [
    "upsert_user_token",
    "get_user_token",
    "delete_user_token",
    "get_user_token_by_username",
    "delete_user_token_by_username",
]
