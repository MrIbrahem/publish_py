from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Column, Date, DateTime, Integer, LargeBinary, String, func, text

from .engine import LONGTEXT, BaseDb
from .utils.decode_bytes import coerce_bytes

logger = logging.getLogger(__name__)


class _CategoryRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS categories (
        id int unsigned NOT NULL AUTO_INCREMENT,
        category varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        campaign varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        display varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        category2 varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        depth int NOT NULL DEFAULT '0',
        is_default int NOT NULL DEFAULT '0',
        PRIMARY KEY (id),
        UNIQUE KEY category (category)
    )
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(120), unique=True, nullable=False)
    campaign = Column(String(120), nullable=False, default="")
    display = Column(String(120), nullable=False, default="")
    category2 = Column(String(120), nullable=False, default="")
    depth = Column(Integer, nullable=False, default=0, server_default=text("0"))
    is_default = Column(Integer, nullable=False, default=0, server_default=text("0"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "campaign": self.campaign,
            "display": self.display,
            "category2": self.category2,
            "depth": self.depth,
            "is_default": self.is_default,
        }


class _PageRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS pages (
        id int unsigned NOT NULL AUTO_INCREMENT,
        title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        word int DEFAULT NULL,
        translate_type varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        cat varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        lang varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        user varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        target varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        date date DEFAULT NULL,
        pupdate varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted int DEFAULT '0',
        mdwiki_revid int DEFAULT NULL,
        PRIMARY KEY (id),
        KEY idx_title (title),
        KEY target (target)
    )
    """

    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    word = Column(Integer, nullable=True)
    translate_type = Column(String(20), nullable=True)
    cat = Column(String(120), nullable=True)
    lang = Column(String(30), nullable=True)
    user = Column(String(120), nullable=True)
    target = Column(String(120), nullable=True)
    date = Column(Date, nullable=True)
    pupdate = Column(String(120), nullable=True)
    add_date = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    deleted = Column(Integer, nullable=False, default=0, server_default=text("0"))
    mdwiki_revid = Column(Integer, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "word": self.word,
            "translate_type": self.translate_type,
            "cat": self.cat,
            "lang": self.lang,
            "user": self.user,
            "target": self.target,
            "date": self.date,
            "pupdate": self.pupdate,
            "add_date": str(self.add_date) if self.add_date else self.add_date,
            "deleted": self.deleted,
            "mdwiki_revid": self.mdwiki_revid,
        }


class _QidRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS qids (
        id int unsigned NOT NULL AUTO_INCREMENT,
        qid varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        UNIQUE KEY title (title),
        KEY qid (qid)
    )
    """

    __tablename__ = "qids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qid = Column(String(20), nullable=False)
    title = Column(String(255), unique=True, nullable=False)
    add_date = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "qid": self.qid,
            "title": self.title,
            "add_date": str(self.add_date) if self.add_date else self.add_date,
        }


class _ReportRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS publish_reports (
        id int NOT NULL AUTO_INCREMENT,
        date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        lang varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        sourcetitle varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        result varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        data longtext CHARACTER
        SET
            utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT publish_reports_chk_1 CHECK (json_valid (data))
    )
    """

    __tablename__ = "publish_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    title = Column(String(255), nullable=False)
    user = Column(String(255), nullable=False)
    lang = Column(String(255), nullable=False)
    sourcetitle = Column(String(255), nullable=False)
    result = Column(String(255), nullable=False)

    # Compiler <sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler object at ...> can't render element of type LONGTEXT
    data = Column(LONGTEXT, nullable=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            # "date": self.date.isoformat() if hasattr(self.date, "isoformat") else str(self.date),
            "date": self.date,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


class _UserPageRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS pages_users (
        id int unsigned NOT NULL AUTO_INCREMENT,
        title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        word int DEFAULT NULL,
        translate_type varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        cat varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        lang varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        user varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        target varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        date date DEFAULT NULL,
        pupdate varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted int DEFAULT '0',
        mdwiki_revid int DEFAULT NULL,
        PRIMARY KEY (id),
        KEY idx_title (title),
        KEY target (target)
    )
    """

    __tablename__ = "pages_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    word = Column(Integer, nullable=True)
    translate_type = Column(String(20), nullable=True)
    cat = Column(String(120), nullable=True)
    lang = Column(String(30), nullable=True)
    user = Column(String(120), nullable=True)
    target = Column(String(120), nullable=True)
    date = Column(Date, nullable=True)
    pupdate = Column(String(120), nullable=True)
    add_date = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    deleted = Column(Integer, nullable=False, default=0, server_default=text("0"))
    mdwiki_revid = Column(Integer, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "word": self.word,
            "translate_type": self.translate_type,
            "cat": self.cat,
            "lang": self.lang,
            "user": self.user,
            "target": self.target,
            "date": self.date,
            "pupdate": self.pupdate,
            "add_date": str(self.add_date) if self.add_date else self.add_date,
            "deleted": self.deleted,
            "mdwiki_revid": self.mdwiki_revid,
        }


class _UserTokenRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS user_tokens (
        user_id int NOT NULL,
        username varchar(255) NOT NULL,
        access_token varbinary(1024) NOT NULL,
        access_secret varbinary(1024) NOT NULL,
        created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        last_used_at datetime DEFAULT NULL,
        rotated_at datetime DEFAULT NULL,
        PRIMARY KEY (user_id),
        UNIQUE KEY uq_user_tokens_username (username)
    )
    """

    __tablename__ = "user_tokens"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    access_token = Column(LargeBinary(1024), nullable=False)
    access_secret = Column(LargeBinary(1024), nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    last_used_at = Column(DateTime, nullable=True, server_default=func.current_timestamp())
    rotated_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            # "access_token": self.access_token,
            # "access_secret": self.access_secret,
            "access_token": coerce_bytes(self.access_token),
            "access_secret": coerce_bytes(self.access_secret),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_used_at": self.last_used_at,
            "rotated_at": self.rotated_at,
        }


__all__ = [
    "_PageRecord",
    "_ReportRecord",
    "_UserTokenRecord",
    "_CategoryRecord",
    "_UserPageRecord",
    "_QidRecord",
]
