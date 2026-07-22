"""
Admin routes for the ``qids_others`` table.

Same shape as ``qids.py`` but targets ``qids_others``.
"""

from __future__ import annotations

import logging

from flask import Blueprint

from ....db.services.wikidata import qid_others_service
from .qids_model import QidsModel

logger = logging.getLogger(__name__)


class QidsOthersRoutes(QidsModel):
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        super().__init__(
            endpoint="qids_others",
            bp=bp,
            title_label="Qids Others",
            service=qid_others_service,
        )


__all__ = [
    "QidsOthersRoutes",
]
