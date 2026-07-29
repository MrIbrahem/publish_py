import pytest

from src.main_app.db.exceptions import RecordNotFoundError
from src.main_app.db.models import WordRecord
from src.main_app.db.services.analytics.word_service import WordService


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = WordService()


class TestWordService(TestSetup):
    """Tests for WordService class."""

    def test_word_workflow(self):
        # Test add
        w = self.service.add_word("Human anatomy", 500, 5000)
        assert w.w_title == "Human anatomy"
        assert w.w_lead_words == 500

        # Test get
        w2 = self.service.get_word(w.w_id)
        assert w2 is not None
        assert w2.w_title == "Human anatomy"

        # Test get by title
        w3 = self.service.get_word_by_title("Human anatomy")
        assert w3 is not None
        assert w3.w_id == w.w_id

        # Test get_word_counts_for_title
        lead, all_words = self.service.get_word_counts_for_title("Human anatomy")
        assert lead == 500
        assert all_words == 5000

        # Test list
        all_w = self.service.list_words()
        assert any(x.w_title == "Human anatomy" for x in all_w)

        # Test update
        updated = self.service.update_word(w.w_id, w_lead_words=600)
        assert updated.w_lead_words == 600

        # Test add_or_update
        w4 = self.service.add_or_update_word("Human anatomy", 700, 6000)
        assert w4.w_lead_words == 700

        # Test delete
        deleted = self.service.delete(w.w_id)
        assert deleted is True
        assert self.service.get_word(w.w_id) is None

    def test_returns_list_of_words(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.add_word("Microscope")
        self.service.add_word("Stethoscope")
        result = self.service.list_words()
        assert len(result) >= 2


class TestGetWord(TestSetup):
    """Tests for get_word method."""

    def test_delegates_to_store_fetch_by_id(self, monkeypatch):
        """Test that method returns record by ID."""
        w = self.service.add_word("Cell structure")
        result = self.service.get_word(w.w_id)
        assert isinstance(result, WordRecord)
        assert result.w_title == "Cell structure"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that method returns None when word not found."""
        assert self.service.get_word(77777) is None


class TestGetWordByTitle(TestSetup):
    """Tests for get_word_by_title method."""

    def test_delegates_to_store_fetch_by_title(self, monkeypatch):
        """Test that method returns record by title."""
        self.service.add_word("DNA replication")
        result = self.service.get_word_by_title("DNA replication")
        assert result is not None
        assert result.w_title == "DNA replication"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_word_by_title("Ghost") is None


class TestAddWord(TestSetup):
    """Tests for add_word method."""

    def test_delegates_to_store_add(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_word("Protein folding", 300, 1500)
        assert record.w_title == "Protein folding"
        assert record.w_lead_words == 300

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional params are passed correctly."""
        record = self.service.add_word("T1", w_lead_words=50)
        assert record.w_lead_words == 50

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_word("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_word("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_word("")


class TestAddOrUpdateWord(TestSetup):
    """Tests for add_or_update_word method."""

    def test_delegates_to_store_add_or_update(self, monkeypatch):
        """Test that method upserts record."""
        self.service.add_word("Antibody", 100, 1000)
        record = self.service.add_or_update_word("Antibody", 150, 1200)
        assert record.w_lead_words == 150
        assert len(self.service.list_words()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_or_update_word("  ")


class TestUpdateWord(TestSetup):
    """Tests for update_word method."""

    def test_delegates_to_store_update(self, monkeypatch):
        """Test that method updates and returns record."""
        w = self.service.add_word("Antigen", 50, 500)
        updated = self.service.update_word(w.w_id, w_lead_words=75)
        assert updated.w_lead_words == 75

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        w = self.service.add_word("No_Change")
        result = self.service.update_word(w.w_id)
        assert result.w_title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_word(9999, w_lead_words=10)


class TestDeleteWord(TestSetup):
    """Tests for delete_word method."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that method deletes the record."""
        w = self.service.add_word("T-cell")
        deleted = self.service.delete(w.w_id)
        assert deleted is True
        assert self.service.get_word(w.w_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestGetWordCountsForTitle(TestSetup):
    """Tests for get_word_counts_for_title method."""

    def test_returns_counts_when_record_exists(self, monkeypatch):
        """Test that method returns word counts when record found."""
        self.service.add_word("B-cell", 80, 800)
        lead, all_w = self.service.get_word_counts_for_title("B-cell")
        assert lead == 80
        assert all_w == 800

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that method returns None counts when record not found."""
        lead, all_w = self.service.get_word_counts_for_title("Ghost_Article")
        assert lead is None
        assert all_w is None
