from __future__ import annotations

from typing import Any

from sqlalchemy import Column, Date, Integer, String, text

from ....shared.sqlalchemy_db.engine import BaseDb


class _UserRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id int NOT NULL AUTO_INCREMENT,
        username varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        email varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        wiki varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        user_group varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Uncategorized',
        reg_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id)
    )
    """

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, default="")
    wiki = Column(String(255), nullable=False, default="")
    user_group = Column(String(120), nullable=False, default="Uncategorized")
    reg_date = Column(Date, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "wiki": self.wiki,
            "user_group": self.user_group,
            "reg_date": self.reg_date,
        }


__all__ = ["_UserRecord"]
