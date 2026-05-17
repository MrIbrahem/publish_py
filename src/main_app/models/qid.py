"""
QID domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, func

from ..shared.engine import BaseDb


class QidRecord(BaseDb):
    """
    CREATE TABLE IF NOT EXISTS qids (
        id int unsigned NOT NULL AUTO_INCREMENT,
        qid varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
        title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
        add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        UNIQUE KEY title (title),
        KEY qid (qid)
    )
    """

    __tablename__ = "qids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qid = Column(String(20), nullable=False)
    title = Column(String(255), unique=True, nullable=False)
    add_date = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Validate that required fields are not empty
        if not self.title:
            raise ValueError("Title cannot be empty")

        if not self.qid:
            raise ValueError("QID cannot be empty")

        # Validate QID format (should start with Q followed by digits)
        if not self.qid.startswith("Q") or not self.qid[1:].isdigit():
            raise ValueError(f"Invalid QID format: {self.qid}. QID should start with 'Q' followed by digits.")


class AllQidsRecord(BaseDb):
    """
    CREATE TABLE all_qids (
        qid varchar(255) NOT NULL,
        category varchar(255) DEFAULT NULL,
        id int NOT NULL AUTO_INCREMENT,
        PRIMARY KEY (id),
        UNIQUE KEY qid (qid)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
    """

    __tablename__ = "all_qids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qid = Column(String(255), unique=True, nullable=False)
    category = Column(String(255), nullable=True)


class AllQidsExistRecord(BaseDb):
    """
    CREATE TABLE all_qids_exists (
        id int NOT NULL AUTO_INCREMENT,
        qid varchar(255) NOT NULL,
        code varchar(25) NOT NULL,
        target varchar(255) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY qid_code (qid, code),
        CONSTRAINT all_qids_exists_ibfk_1 FOREIGN KEY (qid) REFERENCES all_qids (qid)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
    """

    __tablename__ = "all_qids_exists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qid = Column(String(255), nullable=False)
    code = Column(String(25), nullable=False)
    target = Column(String(255), nullable=False)


__all__ = [
    "QidRecord",
    "AllQidsRecord",
    "AllQidsExistRecord",
]
