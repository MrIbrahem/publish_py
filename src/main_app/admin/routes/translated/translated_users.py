"""
Admin routes for translated user pages (``pages_users`` table).
"""

from __future__ import annotations

import logging

from .translated_shared_routes import SharedTranslatedView

# from ...database.services import UserPagesService

logger = logging.getLogger(__name__)


class TranslatedUsersView(SharedTranslatedView):
    """Route registrar for user pages translation management."""

    def __init__(self) -> None:
        super().__init__(
            service_name="pages_users",
            endpoint_name="translated_users",
            table_label="User",
        )


__all__ = [
    "TranslatedUsersView",
]
