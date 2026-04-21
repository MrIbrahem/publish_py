"""
Admin domain models.
"""

from __future__ import annotations

import logging

from sqlalchemy import Column, Enum, Integer, String, text

# from sqlalchemy.dialects.mysql import LONGTEXT
from ..shared.engine import LONGTEXT, BaseDb

logger = logging.getLogger(__name__)


class _CoordinatorRecord(BaseDb):
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

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(120), unique=True, nullable=False)
    is_active: int = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
        }

    def __repr__(self) -> str:
        return f"<Coordinator id={self.id} username={self.username!r} is_active={self.is_active}>"


class _FullTranslatorRecord(BaseDb):
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(120), unique=True, nullable=False)
    is_active = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user,
            "is_active": self.is_active,
        }


class _LanguageSettingRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS language_settings (
        id int NOT NULL AUTO_INCREMENT,
        lang_code varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        move_dots tinyint DEFAULT '0',
        expend tinyint DEFAULT '0',
        add_en_lang tinyint DEFAULT '0',
        PRIMARY KEY (id),
        UNIQUE KEY lang_code (lang_code)
    )
    """

    __tablename__ = "language_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lang_code = Column(String(20), unique=True, nullable=True)
    move_dots = Column(Integer, default=0, server_default=text("0"))
    expend = Column(Integer, default=0, server_default=text("0"))
    add_en_lang = Column(Integer, default=0, server_default=text("0"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lang_code": self.lang_code,
            "move_dots": self.move_dots,
            "expend": self.expend,
            "add_en_lang": self.add_en_lang,
        }


class _SettingRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS settings (
        `id` INT NOT NULL AUTO_INCREMENT,
        `key` VARCHAR(190) NOT NULL,
        `title` VARCHAR(500) NOT NULL,
        `value` text DEFAULT NULL,
        `value_type` enum ('boolean', 'string', 'integer', 'json') NOT NULL DEFAULT 'boolean',
        PRIMARY KEY (`id`),
        UNIQUE KEY unique_key (`key`)
    )
    """

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(190), unique=True, nullable=False)
    title = Column(String(500), nullable=False)

    # Compiler <sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler object at ...> can't render element of type LONGTEXT
    value = Column(LONGTEXT, nullable=True)

    value_type = Column(
        Enum("boolean", "string", "integer", name="setting_value_type"),
        nullable=False,
        default="boolean",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "key": self.key,
            "title": self.title,
            "value": self.value,
            "value_type": self.value_type,
        }


class _UsersNoInprocessRecord(BaseDb):
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(120), unique=True, nullable=False)
    is_active = Column(Integer, nullable=False, default=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user,
            "is_active": self.is_active,
        }


__all__ = [
    "_CoordinatorRecord",
    "_FullTranslatorRecord",
    "_LanguageSettingRecord",
    "_SettingRecord",
    "_UsersNoInprocessRecord",
]
