from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, ForeignKey, Integer, String

from ....shared.sqlalchemy_db.engine import BaseDb


class _PagesUsersToMainRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS pages_users_to_main (
        id int unsigned NOT NULL,
        new_target varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        new_user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        new_qid varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        KEY id (id),
        CONSTRAINT pages_users_to_main_ibfk_1 FOREIGN KEY (id) REFERENCES pages_users (id)
    )
    """

    __tablename__ = "pages_users_to_main"

    id = Column(Integer, ForeignKey("pages_users.id"), primary_key=True)
    new_target = Column(String(255), nullable=False, default="")
    new_user = Column(String(255), nullable=False, default="")
    new_qid = Column(String(255), nullable=False, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "new_target": self.new_target,
            "new_user": self.new_user,
            "new_qid": self.new_qid,
        }


@dataclass
class PagesUsersToMainRecord:
    """Representation of a pages_users_to_main record."""

    id: int
    new_target: str = ""
    new_user: str = ""
    new_qid: str = ""

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "new_target": self.new_target,
            "new_user": self.new_user,
            "new_qid": self.new_qid,
        }


__all__ = ["PagesUsersToMainRecord"]
