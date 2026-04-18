from __future__ import annotations

from sqlalchemy import Column, Integer, String, text

from ....shared.sqlalchemy_db.engine import BaseDb


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


__all__ = ["_TranslateTypeRecord"]
