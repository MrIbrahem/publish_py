from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SettingRecord1:
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


__all__ = ["SettingRecord1"]
