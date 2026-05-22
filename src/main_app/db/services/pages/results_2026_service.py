"""
Raw-SQL services that mirror the PHP ``new_sql_tables.php`` queries used by
the ``results_2026`` flow.

PHP source:
  - src/backend/api_or_sql/new_sql_tables.php
      - missing_by_lang_and_category($lang_code, $category)
      - exists_by_lang_and_category($lang_code, $category)

The PHP queries reference ``category_members``; in the publish_py schema the
equivalent table is ``all_articles`` (same ``article_id`` / ``category``
columns), as already used by ``allqid_service.list_targets_by_lang``.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy import text

from ....shared.core.extensions import db

logger = logging.getLogger(__name__)


# logic from new_sql_tables.php — missing_by_lang_and_category
_MISSING_SQL = text(
    """
    SELECT
        c.article_id   AS title,
        c.category     AS category,
        ase.importance AS importance,
        rc.r_lead_refs AS r_lead_refs,
        rc.r_all_refs  AS r_all_refs,
        ep.en_views    AS en_views,
        q.qid          AS qid,
        w.w_lead_words AS w_lead_words,
        w.w_all_words  AS w_all_words
    FROM all_articles c
    JOIN qids q                   ON q.title    = c.article_id
    LEFT JOIN all_qids_exists aq  ON aq.qid     = q.qid AND aq.code = :lang
    LEFT JOIN assessments ase     ON ase.title  = c.article_id
    LEFT JOIN enwiki_pageviews ep ON ep.title   = c.article_id
    LEFT JOIN refs_counts rc      ON rc.r_title = c.article_id
    LEFT JOIN words w             ON w.w_title  = c.article_id
    WHERE c.category = :cat
      AND aq.target IS NULL
      AND EXISTS (SELECT 1 FROM langs la WHERE la.code = :lang)
    """
)


# logic from new_sql_tables.php — exists_by_lang_and_category
_EXISTS_SQL = text(
    """
    SELECT
        c.article_id   AS title,
        c.category     AS category,
        ase.importance AS importance,
        rc.r_lead_refs AS r_lead_refs,
        rc.r_all_refs  AS r_all_refs,
        ep.en_views    AS en_views,
        q.qid          AS qid,
        w.w_lead_words AS w_lead_words,
        w.w_all_words  AS w_all_words,
        aq.target      AS target
    FROM all_articles c
    JOIN qids q                   ON q.title    = c.article_id
    LEFT JOIN all_qids_exists aq  ON aq.qid     = q.qid AND aq.code = :lang
    LEFT JOIN assessments ase     ON ase.title  = c.article_id
    LEFT JOIN enwiki_pageviews ep ON ep.title   = c.article_id
    LEFT JOIN refs_counts rc      ON rc.r_title = c.article_id
    LEFT JOIN words w             ON w.w_title  = c.article_id
    WHERE c.category = :cat
      AND aq.target IS NOT NULL
      AND EXISTS (SELECT 1 FROM langs la WHERE la.code = :lang)
    """
)


def _rows_to_dicts(rows: list[Any]) -> List[dict]:
    return [dict(row._mapping) for row in rows]


def missing_by_lang_and_category(lang: str, cat: str) -> List[dict]:
    """Return missing-target articles for ``lang`` in category ``cat``."""
    if not lang or not cat:
        return []
    rows = db.session.execute(_MISSING_SQL, {"lang": lang, "cat": cat}).fetchall()
    return _rows_to_dicts(rows)


def exists_by_lang_and_category(lang: str, cat: str) -> List[dict]:
    """Return already-translated articles for ``lang`` in category ``cat``."""
    if not lang or not cat:
        return []
    rows = db.session.execute(_EXISTS_SQL, {"lang": lang, "cat": cat}).fetchall()
    return _rows_to_dicts(rows)


__all__ = [
    "missing_by_lang_and_category",
    "exists_by_lang_and_category",
]
