"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging

from ....extensions import db
from ...models import QidOthersRecord
from .qid_shared_service import BaseQidService

logger = logging.getLogger(__name__)


class QidOthersService(BaseQidService):
    """Service class for managing QID records."""

    def __init__(self) -> None:
        super().__init__(QidOthersRecord, db.session)


__all__ = [
    "QidOthersService",
]
