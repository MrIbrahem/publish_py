"""
Pages domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, func, text

from ..shared.engine import BaseDb


class PageRecord(BaseDb):
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


class UserPageRecord(BaseDb):
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


class PagesUsersToMainRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS pages_users_to_main (
        id int unsigned NOT NULL,
        new_target varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        new_user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        new_qid varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        KEY id (id),
        CONSTRAINT pages_users_to_main_ibfk_1 FOREIGN KEY (id) REFERENCES pages_users (id)
    )
    """

    __tablename__ = "pages_users_to_main"

    id = Column(Integer, ForeignKey("pages_users.id"), primary_key=True)
    new_target = Column(String(255), nullable=False, default="")
    new_user = Column(String(255), nullable=False, default="")
    new_qid = Column(String(255), nullable=False, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "new_target": self.new_target,
            "new_user": self.new_user,
            "new_qid": self.new_qid,
        }


__all__ = [
    "PageRecord",
    "UserPageRecord",
    "PagesUsersToMainRecord",
]
