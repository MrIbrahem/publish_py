"""
Raw-SQL services that mirror the PHP ``missing.php`` helpers.

PHP source:
  - src/backend/api_or_sql/new_sql_tables.php
      - count_category_members($category)
      - statics_by_category($category)

The PHP queries reference ``category_members``; in the publish_py schema the
equivalent table is ``all_articles`` (same ``article_id`` / ``category``
columns), matching the convention already used by
``allqid_service.list_targets_by_lang`` and
``results_2026_service``.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import text

from ....shared.core.extensions import db

logger = logging.getLogger(__name__)


# logic from new_sql_tables.php — count_category_members
_COUNT_MEMBERS_SQL = text(
    """
    SELECT COUNT(c.article_id) AS members
    FROM all_articles c
    WHERE c.category = :cat
    """
)


# logic from new_sql_tables.php — statics_by_category
_STATS_BY_CATEGORY_SQL = text(
    """
    SELECT
        aq.code   AS language_code,
        COUNT(*)  AS available_title_count
    FROM all_articles c
    JOIN qids q              ON q.title = c.article_id
    JOIN all_qids_exists aq  ON aq.qid  = q.qid
    WHERE c.category = :cat
    GROUP BY aq.code
    ORDER BY available_title_count ASC
    """
)


def count_category_members(cat: str) -> int:
    """Return the total number of articles in ``cat`` (PHP count_category_members).

    PHP returns a list of rows; the consumer pulls ``$row['members']`` from
    the first row. The Python port returns the integer directly.
    """
    if not cat:
        return 0
    row = db.session.execute(_COUNT_MEMBERS_SQL, {"cat": cat}).fetchone()
    if row is None:
        return 0
    members = row._mapping.get("members")
    return int(members or 0)


def statics_by_category(cat: str) -> List[dict]:
    """Return per-language counts of available titles for ``cat`` (PHP statics_by_category)."""
    if not cat:
        return []
    rows = db.session.execute(_STATS_BY_CATEGORY_SQL, {"cat": cat}).fetchall()
    return [dict(row._mapping) for row in rows]


__all__ = [
    "count_category_members",
    "statics_by_category",
]
