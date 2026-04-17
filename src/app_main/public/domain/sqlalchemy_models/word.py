from __future__ import annotations



from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


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


__all__ = ["_WordRecord"]
