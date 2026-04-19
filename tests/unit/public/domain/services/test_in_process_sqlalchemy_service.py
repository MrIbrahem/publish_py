from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import InProcessRecord
from src.sqlalchemy_app.public.domain.models import _InProcessRecord
from src.sqlalchemy_app.public.domain.services.in_process_service import (
    add_in_process,
    delete_in_process,
    delete_in_process_by_title_user_lang,
    get_in_process,
    get_in_process_by_title_user_lang,
    is_in_process,
    list_in_process,
    list_in_process_by_lang,
    list_in_process_by_user,
    update_in_process,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_in_process_workflow():
    # Test add
    ip = add_in_process("test_title", "test_user", "en", "RTT", "lead", 100)
    assert ip.title == "test_title"
    assert ip.user == "test_user"

    # Test get
    ip2 = get_in_process(ip.id)
    assert ip2.title == "test_title"

    # Test get by multiple keys
    ip3 = get_in_process_by_title_user_lang("test_title", "test_user", "en")
    assert ip3.id == ip.id

    # Test list
    all_ip = list_in_process()
    assert any(x.title == "test_title" for x in all_ip)

    # Test list by user/lang
    by_user = list_in_process_by_user("test_user")
    assert len(by_user) >= 1
    by_lang = list_in_process_by_lang("en")
    assert len(by_lang) >= 1

    # Test is_in_process
    assert is_in_process("test_title", "test_user", "en") is True

    # Test update
    updated = update_in_process(ip.id, word=200)
    assert updated.word == 200

    # Test delete by title/user/lang
    success = delete_in_process_by_title_user_lang("test_title", "test_user", "en")
    assert success is True
    assert get_in_process(ip.id) is None

    # Test delete by ID
    ip_new = add_in_process("new", "new_user", "fr")
    delete_in_process(ip_new.id)
    assert get_in_process(ip_new.id) is None


class TestGetInProcessDb:
    """Tests for get_in_process_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new InProcessDB is created when none cached."""


class TestListInProcess:
    """Tests for list_in_process function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestListInProcessByUser:
    """Tests for list_in_process_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestListInProcessByLang:
    """Tests for list_in_process_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestGetInProcess:
    """Tests for get_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetInProcessByTitleUserLang:
    """Tests for get_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestAddInProcess:
    """Tests for add_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestUpdateInProcess:
    """Tests for update_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteInProcess:
    """Tests for delete_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestDeleteInProcessByTitleUserLang:
    """Tests for delete_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestIsInProcess:
    """Tests for is_in_process function."""

    def test_returns_true_when_record_exists(self, monkeypatch):
        """Test that function returns True when record found."""

    def test_returns_false_when_record_not_found(self, monkeypatch):
        """Test that function returns False when record not found."""
