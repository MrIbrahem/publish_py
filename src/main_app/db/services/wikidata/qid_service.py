"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging

from ...models import QidRecord
from .qid_shared_service import BaseQidService

logger = logging.getLogger(__name__)

ServiceRecord = QidRecord


class QidService(BaseQidService):
    """Service class for managing QID records."""

    def __init__(self) -> None:
        super().__init__(QidRecord)


__all__ = [
    "QidService",
]
