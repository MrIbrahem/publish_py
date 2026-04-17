from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _RefsCountRecord(BaseDb):
    __tablename__ = "refs_counts"

    r_id = Column(Integer, primary_key=True, autoincrement=True)
    r_title = Column(String(120), unique=True, nullable=False)
    r_lead_refs = Column(Integer, nullable=True)
    r_all_refs = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "r_id": self.r_id,
            "r_title": self.r_title,
            "r_lead_refs": self.r_lead_refs,
            "r_all_refs": self.r_all_refs,
        }


@dataclass
class RefsCountRecord:
    """Representation of a refs_counts record."""

    r_id: int
    r_title: str
    r_lead_refs: int | None = None
    r_all_refs: int | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "r_id": self.r_id,
            "r_title": self.r_title,
            "r_lead_refs": self.r_lead_refs,
            "r_all_refs": self.r_all_refs,
        }


__all__ = ["RefsCountRecord"]
