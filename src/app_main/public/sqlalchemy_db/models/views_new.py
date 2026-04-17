from __future__ import annotations

from sqlalchemy import Column, Integer, String, UniqueConstraint

from ....shared.sqlalchemy_db.engine import BaseDb


class _ViewsNewRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS views_new (
        id int unsigned NOT NULL AUTO_INCREMENT,
        target varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        lang varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
        year int NOT NULL,
        views int DEFAULT '0',
        PRIMARY KEY (id),
        UNIQUE KEY target_lang_year (target, lang, year),
        KEY target (target)
    )
    """

    __tablename__ = "views_new"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String(120), nullable=False)
    lang = Column(String(30), nullable=False)
    year = Column(Integer, nullable=False)
    views = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("target", "lang", "year", name="target_lang_year"),)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "lang": self.lang,
            "year": self.year,
            "views": self.views,
        }


__all__ = ["_ViewsNewRecord"]
