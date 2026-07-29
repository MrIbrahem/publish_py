"""
SQLAlchemy-based service for managing pages_users_to_main.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import PagesUsersToMainRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class PagesUsersToMainService(CRUDService[PagesUsersToMainRecord]):
    model = PagesUsersToMainRecord

    def __init__(self):
        super().__init__(db.session, PagesUsersToMainRecord)

    def list_pages_users_to_main(self) -> list[PagesUsersToMainRecord]:
        """Return all pages_users_to_main records."""
        return list(
            self.list(
                order_by=[PagesUsersToMainRecord.id.asc()],
            )
        )

    def get_pages_users_to_main(self, record_id: int) -> PagesUsersToMainRecord | None:
        """Get a pages_users_to_main record by ID."""
        orm_obj = self.get(record_id)
        if not orm_obj:
            logger.warning(f"PagesUsersToMain record with ID {record_id} not found")
            return None
        return orm_obj

    def add_pages_users_to_main(
        self,
        id: int | None = None,
        new_target: str = "",
        new_user: str = "",
        new_qid: str = "",
    ) -> PagesUsersToMainRecord:
        """Add a new pages_users_to_main record."""
        try:
            return self.create(id=id, new_target=new_target, new_user=new_user, new_qid=new_qid)
        except IntegrityError as e:
            raise ValueError(f"Failed to add pages_users_to_main record: {e}") from None

    def update_pages_users_to_main(self, record_id: int, **kwargs) -> PagesUsersToMainRecord:
        """Update a pages_users_to_main record."""
        return self.update_or_404(record_id, **kwargs)

__all__ = [
    "PagesUsersToMainService",
]
