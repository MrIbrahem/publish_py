"""
Flask extensions initialization.

This module centralizes Flask extensions to prevent circular imports
and enable proper initialization order with the application factory pattern.

IMPORT RULE: Always import extensions from this module.
Never instantiate extensions elsewhere.

Usage:
    from main_app.shared.core.extensions import db, migrate, csrf
"""

from __future__ import annotations

from flask_migrate import Migrate

from ._csrf import (
    csrf,
    csrf_exempt,
    csrf_init_app,
)
from .data_base import (
    LONGTEXT,
    Base,
    db,
    metadata,
)
from .exc import UniqueError

# Flask-Migrate instance (Alembic integration)
migrate = Migrate()


__all__ = [
    "db",
    "metadata",
    "LONGTEXT",
    "Base",
    "migrate",
    "csrf",
    "csrf_init_app",
    "csrf_exempt",
    "UniqueError",
]
