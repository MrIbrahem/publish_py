"""
Admin routes for translated main pages (``pages`` table).
"""

from __future__ import annotations

import logging

from .translated_shared_routes import SharedTranslatedView

logger = logging.getLogger(__name__)


class TranslatedView(SharedTranslatedView):
    """Route registrar for main pages translation management."""

    def __init__(self) -> None:
        super().__init__(
            service_name="pages",
            endpoint_name="translated",
            table_label="Main",
        )


__all__ = [
    "TranslatedView",
]
