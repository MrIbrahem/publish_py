"""
Metrics domain models - SQLAlchemy ORM.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String

from ..shared.engine import BaseDb


class AssessmentRecord(BaseDb):
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), unique=True, nullable=False)
    importance = Column(String(120), nullable=True)


class RefsCountRecord(BaseDb):
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

    r_id = Column(Integer, primary_key=True, autoincrement=True)
    r_title = Column(String(120), unique=True, nullable=False)
    r_lead_refs = Column(Integer, nullable=True)
    r_all_refs = Column(Integer, nullable=True)


class WordRecord(BaseDb):
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

    w_id = Column(Integer, primary_key=True, autoincrement=True)
    w_title = Column(String(120), unique=True, nullable=False)
    w_lead_words = Column(Integer, nullable=True)
    w_all_words = Column(Integer, nullable=True)


__all__ = [
    "AssessmentRecord",
    "RefsCountRecord",
    "WordRecord",
]
