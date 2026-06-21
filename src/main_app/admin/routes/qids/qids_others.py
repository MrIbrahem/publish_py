"""
Admin routes for the ``qids_others`` table.

Same shape as ``qids.py`` but targets ``qids_others``.
"""

from __future__ import annotations

import logging

from ....db.services.wikidata import qid_others_service
from .qids_model import QidsModel

logger = logging.getLogger(__name__)

qids_others_module = QidsModel(
    endpoint="qids_others", url_prefix="/qids_others", title_label="Qids Others", service=qid_others_service,
)
