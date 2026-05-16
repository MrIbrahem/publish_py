"""
QID domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from ..shared.core.extensions import db


class QidRecord(db.Model):
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

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    qid =db.Column(db.String(20), nullable=False)
    title =db.Column(db.String(255), unique=True, nullable=False)
    add_date =db.Column(DateTime, nullable=False, server_default=func.current_timestamp())

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


class AllQidsRecord(db.Model):
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

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    qid =db.Column(db.String(255), unique=True, nullable=False)
    category =db.Column(db.String(255), nullable=True)


class AllQidsExistRecord(db.Model):
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

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    qid =db.Column(db.String(255), nullable=False)
    code =db.Column(db.String(25), nullable=False)
    target =db.Column(db.String(255), nullable=False)


__all__ = [
    "QidRecord",
    "AllQidsRecord",
    "AllQidsExistRecord",
]
