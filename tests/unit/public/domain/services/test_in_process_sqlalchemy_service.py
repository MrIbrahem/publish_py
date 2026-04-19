from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import InProcessRecord
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


class TestListInProcess:
    """Tests for list_in_process function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_in_process("t1", "u1", "en")
        add_in_process("t2", "u2", "en")
        result = list_in_process()
        assert len(result) >= 2


class TestListInProcessByUser:
    """Tests for list_in_process_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by user."""
        add_in_process("t1", "u1", "en")
        add_in_process("t2", "u2", "en")
        result = list_in_process_by_user("u1")
        assert len(result) == 1
        assert result[0].user == "u1"


class TestListInProcessByLang:
    """Tests for list_in_process_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by language."""
        add_in_process("t1", "u1", "en")
        add_in_process("t2", "u1", "fr")
        result = list_in_process_by_lang("fr")
        assert len(result) == 1
        assert result[0].lang == "fr"


class TestGetInProcess:
    """Tests for get_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        ip = add_in_process("t1", "u1", "en")
        result = get_in_process(ip.id)
        assert isinstance(result, InProcessRecord)
        assert result.title == "t1"


class TestGetInProcessByTitleUserLang:
    """Tests for get_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title, user, and language."""
        add_in_process("t1", "u1", "en")
        result = get_in_process_by_title_user_lang("t1", "u1", "en")
        assert result.title == "t1"


class TestAddInProcess:
    """Tests for add_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_in_process("t1", "u1", "en", word=100)
        assert record.title == "t1"
        assert record.word == 100


class TestUpdateInProcess:
    """Tests for update_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        ip = add_in_process("t1", "u1", "en", word=10)
        updated = update_in_process(ip.id, word=20)
        assert updated.word == 20


class TestDeleteInProcess:
    """Tests for delete_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        ip = add_in_process("t1", "u1", "en")
        delete_in_process(ip.id)
        assert get_in_process(ip.id) is None


class TestDeleteInProcessByTitleUserLang:
    """Tests for delete_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes by composite key."""
        add_in_process("t1", "u1", "en")
        success = delete_in_process_by_title_user_lang("t1", "u1", "en")
        assert success is True
        assert get_in_process_by_title_user_lang("t1", "u1", "en") is None


class TestIsInProcess:
    """Tests for is_in_process function."""

    def test_returns_true_when_record_exists(self, monkeypatch):
        """Test that function returns True when record found."""
        add_in_process("t1", "u1", "en")
        assert is_in_process("t1", "u1", "en") is True

    def test_returns_false_when_record_not_found(self, monkeypatch):
        """Test that function returns False when record not found."""
        assert is_in_process("ghost", "u1", "en") is False
