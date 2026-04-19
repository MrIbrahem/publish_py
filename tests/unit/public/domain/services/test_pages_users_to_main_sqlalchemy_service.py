from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import PagesUsersToMainRecord
from src.sqlalchemy_app.public.domain.models import _PagesUsersToMainRecord
from src.sqlalchemy_app.public.domain.services.pages_users_to_main_service import (
    add_pages_users_to_main,
    delete_pages_users_to_main,
    get_pages_users_to_main,
    list_pages_users_to_main,
    update_pages_users_to_main,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    # Need to create pages_users table first because of FK
    from sqlalchemy import Column, Integer, MetaData, String, Table

    meta = MetaData()
    pages_users = Table("pages_users", meta, Column("id", Integer, primary_key=True), Column("title", String(255)))
    pages_users.create(engine)

    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_pages_users_to_main_workflow():
    from sqlalchemy import text
    from src.sqlalchemy_app.shared.domain.engine import get_session

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
        from src.sqlalchemy_app.shared.domain.engine import get_session
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
        from src.sqlalchemy_app.shared.domain.engine import get_session
        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (30, 'Dengue fever')"))
            session.commit()

        add_pages_users_to_main(id=30, new_target="Dengue")
        result = get_pages_users_to_main(30)
        assert isinstance(result, PagesUsersToMainRecord)
        assert result.id == 30


class TestAddPagesUsersToMain:
    """Tests for add_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.domain.engine import get_session
        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (40, 'Yellow fever')"))
            session.commit()

        record = add_pages_users_to_main(id=40, new_target="Fièvre jaune")
        assert record.id == 40
        assert record.new_target == "Fièvre jaune"


class TestUpdatePagesUsersToMain:
    """Tests for update_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.domain.engine import get_session
        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (50, 'Zika virus')"))
            session.commit()

        add_pages_users_to_main(id=50, new_target="Virus Zika")
        updated = update_pages_users_to_main(50, new_target="Zika")
        assert updated.new_target == "Zika"


class TestDeletePagesUsersToMain:
    """Tests for delete_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        from sqlalchemy import text
        from src.sqlalchemy_app.shared.domain.engine import get_session
        with get_session() as session:
            session.execute(text("INSERT INTO pages_users (id, title) VALUES (60, 'Ebola virus')"))
            session.commit()

        add_pages_users_to_main(id=60, new_target="Ebola")
        delete_pages_users_to_main(60)
        assert get_pages_users_to_main(60) is None
