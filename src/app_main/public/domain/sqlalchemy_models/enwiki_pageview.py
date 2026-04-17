from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _EnwikiPageviewRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS enwiki_pageviews (
        id int unsigned NOT NULL AUTO_INCREMENT,
        title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        en_views int DEFAULT '0',
        PRIMARY KEY (id),
        UNIQUE KEY title (title)
    )
    """

    __tablename__ = "enwiki_pageviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), unique=True, nullable=False)
    en_views = Column(Integer, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "en_views": self.en_views,
        }


@dataclass
class EnwikiPageviewRecord:
    """Representation of an enwiki pageview record."""

    id: int
    title: str
    en_views: int | None = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "en_views": self.en_views,
        }


__all__ = ["EnwikiPageviewRecord"]
