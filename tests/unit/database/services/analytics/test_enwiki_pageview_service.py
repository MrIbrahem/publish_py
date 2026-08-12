import pytest

from src.main_app.database.models import EnwikiPageviewRecord
from src.main_app.database.services.analytics.enwiki_pageview_service import EnwikiPageviewService
from src.main_app.db.exceptions import RecordNotFoundError


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = EnwikiPageviewService()


class TestEnwikiPageviewService(TestSetup):
    """Tests for EnwikiPageviewService class."""

    def test_enwiki_pageview_workflow(self):
        # Test add
        p = self.service.add_enwiki_pageview("Anatomy", 5000)
        assert p.title == "Anatomy"
        assert p.en_views == 5000

        # Test get
        p2 = self.service.get_enwiki_pageview(p.id)
        assert p2 is not None
        assert p2.title == "Anatomy"

        # Test get by title
        p3 = self.service.get_enwiki_pageview_by_title("Anatomy")
        assert p3 is not None
        assert p3.id == p.id

        # Test list
        all_p = self.service.list_enwiki_pageviews()
        assert any(x.title == "Anatomy" for x in all_p)

        # Test top views
        top = self.service.get_top_enwiki_pageviews(1)
        assert top[0].title == "Anatomy"

        # Test update
        updated = self.service.update_enwiki_pageview(p.id, en_views=7500)
        assert updated.en_views == 7500

        # Test add_or_update
        p4 = self.service.add_or_update_enwiki_pageview("Anatomy", 10000)
        assert p4.en_views == 10000

        # Test delete
        deleted = self.service.delete(p.id)
        assert deleted is True
        assert self.service.get_enwiki_pageview(p.id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.add_enwiki_pageview("Biology")
        self.service.add_enwiki_pageview("Chemistry")
        result = self.service.list_enwiki_pageviews()
        assert len(result) >= 2


class TestGetTopEnwikiPageviews(TestSetup):
    """Tests for get_top_enwiki_pageviews method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns top records by views."""
        self.service.add_enwiki_pageview("Physics", 100)
        self.service.add_enwiki_pageview("Mathematics", 1000)
        top = self.service.get_top_enwiki_pageviews(1)
        assert len(top) == 1
        assert top[0].title == "Mathematics"

    def test_uses_default_limit(self, monkeypatch):
        """Test that method uses default limit."""
        self.service.get_top_enwiki_pageviews()


class TestGetEnwikiPageview(TestSetup):
    """Tests for get_enwiki_pageview method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        p = self.service.add_enwiki_pageview("Genetics")
        result = self.service.get_enwiki_pageview(p.id)
        assert isinstance(result, EnwikiPageviewRecord)
        assert result.title == "Genetics"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_enwiki_pageview(9999) is None


class TestGetEnwikiPageviewByTitle(TestSetup):
    """Tests for get_enwiki_pageview_by_title method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by title."""
        self.service.add_enwiki_pageview("Microbiology")
        result = self.service.get_enwiki_pageview_by_title("Microbiology")
        assert result is not None
        assert result.title == "Microbiology"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_enwiki_pageview_by_title("Ghost") is None


class TestAddEnwikiPageview(TestSetup):
    """Tests for add_enwiki_pageview method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_enwiki_pageview("Virology", 300)
        assert record.title == "Virology"
        assert record.en_views == 300

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_enwiki_pageview("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_enwiki_pageview("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_enwiki_pageview("")


class TestAddOrUpdateEnwikiPageview(TestSetup):
    """Tests for add_or_update_enwiki_pageview method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method upserts record."""
        self.service.add_enwiki_pageview("Epidemiology", 50)
        record = self.service.add_or_update_enwiki_pageview("Epidemiology", 150)
        assert record.en_views == 150
        assert len(self.service.list_enwiki_pageviews()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_or_update_enwiki_pageview("  ")


class TestUpdateEnwikiPageview(TestSetup):
    """Tests for update_enwiki_pageview method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns record."""
        p = self.service.add_enwiki_pageview("Immunology", 100)
        updated = self.service.update_enwiki_pageview(p.id, en_views=200)
        assert updated.en_views == 200

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        p = self.service.add_enwiki_pageview("No_Change")
        result = self.service.update_enwiki_pageview(p.id)
        assert result.title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_enwiki_pageview(9999, en_views=10)


class TestDeleteEnwikiPageview(TestSetup):
    """Tests for delete_enwiki_pageview method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        p = self.service.add_enwiki_pageview("Pathology")
        deleted = self.service.delete(p.id)
        assert deleted is True
        assert self.service.get_enwiki_pageview(p.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False
