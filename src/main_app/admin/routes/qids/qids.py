"""
Admin routes for the ``qids`` table.

Same shape as ``qids_others.py`` but targets ``qids``.
"""

from __future__ import annotations

import logging

from flask import Blueprint

from ....db.services.wikidata import QidService
from .qids_model import QidsModel

logger = logging.getLogger(__name__)


class QidsRoutes(QidsModel):
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        super().__init__(
            endpoint="qids",
            bp=bp,
            title_label="TD Qids",
            service=QidService(),
        )


__all__ = [
    "QidsRoutes",
]
