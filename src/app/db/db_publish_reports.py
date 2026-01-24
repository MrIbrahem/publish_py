"""
TODO: should be updated to match php_src/bots/sql/db_publish_reports.php
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, List
from . import Database

logger = logging.getLogger(__name__)
table_creation_sql = """
CREATE TABLE IF NOT EXISTS `publish_reports` (
    `id` int NOT NULL AUTO_INCREMENT,
    `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    `user` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    `lang` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    `sourcetitle` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    `result` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `publish_reports_chk_1` CHECK (json_valid(`data`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


@dataclass
class ReportRecord:
    """Representation of a report record."""

    id: int
    date: Any
    title: str
    user: str
    lang: str
    sourcetitle: str
    result: str
    data: str


class ReportsDB:
    """MySQL-backed"""

    def __init__(self, db_data: dict[str, Any]):
        self.db = Database(db_data)
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.db.execute_query_safe(table_creation_sql)

    def _row_to_record(self, row: dict[str, Any]) -> ReportRecord:
        return ReportRecord(
            id=int(row["id"]),
            date=row["date"],
            title=row["title"],
            user=row["user"],
            lang=row["lang"],
            sourcetitle=row["sourcetitle"],
            result=row["result"],
            data=row["data"],
        )

    def _fetch_by_id(self, report_id: int) -> ReportRecord:
        rows = self.db.fetch_query_safe(
            """
            SELECT id, date, title, user, lang, sourcetitle, result, data
            FROM publish_reports
            WHERE id = %s
            """,
            (report_id,),
        )
        if not rows:
            raise LookupError(f"Report id {report_id} was not found")
        return self._row_to_record(rows[0])

    def list(self) -> List[ReportRecord]:
        rows = self.db.fetch_query_safe(
            """
            SELECT id, date, title, user, lang, sourcetitle, result, data
            FROM publish_reports
            ORDER BY id DESC
            """
        )
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        title: str,
        user: str,
        lang: str,
        sourcetitle: str,
        result: str,
        data: str,
    ) -> ReportRecord:
        last_id = self.db.execute_query_safe(
            """
            INSERT INTO publish_reports (title, user, lang, sourcetitle, result, data)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (title, user, lang, sourcetitle, result, data),
        )
        return self._fetch_by_id(last_id)

    def delete(self, report_id: int) -> ReportRecord:
        record = self._fetch_by_id(report_id)
        self.db.execute_query_safe(
            "DELETE FROM publish_reports WHERE id = %s",
            (report_id,),
        )
        return record


__all__ = [
    "ReportsDB",
    "ReportRecord",
]
