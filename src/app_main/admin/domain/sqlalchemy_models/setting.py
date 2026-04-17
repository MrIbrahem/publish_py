from __future__ import annotations

import json

from typing import Any, Optional

from sqlalchemy import Column, Enum, Integer, String, Text

from ....shared.sqlalchemy_db.engine import BaseDb


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
    value = Column(Text, nullable=True)
    value_type = Column(Enum("boolean", "string", "integer", "json"), nullable=False, default="boolean")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "key": self.key,
            "title": self.title,
            "value": self.value,
            "value_type": self.value_type,
        }


__all__ = ["_SettingRecord"]
