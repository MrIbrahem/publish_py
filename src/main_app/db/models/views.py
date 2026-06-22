"""
Views domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import db


class EnwikiPageviewRecord(db.Model):
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    en_views: Mapped[int | None] = mapped_column(default=0, server_default=text("0"))

    def __init__(self, **kwargs) -> None:
        # Apply Python-level defaults for fields not provided
        if "en_views" not in kwargs:
            kwargs["en_views"] = 0
        super().__init__(**kwargs)


class ViewsNewRecord(db.Model):
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
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    target: Mapped[str] = mapped_column(String(120), nullable=False)
    lang: Mapped[str] = mapped_column(String(30), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    views: Mapped[int | None] = mapped_column(default=0, server_default=text("0"))

    __table_args__ = (UniqueConstraint("target", "lang", "year", name="target_lang_year"),)

    def __init__(self, **kwargs) -> None:
        # Apply Python-level defaults for fields not provided
        if "views" not in kwargs:
            kwargs["views"] = 0
        super().__init__(**kwargs)


class ViewsNewAllRecord(db.Model):
    """
    CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `views_new_all` AS
        SELECT `v`.`target` AS `target`,
               `v`.`lang` AS `lang`,
               SUM(`v`.`views`) AS `views`
        FROM `views_new` `v`
        GROUP BY `v`.`target`, `v`.`lang`
    """

    __tablename__ = "views_new_all"

    target: Mapped[str] = mapped_column(String(120), primary_key=True, nullable=False)
    lang: Mapped[str] = mapped_column(String(30), primary_key=True, nullable=False)
    views: Mapped[int | None] = mapped_column(default=0, server_default=text("0"))

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


__all__ = [
    "EnwikiPageviewRecord",
    "ViewsNewRecord",
    "ViewsNewAllRecord",
]
