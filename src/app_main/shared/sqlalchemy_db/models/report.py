from __future__ import annotations

from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text, text

from ..engine import BaseDb


class _ReportRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS publish_reports (
        id int NOT NULL AUTO_INCREMENT,
        date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        lang varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        sourcetitle varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        result varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        data longtext CHARACTER
        SET
            utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT publish_reports_chk_1 CHECK (json_valid (data))
    )
    """

    __tablename__ = "publish_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    title = Column(String(255), nullable=False)
    user = Column(String(255), nullable=False)
    lang = Column(String(255), nullable=False)
    sourcetitle = Column(String(255), nullable=False)
    result = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date.isoformat() if hasattr(self.date, "isoformat") else str(self.date),
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


__all__ = ["_ReportRecord"]
