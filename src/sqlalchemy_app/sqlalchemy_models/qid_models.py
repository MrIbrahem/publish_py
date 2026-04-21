"""
QID domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, func

from ..shared.engine import BaseDb


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


__all__ = [
    "_QidRecord",
]
