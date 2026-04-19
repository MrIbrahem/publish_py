from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import LangRecord
from src.sqlalchemy_app.public.domain.models import _LangRecord
from src.sqlalchemy_app.public.domain.services.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    list_langs,
    update_lang,
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


def test_lang_workflow():
    # Test add
    l = add_lang("en", "English", "English")
    assert l.code == "en"
    assert l.autonym == "English"

    # Test get
    l2 = get_lang(l.lang_id)
    assert l2.code == "en"

    # Test get by code
    l3 = get_lang_by_code("en")
    assert l3.lang_id == l.lang_id

    # Test list
    all_l = list_langs()
    assert any(x.code == "en" for x in all_l)

    # Test update
    updated = update_lang(l.lang_id, autonym="Eng")
    assert updated.autonym == "Eng"

    # Test add_or_update
    l4 = add_or_update_lang("en", "English", "English Lang")
    assert l4.name == "English Lang"

    # Test delete
    delete_lang(l.lang_id)
    assert get_lang(l.lang_id) is None


class TestListLangs:
    """Tests for list_langs function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_lang("en", "English", "English")
        add_lang("fr", "Français", "French")
        result = list_langs()
        assert len(result) >= 2


class TestGetLang:
    """Tests for get_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        l = add_lang("en", "English", "English")
        result = get_lang(l.lang_id)
        assert isinstance(result, LangRecord)
        assert result.code == "en"


class TestGetLangByCode:
    """Tests for get_lang_by_code function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by code."""
        add_lang("en", "English", "English")
        result = get_lang_by_code("en")
        assert result.code == "en"


class TestAddLang:
    """Tests for add_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_lang("en", "English", "English")
        assert record.code == "en"


class TestAddOrUpdateLang:
    """Tests for add_or_update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_lang("en", "Old Autonym", "Old Name")
        record = add_or_update_lang("en", "New Autonym", "New Name")
        assert record.autonym == "New Autonym"
        assert record.name == "New Name"
        assert len(list_langs()) == 1


class TestUpdateLang:
    """Tests for update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        l = add_lang("en", "English", "English")
        updated = update_lang(l.lang_id, autonym="Eng")
        assert updated.autonym == "Eng"


class TestDeleteLang:
    """Tests for delete_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        l = add_lang("en", "English", "English")
        delete_lang(l.lang_id)
        assert get_lang(l.lang_id) is None
