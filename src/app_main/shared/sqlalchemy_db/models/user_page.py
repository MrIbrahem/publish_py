from __future__ import annotations

from typing import Any

from sqlalchemy import Column, Date, Integer, String, func, text
from sqlalchemy.dialects.mysql import INTEGER

from ..engine import BaseDb


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
    add_date = Column(Date, nullable=False, server_default=func.current_timestamp())
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
            "add_date": self.add_date,
            "deleted": self.deleted,
            "mdwiki_revid": self.mdwiki_revid,
        }


__all__ = [
    "_UserPageRecord",
]
