from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LanguageSettingRecord:
    """Representation of a language setting record."""

    id: int
    lang_code: str | None = None
    move_dots: int | None = 0
    expend: int | None = 0
    add_en_lang: int | None = 0
    add_en_lng: int | None = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "lang_code": self.lang_code,
            "move_dots": self.move_dots,
            "expend": self.expend,
            "add_en_lang": self.add_en_lang,
            "add_en_lng": self.add_en_lng,
        }


__all__ = ["LanguageSettingRecord"]
