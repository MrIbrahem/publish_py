"""
Public domain models - SQLAlchemy ORM.

Note: Several models have been moved to specialized modules:
- pages_models.py: PagesUsersToMainRecord
- views_models.py: EnwikiPageviewRecord, ViewsNewRecord, ViewsNewAllRecord
- metrics_models.py: AssessmentRecord, RefsCountRecord, WordRecord
- qid_models.py: QidRecord
"""

from __future__ import annotations

from sqlalchemy import JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import db


class LangRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS langs (
        lang_id int NOT NULL AUTO_INCREMENT,
        code varchar(20) NOT NULL,
        autonym varchar(70) NOT NULL,
        name varchar(70) NOT NULL,
        redirects json DEFAULT NULL,
        PRIMARY KEY (lang_id)
    )
    """

    __tablename__ = "langs"

    lang_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    autonym: Mapped[str] = mapped_column(String(70), nullable=False)
    name: Mapped[str] = mapped_column(String(70), nullable=False)
    redirects: Mapped[dict | list | None] = mapped_column(JSON, server_default=text("NULL"))


class MdwikiRevidRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS mdwiki_revids (
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        revid int NOT NULL,
        PRIMARY KEY (title)
    )
    """

    __tablename__ = "mdwiki_revids"

    title: Mapped[str] = mapped_column(String(255), primary_key=True)
    revid: Mapped[int] = mapped_column(nullable=False)


class TranslateTypeRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS translate_type (
        tt_id int unsigned NOT NULL AUTO_INCREMENT,
        tt_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        tt_lead int NOT NULL DEFAULT '1',
        tt_full int NOT NULL DEFAULT '0',
        PRIMARY KEY (tt_id),
        UNIQUE KEY tt_title (tt_title)
    )
    """

    __tablename__ = "translate_type"

    tt_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tt_title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tt_lead: Mapped[int] = mapped_column(nullable=False, default=1)
    tt_full: Mapped[int] = mapped_column(nullable=False, default=0, server_default=text("0"))

    def __init__(self, **kwargs) -> None:
        # Apply Python-level defaults for fields not provided
        if "tt_lead" not in kwargs:
            kwargs["tt_lead"] = 1
        if "tt_full" not in kwargs:
            kwargs["tt_full"] = 0
        super().__init__(**kwargs)


__all__ = [
    "LangRecord",
    "MdwikiRevidRecord",
    "TranslateTypeRecord",
]
