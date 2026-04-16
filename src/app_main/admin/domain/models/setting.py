from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingRecord:
    """Representation of a setting record."""

    id: int
    title: str
    displayed: str
    Type: str = "check"
    value: int = 0
    ignored: int = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "displayed": self.displayed,
            "Type": self.Type,
            "value": self.value,
            "ignored": self.ignored,
        }


__all__ = ["SettingRecord"]
