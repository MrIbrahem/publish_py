"""
Admin routes for the ``qids`` table.

Same shape as ``qids_others.py`` but targets ``qids``.
"""

from __future__ import annotations

import logging

from ....db.services.wikidata import qid_service
from .qids_model import QidsModel

logger = logging.getLogger(__name__)

qids_module = QidsModel(endpoint="qids", url_prefix="/qids", title_label="TD Qids", service=qid_service)
