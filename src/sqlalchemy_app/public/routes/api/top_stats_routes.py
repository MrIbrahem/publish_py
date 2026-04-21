"""API endpoints for top language and user statistics.

Endpoints:
- /api/top_langs: Aggregated statistics per language
- /api/top_users: Aggregated statistics per user
"""

import logging
from typing import Any, Dict, List

from flask import Response, jsonify, request
from sqlalchemy import Integer, case, cast, func

from ....shared.core.cors import check_cors
from ....shared.engine import get_session
from ....sqlalchemy_models import _LangRecord, _PageRecord, _ViewsNewAllRecord, _WordRecord

logger = logging.getLogger(__name__)


@check_cors
def get_top_langs() -> Response:
    """
    Handle top_langs API requests.
    Returns aggregated statistics per language.

    Query:
        SELECT
            p.lang,
            la.name as lang_name,
            COUNT(p.target) AS targets,
            SUM(
                CASE
                    WHEN p.word IS NOT NULL
                    AND p.word != 0
                    AND p.word != '' THEN p.word
                    WHEN translate_type = 'all' THEN w.w_all_words
                    ELSE w.w_lead_words
                END
            ) AS words,
            SUM(
                CASE
                    WHEN v.views IS NULL
                    OR v.views = '' THEN 0
                    ELSE CAST(v.views AS UNSIGNED)
                END
            ) AS views
        FROM
            pages p
            LEFT JOIN words w ON w.w_title = p.title
            LEFT JOIN views_new_all v ON p.target = v.target
            AND p.lang = v.lang
            LEFT JOIN langs la ON p.lang = la.code
        WHERE
            p.target != ''
            AND p.target IS NOT NULL
            AND p.user != ''
            AND p.user IS NOT NULL
            AND p.lang != ''
            AND p.lang IS NOT NULL
        GROUP BY
            p.lang
        ORDER BY
            targets DESC

    Returns:
        JSON response with language statistics
    """
    limit = request.args.get("limit", 50)
    try:
        with get_session() as session:
            # Build the word count expression
            word_expr = case(
                (
                    _PageRecord.word.is_not(None) & (_PageRecord.word != 0) & (_PageRecord.word != ""),
                    _PageRecord.word,
                ),
                (_PageRecord.translate_type == "all", _WordRecord.w_all_words),
                else_=_WordRecord.w_lead_words,
            )

            # Build the views expression (CAST to UNSIGNED)
            views_expr = case(
                (_ViewsNewAllRecord.views.is_(None) | (_ViewsNewAllRecord.views == ""), 0),
                else_=cast(_ViewsNewAllRecord.views, Integer),
            )

            # Query with joins
            query = (
                session.query(
                    _PageRecord.lang,
                    _LangRecord.name.label("lang_name"),
                    func.count(_PageRecord.target).label("targets"),
                    func.sum(word_expr).label("words"),
                    func.sum(views_expr).label("views"),
                )
                .outerjoin(_WordRecord, _WordRecord.w_title == _PageRecord.title)
                .outerjoin(
                    _ViewsNewAllRecord,
                    (_PageRecord.target == _ViewsNewAllRecord.target) & (_PageRecord.lang == _ViewsNewAllRecord.lang),
                )
                .outerjoin(_LangRecord, _PageRecord.lang == _LangRecord.code)
                .filter(_PageRecord.target != "")
                .filter(_PageRecord.target.is_not(None))
                .filter(_PageRecord.user != "")
                .filter(_PageRecord.user.is_not(None))
                .filter(_PageRecord.lang != "")
                .filter(_PageRecord.lang.is_not(None))
                .group_by(_PageRecord.lang, _LangRecord.name)
                .order_by(func.count(_PageRecord.target).desc())
            )

            if limit:
                query = query.limit(int(limit))

            results = query.all()

            # Convert results to list of dicts
            data: List[Dict[str, Any]] = [
                {
                    "lang": row.lang,
                    "lang_name": row.lang_name if row.lang_name else row.lang,
                    "targets": row.targets,
                    "words": int(row.words) if row.words else 0,
                    "views": int(row.views) if row.views else 0,
                }
                for row in results
            ]

    except Exception:
        logger.exception("Error fetching top_langs data")
        return jsonify({"error": "An internal error occurred while fetching top_langs data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


@check_cors
def get_top_users() -> Response:
    """
    Handle top_users API requests.
    Returns aggregated statistics per user.

    Query:
        SELECT
            p.user,
            COUNT(p.target) AS targets,
            SUM(
                CASE
                    WHEN p.word IS NOT NULL
                    AND p.word != 0
                    AND p.word != '' THEN p.word
                    WHEN translate_type = 'all' THEN w.w_all_words
                    ELSE w.w_lead_words
                END
            ) AS words,
            SUM(
                CASE
                    WHEN v.views IS NULL
                    OR v.views = '' THEN 0
                    ELSE CAST(v.views AS UNSIGNED)
                END
            ) AS views
        FROM
            pages p
            LEFT JOIN words w ON w.w_title = p.title
            LEFT JOIN views_new_all v ON p.target = v.target
            AND p.lang = v.lang
        WHERE
            p.target != ''
            AND p.target IS NOT NULL
            AND p.user != ''
            AND p.user IS NOT NULL
            AND p.lang != ''
            AND p.lang IS NOT NULL
        GROUP BY
            p.user
        ORDER BY
            targets DESC

    Returns:
        JSON response with user statistics
    """

    limit = request.args.get("limit", 50)
    try:
        with get_session() as session:
            # Build the word count expression
            word_expr = case(
                (
                    _PageRecord.word.is_not(None) & (_PageRecord.word != 0) & (_PageRecord.word != ""),
                    _PageRecord.word,
                ),
                (_PageRecord.translate_type == "all", _WordRecord.w_all_words),
                else_=_WordRecord.w_lead_words,
            )

            # Build the views expression (CAST to UNSIGNED)
            views_expr = case(
                (_ViewsNewAllRecord.views.is_(None) | (_ViewsNewAllRecord.views == ""), 0),
                else_=cast(_ViewsNewAllRecord.views, Integer),
            )

            # Query with joins
            query = (
                session.query(
                    _PageRecord.user,
                    func.count(_PageRecord.target).label("targets"),
                    func.sum(word_expr).label("words"),
                    func.sum(views_expr).label("views"),
                )
                .outerjoin(_WordRecord, _WordRecord.w_title == _PageRecord.title)
                .outerjoin(
                    _ViewsNewAllRecord,
                    (_PageRecord.target == _ViewsNewAllRecord.target) & (_PageRecord.lang == _ViewsNewAllRecord.lang),
                )
                .filter(_PageRecord.target != "")
                .filter(_PageRecord.target.is_not(None))
                .filter(_PageRecord.user != "")
                .filter(_PageRecord.user.is_not(None))
                .filter(_PageRecord.lang != "")
                .filter(_PageRecord.lang.is_not(None))
                .group_by(_PageRecord.user)
                .order_by(func.count(_PageRecord.target).desc())
            )

            if limit:
                query = query.limit(int(limit))

            results = query.all()

            # Convert results to list of dicts
            data: List[Dict[str, Any]] = [
                {
                    "user": row.user,
                    "targets": row.targets,
                    "words": int(row.words) if row.words else 0,
                    "views": int(row.views) if row.views else 0,
                }
                for row in results
            ]

    except Exception:
        logger.exception("Error fetching top_users data")
        return jsonify({"error": "An internal error occurred while fetching top_users data"}), 500

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


__all__ = ["get_top_langs", "get_top_users"]
