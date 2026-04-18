"""
Public domain models.
"""
from __future__ import annotations


from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, func, text, DateTime

from ...shared.sqlalchemy_db.engine import BaseDb


class _AssessmentRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS assessments (
        id int unsigned NOT NULL AUTO_INCREMENT,
        title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        importance varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY title (title)
      )
    """

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), unique=True, nullable=False)
    importance = Column(String(120), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "importance": self.importance,
        }


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
    en_views = Column(Integer, default=0, server_default=text("0"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "en_views": self.en_views,
        }


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
    cat = Column(String(255), default="RTT", server_default=text("'RTT'"))
    translate_type = Column(String(20), default="lead", server_default=text("'lead'"))
    word = Column(Integer, default=0, server_default=text("0"))
    add_date = Column(DateTime, nullable=False, server_default=func.current_timestamp())

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


class _LangRecord(BaseDb):
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


class _MdwikiRevidRecord(BaseDb):
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


class _PagesUsersToMainRecord(BaseDb):
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


class _ProjectRecord(BaseDb):
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


class _RefsCountRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS refs_counts (
        r_id int unsigned NOT NULL AUTO_INCREMENT,
        r_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        r_lead_refs int DEFAULT NULL,
        r_all_refs int DEFAULT NULL,
        PRIMARY KEY (r_id),
        UNIQUE KEY r_title (r_title)
    )
    """

    __tablename__ = "refs_counts"

    r_id = Column(Integer, primary_key=True, autoincrement=True)
    r_title = Column(String(120), unique=True, nullable=False)
    r_lead_refs = Column(Integer, nullable=True)
    r_all_refs = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "r_id": self.r_id,
            "r_title": self.r_title,
            "r_lead_refs": self.r_lead_refs,
            "r_all_refs": self.r_all_refs,
        }


class _TranslateTypeRecord(BaseDb):
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

    def to_dict(self) -> dict:
        return {
            "tt_id": self.tt_id,
            "tt_title": self.tt_title,
            "tt_lead": self.tt_lead,
            "tt_full": self.tt_full,
        }


class _UserRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id int NOT NULL AUTO_INCREMENT,
        username varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        email varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        wiki varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        user_group varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Uncategorized',
        reg_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id)
    )
    """

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, default="")
    wiki = Column(String(255), nullable=False, default="")
    user_group = Column(String(120), nullable=False, default="Uncategorized", server_default=text("'Uncategorized'"))
    reg_date = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "wiki": self.wiki,
            "user_group": self.user_group,
            "reg_date": self.reg_date,
        }


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
    views = Column(Integer, default=0, server_default=text("0"))

    __table_args__ = (UniqueConstraint("target", "lang", "year", name="target_lang_year"),)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "lang": self.lang,
            "year": self.year,
            "views": self.views,
        }


class _WordRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS words (
        w_id int unsigned NOT NULL AUTO_INCREMENT,
        w_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        w_lead_words int DEFAULT NULL,
        w_all_words int DEFAULT NULL,
        PRIMARY KEY (w_id),
        UNIQUE KEY w_title (w_title)
    )
    """

    __tablename__ = "words"

    w_id = Column(Integer, primary_key=True, autoincrement=True)
    w_title = Column(String(120), unique=True, nullable=False)
    w_lead_words = Column(Integer, nullable=True)
    w_all_words = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "w_id": self.w_id,
            "w_title": self.w_title,
            "w_lead_words": self.w_lead_words,
            "w_all_words": self.w_all_words,
        }


__all__ = [
    "_AssessmentRecord",
    "_EnwikiPageviewRecord",
    "_InProcessRecord",
    "_LangRecord",
    "_MdwikiRevidRecord",
    "_PagesUsersToMainRecord",
    "_ProjectRecord",
    "_RefsCountRecord",
    "_TranslateTypeRecord",
    "_UserRecord",
    "_ViewsNewRecord",
    "_WordRecord",
]
