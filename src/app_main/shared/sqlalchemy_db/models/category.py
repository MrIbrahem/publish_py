from __future__ import annotations

import logging

from sqlalchemy import Column, Integer, String

from ..engine import BaseDb

logger = logging.getLogger(__name__)


class _CategoryRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS categories (
        id int unsigned NOT NULL AUTO_INCREMENT,
        category varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        campaign varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        display varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        category2 varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        depth int NOT NULL DEFAULT '0',
        is_default int NOT NULL DEFAULT '0',
        PRIMARY KEY (id),
        UNIQUE KEY category (category)
    )
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(120), unique=True, nullable=False)
    campaign = Column(String(120), nullable=False, default="")
    display = Column(String(120), nullable=False, default="")
    category2 = Column(String(120), nullable=False, default="")
    depth = Column(Integer, nullable=False, default=0, server_default=text("0"))
    is_default = Column(Integer, nullable=False, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "campaign": self.campaign,
            "display": self.display,
            "category2": self.category2,
            "depth": self.depth,
            "is_default": self.is_default,
        }


__all__ = [
    "_CategoryRecord",
]
