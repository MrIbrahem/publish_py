from __future__ import annotations

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


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


__all__ = ["_MdwikiRevidRecord"]
