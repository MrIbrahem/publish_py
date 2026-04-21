"""
Public domain models - SQLAlchemy ORM.

Note: Several models have been moved to specialized modules:
- pages_models.py: PagesUsersToMainRecord
- views_models.py: EnwikiPageviewRecord, ViewsNewRecord, ViewsNewAllRecord
- metrics_models.py: AssessmentRecord, RefsCountRecord, WordRecord
- qid_models.py: QidRecord
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, func, text

from ..shared.engine import BaseDb


class InProcessRecord(BaseDb):
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
    cat = Column(String(255), default="RTT", server_default=text("'RTT'"))
    translate_type = Column(String(20), default="lead", server_default=text("'lead'"))
    word = Column(Integer, default=0, server_default=text("0"))
    add_date = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "cat" not in kwargs:
            kwargs["cat"] = "RTT"
        if "translate_type" not in kwargs:
            kwargs["translate_type"] = "lead"
        if "word" not in kwargs:
            kwargs["word"] = 0
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "cat": self.cat,
            "translate_type": self.translate_type,
            "word": self.word,
            "add_date": str(self.add_date) if self.add_date else self.add_date,
        }


class LangRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS langs (
        lang_id int NOT NULL AUTO_INCREMENT,
        code varchar(20) NOT NULL,
        autonym varchar(70) NOT NULL,
        name varchar(70) NOT NULL,
        PRIMARY KEY (lang_id)
    )
    """

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

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "revid": self.revid,
        }


class ProjectRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS projects (
        g_id int unsigned NOT NULL AUTO_INCREMENT,
        g_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        PRIMARY KEY (g_id),
        UNIQUE KEY g_title (g_title)
    )
    """

    __tablename__ = "projects"

    g_id = Column(Integer, primary_key=True, autoincrement=True)
    g_title = Column(String(120), unique=True, nullable=False)

    def to_dict(self) -> dict:
        return {
            "g_id": self.g_id,
            "g_title": self.g_title,
        }


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

    def to_dict(self) -> dict:
        return {
            "tt_id": self.tt_id,
            "tt_title": self.tt_title,
            "tt_lead": self.tt_lead,
            "tt_full": self.tt_full,
        }


__all__ = [
    "InProcessRecord",
    "LangRecord",
    "MdwikiRevidRecord",
    "ProjectRecord",
    "TranslateTypeRecord",
]
