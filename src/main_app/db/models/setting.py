"""
Admin domain models.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy import Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column

from ...extensions import LONGTEXT, db

logger = logging.getLogger(__name__)


class LanguageSettingRecord(db.Model):
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lang_code: Mapped[str | None] = mapped_column(String(20), unique=True)
    move_dots: Mapped[int | None] = mapped_column(default=0, server_default=text("0"))
    expend: Mapped[int | None] = mapped_column(default=0, server_default=text("0"))
    add_en_lang: Mapped[int | None] = mapped_column(default=0, server_default=text("0"))

    def __init__(self, **kwargs: Any) -> None:
        # Apply Python-level defaults for fields not provided
        if "move_dots" not in kwargs:
            kwargs["move_dots"] = 0
        if "expend" not in kwargs:
            kwargs["expend"] = 0
        if "add_en_lang" not in kwargs:
            kwargs["add_en_lang"] = 0


    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "lang_code": self.lang_code,
            "move_dots": self.move_dots,
            "expend": self.expend,
            "add_en_lang": self.add_en_lang,
        }


class SettingRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS new_settings (
        `id` INT NOT NULL AUTO_INCREMENT,
        `key` VARCHAR(190) NOT NULL,
        `title` VARCHAR(500) NOT NULL,
        `value` text DEFAULT NULL,
        `value_type` enum ('boolean', 'string', 'integer', 'json') NOT NULL DEFAULT 'boolean',
        PRIMARY KEY (`id`),
        UNIQUE KEY unique_key (`key`)
    )
    """

    __tablename__ = "new_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(190), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # Compiler <sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler object at ...> can't render element of type LONGTEXT
    value: Mapped[str | None] = mapped_column(LONGTEXT)

    value_type: Mapped[str] = mapped_column(
        Enum("boolean", "string", "integer", name="setting_value_type"),
        nullable=False,
        default="boolean",
    )

    def __init__(self, **kwargs: Any) -> None:
        # Apply Python-level defaults for fields not provided
        if "value_type" not in kwargs:
            kwargs["value_type"] = "boolean"

        # Parse value based on value_type after initialization
        self.value = self._parse_value(self.value, self.value_type)

    def _parse_value(self, value: Optional[str], value_type: str) -> Any:
        if value is None:
            return None
        if value_type == "boolean":
            return str(value)  # ("1", "0")
        elif value_type == "integer":
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0

        return str(value)  # string

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "title": self.title,
            "value": self.value,
            "value_type": self.value_type,
        }


__all__ = [
    "LanguageSettingRecord",
    "SettingRecord",
]
