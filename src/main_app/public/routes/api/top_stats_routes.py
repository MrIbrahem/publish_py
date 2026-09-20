"""
API endpoints for top language and user statistics.

Endpoints:
- /api/top_langs: Aggregated statistics per language
- /api/top_users: Aggregated statistics per user
"""

from __future__ import annotations

import logging

from ....database.services import TopStatsService
from ...mapping import ApiFormData
from .mapping import (
    TopLangsResult,
    TopLangStat,
    TopUsersResult,
    TopUserStat,
)

logger = logging.getLogger(__name__)


def get_top_langs(form: ApiFormData) -> TopLangsResult:
    """
    Handle top_langs API requests.
    Returns aggregated statistics per language.

    Returns:
        JSON response with language statistics
    """
    service = TopStatsService()
    # /api/top_langs?camp=Video&user_group=all&year=all&month=All&cat=RTTVideo
    try:
        results = service.query_top_langs(form)
    except Exception:
        logger.exception("Error fetching top_langs data")
        return TopLangsResult(error="An internal error occurred while fetching top_langs data")

    try:
        data: list[TopLangStat] = [
            TopLangStat(
                lang=row.lang,
                lang_name=row.lang_name if row.lang_name else row.lang,
                targets=row.targets,
                words=int(row.words) if row.words else 0,
                views=int(row.views) if row.views else 0,
            )
            for row in results
        ]
    except Exception:
        logger.exception("Error processing top_langs data")
        return TopLangsResult(error="An internal error occurred while processing top_langs data")

    return TopLangsResult(results=data, count=len(data))


def get_top_users(form: ApiFormData) -> TopUsersResult:
    """
    Handle top_users API requests.
    Returns aggregated statistics per user.
    Returns:
        JSON response with user statistics
    """
    service = TopStatsService()
    try:
        results = service.query_top_users(form)
    except Exception as e:
        logger.error("Error fetching top_users data %s", str(e))
        return TopUsersResult(error="An internal error occurred while fetching top_users data")

    try:
        data: list[TopUserStat] = [
            TopUserStat(
                user=row.user,
                targets=row.targets,
                words=int(row.words) if row.words else 0,
                views=int(row.views) if row.views else 0,
            )
            for row in results
        ]
    except Exception as e:
        logger.error("Error converting top_users data %s", str(e))
        return TopUsersResult(error="An internal error occurred while converting top_users data")

    return TopUsersResult(results=data, count=len(data))


__all__ = [
    "get_top_langs",
    "get_top_users",
]
