"""
shared/
└── domain/
    ├── db/
    ├── models/
    └── services/
"""

from .db_ensure_tables import ensure_db_tables

__all__ = [
    "ensure_db_tables",
]
