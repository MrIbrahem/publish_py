import pytest

from src.main_app.database.exceptions import RecordNotFoundError
from src.main_app.database.models import RefsCountRecord
from src.main_app.database.services.analytics.refs_count_service import RefsCountService


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = RefsCountService()


class TestRefsCountService(TestSetup):
    """Tests for RefsCountService class."""

    def test_refs_count_workflow(self):
        # Test add
        r = self.service.add_refs_count("Aspirin", 15, 120)
        assert r.r_title == "Aspirin"
        assert r.r_lead_refs == 15

        # Test get
        r2 = self.service.get_refs_count(r.r_id)
        assert r2 is not None
        assert r2.r_title == "Aspirin"

        # Test get by title
        r3 = self.service.get_refs_count_by_title("Aspirin")
        assert r3 is not None
        assert r3.r_id == r.r_id

        # Test get_ref_counts_for_title
        lead, all_refs = self.service.get_ref_counts_for_title("Aspirin")
        assert lead == 15
        assert all_refs == 120

        # Test list
        all_r = self.service.list_refs_counts()
        assert any(x.r_title == "Aspirin" for x in all_r)

        # Test update
        updated = self.service.update_refs_count(r.r_id, r_lead_refs=20)
        assert updated.r_lead_refs == 20

        # Test add_or_update
        r4 = self.service.add_or_update_refs_count("Aspirin", 25, 150)
        assert r4.r_lead_refs == 25

        # Test delete
        deleted = self.service.delete(r.r_id)
        assert deleted is True
        assert self.service.get_refs_count(r.r_id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.add_refs_count("Paracetamol")
        self.service.add_refs_count("Ibuprofen")
        result = self.service.list_refs_counts()
        assert len(result) >= 2


class TestGetRefsCount(TestSetup):
    """Tests for get_refs_count method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        r = self.service.add_refs_count("Insulin")
        result = self.service.get_refs_count(r.r_id)
        assert isinstance(result, RefsCountRecord)
        assert result.r_title == "Insulin"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_refs_count(9999) is None


class TestGetRefsCountByTitle(TestSetup):
    """Tests for get_refs_count_by_title method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by title."""
        self.service.add_refs_count("Penicillin")
        result = self.service.get_refs_count_by_title("Penicillin")
        assert result is not None
        assert result.r_title == "Penicillin"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_refs_count_by_title("Ghost") is None


class TestAddRefsCount(TestSetup):
    """Tests for add_refs_count method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_refs_count("Morphine", 10, 80)
        assert record.r_title == "Morphine"
        assert record.r_lead_refs == 10
        assert record.r_all_refs == 80

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_refs_count("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_refs_count("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_refs_count("")


class TestAddOrUpdateRefsCount(TestSetup):
    """Tests for add_or_update_refs_count method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method upserts record."""
        self.service.add_refs_count("Dopamine", 5, 40)
        record = self.service.add_or_update_refs_count("Dopamine", 8, 50)
        assert record.r_lead_refs == 8
        assert record.r_all_refs == 50
        assert len(self.service.list_refs_counts()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_or_update_refs_count(" ")


class TestUpdateRefsCount(TestSetup):
    """Tests for update_refs_count method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns record."""
        r = self.service.add_refs_count("Adrenaline", 2, 20)
        updated = self.service.update_refs_count(r.r_id, r_lead_refs=5)
        assert updated.r_lead_refs == 5

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        r = self.service.add_refs_count("No_Change")
        result = self.service.update_refs_count(r.r_id)
        assert result.r_title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_refs_count(9999, r_lead_refs=10)


class TestDeleteRefsCount(TestSetup):
    """Tests for delete_refs_count method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        r = self.service.add_refs_count("Diazepam")
        deleted = self.service.delete(r.r_id)
        assert deleted is True
        assert self.service.get_refs_count(r.r_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestGetRefsCountsForTitle(TestSetup):
    """Tests for get_ref_counts_for_title method."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that method returns counts when record found."""
        self.service.add_refs_count("Caffeine", 30, 200)
        lead, all_refs = self.service.get_ref_counts_for_title("Caffeine")
        assert lead == 30
        assert all_refs == 200

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that method returns None when record not found."""
        lead, all_refs = self.service.get_ref_counts_for_title("Ghost_Article")
        assert lead is None
        assert all_refs is None
