"""
Utilities for managing qids
"""

from __future__ import annotations

import logging
from typing import List
from ....config import settings
from ..db import QidsDB
from ..models import QidRecord
from .db_service import has_db_config

logger = logging.getLogger(__name__)


def get_qids_db() -> QidsDB:
    """Get an instance of QidsDB."""
    if not has_db_config():
        raise RuntimeError("Database configuration is missing.")
    return QidsDB(settings.db_config)
