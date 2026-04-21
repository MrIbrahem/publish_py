from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.db_models import InProcessRecord
from src.sqlalchemy_app.public.services.in_process_service import (
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
from src.sqlalchemy_app.sqlalchemy_models import _InProcessRecord


def test_in_process_workflow():
    # Test add
    ip = add_in_process("World Health Organization", "Public_Health_Expert", "ar", "Medicine", "lead", 2500)
    assert ip.title == "World Health Organization"
    assert ip.user == "Public_Health_Expert"

    # Test get
    ip2 = get_in_process(ip.id)
    assert ip2.title == "World Health Organization"

    # Test get by multiple keys
    ip3 = get_in_process_by_title_user_lang("World Health Organization", "Public_Health_Expert", "ar")
    assert ip3.id == ip.id

    # Test list
    all_ip = list_in_process()
    assert any(x.title == "World Health Organization" for x in all_ip)

    # Test list by user/lang
    by_user = list_in_process_by_user("Public_Health_Expert")
    assert len(by_user) >= 1
    by_lang = list_in_process_by_lang("ar")
    assert len(by_lang) >= 1

    # Test is_in_process
    assert is_in_process("World Health Organization", "Public_Health_Expert", "ar") is True

    # Test update
    updated = update_in_process(ip.id, word=3000)
    assert updated.word == 3000

    # Test delete by title/user/lang
    success = delete_in_process_by_title_user_lang("World Health Organization", "Public_Health_Expert", "ar")
    assert success is True
    assert get_in_process(ip.id) is None

    # Test delete by ID
    ip_new = add_in_process("Common cold", "Medical_Student", "es")
    delete_in_process(ip_new.id)
    assert get_in_process(ip_new.id) is None


class TestListInProcess:
    """Tests for list_in_process function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_in_process("Fever", "User_One", "en")
        add_in_process("Cough", "User_Two", "en")
        result = list_in_process()
        assert len(result) >= 2


class TestListInProcessByUser:
    """Tests for list_in_process_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by user."""
        add_in_process("Headache", "Brain_User", "en")
        add_in_process("Migraine", "Other_User", "en")
        result = list_in_process_by_user("Brain_User")
        assert len(result) == 1
        assert result[0].user == "Brain_User"


class TestListInProcessByLang:
    """Tests for list_in_process_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by language."""
        add_in_process("Back pain", "User_A", "en")
        add_in_process("Douleur dorsale", "User_A", "fr")
        result = list_in_process_by_lang("fr")
        assert len(result) == 1
        assert result[0].lang == "fr"


class TestGetInProcess:
    """Tests for get_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        ip = add_in_process("Sore throat", "User_B", "en")
        result = get_in_process(ip.id)
        assert isinstance(result, InProcessRecord)
        assert result.title == "Sore throat"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_in_process(9999) is None


class TestGetInProcessByTitleUserLang:
    """Tests for get_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title, user, and language."""
        add_in_process("Insomnia", "Sleepy_Editor", "en")
        result = get_in_process_by_title_user_lang("Insomnia", "Sleepy_Editor", "en")
        assert result.title == "Insomnia"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_in_process_by_title_user_lang("Ghost", "Ghost", "en") is None


class TestAddInProcess:
    """Tests for add_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_in_process("Nausea", "Stomach_Expert", "en", word=150)
        assert record.title == "Nausea"
        assert record.word == 150

    def test_raises_error_if_exists(self, monkeypatch):
        from sqlalchemy.exc import IntegrityError

        with patch("src.sqlalchemy_app.public.services.in_process_service.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.commit.side_effect = IntegrityError(None, None, None)
            mock_get_session.return_value.__enter__.return_value = mock_session
            with pytest.raises(ValueError, match="already exists"):
                add_in_process("Duplicate", "User", "en")

    def test_raises_error_if_missing_required(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_in_process("", "U", "L")
        with pytest.raises(ValueError, match="User is required"):
            add_in_process("T", "", "L")
        with pytest.raises(ValueError, match="Language is required"):
            add_in_process("T", "U", " ")


class TestUpdateInProcess:
    """Tests for update_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        ip = add_in_process("Rash", "Skin_Expert", "en", word=100)
        updated = update_in_process(ip.id, word=200)
        assert updated.word == 200

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        ip = add_in_process("No_Change", "U", "en")
        result = update_in_process(ip.id)
        assert result.title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_in_process(9999, word=10)


class TestDeleteInProcess:
    """Tests for delete_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        ip = add_in_process("Allergy", "Immune_Expert", "en")
        delete_in_process(ip.id)
        assert get_in_process(ip.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_in_process(9999)


class TestDeleteInProcessByTitleUserLang:
    """Tests for delete_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes by composite key."""
        add_in_process("Asthma", "Lung_Expert", "en")
        success = delete_in_process_by_title_user_lang("Asthma", "Lung_Expert", "en")
        assert success is True
        assert get_in_process_by_title_user_lang("Asthma", "Lung_Expert", "en") is None


class TestIsInProcess:
    """Tests for is_in_process function."""

    def test_returns_true_when_record_exists(self, monkeypatch):
        """Test that function returns True when record found."""
        add_in_process("Diabetes", "Endo_Expert", "en")
        assert is_in_process("Diabetes", "Endo_Expert", "en") is True

    def test_returns_false_when_record_not_found(self, monkeypatch):
        """Test that function returns False when record not found."""
        assert is_in_process("Ghost_Article", "Nonexistent_User", "en") is False
