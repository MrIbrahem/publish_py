"""
Admin domain models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


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


@dataclass
class LanguageSettingRecord:
    """Representation of a language setting record."""

    id: int
    lang_code: str | None = None
    move_dots: int | None = 0
    expend: int | None = 0
    add_en_lang: int | None = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "lang_code": self.lang_code,
            "move_dots": self.move_dots,
            "expend": self.expend,
            "add_en_lang": self.add_en_lang,
        }


@dataclass
class SettingRecord:
    """
    Representation of a setting1 record.

    `id` INT NOT NULL AUTO_INCREMENT,
    `key` VARCHAR(190) NOT NULL,
    `title` VARCHAR(500) NOT NULL,
    `value` text DEFAULT NULL,
    `value_type` enum ('boolean', 'string', 'integer') NOT NULL DEFAULT 'boolean',
    """

    id: int
    key: str
    title: str
    value: str | None = None
    value_type: str = "boolean"

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
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


__all__ = [
    "CoordinatorRecord",
    "FullTranslatorRecord",
    "LanguageSettingRecord",
    "SettingRecord",
    "UsersNoInprocessRecord",
]
