from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _LangRecord(BaseDb):
    __tablename__ = "langs"

    lang_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False)
    autonym = Column(String(70), nullable=False)
    name = Column(String(70), nullable=False)

    def to_dict(self) -> dict:
        return {
            "lang_id": self.lang_id,
            "code": self.code,
            "autonym": self.autonym,
            "name": self.name,
        }


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
