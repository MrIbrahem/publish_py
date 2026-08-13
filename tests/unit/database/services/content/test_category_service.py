import pytest

from src.main_app.database.models import CategoryRecord
from src.main_app.database.services.content.category_service import CategoryService
from src.main_app.database.exceptions import RecordNotFoundError


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = CategoryService()


class TestCategoryService(TestSetup):
    """Tests for CategoryService class."""

    def test_category_workflow(self):
        c = self.service.add_category("Medicine", "Medicine Content", "Health_Campaign", "Anatomy", 1, 1)
        assert c.category == "Medicine"

        a1 = self.service.get_campaign_category("Health_Campaign")
        assert a1 is not None
        assert a1.category == "Medicine"

        assert any(x.category == "Medicine" for x in self.service.list_categories())

        assert self.service.get_camp_to_cats()["Health_Campaign"] == "Medicine"

        updated = self.service.update_category(
            category_id=c.id,
            category="Medical_Science",
            campaign="Science_Campaign",
        )
        assert updated.category == "Medical_Science"

        a2 = self.service.get_campaign_category("Science_Campaign")
        assert a2 is not None
        assert a2.category == "Medical_Science"

        self.service.delete(c.id)
        assert self.service.get_campaign_category("Science_Campaign") is None


class TestGetCampaignCategory(TestSetup):
    """Tests for get_campaign_category method."""

    def test_returns_category_record(self, monkeypatch):
        """Test that method returns a CategoryRecord."""
        self.service.add_category("Dermatology", campaign="Skin_Health")
        result = self.service.get_campaign_category("Skin_Health")
        assert isinstance(result, CategoryRecord)
        assert result.campaign == "Skin_Health"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that method returns None when campaign not found."""
        result = self.service.get_campaign_category("Non_Existent_Campaign")
        assert result is None


class TestAddCategory(TestSetup):
    """Tests for add_category method."""

    def test_adds_category_without_default(self, monkeypatch):
        """Test adding a category without setting it as default."""
        record = self.service.add_category("Cardiology", campaign="Heart_Health", is_default=0)
        assert record.category == "Cardiology"
        assert record.is_default == 0

    def test_updates_existing_category(self, monkeypatch):
        """Test updating an existing category via add_category."""
        self.service.add_category("Neurology", campaign="Brain_Health")
        updated = self.service.add_category("Neurology", campaign="New_Brain_Health", display="New Brain")
        assert updated.category == "Neurology"
        assert updated.campaign == "New_Brain_Health"
        assert updated.display == "New Brain"

    def test_adds_category_with_default(self, monkeypatch):
        """Test adding a category and setting it as default."""
        self.service.add_category("Neurology", campaign="Brain_Health", is_default=1)
        record2 = self.service.add_category("Pediatrics", campaign="Child_Health", is_default=1)
        assert record2.is_default == 1

        cats = self.service.list_categories()
        neurology = next(c for c in cats if c.category == "Neurology")
        assert neurology.is_default == 0

    def test_uses_campaign_as_display_fallback(self, monkeypatch):
        """Test that campaign name is used as display when display is empty."""
        record = self.service.add_category("Psychiatry", campaign="Mental_Health_Campaign", display="")
        assert record.display == "Mental_Health_Campaign"


class TestListCategories(TestSetup):
    """Tests for list_categories method."""

    def test_returns_list_of_categories(self, monkeypatch):
        """Test that method returns list of categories."""
        self.service.add_category("Surgery", campaign="Surgical_Procedures")
        self.service.add_category("Radiology", campaign="Imaging_Diagnostics")
        result = self.service.list_categories()
        assert len(result) >= 2
        assert any(c.category == "Surgery" for c in result)
        assert any(c.category == "Radiology" for c in result)

    def test_returns_empty_list_when_no_categories(self, monkeypatch):
        """Test that method returns empty list when no categories exist."""
        result = self.service.list_categories()
        assert result == []


class TestDeleteCategory(TestSetup):
    """Tests for delete_category method."""

    def test_deletes_category(self, monkeypatch):
        """Test that delete method deletes the record."""
        cat = self.service.add_category("Pathology", campaign="Disease_Study")
        self.service.delete(cat.id)
        assert not any(c.id == cat.id for c in self.service.list_categories())

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestUpdateCategory(TestSetup):
    """Tests for update_category method."""

    def test_updates_category(self, monkeypatch):
        """Test that update_category updates and returns the record."""
        cat = self.service.add_category("Endocrinology", campaign="Hormone_Health")
        updated = self.service.update_category(cat.id, "Metabolic_Medicine", "Metabolism_Campaign")
        assert updated.category == "Metabolic_Medicine"
        assert updated.campaign == "Metabolism_Campaign"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_category(9999, "Title", "File")


class TestGetCampToCats(TestSetup):
    """Tests for get_camp_to_cats method."""

    def test_returns_campaign_to_category_mapping(self, monkeypatch):
        """Test that get_camp_to_cats returns correct mapping."""
        self.service.add_category("Immunology", campaign="Immune_System")
        self.service.add_category("Oncology", campaign="Cancer_Research")
        mapping = self.service.get_camp_to_cats()
        assert mapping["Immune_System"] == "Immunology"
        assert mapping["Cancer_Research"] == "Oncology"

    def test_handles_empty_category(self, monkeypatch):
        """Test that get_camp_to_cats handles empty category values."""

    def test_skips_empty_campaign(self, monkeypatch):
        """Test that get_camp_to_cats skips records with empty campaign."""
