"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging

from ...models import QidOthersRecord

from .qid_shared_service import BaseQidService

logger = logging.getLogger(__name__)

ServiceRecord = QidOthersRecord

class QidOthersService(BaseQidService):
    """Service class for managing QID records."""

    def __init__(self) -> None:
        super().__init__(QidOthersRecord)

__all__ = [
    "QidOthersService",
]
