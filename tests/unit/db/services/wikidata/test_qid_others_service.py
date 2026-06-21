"""Unit tests for the ``qid_others_service`` admin helpers.

Covers the new functions exposed for the admin/qids_others blueprint:
- ``list_records(dis=)``  -> all / empty / duplicate filters
- ``get_by_qid``
- ``get_by_title``
- ``insert``
- ``update``
"""

from unittest.mock import MagicMock, patch

import pytest

from src.main_app.db.models import QidOthersRecord
from src.main_app.db.services.wikidata.qid_others_service import (
    add_qid_other,
    get_by_qid,
    get_by_title,
    insert,
    list_records,
    update,
)
from src.main_app.shared.core.extensions import db as _db

pytestmark = pytest.mark.unit


def _add_with_empty_qid(title: str) -> QidOthersRecord:
    """Insert a row whose qid column is empty (model __init__ rejects ``""``)."""
    record = add_qid_other(title, "Q999")
    record.qid = ""
    _db.session.commit()
    return record


class TestListQidsOthersByDis:
    """Tests for the ``dis`` filter on list_records."""

    def test_dis_all_returns_every_row(self, monkeypatch):
        add_qid_other("A", "Q1")
        add_qid_other("B", "Q2")
        rows = list_records(dis="all")
        assert {r.title for r in rows} >= {"A", "B"}

    def test_dis_empty_returns_only_rows_with_empty_or_null_qid(self, monkeypatch):
        add_qid_other("Has_qid", "Q1")
        _add_with_empty_qid("Missing_qid")
        rows = list_records(dis="empty")
        assert {r.title for r in rows} == {"Missing_qid"}

    def test_dis_duplicate_returns_rows_sharing_qid(self, monkeypatch):
        # Title is UNIQUE, qid is not -> two rows sharing the same qid get
        # surfaced by the duplicate filter.
        add_qid_other("First", "Q42")
        add_qid_other("Second", "Q42")
        add_qid_other("Solo", "Q43")
        titles = {r.title for r in list_records(dis="duplicate")}
        assert "First" in titles
        assert "Second" in titles
        assert "Solo" not in titles

    def test_dis_default_is_all(self, monkeypatch):
        add_qid_other("Anything", "Q1")
        assert len(list_records()) == 1


class TestGetByQid:
    def test_returns_record_when_qid_exists(self, monkeypatch):
        add_qid_other("Some_title", "Q100")
        record = get_by_qid("Q100")
        assert record is not None
        assert record.title == "Some_title"

    def test_returns_none_when_qid_missing(self, monkeypatch):
        assert get_by_qid("Q9999") is None

    def test_returns_none_when_qid_is_empty_string(self, monkeypatch):
        assert get_by_qid("") is None


class TestGetByTitle:
    def test_returns_record_when_title_exists(self, monkeypatch):
        add_qid_other("Findable", "Q200")
        record = get_by_title("Findable")
        assert record is not None
        assert record.qid == "Q200"

    def test_returns_none_when_title_missing(self, monkeypatch):
        assert get_by_title("Ghost") is None

    def test_returns_none_when_title_is_empty_string(self, monkeypatch):
        assert get_by_title("") is None


class TestInsert:
    def test_inserts_new_row(self, monkeypatch):
        ok = insert("Brand_new", "Q300")
        assert ok is True
        rows = list_records()
        assert any(r.title == "Brand_new" and r.qid == "Q300" for r in rows)

    def test_fills_empty_qid_for_existing_title(self, monkeypatch):
        record = _add_with_empty_qid("Will_be_filled")
        ok = insert("Will_be_filled", "Q301")
        assert ok is True
        _db.session.refresh(record)
        assert record.qid == "Q301"

    def test_does_not_overwrite_existing_non_empty_qid(self, monkeypatch):
        record = add_qid_other("Already_set", "Q302")
        ok = insert("Already_set", "Q303")
        assert ok is True
        _db.session.refresh(record)
        assert record.qid == "Q302"

    def test_returns_false_when_title_or_qid_blank(self, monkeypatch):
        assert insert("", "Q1") is False
        assert insert("X", "") is False
        assert insert("   ", "Q1") is False

    def test_returns_false_and_rolls_back_on_db_error(self, monkeypatch):
        with patch("src.main_app.db.services.wikidata.qid_others_service.db.session") as mock_session:
            mock_session.query.return_value.filter.return_value.first.return_value = None
            mock_session.commit.side_effect = Exception("boom")
            ok = insert("Will_fail", "Q1")
            assert ok is False
            mock_session.rollback.assert_called_once()


class TestUpdate:
    def test_updates_existing_row(self, monkeypatch):
        record = add_qid_other("Old_title", "Q400")
        ok = update(record.id, "New_title", "Q401")
        assert ok is True
        _db.session.refresh(record)
        assert record.title == "New_title"
        assert record.qid == "Q401"

    def test_returns_false_when_id_missing(self, monkeypatch):
        assert update(0, "T", "Q1") is False
        assert update(99999, "T", "Q1") is False

    def test_returns_false_when_title_or_qid_blank(self, monkeypatch):
        record = add_qid_other("Solid", "Q500")
        assert update(record.id, "", "Q1") is False
        assert update(record.id, "T", "") is False

    def test_returns_false_and_rolls_back_on_db_error(self, monkeypatch):
        with patch("src.main_app.db.services.wikidata.qid_others_service.db.session") as mock_session:
            mock_session.commit.side_effect = Exception("boom")
            mock_session.get.return_value = MagicMock()
            ok = update(1, "T", "Q1")
            assert ok is False
            mock_session.rollback.assert_called_once()
