"""
Flask extensions initialization.

This module centralizes Flask extensions to prevent circular imports
and enable proper initialization order with the application factory pattern.

IMPORT RULE: Always import extensions from this module.
Never instantiate extensions elsewhere.

Usage:
    from main_app.extensions import db, migrate, csrf
"""

from __future__ import annotations

from flask_migrate import Migrate

from ..db.exceptions import UniqueError
from ._csrf import (
    csrf,
    csrf_exempt,
    csrf_init_app,
)
from .data_base import (
    db,
    metadata,
    BaseModel,
)
from .db_types import LONGTEXT

# Flask-Migrate instance (Alembic integration)
migrate = Migrate()

__all__ = [
    "db",
    "BaseModel",
    "migrate",
    "csrf",
    "csrf_init_app",
    "UniqueError",
    "csrf_exempt",
    "metadata",
    "LONGTEXT",
]
