from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _LanguageSettingRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS language_settings (
        id int NOT NULL AUTO_INCREMENT,
        lang_code varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        move_dots tinyint DEFAULT '0',
        expend tinyint DEFAULT '0',
        add_en_lang tinyint DEFAULT '0',
        add_en_lng tinyint DEFAULT '0',
        PRIMARY KEY (id),
        UNIQUE KEY lang_code (lang_code)
    )
    """

    __tablename__ = "language_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lang_code = Column(String(20), unique=True, nullable=True)
    move_dots = Column(Integer, default=0)
    expend = Column(Integer, default=0)
    add_en_lang = Column(Integer, default=0)
    add_en_lng = Column(Integer, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lang_code": self.lang_code,
            "move_dots": self.move_dots,
            "expend": self.expend,
            "add_en_lang": self.add_en_lang,
            "add_en_lng": self.add_en_lng,
        }


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
