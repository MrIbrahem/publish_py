"""
Public domain models - SQLAlchemy ORM.

Note: Several models have been moved to specialized modules:
- pages_models.py: PagesUsersToMainRecord
- views_models.py: EnwikiPageviewRecord, ViewsNewRecord, ViewsNewAllRecord
- metrics_models.py: AssessmentRecord, RefsCountRecord, WordRecord
- qid_models.py: QidRecord
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, JSON, text

from ..shared.engine import BaseDb


class LangRecord(BaseDb):
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

    lang_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False)
    autonym = Column(String(70), nullable=False)
    name = Column(String(70), nullable=False)
    redirects = Column(JSON, nullable=True, server_default=text("NULL"))


class MdwikiRevidRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS mdwiki_revids (
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        revid int NOT NULL,
        PRIMARY KEY (title)
    )
    """

    __tablename__ = "mdwiki_revids"

    title = Column(String(255), primary_key=True)
    revid = Column(Integer, nullable=False)


class TranslateTypeRecord(BaseDb):
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

    tt_id = Column(Integer, primary_key=True, autoincrement=True)
    tt_title = Column(String(120), unique=True, nullable=False)
    tt_lead = Column(Integer, nullable=False, default=1)
    tt_full = Column(Integer, nullable=False, default=0, server_default=text("0"))

    def __init__(self, **kwargs):
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
