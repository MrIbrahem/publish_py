from __future__ import annotations

import logging

from sqlalchemy import Column, Date, Integer, String, text

from ..engine import BaseDb

logger = logging.getLogger(__name__)


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
    add_date = Column(Date, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "qid": self.qid,
            "title": self.title,
            "add_date": self.add_date,
        }


__all__ = [
    "_QidRecord",
]
