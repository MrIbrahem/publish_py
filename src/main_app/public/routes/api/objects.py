"""API endpoints for top language and user statistics.

Endpoints:
- /api/top_langs: Aggregated statistics per language
- /api/top_users: Aggregated statistics per user
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any



logger = logging.getLogger(__name__)


@dataclass
class TopLangStat:
    lang: str
    lang_name: str
    targets: int
    words: int
    views: int


@dataclass
class TopUserStat:
    user: str
    targets: int
    words: int
    views: int


@dataclass
class TopLangsResult:
    results: list[TopLangStat] = field(default_factory=list)
    count: int = 0
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TopUsersResult:
    results: list[TopUserStat] = field(default_factory=list)
    count: int = 0
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


__all__ = [
    "TopLangStat",
    "TopLangsResult",
    "TopUserStat",
    "TopUsersResult",
]
