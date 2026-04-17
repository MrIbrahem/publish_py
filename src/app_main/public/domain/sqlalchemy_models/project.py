from __future__ import annotations



from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


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


__all__ = ["_ProjectRecord"]
