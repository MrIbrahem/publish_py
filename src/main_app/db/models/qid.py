"""
QID domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import db


class QidRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS qids (
        id int unsigned NOT NULL AUTO_INCREMENT,
        qid varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY title (title),
        KEY qid (qid)
    )
    """

    __tablename__ = "qids"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    qid: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        # Validate that required fields are not empty
        if not self.title:
            raise ValueError("Title cannot be empty")

        if not self.qid:
            raise ValueError("QID cannot be empty")

        # Validate QID format (should start with Q followed by digits)
        if not self.qid.startswith("Q") or not self.qid[1:].isdigit():
            raise ValueError(f"Invalid QID format: {self.qid}. QID should start with 'Q' followed by digits.")


class QidOthersRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS qids_others (
        id int unsigned NOT NULL AUTO_INCREMENT,
        qid varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY title (title),
        KEY qid (qid)
    )
    """

    __tablename__ = "qids_others"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    qid: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.validate()

    def validate(self):
        # Validate that required fields are not empty
        if not self.title:
            raise ValueError("Title cannot be empty")

        if not self.qid:
            raise ValueError("QID cannot be empty")

        # Validate QID format (should start with Q followed by digits)
        if not self.qid.startswith("Q") or not self.qid[1:].isdigit():
            raise ValueError(f"Invalid QID format: {self.qid}. QID should start with 'Q' followed by digits.")


class AllQidsExistRecord(db.Model):
    """
    CREATE TABLE all_qids_exists (
        id int NOT NULL AUTO_INCREMENT,
        qid varchar(255) NOT NULL,
        code varchar(25) NOT NULL,
        target varchar(255) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY qid_code (qid, code),
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
    """

    __tablename__ = "all_qids_exists"
    __table_args__ = (UniqueConstraint("qid", "code", name="qid_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    qid: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(25), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)


__all__ = [
    "QidRecord",
    "AllQidsExistRecord",
]
