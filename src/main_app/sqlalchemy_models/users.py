from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import validates

from ..shared.core.crypto import decrypt_value
from ..shared.utils.decode_bytes import coerce_bytes
from ..shared.core.extensions import db
logger = logging.getLogger(__name__)


class UserTokenRecord(db.Model):
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

    user_id =db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String(255), unique=True, nullable=False)
    access_token =db.Column(db.LargeBinary(1024), nullable=False)
    access_secret =db.Column(db.LargeBinary(1024), nullable=False)

    created_at =db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at =db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        server_onupdate=db.func.current_timestamp(),
        # server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    last_used_at =db.Column(db.DateTime, nullable=True, server_default=db.func.current_timestamp())
    rotated_at =db.Column(db.DateTime, nullable=True)

    @validates("access_token", "access_secret")
    def validate_bytes(self, key, value):
        return coerce_bytes(value)

    def decrypted(self) -> tuple[str, str]:
        """Return the decrypted access token and secret."""

        access_key = decrypt_value(self.access_token)
        access_secret = decrypt_value(self.access_secret)
        return access_key, access_secret


class UserRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id int NOT NULL AUTO_INCREMENT,
        username varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        email varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        wiki varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        user_group varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Uncategorized',
        reg_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id)
    )
    """

    __tablename__ = "users"

    user_id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    username =db.Column(db.String(255), nullable=False)
    email =db.Column(db.String(255), nullable=False, default="")
    wiki =db.Column(db.String(255), nullable=False, default="")
    user_group =db.Column(db.String(120), nullable=False, default="Uncategorized", server_default=db.text("'Uncategorized'"))
    reg_date =db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "email" not in kwargs:
            kwargs["email"] = ""
        if "wiki" not in kwargs:
            kwargs["wiki"] = ""
        if "user_group" not in kwargs:
            kwargs["user_group"] = "Uncategorized"
        super().__init__(**kwargs)


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

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    user =db.Column(db.String(120), unique=True, nullable=False)
    is_active =db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "is_active" not in kwargs:
            kwargs["is_active"] = 1
        super().__init__(**kwargs)


class CoordinatorRecord(db.Model):
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

    id: int =db.Column(db.Integer, primary_key=True, autoincrement=True)
    username: str =db.Column(db.String(120), unique=True, nullable=False)
    is_active: int =db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "is_active" not in kwargs:
            kwargs["is_active"] = 1
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Coordinator id={self.id} username={self.username!r} is_active={self.is_active}>"


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

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    user =db.Column(db.String(120), unique=True, nullable=False)
    is_active =db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "is_active" not in kwargs:
            kwargs["is_active"] = 1
        super().__init__(**kwargs)


__all__ = [
    "CoordinatorRecord",
    "FullTranslatorRecord",
    "UsersNoInprocessRecord",
    "UserTokenRecord",
    "UserRecord",
]
