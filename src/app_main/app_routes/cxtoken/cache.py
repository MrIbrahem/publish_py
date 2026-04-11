"""
Content Translation token endpoint cache.
"""

import logging
import time
from typing import Any

from cachetools import cached, TTLCache
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

cache = TTLCache(maxsize=100, ttl=3600)


@dataclass
class CxToken:
    age: int
    exp: int
    jwt: str
    stored_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        elapsed = time.time() - self.stored_at
        remaining_age = int(self.age - elapsed)

        return {
            "age": remaining_age,
            "exp": self.exp,
            "jwt": self.jwt,
        }

    def __post_init__(self):
        self.stored_at = time.time()


def store_jwt(cxtoken: dict, user: str, wiki: str) -> None:
    """
    cxtoken: { "age": 3600, "exp": 1775879885, "jwt": "..." }
    """
    cache[(user, wiki)] = CxToken(
        age=cxtoken["age"],
        exp=cxtoken["exp"],
        jwt=cxtoken["jwt"],
    )


def get_from_store(user: str, wiki: str) -> dict:
    """
    { "age": 3600, "exp": 1775879885, "jwt": "..." }
    """
    in_cache: CxToken = cache.get((user, wiki))
    if not in_cache:
        return None

    return in_cache.to_dict()
