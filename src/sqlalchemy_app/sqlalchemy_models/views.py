"""
Views domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, UniqueConstraint, text

from ..shared.engine import BaseDb


class EnwikiPageviewRecord(BaseDb):
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
    en_views = Column(Integer, default=0, server_default=text("0"))

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "en_views" not in kwargs:
            kwargs["en_views"] = 0
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "en_views": self.en_views,
        }


class ViewsNewRecord(BaseDb):
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
    views = Column(Integer, default=0, server_default=text("0"))

    __table_args__ = (UniqueConstraint("target", "lang", "year", name="target_lang_year"),)

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "views" not in kwargs:
            kwargs["views"] = 0
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "lang": self.lang,
            "year": self.year,
            "views": self.views,
        }


class ViewsNewAllRecord(BaseDb):
    """
    CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `views_new_all` AS
        SELECT `v`.`target` AS `target`,
               `v`.`lang` AS `lang`,
               SUM(`v`.`views`) AS `views`
        FROM `views_new` `v`
        GROUP BY `v`.`target`, `v`.`lang`
    """

    __tablename__ = "views_new_all"

    target = Column(String(120), primary_key=True, nullable=False)
    lang = Column(String(30), primary_key=True, nullable=False)
    views = Column(Integer, default=0, server_default=text("0"))

    __table_args__ = (
        # Prevent SQLAlchemy from trying to create this as a table
        {
            "info": {
                "is_view": True,
                "create_query": """
                    CREATE VIEW views_new_all AS
                    SELECT v.target AS target,
                        v.lang AS lang,
                        SUM(v.views) AS views
                    FROM views_new v
                    GROUP BY v.target, v.lang
                    """,
            }
        },
    )

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "lang": self.lang,
            "views": self.views,
        }


__all__ = [
    "EnwikiPageviewRecord",
    "ViewsNewRecord",
    "ViewsNewAllRecord",
]
