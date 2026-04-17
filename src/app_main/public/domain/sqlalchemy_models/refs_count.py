from __future__ import annotations



from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


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


__all__ = ["_RefsCountRecord"]
