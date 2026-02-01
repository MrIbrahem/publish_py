"""
Database handler for publish_reports table.

Mirrors: php_src/bots/sql/db_publish_reports.php
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..config import DbConfig

from . import Database

logger = logging.getLogger(__name__)

# Parameter configuration matching PHP endpoint_params
# These are hardcoded and trusted - column names are NOT from user input
PUBLISH_REPORTS_PARAMS = [
    {"name": "year", "column": "YEAR(date)", "type": "number"},
    {"name": "month", "column": "MONTH(date)", "type": "number"},
    {"name": "title", "column": "title", "type": "text"},
    {"name": "user", "column": "user", "type": "text"},
    {"name": "lang", "column": "lang", "type": "text"},
    {"name": "sourcetitle", "column": "sourcetitle", "type": "text"},
    {"name": "result", "column": "result", "type": "text"},
]

# Valid columns that can be used in SELECT and WHERE clauses (for validation)
_VALID_COLUMNS = frozenset({
    "id", "date", "title", "user", "lang", "sourcetitle", "result", "data",
    "YEAR(date)", "MONTH(date)",
})

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

    def __init__(self, db_data: DbConfig):
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

    def query_with_filters(
        self,
        filters: Dict[str, Any],
        select_fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[ReportRecord]:
        """Query reports with dynamic filtering.

        Args:
            filters: Dictionary of filter parameters
            select_fields: Optional list of fields to return
            limit: Optional result limit

        Returns:
            List of matching ReportRecord objects
        """
        # Build SELECT clause
        valid_fields = {"id", "date", "title", "user", "lang", "sourcetitle", "result", "data"}
        if select_fields:
            fields = [f for f in select_fields if f in valid_fields]
            # Always include 'id' for record mapping
            if "id" not in fields:
                fields.insert(0, "id")
            select_clause = ", ".join(fields)
        else:
            select_clause = "id, date, title, user, lang, sourcetitle, result, data"

        query = f"SELECT DISTINCT {select_clause} FROM publish_reports"
        params: List[Any] = []
        conditions: List[str] = []

        for param_def in PUBLISH_REPORTS_PARAMS:
            name = param_def["name"]
            column = param_def["column"]

            # Validate column is in the trusted allowlist (defense in depth)
            if column not in _VALID_COLUMNS:
                logger.warning(f"Skipping unrecognized column: {column}")
                continue

            if name not in filters:
                continue

            value = filters[name]

            # Handle special values
            if value in ("not_mt", "not_empty"):
                conditions.append(f"({column} != '' AND {column} IS NOT NULL)")
            elif value in ("mt", "empty"):
                conditions.append(f"({column} = '' OR {column} IS NULL)")
            elif value in (">0", "&#62;0"):
                conditions.append(f"{column} > 0")
            elif str(value).lower() == "all":
                continue  # Skip this filter
            else:
                conditions.append(f"{column} = %s")
                params.append(value)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC"

        if limit:
            # Use parameterized query for LIMIT
            query += " LIMIT %s"
            params.append(int(limit))

        rows = self.db.fetch_query_safe(query, tuple(params) if params else None)

        # Handle partial field selection by providing defaults
        result_records = []
        for row in rows:
            record = ReportRecord(
                id=int(row.get("id", 0)),
                date=row.get("date", ""),
                title=row.get("title", ""),
                user=row.get("user", ""),
                lang=row.get("lang", ""),
                sourcetitle=row.get("sourcetitle", ""),
                result=row.get("result", ""),
                data=row.get("data", ""),
            )
            result_records.append(record)

        return result_records


__all__ = [
    "ReportsDB",
    "ReportRecord",
    "PUBLISH_REPORTS_PARAMS",
]
