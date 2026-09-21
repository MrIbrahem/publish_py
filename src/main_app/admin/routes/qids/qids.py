"""
Admin routes for the ``qids`` table.

Same shape as ``qids_others.py`` but targets ``qids``.
"""

from __future__ import annotations

import logging

from ....database.services import QidService
from .qids_model import QidsSharedModelView

logger = logging.getLogger(__name__)


class QidsView(QidsSharedModelView):
    """Registrar for standard QIDs MethodView routes."""

    def __init__(self) -> None:
        super().__init__(
            endpoint="qids",
            title_label="TD Qids",
            service=QidService(),
        )


__all__ = [
    "QidsView",
]
