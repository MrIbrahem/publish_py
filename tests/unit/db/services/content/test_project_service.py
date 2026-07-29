import pytest

from src.main_app.db.models import ProjectRecord
from src.main_app.db.services.content.project_service import (
    ProjectService,
    add_project,
    get_project,
    get_project_by_title,
    list_projects,
    update_project,
)


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = ProjectService()


class TestProjectService(TestSetup):
    """Tests for ProjectService class."""

    def test_project_workflow(self):
        # Test add
        p = add_project("WikiProject Medicine")
        assert p.g_title == "WikiProject Medicine"

        # Test get
        p2 = get_project(p.g_id)
        assert p2 is not None
        assert p2.g_title == "WikiProject Medicine"

        # Test get by title
        p3 = get_project_by_title("WikiProject Medicine")
        assert p3 is not None
        assert p3.g_id == p.g_id

        # Test list
        all_p = list_projects()
        assert any(x.g_title == "WikiProject Medicine" for x in all_p)

        # Test update
        updated = update_project(p.g_id, g_title="WP:MED")
        assert updated.g_title == "WP:MED"

        # Test delete
        deleted = ProjectService().delete(p.g_id)
        assert deleted is True
        assert get_project(p.g_id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_project("WikiProject History")
        add_project("WikiProject Science")
        result = list_projects()
        assert len(result) >= 2


class TestGetProject(TestSetup):
    """Tests for get_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        p = add_project("WikiProject Anatomy")
        result = get_project(p.g_id)
        assert isinstance(result, ProjectRecord)
        assert result.g_title == "WikiProject Anatomy"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_project(9999) is None


class TestGetProjectByTitle(TestSetup):
    """Tests for get_project_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_project("WikiProject Physiology")
        result = get_project_by_title("WikiProject Physiology")
        assert result is not None
        assert result.g_title == "WikiProject Physiology"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_project_by_title("Ghost") is None


class TestAddProject(TestSetup):
    """Tests for add_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_project("WikiProject Pharmacology")
        assert record.g_title == "WikiProject Pharmacology"

    def test_raises_error_if_exists(self, monkeypatch):
        add_project("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_project("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Project title is required"):
            add_project("")


class TestUpdateProject(TestSetup):
    """Tests for update_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        p = add_project("WikiProject Genetics")
        updated = update_project(p.g_id, g_title="WP:GENETICS")
        assert updated.g_title == "WP:GENETICS"

    def test_raises_error_if_not_found(self, monkeypatch):
        from src.main_app.db.exceptions import RecordNotFoundError

        with pytest.raises(RecordNotFoundError, match="not found"):
            update_project(9999, g_title="T")


class TestDeleteProject(TestSetup):
    """Tests for delete_project function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        p = add_project("WikiProject Temporary")
        deleted = ProjectService().delete(p.g_id)
        assert deleted is True
        assert get_project(p.g_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert ProjectService().delete(9999) is False
