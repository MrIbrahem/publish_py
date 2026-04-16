"""
Unit tests for db.db_qids module.

Tests for Qids database operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from src.app_main.config import DbConfig
from src.app_main.shared.domain.db.db_qids import (
    QidsDB,
)


@pytest.fixture
def db_config():
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="test_db",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


class TestQidsDB:
    """Tests for QidsDB class."""

    def test_fetch_by_title_returns_qid_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns QID when title exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"qid": "Q12345"}]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_title("TestArticle")

        assert result == "Q12345"
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT qid FROM qids WHERE title = %s",
            ("TestArticle",),
        )

    def test_fetch_by_title_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns None when title not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_title("MissingArticle")

        assert result is None

    def test_fetch_by_title_returns_none_when_row_has_no_qid(self, monkeypatch, db_config):
        """Test handling when row exists but has no qid field."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"other_field": "value"}]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_title("TestArticle")

        assert result is None

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new QID record."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        qids_db.add("TestArticle", "Q12345")

        mock_db.execute_query_safe.assert_called_with(
            """
            INSERT INTO qids (title, qid)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                qid = VALUES(qid)
            """,
            ("TestArticle", "Q12345"),
        )

    def test_add_updates_existing_record(self, monkeypatch, db_config):
        """Test that add updates existing record via ON DUPLICATE KEY."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        qids_db.add("ExistingArticle", "Q99999")

        # Should use upsert pattern
        call_args = mock_db.execute_query_safe.call_args
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
