from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, text

from ....shared.sqlalchemy_db.engine import BaseDb


class _InProcessRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS in_process (
        id int unsigned NOT NULL AUTO_INCREMENT,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        lang varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
        cat varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT 'RTT',
        translate_type varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'lead',
        word int DEFAULT '0',
        add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY title (title)
    )
    """

    __tablename__ = "in_process"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    user = Column(String(255), nullable=False)
    lang = Column(String(30), nullable=False)
    cat = Column(String(255), default="RTT")
    translate_type = Column(String(20), default="lead")
    word = Column(Integer, default=0)
    add_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "cat": self.cat,
            "translate_type": self.translate_type,
            "word": self.word,
            "add_date": self.add_date,
        }


@dataclass
class InProcessRecord:
    """Representation of an in_process record."""

    id: int
    title: str
    user: str
    lang: str
    cat: str | None = "RTT"
    translate_type: str | None = "lead"
    word: int | None = 0
    add_date: Any | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "cat": self.cat,
            "translate_type": self.translate_type,
            "word": self.word,
            "add_date": self.add_date,
        }


__all__ = ["InProcessRecord"]
