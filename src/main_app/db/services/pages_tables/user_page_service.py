"""
SQLAlchemy-based service for managing pages_users and page targets.
"""

from __future__ import annotations

import logging

from .pages_shared_service import BasePagesService

from ....extensions import db
from ...models import UserPageRecord

logger = logging.getLogger(__name__)

class UserPagesService(BasePagesService):
    def __init__(self) -> None:
        super().__init__(UserPageRecord, db.session)

__all__ = [
    "UserPagesService",
]
