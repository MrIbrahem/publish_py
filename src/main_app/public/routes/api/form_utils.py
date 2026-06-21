"""
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)

@dataclass
class FormData:
    limit: int | None
    user_group: str | None
    cat: str | None
    camp: str | None
    year: int | None
    month: int | None

def get_form(request_args) -> FormData:
    # limit
    limit = request_args.get("limit", default=50, type=int)
    if limit is None or limit <= 0:
        limit = 50
    limit = min(limit, 1000)

    # /api/top_langs?camp=Video&user_group=all&year=all&month=All&cat=RTTVideo
    user_group = request_args.get("user_group", default="all", type=str)
    cat = request_args.get("cat", default="all", type=str)
    camp = request_args.get("camp", default="all", type=str)
    month = request_args.get("month", type=int)
    year = request_args.get("year", type=int)

    if user_group.lower() == "all":
        user_group = None

    if cat.lower() == "all":
        cat = None

    if camp.lower() == "all":
        camp = None

    return FormData(
        limit=limit,
        user_group=user_group,
        cat=cat,
        camp=camp,
        year=year,
        month=month,
    )
