"""
"""

from __future__ import annotations

import logging

from flask import Response, jsonify, request

from ....db.services import get_leaderboard_chart_data
from .form_utils import get_form, FormData

logger = logging.getLogger(__name__)


def leaderboard_status() -> Response:
    """
    Handle leaderboard API requests.
    /api/status?camp=Video&user_group=WIKI&year=2025&month=02&cat=RTTVideo
    """
    form: FormData = get_form(request.args)

    data = get_leaderboard_chart_data(
        camp=form.camp,
        cat=form.cat,
        user_group=form.user_group,
        year=form.year,
        month=form.month,
        lang=form.lang,
        user=form.user,
    )

    response_data = {
        "results": data,
        "count": len(data),
    }

    return jsonify(response_data)


__all__ = [
    "leaderboard_status",
]
