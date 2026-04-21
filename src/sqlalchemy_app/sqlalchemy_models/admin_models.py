"""
Admin domain models.
"""

from __future__ import annotations

import logging

from typing import Any, Optional

from sqlalchemy import Column, Enum, Integer, String, text

# from sqlalchemy.dialects.mysql import LONGTEXT
from ..shared.engine import LONGTEXT, BaseDb

logger = logging.getLogger(__name__)


class LanguageSettingRecord(BaseDb):
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


class SettingRecord(BaseDb):
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

    def __post_init__(self):
        """Determine form type based on displayed value."""
        self.value = self._parse_value(self.value, self.value_type)

    def _parse_value(self, value: Optional[str], value_type: str) -> Any:
        if value is None:
            return None
        if value_type == "boolean":
            return "true" if value.lower() in ("1", "true", "yes", "on") else "false"
        elif value_type == "integer":
            try:
                return int(value)
            except ValueError:
                return 0

        return str(value)  # string


__all__ = [
    "LanguageSettingRecord",
    "SettingRecord",
]
