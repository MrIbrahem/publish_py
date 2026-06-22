"""
Metrics domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ...shared.core.extensions import db


class AssessmentRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS assessments (
        id int unsigned NOT NULL AUTO_INCREMENT,
        title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        importance varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY title (title)
      )
    """

    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    importance: Mapped[str | None] = mapped_column(String(120))


class RefsCountRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS refs_counts (
        r_id int unsigned NOT NULL AUTO_INCREMENT,
        r_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        r_lead_refs int DEFAULT NULL,
        r_all_refs int DEFAULT NULL,
        PRIMARY KEY (r_id),
        UNIQUE KEY r_title (r_title)
    )
    """

    __tablename__ = "refs_counts"

    r_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    r_title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    r_lead_refs: Mapped[int | None] = mapped_column()
    r_all_refs: Mapped[int | None] = mapped_column()


class WordRecord(db.Model):
    """
    CREATE TABLE IF NOT EXISTS words (
        w_id int unsigned NOT NULL AUTO_INCREMENT,
        w_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
        w_lead_words int DEFAULT NULL,
        w_all_words int DEFAULT NULL,
        PRIMARY KEY (w_id),
        UNIQUE KEY w_title (w_title)
    )
    """

    __tablename__ = "words"

    w_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    w_title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    w_lead_words: Mapped[int | None] = mapped_column()
    w_all_words: Mapped[int | None] = mapped_column()


__all__ = [
    "AssessmentRecord",
    "RefsCountRecord",
    "WordRecord",
]
