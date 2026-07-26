from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT")
PKT = TypeVar("PKT")


class CRUDService(Generic[ModelT, PKT]):
    """
    Generic CRUD service wrapping a single SQLAlchemy model.

    Subclass and set `model` to the mapped class. The generic parameters
    let type checkers know exactly what type `get`, `create`, etc. return:

        class UserService(CRUDService[User, int]):
            model = User
    """

    model: Type[ModelT]

    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        if self._session is not None:
            return self._session
        # Support mocking of db in subclass module namespaces during tests
        import sys
        module_name = self.__class__.__module__
        if module_name in sys.modules:
            mod = sys.modules[module_name]
            if hasattr(mod, "db"):
                return getattr(mod, "db").session
        from ...extensions import db
        return db.session

    def _base_select(self):
        """Return the base SELECT statement for the model."""
        return select(self.model)

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #

    def get(self, pk: PKT) -> ModelT | None:
        """Fetch a single row by primary key, or None if it doesn't exist."""
        return self.session.get(self.model, pk)

    def get_by(self, **filters: Any) -> ModelT | None:
        """Fetch a single row matching the given column=value filters."""
        stmt = self._base_select().filter_by(**filters)
        return self.session.execute(stmt).scalars().first()

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        order_by: Iterable[Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ModelT]:
        """
        Fetch multiple rows.

        `filters` is a simple column=value equality mapping. For anything
        more complex (OR, LIKE, joins, etc.), build your own `Select` and
        pass it to `list_by_statement` instead.
        """
        stmt = self._base_select()
        if filters:
            stmt = stmt.filter_by(**filters)
        if order_by:
            if isinstance(order_by, str) or not isinstance(order_by, Iterable):
                order_by = [order_by]
            stmt = stmt.order_by(*order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        return self.session.execute(stmt).scalars().all()

    def count(self, *, filters: dict[str, Any] | None = None) -> int:
        """Return the count of rows matching the filters."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        return self.session.execute(stmt).scalar_one()

    # ------------------------------------------------------------------ #
    # Write
    # ------------------------------------------------------------------ #

    def create(self, **kwargs: Any) -> ModelT:
        """Create a new record."""
        obj = self.model(**kwargs)
        self.session.add(obj)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(obj)
        return obj

    def update(self, pk: PKT, **kwargs: Any) -> ModelT:
        """Update an existing record by primary key."""
        obj = self.get(pk)
        if not obj:
            raise ValueError(f"{self.model.__name__} record with PK {pk} not found")
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(obj)
        return obj

    def upsert(self, keys: dict[str, Any], **kwargs: Any) -> ModelT:
        """Add or update a record matching keys."""
        obj = self.get_by(**keys)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
        else:
            obj = self.model(**keys, **kwargs)
            self.session.add(obj)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(obj)
        return obj

    def delete(self, pk: PKT) -> bool:
        """Delete a record by primary key."""
        obj = self.get(pk)
        if not obj:
            return False
        self.session.delete(obj)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return True
