from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LangRecord:
    """Representation of a language record."""

    lang_id: int
    code: str
    autonym: str
    name: str

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "lang_id": self.lang_id,
            "code": self.code,
            "autonym": self.autonym,
            "name": self.name,
        }


__all__ = ["LangRecord"]
