from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import PagesUsersToMainRecord
from src.sqlalchemy_app.public.models import _PagesUsersToMainRecord
from src.sqlalchemy_app.public.services.pages_users_to_main_service import (
    add_pages_users_to_main,
    delete_pages_users_to_main,
    get_pages_users_to_main,
    list_pages_users_to_main,
    update_pages_users_to_main,
)


def test_pages_users_to_main_workflow():
    from sqlalchemy import text
    from src.sqlalchemy_app.shared.engine import get_session

    with get_session() as session:
        session.execute(text("INSERT INTO pages_users (id, title) VALUES (1, 'Hepatitis B')"))
        session.commit()

    # Test add
    p = add_pages_users_to_main(id=1, new_target="Hépatite B", new_user="French_Editor", new_qid="Q181056")
    assert p.id == 1
    assert p.new_target == "Hépatite B"

    # Test get
    p2 = get_pages_users_to_main(1)
    assert p2.new_target == "Hépatite B"

    # Test list
    all_p = list_pages_users_to_main()
    assert any(x.id == 1 for x in all_p)

    # Test update
    updated = update_pages_users_to_main(1, new_target="Hépatite B (maladie)")
    assert updated.new_target == "Hépatite B (maladie)"

    # Test delete
    delete_pages_users_to_main(1)
    assert get_pages_users_to_main(1) is None


class TestListPagesUsersToMain:
    """Tests for list_pages_users_to_main function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.engine import get_session

        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (10, 'Malaria'), (20, 'Cholera')"))
            session.commit()

        add_pages_users_to_main(id=10, new_target="Paludisme")
        add_pages_users_to_main(id=20, new_target="Choléra")
        result = list_pages_users_to_main()
        assert len(result) >= 2


class TestGetPagesUsersToMain:
    """Tests for get_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.engine import get_session

        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (30, 'Dengue fever')"))
            session.commit()

        add_pages_users_to_main(id=30, new_target="Dengue")
        result = get_pages_users_to_main(30)
        assert isinstance(result, PagesUsersToMainRecord)
        assert result.id == 30

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_pages_users_to_main(9999) is None


class TestAddPagesUsersToMain:
    """Tests for add_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.engine import get_session

        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (40, 'Yellow fever')"))
            session.commit()

        record = add_pages_users_to_main(id=40, new_target="Fièvre jaune")
        assert record.id == 40
        assert record.new_target == "Fièvre jaune"

    def test_raises_error_on_failure(self, monkeypatch):
        from sqlalchemy.exc import IntegrityError

        with patch("src.sqlalchemy_app.public.services.pages_users_to_main_service.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.commit.side_effect = IntegrityError(None, None, None)
            mock_get_session.return_value.__enter__.return_value = mock_session
            with pytest.raises(ValueError, match="Failed to add"):
                add_pages_users_to_main(id=9999)


class TestUpdatePagesUsersToMain:
    """Tests for update_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.engine import get_session

        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (50, 'Zika virus')"))
            session.commit()

        add_pages_users_to_main(id=50, new_target="Virus Zika")
        updated = update_pages_users_to_main(50, new_target="Zika")
        assert updated.new_target == "Zika"

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.engine import get_session

        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (51, 'T')"))
            session.commit()
        add_pages_users_to_main(id=51)
        result = update_pages_users_to_main(51)
        assert result.id == 51

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_pages_users_to_main(9999, new_target="T")


class TestDeletePagesUsersToMain:
    """Tests for delete_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.engine import get_session

        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (60, 'Ebola virus')"))
            session.commit()

        add_pages_users_to_main(id=60, new_target="Ebola")
        delete_pages_users_to_main(60)
        assert get_pages_users_to_main(60) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_pages_users_to_main(9999)
