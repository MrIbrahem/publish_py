from unittest.mock import patch

import pytest

from src.main_app.database.exceptions import RecordNotFoundError
from src.main_app.database.models import PagesUsersToMainRecord
from src.main_app.database.services.reports.pages_users_to_main_service import PagesUsersToMainService

pytestmark = pytest.mark.unit


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = PagesUsersToMainService()


class TestPagesUsersToMainService(TestSetup):
    def test_pages_users_to_main_workflow(self, sqlite_db):
        from sqlalchemy import text

        sqlite_db.session.execute(text("INSERT INTO pages_users (id, title) VALUES (1, 'Hepatitis B')"))
        sqlite_db.session.commit()

        # Test add
        p = self.service.add_pages_users_to_main(
            id=1, new_target="Hépatite B", new_user="French_Editor", new_qid="Q181056"
        )
        assert p.id == 1
        assert p.new_target == "Hépatite B"

        # Test get
        p2 = self.service.get_pages_users_to_main(1)
        assert p2 is not None
        assert p2.new_target == "Hépatite B"

        # Test list
        all_p = self.service.list_pages_users_to_main()
        assert any(x.id == 1 for x in all_p)

        # Test update
        updated = self.service.update_pages_users_to_main(1, new_target="Hépatite B (maladie)")
        assert updated.new_target == "Hépatite B (maladie)"

        # Test delete
        deleted = self.service.delete(1)
        assert deleted is True
        assert self.service.get_pages_users_to_main(1) is None


class TestListPagesUsersToMain(TestSetup):
    """Tests for list_pages_users_to_main method."""

    def test_returns_list_from_store(self, sqlite_db):
        """Test that method returns list from store."""
        from sqlalchemy import text

        sqlite_db.session.execute(text("INSERT INTO pages_users (id, title) VALUES (10, 'Malaria'), (20, 'Cholera')"))
        sqlite_db.session.commit()

        self.service.add_pages_users_to_main(id=10, new_target="Paludisme")
        self.service.add_pages_users_to_main(id=20, new_target="Choléra")
        result = self.service.list_pages_users_to_main()
        assert len(result) >= 2


class TestGetPagesUsersToMain(TestSetup):
    """Tests for get_pages_users_to_main method."""

    def test_delegates_to_store(self, sqlite_db):
        """Test that method returns record by ID."""
        from sqlalchemy import text

        sqlite_db.session.execute(text("INSERT INTO pages_users (id, title) VALUES (30, 'Dengue fever')"))
        sqlite_db.session.commit()

        self.service.add_pages_users_to_main(id=30, new_target="Dengue")
        result = self.service.get_pages_users_to_main(30)
        assert isinstance(result, PagesUsersToMainRecord)
        assert result.id == 30

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_pages_users_to_main(9999) is None


class TestAddPagesUsersToMain(TestSetup):
    """Tests for add_pages_users_to_main method."""

    def test_delegates_to_store(self, sqlite_db):
        """Test that method adds and returns record."""
        from sqlalchemy import text

        sqlite_db.session.execute(text("INSERT INTO pages_users (id, title) VALUES (40, 'Yellow fever')"))
        sqlite_db.session.commit()

        record = self.service.add_pages_users_to_main(id=40, new_target="Fièvre jaune")
        assert record.id == 40
        assert record.new_target == "Fièvre jaune"

    def test_raises_error_on_failure(self, sqlite_db):
        from sqlalchemy.exc import IntegrityError

        with patch.object(sqlite_db.session, "commit", side_effect=IntegrityError(None, None, None)):  # type: ignore
            with pytest.raises(ValueError, match="Failed to add"):
                self.service.add_pages_users_to_main(id=9999)


class TestUpdatePagesUsersToMain(TestSetup):
    """Tests for update_pages_users_to_main method."""

    def test_delegates_to_store(self, sqlite_db):
        """Test that method updates and returns record."""
        from sqlalchemy import text

        sqlite_db.session.execute(text("INSERT INTO pages_users (id, title) VALUES (50, 'Zika virus')"))
        sqlite_db.session.commit()

        self.service.add_pages_users_to_main(id=50, new_target="Virus Zika")
        updated = self.service.update_pages_users_to_main(50, new_target="Zika")
        assert updated.new_target == "Zika"

    def test_returns_record_if_no_kwargs(self, sqlite_db):
        from sqlalchemy import text

        sqlite_db.session.execute(text("INSERT INTO pages_users (id, title) VALUES (51, 'T')"))
        sqlite_db.session.commit()
        self.service.add_pages_users_to_main(id=51)
        result = self.service.update_pages_users_to_main(51)
        assert result.id == 51

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_pages_users_to_main(9999, new_target="T")


class TestDeletePagesUsersToMain(TestSetup):
    """Tests for delete_pages_users_to_main method."""

    def test_delegates_to_store(self, sqlite_db):
        """Test that method deletes the record."""
        from sqlalchemy import text

        sqlite_db.session.execute(text("INSERT INTO pages_users (id, title) VALUES (60, 'Ebola virus')"))
        sqlite_db.session.commit()

        self.service.add_pages_users_to_main(id=60, new_target="Ebola")
        deleted = self.service.delete(60)
        assert deleted is True
        assert self.service.get_pages_users_to_main(60) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False
