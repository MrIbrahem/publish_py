import pytest

from src.main_app.database.models import ProjectRecord
from src.main_app.database.services.content.project_service import ProjectService
from src.main_app.db.exceptions import RecordNotFoundError


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = ProjectService()


class TestProjectService(TestSetup):
    """Tests for ProjectService class."""

    def test_project_workflow(self):
        # Test add
        p = self.service.add_project("WikiProject Medicine")
        assert p.g_title == "WikiProject Medicine"

        # Test get
        p2 = self.service.get_project(p.g_id)
        assert p2 is not None
        assert p2.g_title == "WikiProject Medicine"

        # Test get by title
        p3 = self.service.get_project_by_title("WikiProject Medicine")
        assert p3 is not None
        assert p3.g_id == p.g_id

        # Test list
        all_p = self.service.list_projects()
        assert any(x.g_title == "WikiProject Medicine" for x in all_p)

        # Test update
        updated = self.service.update_project(p.g_id, g_title="WP:MED")
        assert updated.g_title == "WP:MED"

        # Test delete
        deleted = self.service.delete(p.g_id)
        assert deleted is True
        assert self.service.get_project(p.g_id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.add_project("WikiProject History")
        self.service.add_project("WikiProject Science")
        result = self.service.list_projects()
        assert len(result) >= 2


class TestGetProject(TestSetup):
    """Tests for get_project method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        p = self.service.add_project("WikiProject Anatomy")
        result = self.service.get_project(p.g_id)
        assert isinstance(result, ProjectRecord)
        assert result.g_title == "WikiProject Anatomy"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_project(9999) is None


class TestGetProjectByTitle(TestSetup):
    """Tests for get_project_by_title method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by title."""
        self.service.add_project("WikiProject Physiology")
        result = self.service.get_project_by_title("WikiProject Physiology")
        assert result is not None
        assert result.g_title == "WikiProject Physiology"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_project_by_title("Ghost") is None


class TestAddProject(TestSetup):
    """Tests for add_project method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_project("WikiProject Pharmacology")
        assert record.g_title == "WikiProject Pharmacology"

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_project("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_project("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Project title is required"):
            self.service.add_project("")


class TestUpdateProject(TestSetup):
    """Tests for update_project method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns record."""
        p = self.service.add_project("WikiProject Genetics")
        updated = self.service.update_project(p.g_id, g_title="WP:GENETICS")
        assert updated.g_title == "WP:GENETICS"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_project(9999, g_title="T")


class TestDeleteProject(TestSetup):
    """Tests for delete_project method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        p = self.service.add_project("WikiProject Temporary")
        deleted = self.service.delete(p.g_id)
        assert deleted is True
        assert self.service.get_project(p.g_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False
