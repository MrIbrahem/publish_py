"""
Admin routes for the ``qids_others`` table.

Same shape as ``qids.py`` but targets ``qids_others``.
"""

from __future__ import annotations

import logging


from ....database.services import QidOthersService
from .qids_model import QidsSharedModel

logger = logging.getLogger(__name__)


class QidsOthersRoutes(QidsSharedModel):
    def __init__(self) -> None:
        super().__init__(
            endpoint="qids_others",
            title_label="Qids Others",
            service=QidOthersService(),
        )


__all__ = [
    "QidsOthersRoutes",
]
