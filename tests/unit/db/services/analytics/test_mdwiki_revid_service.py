import pytest

from src.main_app.db.services.analytics.mdwiki_revid_service import MdwikiRevidService


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = MdwikiRevidService()


class TestMdwikiRevidService(TestSetup):
    """Tests for MdwikiRevidService class."""

    def test_mdwiki_revid_workflow(self):
        # Test add
        r = self.service.add_mdwiki_revid("Cell biology", 1234567)
        assert r.title == "Cell biology"
        assert r.revid == 1234567

        # Test get by title
        r2 = self.service.get_mdwiki_revid_by_title("Cell biology")
        assert r2 is not None
        assert r2.revid == 1234567

        # Test get_revid_for_title
        revid = self.service.get_revid_for_title("Cell biology")
        assert revid == 1234567

        # Test list
        all_r = self.service.list_mdwiki_revids()
        assert any(x.title == "Cell biology" for x in all_r)

        # Test update
        updated = self.service.update_mdwiki_revid("Cell biology", 7654321)
        assert updated is not None
        assert updated.revid == 7654321

        # Test add_or_update
        r3 = self.service.add_or_update_mdwiki_revid("Cell biology", 9999999)
        assert r3 is not None
        assert r3.revid == 9999999

        # Test delete
        MdwikiRevidService().delete("Cell biology")
        assert self.service.get_mdwiki_revid_by_title("Cell biology") is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        self.service.add_mdwiki_revid("Vaccine", 1010101)
        self.service.add_mdwiki_revid("Antibiotics", 2020202)
        result = self.service.list_mdwiki_revids()
        assert len(result) >= 2


class TestGetMdwikiRevidByTitle(TestSetup):
    """Tests for get_mdwiki_revid_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        self.service.add_mdwiki_revid("Aspirin", 3030303)
        result = self.service.get_mdwiki_revid_by_title("Aspirin")
        assert result is not None
        assert result.revid == 3030303

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_mdwiki_revid_by_title("Ghost") is None


class TestAddMdwikiRevid(TestSetup):
    """Tests for add_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = self.service.add_mdwiki_revid("Penicillin", 4040404)
        assert record.title == "Penicillin"
        assert record.revid == 4040404

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_mdwiki_revid("Duplicate", 1)
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_mdwiki_revid("Duplicate", 2)

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_mdwiki_revid("", 123)


class TestAddOrUpdateMdwikiRevid(TestSetup):
    """Tests for add_or_update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        self.service.add_mdwiki_revid("Insulin", 5050505)
        record = self.service.add_or_update_mdwiki_revid("Insulin", 6060606)
        assert record is not None
        assert record.revid == 6060606
        assert len(self.service.list_mdwiki_revids()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_or_update_mdwiki_revid(" ", 123)


class TestUpdateMdwikiRevid(TestSetup):
    """Tests for update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        self.service.add_mdwiki_revid("Paracetamol", 7070707)
        updated = self.service.update_mdwiki_revid("Paracetamol", 8080808)
        assert updated is not None
        assert updated.revid == 8080808

    def test_raises_error_if_not_found(self, monkeypatch):
        from src.main_app.db.exceptions import RecordNotFoundError

        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_mdwiki_revid("Ghost", 123)


class TestDeleteMdwikiRevid(TestSetup):
    """Tests for delete_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        self.service.add_mdwiki_revid("Ibuprofen", 9090909)
        MdwikiRevidService().delete("Ibuprofen")
        assert self.service.get_mdwiki_revid_by_title("Ibuprofen") is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert MdwikiRevidService().delete("Ghost") is False


class TestGetRevidForTitle(TestSetup):
    """Tests for get_revid_for_title function."""

    def test_returns_revid_when_record_exists(self, monkeypatch):
        """Test that function returns revid when record found."""
        self.service.add_mdwiki_revid("Morphine", 1112223)
        assert self.service.get_revid_for_title("Morphine") == 1112223

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
        assert self.service.get_revid_for_title("Ghost_Article") is None
