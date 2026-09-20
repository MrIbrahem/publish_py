""" """

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

from werkzeug.datastructures import MultiDict

logger = logging.getLogger(__name__)


@dataclass
class FormsBase:
    lang: str | None
    camp: str | None
    user_group: str | None
    year: int | None
    month: int | None

    @classmethod
    def _normalize(cls, value: str | None | int) -> Any | None:
        if value == "all":
            return None
        return value

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ApiFormData(FormsBase):
    user: str | None
    cat: str | None
    limit: int | None

    @classmethod
    def from_request(cls, request_args: MultiDict[str, str]) -> ApiFormData:
        limit = request_args.get("limit", type=int)
        year = request_args.get("year", type=int)
        month = request_args.get("month", type=int)

        # /api/top_langs?camp=Video&user_group=all&year=all&month=All&cat=RTTVideo
        lang = request_args.get("lang", default="all", type=str)
        user_group = request_args.get("user_group", default="all", type=str)
        camp = request_args.get("camp", default="all", type=str)
        cat = request_args.get("cat", default="all", type=str)
        user = request_args.get("user", default="all", type=str)

        user_group = cls._normalize(user_group)
        year = cls._normalize(year)
        camp = cls._normalize(camp)
        lang = cls._normalize(lang)
        user = cls._normalize(user)
        cat = cls._normalize(cat)

        return cls(
            user_group=user_group,
            camp=camp,
            year=year,
            month=month,
            lang=lang,
            limit=limit,
            cat=cat,
            user=user,
        )


@dataclass
class LeaderBoardData(FormsBase):

    @classmethod
    def from_request(cls, request_args: MultiDict[str, str]) -> LeaderBoardData:
        year = request_args.get("year", type=int)
        month = request_args.get("month", type=int)

        lang = request_args.get("lang", type=str)
        user_group = request_args.get("user_group", type=str)
        camp = request_args.get("camp", type=str)

        user_group = cls._normalize(user_group)
        year = cls._normalize(year)
        camp = cls._normalize(camp)
        lang = cls._normalize(lang)

        return cls(
            user_group=user_group,
            camp=camp,
            year=year,
            month=month,
            lang=lang,
        )


__all__ = [
    "ApiFormData",
    "LeaderBoardData",
]
