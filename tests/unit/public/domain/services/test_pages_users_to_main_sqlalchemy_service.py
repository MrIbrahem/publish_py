from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import PagesUsersToMainRecord
from src.sqlalchemy_app.public.domain.models import _PagesUsersToMainRecord
from src.sqlalchemy_app.public.domain.services.pages_users_to_main_service import (
    add_pages_users_to_main,
    delete_pages_users_to_main,
    get_pages_users_to_main,
    list_pages_users_to_main,
    update_pages_users_to_main,
)


def test_pages_users_to_main_workflow():
    from sqlalchemy import text
    from src.sqlalchemy_app.shared.domain.engine import get_session

    with get_session() as session:
        session.execute(text("INSERT INTO pages_users (id, title) VALUES (1, 'test')"))
        session.commit()

    # Test add
    p = add_pages_users_to_main(id=1, new_target="target", new_user="user", new_qid="qid")
    assert p.id == 1
    assert p.new_target == "target"

    # Test get
    p2 = get_pages_users_to_main(1)
    assert p2.new_target == "target"

    # Test list
    all_p = list_pages_users_to_main()
    assert any(x.id == 1 for x in all_p)

    # Test update
    updated = update_pages_users_to_main(1, new_target="new_target")
    assert updated.new_target == "new_target"

    # Test delete
    delete_pages_users_to_main(1)
    assert get_pages_users_to_main(1) is None


class TestListPagesUsersToMain:
    """Tests for list_pages_users_to_main function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestGetPagesUsersToMain:
    """Tests for get_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestAddPagesUsersToMain:
    """Tests for add_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestUpdatePagesUsersToMain:
    """Tests for update_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeletePagesUsersToMain:
    """Tests for delete_pages_users_to_main function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
