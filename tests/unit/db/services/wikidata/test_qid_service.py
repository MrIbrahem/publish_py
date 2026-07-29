"""
Unit tests for the ``qid_service`` admin helpers.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.main_app.db.models import QidRecord
from src.main_app.db.services.wikidata.qid_service import (
    QidService,
)

pytestmark = pytest.mark.unit

ServiceRecord = QidRecord


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self, sqlite_db):
        self.service = QidService()
        self.sqlite_db = sqlite_db

    def _add_with_empty_qid(self, title: str) -> ServiceRecord:
        """
        Insert a row with an empty qid column (model __init__ rejects ``""``).
        """
        record = self.service.add_or_update(title, "Q999")
        assert record is not None

        record.qid = ""
        self.sqlite_db.session.commit()
        return record  # type: ignore


class TestQidAndQidOthersService(TestSetup):
    """Tests for `QidService/QidOthersService` class."""

    def test_qid_workflow(self):
        # Test add
        q = self.service.add_or_update("Earth", "Q2")
        assert q is not None
        assert q.title == "Earth"
        assert q.qid == "Q2"

        # Test get
        q2 = self.service.get_by_title("Earth")
        assert q2 is not None
        assert q2.qid == "Q2"

        # Test list
        all_q = self.service.list_records()
        assert any(x.title == "Earth" for x in all_q)

        # Test mapping
        mapping = self.service.get_title_to_qid()
        assert mapping["Earth"] == "Q2"

        updated = self.service.update_qid(q.id, "World", "Q2")
        assert updated is not None
        assert updated.title == "World"

        # Test delete
        self.service.delete(q.id)
        assert self.service.get_by_title("World") is None

    def test_get_by_qid_returns_none_when_qid_missing(self):
        assert self.service.get_by_qid("Q9999") is None


class TestGetPageQid(TestSetup):
    """Tests for get_by_title function."""

    def test_returns_qid_record(self):
        """Test that function returns a ServiceRecord."""
        self.service.add_or_update("Mars", "Q111")
        result = self.service.get_by_title("Mars")
        assert isinstance(result, ServiceRecord)
        assert result.qid == "Q111"

    def test_returns_none_when_not_found(self):
        """Test that function returns None when QID not found."""
        result = self.service.get_by_title("Nonexistent Planet")
        assert result is None


class TestAddQid(TestSetup):
    """Tests for add_or_update function."""

    def test_adds_qid_and_returns_record(self):
        """Test that self.service.add_or_update adds a QID and returns the record."""
        record = self.service.add_or_update("Jupiter", "Q121")
        assert record is not None
        assert record.title == "Jupiter"
        assert record.qid == "Q121"

    def test_updates_existing_qid(self):
        self.service.add_or_update("Venus", "Q1")

        updated = self.service.add_or_update("Venus", "Q2")
        assert updated is not None

        assert updated.qid == "Q2"


class TestUpdateQid(TestSetup):
    """Tests for update_qid function."""

    def test_updates_qid_and_returns_record(self):
        """Test that self.service.update_qid updates and returns the record."""
        q = self.service.add_or_update("Saturn", "Q193")
        assert q is not None

        updated = self.service.update_qid(q.id, "Saturnian System", "Q193")
        assert updated is not None

        assert updated.title == "Saturnian System"
        assert updated.qid == "Q193"


class TestDeleteQid(TestSetup):
    """Tests for delete function."""

    def test_deletes_qid(self):
        """Test that self.service.delete calls store delete."""
        q = self.service.add_or_update("Uranus", "Q324")
        assert q is not None

        self.service.delete(q.id)
        assert not any(x.id == q.id for x in self.service.list_records())

    def test_raises_error_if_not_found(self):
        assert self.service.delete(9999) is False


class TestListQids(TestSetup):
    """Tests for list_records function."""

    def test_returns_list_of_records(self):
        """Test that self.service.list_records returns all records."""
        self.service.add_or_update("Neptune", "Q332")
        self.service.add_or_update("Pluto", "Q339")
        result = self.service.list_records()
        assert len(result) >= 2

    def test_returns_empty_list_when_no_records(self):
        """Test that self.service.list_records returns empty list when no records exist."""
        result = self.service.list_records()
        assert result == []


class TestGetTitleToQid(TestSetup):
    """Tests for get_title_to_qid function."""

    def test_returns_title_to_qid_mapping(self):
        """Test that self.service.get_title_to_qid returns correct mapping."""
        self.service.add_or_update("Sun", "Q525")
        self.service.add_or_update("Moon", "Q405")
        mapping = self.service.get_title_to_qid()
        assert mapping["Sun"] == "Q525"
        assert mapping["Moon"] == "Q405"

    def test_handles_empty_qid(self):
        """Test that self.service.get_title_to_qid handles empty QID values."""


# ---------------------------------------------------------------------------
# Tests for new service functions added with admin/qids work:
#   - self.service.list_records(dis=)  (empty / duplicate filters)
#   - self.service.get_by_qid(qid)
#   - self.service.get_by_title(title)
#   - self.service.insert(title, qid)
# ---------------------------------------------------------------------------


class TestListQidsByDis(TestSetup):
    """
    Tests for the ``dis`` filter on list_records.
    """

    def test_dis_all_returns_every_row(self):
        self.service.add_or_update("A", "Q1")
        self.service.add_or_update("B", "Q2")
        rows = self.service.list_records(dis="all")
        titles = {r.title for r in rows}
        assert {"A", "B"}.issubset(titles)

    def test_dis_empty_returns_only_rows_with_empty_or_null_qid(self):
        self.service.add_or_update("Has_qid", "Q1")
        self._add_with_empty_qid("Missing_qid")
        rows = self.service.list_records(dis="empty")
        titles = {r.title for r in rows}
        assert titles == {"Missing_qid"}

    def test_dis_duplicate_returns_rows_sharing_qid(self):
        # Title is UNIQUE, qid is not -> two rows sharing the same qid get
        # surfaced by the duplicate filter.
        self.service.add_or_update("First_title", "Q42")
        self.service.add_or_update("Second_title", "Q42")
        self.service.add_or_update("Solo_title", "Q43")
        rows = self.service.list_records(dis="duplicate")
        titles = {r.title for r in rows}
        assert "First_title" in titles
        assert "Second_title" in titles
        assert "Solo_title" not in titles

    def test_dis_default_is_all(self):
        self.service.add_or_update("Anything", "Q1")
        assert len(self.service.list_records()) == 1


class TestGetByQid(TestSetup):
    """Tests for get_by_qid."""

    def test_returns_record_when_qid_exists(self):
        self.service.add_or_update("Some_title", "Q100")
        record = self.service.get_by_qid("Q100")
        assert record is not None
        assert record.title == "Some_title"

    def test_returns_none_when_qid_missing(self):
        assert self.service.get_by_qid("Q9999") is None

    def test_returns_none_when_qid_is_empty_string(self):
        assert self.service.get_by_qid("") is None


class TestGetByTitle(TestSetup):
    """Tests for get_by_title."""

    def test_returns_record_when_title_exists(self):
        self.service.add_or_update("Findable", "Q200")
        record = self.service.get_by_title("Findable")
        assert record is not None
        assert record.qid == "Q200"

    def test_returns_none_when_title_missing(self):
        assert self.service.get_by_title("Ghost") is None

    def test_returns_none_when_title_is_empty_string(self):
        assert self.service.get_by_title("") is None


class TestInsert(TestSetup):
    """Tests for the insert helper used by the admin/qids POST handler."""

    def test_inserts_new_row(self):
        ok = self.service.insert("Brand_new", "Q300")
        assert ok is True
        rows = self.service.list_records()
        assert any(r.title == "Brand_new" and r.qid == "Q300" for r in rows)

    def test_fills_empty_qid_for_existing_title(self, sqlite_db):
        # Mirrors PHP "fill empty qid" follow-up after the INSERT-WHERE-NOT-EXISTS.
        record = self._add_with_empty_qid("Will_be_filled")
        ok = self.service.insert("Will_be_filled", "Q301")
        assert ok is True
        sqlite_db.session.refresh(record)
        assert record.qid == "Q301"

    def test_does_not_overwrite_existing_non_empty_qid(self, sqlite_db):
        record = self.service.add_or_update("Already_set", "Q302")
        assert record is not None

        ok = self.service.insert("Already_set", "Q303")
        assert ok is True
        sqlite_db.session.refresh(record)
        assert record.qid == "Q302"  # not overwritten

    def test_returns_false_when_title_or_qid_blank(self):
        assert self.service.insert("", "Q1") is False
        assert self.service.insert("X", "") is False
        assert self.service.insert("   ", "Q1") is False

    def test_insert_returns_false(self):
        ok = self.service.insert("Will_fail", "")
        assert ok is False
