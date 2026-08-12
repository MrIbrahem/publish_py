import pytest

from src.main_app.database.models import ViewsNewRecord
from src.main_app.database.services.analytics.views_new_service import ViewsNewService
from src.main_app.database.exceptions import RecordNotFoundError


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = ViewsNewService()


class TestViewsNewService(TestSetup):
    """Tests for ViewsNewService class."""

    def test_views_new_workflow(self):
        # Test add
        v = self.service.add_views_new("Dengue_fever", "en", 2023, 1500000)
        assert v.target == "Dengue_fever"
        assert v.views == 1500000

        # Test get
        v2 = self.service.get_views_new(v.id)
        assert v2 is not None
        assert v2.target == "Dengue_fever"

        # Test get by target, lang, year
        v3 = self.service.get_views_by_target_lang_year("Dengue_fever", "en", 2023)
        assert v3 is not None
        assert v3.id == v.id

        # Test list
        all_v = self.service.list_views_new()
        assert any(x.target == "Dengue_fever" for x in all_v)

        # Test list by target/lang
        by_target = self.service.list_views_by_target("Dengue_fever")
        assert len(by_target) >= 1
        by_lang = self.service.list_views_by_lang("en")
        assert len(by_lang) >= 1

        # Test update
        updated = self.service.update_views_new(v.id, views=1600000)
        assert updated.views == 1600000

        # Test total views
        total = self.service.get_total_views_for_target("Dengue_fever")
        assert total == 1600000

        # Test add_or_update
        v4 = self.service.add_or_update_views_new("Dengue_fever", "en", 2023, 1700000)
        assert v4.views == 1700000

        # Test delete
        deleted = self.service.delete(v.id)
        assert deleted is True
        assert self.service.get_views_new(v.id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.add_views_new("Malaria", "en", 2023)
        self.service.add_views_new("Cholera", "en", 2023)
        result = self.service.list_views_new()
        assert len(result) >= 2


class TestListViewsByTarget(TestSetup):
    """Tests for list_views_by_target method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns records by target."""
        self.service.add_views_new("Tuberculosis", "en", 2022)
        self.service.add_views_new("Tuberculosis", "en", 2023)
        self.service.add_views_new("Diabetes", "en", 2023)
        result = self.service.list_views_by_target("Tuberculosis")
        assert len(result) == 2
        assert all(r.target == "Tuberculosis" for r in result)


class TestListViewsByLang(TestSetup):
    """Tests for list_views_by_lang method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns records by language."""
        self.service.add_views_new("Influenza", "en", 2023)
        self.service.add_views_new("Influenza", "fr", 2023)
        result = self.service.list_views_by_lang("fr")
        assert len(result) == 1
        assert result[0].lang == "fr"


class TestGetViewsNew(TestSetup):
    """Tests for get_views_new method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        v = self.service.add_views_new("Hepatitis_B", "en", 2023)
        result = self.service.get_views_new(v.id)
        assert isinstance(result, ViewsNewRecord)
        assert result.target == "Hepatitis_B"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_views_new(9999) is None


class TestGetViewsByTargetLangYear(TestSetup):
    """Tests for get_views_by_target_lang_year method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by target, lang, and year."""
        self.service.add_views_new("Measles", "en", 2023)
        result = self.service.get_views_by_target_lang_year("Measles", "en", 2023)
        assert result is not None
        assert result.target == "Measles"
        assert result.year == 2023

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_views_by_target_lang_year("Ghost", "en", 2023) is None


class TestAddViewsNew(TestSetup):
    """Tests for add_views_new method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_views_new("Smallpox", "en", 2023, 500000)
        assert record.target == "Smallpox"
        assert record.views == 500000

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_views_new("Duplicate", "en", 2023)
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_views_new("Duplicate", "en", 2023)

    def test_raises_error_if_no_target_or_lang(self, monkeypatch):
        with pytest.raises(ValueError, match="Target is required"):
            self.service.add_views_new("", "en", 2023)
        with pytest.raises(ValueError, match="Language is required"):
            self.service.add_views_new("T", " ", 2023)


class TestAddOrUpdateViewsNew(TestSetup):
    """Tests for add_or_update_views_new method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method upserts record."""
        self.service.add_views_new("Polio", "en", 2023, 100000)
        record = self.service.add_or_update_views_new("Polio", "en", 2023, 200000)
        assert record.views == 200000
        assert len(self.service.list_views_new()) == 1

    def test_raises_error_if_no_target_or_lang(self, monkeypatch):
        with pytest.raises(ValueError, match="Target is required"):
            self.service.add_or_update_views_new("", "en", 2023)
        with pytest.raises(ValueError, match="Language is required"):
            self.service.add_or_update_views_new("T", " ", 2023)


class TestUpdateViewsNew(TestSetup):
    """Tests for update_views_new method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns record."""
        v = self.service.add_views_new("Stroke", "en", 2023, 1000000)
        updated = self.service.update_views_new(v.id, views=1100000)
        assert updated.views == 1100000

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        v = self.service.add_views_new("No_Change", "en", 2023)
        result = self.service.update_views_new(v.id)
        assert result.target == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_views_new(9999, views=10)


class TestDeleteViewsNew(TestSetup):
    """Tests for delete_views_new method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        v = self.service.add_views_new("Asthma", "en", 2023)
        deleted = self.service.delete(v.id)
        assert deleted is True
        assert self.service.get_views_new(v.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestGetTotalViewsForTarget(TestSetup):
    """Tests for get_total_views_for_target method."""

    def test_returns_sum_of_views(self, monkeypatch):
        """Test that method returns sum of views."""
        self.service.add_views_new("Cancer", "en", 2022, 5000000)
        self.service.add_views_new("Cancer", "fr", 2023, 1000000)
        assert self.service.get_total_views_for_target("Cancer") == 6000000

    def test_returns_zero_when_no_records(self, monkeypatch):
        """Test that method returns 0 when no records."""
        assert self.service.get_total_views_for_target("Ghost_Article") == 0

    def test_handles_none_views(self, monkeypatch):
        """Test that method handles None views."""
        self.service.add_views_new("Empty_Views", "en", 2022, None)
        assert self.service.get_total_views_for_target("Empty_Views") == 0
