from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProjectRecord:
    """Representation of a project record."""

    g_id: int
    g_title: str

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "g_id": self.g_id,
            "g_title": self.g_title,
        }


__all__ = ["ProjectRecord"]
