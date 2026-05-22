"""
Pages domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from ...shared.core.extensions import db


class PageRecord(db.Model):
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    word = db.Column(db.Integer, nullable=True)
    translate_type = db.Column(db.String(20), nullable=False, default="lead", server_default=db.text("'lead'"))
    cat = db.Column(db.String(120), nullable=True)
    lang = db.Column(db.String(30), nullable=True)
    user = db.Column(db.String(120), nullable=True)
    target = db.Column(db.String(120), nullable=True)
    date = db.Column(db.Date, nullable=True)
    pupdate = db.Column(db.String(120), nullable=True)
    add_date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    deleted = db.Column(db.Integer, nullable=False, default=0, server_default=db.text("0"))
    mdwiki_revid = db.Column(db.Integer, nullable=True)

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "deleted" not in kwargs:
            kwargs["deleted"] = 0
        super().__init__(**kwargs)


class UserPageRecord(db.Model):
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    word = db.Column(db.Integer, nullable=True)
    translate_type = db.Column(db.String(20), nullable=False, default="lead", server_default=db.text("'lead'"))
    cat = db.Column(db.String(120), nullable=True)
    lang = db.Column(db.String(30), nullable=True)
    user = db.Column(db.String(120), nullable=True)
    target = db.Column(db.String(120), nullable=True)
    date = db.Column(db.Date, nullable=True)
    pupdate = db.Column(db.String(120), nullable=True)
    add_date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    deleted = db.Column(db.Integer, nullable=False, default=0, server_default=db.text("0"))
    mdwiki_revid = db.Column(db.Integer, nullable=True)

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "deleted" not in kwargs:
            kwargs["deleted"] = 0
        super().__init__(**kwargs)


class PagesUsersToMainRecord(db.Model):
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

    id = db.Column(db.Integer, db.ForeignKey("pages_users.id"), primary_key=True)
    new_target = db.Column(db.String(255), nullable=False, default="", server_default=db.text("''"))
    new_user = db.Column(db.String(255), nullable=False, default="", server_default=db.text("''"))
    new_qid = db.Column(db.String(255), nullable=False, default="", server_default=db.text("''"))

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "new_target" not in kwargs:
            kwargs["new_target"] = ""
        if "new_user" not in kwargs:
            kwargs["new_user"] = ""
        if "new_qid" not in kwargs:
            kwargs["new_qid"] = ""
        super().__init__(**kwargs)


class InProcessRecord(db.Model):
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    user = db.Column(db.String(255), nullable=False)
    lang = db.Column(db.String(30), nullable=False)
    cat = db.Column(db.String(255), default="RTT", server_default=db.text("'RTT'"))
    translate_type = db.Column(db.String(20), nullable=False, default="lead", server_default=db.text("'lead'"))
    word = db.Column(db.Integer, default=0, server_default=db.text("0"))
    add_date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def __init__(self, **kwargs):
        # Apply Python-level defaults for fields not provided
        if "cat" not in kwargs:
            kwargs["cat"] = "RTT"
        if "translate_type" not in kwargs:
            kwargs["translate_type"] = "lead"
        if "word" not in kwargs:
            kwargs["word"] = 0
        super().__init__(**kwargs)


__all__ = [
    "PageRecord",
    "UserPageRecord",
    "PagesUsersToMainRecord",
    "InProcessRecord",
]
