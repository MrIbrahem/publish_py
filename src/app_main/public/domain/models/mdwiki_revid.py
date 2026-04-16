from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MdwikiRevidRecord:
    """Representation of an mdwiki_revids record."""

    title: str
    revid: int

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "title": self.title,
            "revid": self.revid,
        }


__all__ = ["MdwikiRevidRecord"]
