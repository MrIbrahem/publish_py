"""
Admin routes for the ``qids`` table.

Same shape as ``qids_others.py`` but targets ``qids``.
"""

from __future__ import annotations

import logging


from ....database.services import QidService
from .qids_model import QidsSharedModel

logger = logging.getLogger(__name__)


class QidsRoutes(QidsSharedModel):
    def __init__(self) -> None:
        super().__init__(
            endpoint="qids",
            title_label="TD Qids",
            service=QidService(),
        )


__all__ = [
    "QidsRoutes",
]
