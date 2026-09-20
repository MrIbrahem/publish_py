""" """

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from werkzeug.datastructures import MultiDict

logger = logging.getLogger(__name__)


@dataclass
class LeaderBoardData:
    lang: str | None
    camp: str | None
    user_group: str | None
    year: int | None
    month: int | None

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

    @classmethod
    def _normalize(cls, value: str | None | int) -> Any | None:
        if value == "all":
            return None
        return value


__all__ = [
    "LeaderBoardData",
]
