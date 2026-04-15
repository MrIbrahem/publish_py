"""Unit tests for db.db_qids module.

Tests for Qids database operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from src.app_main.config import DbConfig
from src.app_main.db.db_qids import (
    QidsDB,
    ensure_qids_table,
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

    def test_init_creates_database_instance(self, monkeypatch, db_config):
        """Test that initialization creates a Database instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)

        assert qids_db.db is mock_db
        # Should call execute_query_safe to ensure table
        mock_db.execute_query_safe.assert_called_once()

    def test_get_qid_by_title_returns_qid_when_found(self, monkeypatch, db_config):
        """Test that get_qid_by_title returns QID when title exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"qid": "Q12345"}]

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.get_qid_by_title("TestArticle")

        assert result == "Q12345"
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT qid FROM qids WHERE title = %s",
            ("TestArticle",),
        )

    def test_get_qid_by_title_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that get_qid_by_title returns None when title not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.get_qid_by_title("MissingArticle")

        assert result is None

    def test_get_qid_by_title_returns_none_when_row_has_no_qid(self, monkeypatch, db_config):
        """Test handling when row exists but has no qid field."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"other_field": "value"}]

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.get_qid_by_title("TestArticle")

        assert result is None

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new QID record."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        qids_db.add("TestArticle", "Q12345")

        mock_db.execute_query_safe.assert_called_with(
            """
            INSERT INTO qids (title, qid)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE qid = VALUES(qid)
            """,
            ("TestArticle", "Q12345"),
        )

    def test_add_updates_existing_record(self, monkeypatch, db_config):
        """Test that add updates existing record via ON DUPLICATE KEY."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        qids_db.add("ExistingArticle", "Q99999")

        # Should use upsert pattern
        call_args = mock_db.execute_query_safe.call_args
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]


class TestEnsureQidsTable:
    """Tests for ensure_qids_table function."""

    def test_returns_true_on_success(self, monkeypatch, db_config):
        """Test that function returns True when table creation succeeds."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        result = ensure_qids_table(db_config)

        assert result is True
        mock_db.execute_query_safe.assert_called_once()

    def test_returns_false_on_exception(self, monkeypatch, db_config):
        """Test that function returns False when an exception occurs."""
        mock_db = MagicMock()
        mock_db.execute_query_safe.side_effect = Exception("DB Error")

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        result = ensure_qids_table(db_config)

        assert result is False

    def test_logs_error_on_failure(self, monkeypatch, db_config, caplog):
        """Test that errors are logged when table creation fails."""
        import logging

        mock_db = MagicMock()
        mock_db.execute_query_safe.side_effect = Exception("DB Connection Failed")

        monkeypatch.setattr("src.app_main.db.db_qids.Database", lambda db_data: mock_db)

        with caplog.at_level(logging.ERROR):
            result = ensure_qids_table(db_config)
            assert result is False
            assert "Failed to ensure qids table" in caplog.text
