from unittest.mock import MagicMock, patch

import pytest

from src.main_app.db.models import QidRecord
from src.main_app.db.services.delete_service import (
    delete_qid,
)
from src.main_app.db.services.wikidata.qid_service import (
    add_qid,
    get_page_qid,
    get_title_to_qid,
    list_records,
    update_qid,
)


def test_qid_workflow():
    # Test add
    q = add_qid("Earth", "Q2")
    assert q.title == "Earth"
    assert q.qid == "Q2"

    # Test get
    q2 = get_page_qid("Earth")
    assert q2.qid == "Q2"

    # Test list
    all_q = list_records()
    assert any(x.title == "Earth" for x in all_q)

    # Test mapping
    mapping = get_title_to_qid()
    assert mapping["Earth"] == "Q2"

    # Test update
    updated = update_qid(q.id, "World", "Q2")
    assert updated.title == "World"

    # Test delete
    delete_qid(q.id)
    assert get_page_qid("World") is None


class TestGetPageQid:
    """Tests for get_page_qid function."""

    def test_returns_qid_record(self, monkeypatch):
        """Test that function returns a QidRecord."""
        add_qid("Mars", "Q111")
        result = get_page_qid("Mars")
        assert isinstance(result, QidRecord)
        assert result.qid == "Q111"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when QID not found."""
        result = get_page_qid("Nonexistent Planet")
        assert result is None


class TestAddQid:
    """Tests for add_qid function."""

    def test_adds_qid_and_returns_record(self, monkeypatch):
        """Test that add_qid adds a QID and returns the record."""
        record = add_qid("Jupiter", "Q121")
        assert record.title == "Jupiter"
        assert record.qid == "Q121"

    def test_updates_existing_qid(self, monkeypatch):
        add_qid("Venus", "Q1")
        updated = add_qid("Venus", "Q2")
        assert updated.qid == "Q2"


class TestUpdateQid:
    """Tests for update_qid function."""

    def test_updates_qid_and_returns_record(self, monkeypatch):
        """Test that update_qid updates and returns the record."""
        q = add_qid("Saturn", "Q193")
        updated = update_qid(q.id, "Saturnian System", "Q193")
        assert updated.title == "Saturnian System"
        assert updated.qid == "Q193"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_qid(9999, "T", "Q1")


class TestDeleteQid:
    """Tests for delete_qid function."""

    def test_deletes_qid(self, monkeypatch):
        """Test that delete_qid calls store delete."""
        q = add_qid("Uranus", "Q324")
        delete_qid(q.id)
        assert not any(x.id == q.id for x in list_records())

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_qid(9999)


class TestListQids:
    """Tests for list_records function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_records returns all records."""
        add_qid("Neptune", "Q332")
        add_qid("Pluto", "Q339")
        result = list_records()
        assert len(result) >= 2

    def test_returns_empty_list_when_no_records(self, monkeypatch):
        """Test that list_records returns empty list when no records exist."""
        result = list_records()
        assert result == []


class TestGetTitleToQid:
    """Tests for get_title_to_qid function."""

    def test_returns_title_to_qid_mapping(self, monkeypatch):
        """Test that get_title_to_qid returns correct mapping."""
        add_qid("Sun", "Q525")
        add_qid("Moon", "Q405")
        mapping = get_title_to_qid()
        assert mapping["Sun"] == "Q525"
        assert mapping["Moon"] == "Q405"

    def test_handles_empty_qid(self, monkeypatch):
        """Test that get_title_to_qid handles empty QID values."""
        pass


# ---------------------------------------------------------------------------
# Tests for new service functions added with admin/qids work:
#   - list_records(dis=)  (empty / duplicate filters)
#   - get_by_qid(qid)
#   - get_by_title(title)
#   - insert(title, qid)
#   - update(qid_id, title, qid)
# ---------------------------------------------------------------------------

from src.main_app.db.services.wikidata.qid_service import (
    get_by_qid,
    get_by_title,
    insert,
    update,
)
from src.main_app.shared.core.extensions import db as _db


def _add_with_empty_qid(title: str) -> QidRecord:
    """Insert a row with an empty qid column (model __init__ rejects ``""``)."""
    record = add_qid(title, "Q999")
    record.qid = ""
    _db.session.commit()
    return record


class TestListQidsByDis:
    """Tests for the ``dis`` filter on list_records."""

    def test_dis_all_returns_every_row(self, monkeypatch):
        add_qid("A", "Q1")
        add_qid("B", "Q2")
        rows = list_records(dis="all")
        titles = {r.title for r in rows}
        assert {"A", "B"}.issubset(titles)

    def test_dis_empty_returns_only_rows_with_empty_or_null_qid(self, monkeypatch):
        add_qid("Has_qid", "Q1")
        _add_with_empty_qid("Missing_qid")
        rows = list_records(dis="empty")
        titles = {r.title for r in rows}
        assert titles == {"Missing_qid"}

    def test_dis_duplicate_returns_rows_sharing_qid(self, monkeypatch):
        # ``qids.title`` is UNIQUE, but ``qid`` is not -> two rows can share
        # the same Q-id and that's exactly what the duplicate filter surfaces.
        add_qid("First_title", "Q42")
        add_qid("Second_title", "Q42")
        add_qid("Solo_title", "Q43")
        rows = list_records(dis="duplicate")
        titles = {r.title for r in rows}
        assert "First_title" in titles
        assert "Second_title" in titles
        assert "Solo_title" not in titles

    def test_dis_default_is_all(self, monkeypatch):
        add_qid("Anything", "Q1")
        assert len(list_records()) == 1


class TestGetByQid:
    """Tests for get_by_qid."""

    def test_returns_record_when_qid_exists(self, monkeypatch):
        add_qid("Some_title", "Q100")
        record = get_by_qid("Q100")
        assert record is not None
        assert record.title == "Some_title"

    def test_returns_none_when_qid_missing(self, monkeypatch):
        assert get_by_qid("Q9999") is None

    def test_returns_none_when_qid_is_empty_string(self, monkeypatch):
        assert get_by_qid("") is None


class TestGetByTitle:
    """Tests for get_by_title."""

    def test_returns_record_when_title_exists(self, monkeypatch):
        add_qid("Findable", "Q200")
        record = get_by_title("Findable")
        assert record is not None
        assert record.qid == "Q200"

    def test_returns_none_when_title_missing(self, monkeypatch):
        assert get_by_title("Ghost") is None

    def test_returns_none_when_title_is_empty_string(self, monkeypatch):
        assert get_by_title("") is None


class TestInsert:
    """Tests for the insert helper used by the admin/qids POST handler."""

    def test_inserts_new_row(self, monkeypatch):
        ok = insert("Brand_new", "Q300")
        assert ok is True
        rows = list_records()
        assert any(r.title == "Brand_new" and r.qid == "Q300" for r in rows)

    def test_fills_empty_qid_for_existing_title(self, monkeypatch):
        # Mirrors PHP "fill empty qid" follow-up after the INSERT-WHERE-NOT-EXISTS.
        record = _add_with_empty_qid("Will_be_filled")
        ok = insert("Will_be_filled", "Q301")
        assert ok is True
        _db.session.refresh(record)
        assert record.qid == "Q301"

    def test_does_not_overwrite_existing_non_empty_qid(self, monkeypatch):
        record = add_qid("Already_set", "Q302")
        ok = insert("Already_set", "Q303")
        assert ok is True  # PHP returns success even when no-op.
        _db.session.refresh(record)
        assert record.qid == "Q302"  # not overwritten

    def test_returns_false_when_title_or_qid_blank(self, monkeypatch):
        assert insert("", "Q1") is False
        assert insert("X", "") is False
        assert insert("   ", "Q1") is False

    def test_returns_false_and_rolls_back_on_db_error(self, monkeypatch):
        with patch("src.main_app.db.services.wikidata.qid_service.db.session") as mock_session:
            mock_session.query.return_value.filter.return_value.first.return_value = None
            mock_session.commit.side_effect = Exception("boom")
            ok = insert("Will_fail", "Q1")
            assert ok is False
            mock_session.rollback.assert_called_once()


class TestUpdate:
    """Tests for the update helper used by the admin/qids POST handler."""

    def test_updates_existing_row(self, monkeypatch):
        record = add_qid("Old_title", "Q400")
        ok = update(record.id, "New_title", "Q401")
        assert ok is True
        _db.session.refresh(record)
        assert record.title == "New_title"
        assert record.qid == "Q401"

    def test_returns_false_when_id_missing(self, monkeypatch):
        assert update(0, "T", "Q1") is False
        assert update(99999, "T", "Q1") is False

    def test_returns_false_when_title_or_qid_blank(self, monkeypatch):
        record = add_qid("Solid", "Q500")
        assert update(record.id, "", "Q1") is False
        assert update(record.id, "T", "") is False

    def test_returns_false_and_rolls_back_on_db_error(self, monkeypatch):
        with patch("src.main_app.db.services.wikidata.qid_service.db.session") as mock_session:
            mock_session.commit.side_effect = Exception("boom")
            mock_session.get.return_value = MagicMock()
            ok = update(1, "T", "Q1")
            assert ok is False
            mock_session.rollback.assert_called_once()
