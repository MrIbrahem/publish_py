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
from src.app_main.shared.domain.models import QidRecord


class TestQidsDB:
    """Tests for QidsDB class."""

    def test_fetch_by_title_returns_qid_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_title returns QID when title exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 5, "qid": "Q12345", "title": "TestArticle", "add_date": "2024-01-01"}
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_title("TestArticle")

        assert result.qid == "Q12345"
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT id, title, qid, add_date FROM qids WHERE title = %s",
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
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_title("TestArticle")

        assert result is None

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new QID record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "title": "TestArticle",
                "qid": "Q12345",
                "add_date": "2024-01-01 12:00:00",
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.add("TestArticle", "Q12345")

        mock_db.execute_query_safe.assert_called_with(
            """
            INSERT INTO qids (title, qid)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                qid = VALUES(qid)
            """,
            ("TestArticle", "Q12345"),
        )
        assert isinstance(result, QidRecord)
        assert result.title == "TestArticle"

    def test_add_updates_existing_record(self, monkeypatch, db_config):
        """Test that add updates existing record via ON DUPLICATE KEY."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "title": "ExistingArticle",
                "qid": "Q99999",
                "add_date": "2024-01-01 12:00:00",
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.add("ExistingArticle", "Q99999")

        # Should use upsert pattern
        call_args = mock_db.execute_query_safe.call_args
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]
        assert isinstance(result, QidRecord)
        assert result.qid == "Q99999"

    def test_fetch_by_id_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns QidRecord when ID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "title": "TestArticle",
                "qid": "Q12345",
                "add_date": "2024-01-01 12:00:00",
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_id(1)

        assert isinstance(result, QidRecord)
        assert result.id == 1
        assert result.title == "TestArticle"
        assert result.qid == "Q12345"

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when ID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_id(999)

        assert result is None

    def test_fetch_by_qid_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_qid returns QidRecord when QID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "title": "TestArticle",
                "qid": "Q12345",
                "add_date": "2024-01-01 12:00:00",
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_qid("Q12345")

        assert isinstance(result, QidRecord)
        assert result.qid == "Q12345"

    def test_fetch_by_qid_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_qid returns None when QID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.fetch_by_qid("Q99999")

        assert result is None

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all QID records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"id": 1, "title": "Article1", "qid": "Q12345", "add_date": "2024-01-01 12:00:00"},
            {"id": 2, "title": "Article2", "qid": "Q67890", "add_date": "2024-01-02 12:00:00"},
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.list()

        assert len(result) == 2
        assert all(isinstance(r, QidRecord) for r in result)
        assert result[0].title == "Article1"
        assert result[1].title == "Article2"

    def test_list_returns_empty_list_when_no_records(self, monkeypatch, db_config):
        """Test that list returns empty list when no records exist."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.list()

        assert result == []

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes a QID record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "title": "TestArticle",
                "qid": "Q12345",
                "add_date": "2024-01-01 12:00:00",
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        qids_db.delete(1)

        mock_db.execute_query_safe.assert_called_with(
            "DELETE FROM qids WHERE id = %s",
            (1,),
        )

    def test_delete_raises_error_when_record_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when record not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        with pytest.raises(ValueError, match="QID record with ID 999 not found"):
            qids_db.delete(999)

    def test_update_modifies_record(self, monkeypatch, db_config):
        """Test that update modifies a QID record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.side_effect = [
            [
                {
                    "id": 1,
                    "title": "OldArticle",
                    "qid": "Q12345",
                    "add_date": "2024-01-01 12:00:00",
                }
            ],
            [
                {
                    "id": 1,
                    "title": "UpdatedArticle",
                    "qid": "Q99999",
                    "add_date": "2024-01-01 12:00:00",
                }
            ],
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        result = qids_db.update(1, "UpdatedArticle", "Q99999")

        mock_db.execute_query_safe.assert_called_with(
            "UPDATE qids SET title = %s, qid = %s WHERE id = %s",
            ("UpdatedArticle", "Q99999", 1),
        )
        assert isinstance(result, QidRecord)
        assert result.title == "UpdatedArticle"
        assert result.qid == "Q99999"

    def test_update_raises_error_when_record_not_found(self, monkeypatch, db_config):
        """Test that update raises ValueError when record not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_qids.Database", lambda db_data: mock_db)

        qids_db = QidsDB(db_config)
        with pytest.raises(ValueError, match="QID record with ID 999 not found"):
            qids_db.update(999, "NewTitle", "Q12345")
