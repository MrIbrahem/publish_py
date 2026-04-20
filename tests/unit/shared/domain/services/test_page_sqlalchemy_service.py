from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, get_session, init_db
from src.sqlalchemy_app.shared.domain.models import _PageRecord
from src.sqlalchemy_app.shared.domain.services.page_service import (
    add_or_update_page,
    add_page,
    delete_page,
    find_exists_or_update_page,
    insert_page_target,
    list_pages,
    update_page,
)
from src.sqlalchemy_app.shared.domain_models import PageRecord


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


def test_page_workflow():
    p = add_page("COVID-19 pandemic", "COVID-19_pandemic.html")
    assert p.title == "COVID-19 pandemic"
    assert any(x.title == "COVID-19 pandemic" for x in list_pages())
    updated = update_page(p.id, "COVID-19", "COVID-19.html")
    assert updated.title == "COVID-19"
    p2 = add_or_update_page("COVID-19", "Coronavirus_disease_2019.html")
    assert p2.target == "Coronavirus_disease_2019.html"
    with get_session() as session:
        orm_p = session.query(_PageRecord).filter(_PageRecord.id == p.id).first()
        orm_p.lang = "en"
        orm_p.user = "WikiUser"
        orm_p.target = ""
        session.commit()
    assert find_exists_or_update_page("COVID-19", "en", "WikiUser", "Pandemic_target.html") is True
    success = insert_page_target("Black Death", "lead", "History", "fr", "Historian", "Peste_noire.html", word=5000)
    assert success is True
    delete_page(p.id)
    assert not any(x.id == p.id for x in list_pages())


class TestListPages:
    """Tests for list_pages function."""

    def test_returns_list_of_pages(self, monkeypatch):
        """Test that function returns list from store."""
        add_page("Evolution", "Evolution.html")
        add_page("Genetics", "Genetics.html")
        result = list_pages()
        assert len(result) >= 2
        assert any(p.title == "Evolution" for p in result)


class TestAddPage:
    """Tests for add_page function."""

    def test_adds_page(self, monkeypatch):
        """Test that function adds a page."""
        record = add_page("Quantum mechanics", "Quantum_mechanics.html")
        assert record.title == "Quantum mechanics"
        assert record.target == "Quantum_mechanics.html"

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_page("", "test.html")

    def test_raises_error_if_exists(self, monkeypatch):
        from sqlalchemy.exc import IntegrityError

        with patch("src.sqlalchemy_app.shared.domain.services.page_service.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.commit.side_effect = IntegrityError(None, None, None)
            mock_get_session.return_value.__enter__.return_value = mock_session
            with pytest.raises(ValueError, match="already exists"):
                add_page("Duplicate", "t1.html")


class TestAddOrUpdatePage:
    """Tests for add_or_update_page function."""

    def test_updates_if_exists(self, monkeypatch):
        """Test that function updates if exists."""
        add_page("Relativity", "Relativity.html")
        record = add_or_update_page("Relativity", "General_relativity.html")
        assert record.target == "General_relativity.html"

    def test_adds_if_not_exists(self, monkeypatch):
        record = add_or_update_page("New Page", "new.html")
        assert record.title == "New Page"

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_or_update_page(" ", "test.html")


class TestUpdatePage:
    """Tests for update_page function."""

    def test_updates_the_record(self, monkeypatch):
        """Test that function updates the record."""
        p = add_page("Sociology", "Sociology.html")
        updated = update_page(p.id, "Social Science", "Social_Science.html")
        assert updated.title == "Social Science"
        assert updated.target == "Social_Science.html"

    def test_raises_lookup_error_if_not_found(self, monkeypatch):
        with pytest.raises(LookupError, match="not found"):
            update_page(9999, "T", "F")


class TestDeletePage:
    """Tests for delete_page function."""

    def test_deletes_the_record(self, monkeypatch):
        """Test that function deletes the record."""
        p = add_page("Economics", "Economics.html")
        delete_page(p.id)
        assert not any(x.id == p.id for x in list_pages())

    def test_raises_lookup_error_if_not_found(self, monkeypatch):
        with pytest.raises(LookupError, match="not found"):
            delete_page(9999)


class TestFindExistsOrUpdate:
    """Tests for find_exists_or_update_page function."""

    def test_updates_target_if_empty(self, monkeypatch):
        """Test that function updates target if empty."""
        # Manual insert to set specific fields
        with get_session() as session:
            session.add(_PageRecord(title="Philosophy", lang="en", user="PhilAuthor", target=""))
            session.commit()

        result = find_exists_or_update_page("Philosophy", "en", "PhilAuthor", "Philosophy_article.html")
        assert result is True

        # Verify update
        pages = list_pages()
        p = next(p for p in pages if p.title == "Philosophy")
        assert p.target == "Philosophy_article.html"

    def test_returns_false_when_not_exists(self, monkeypatch):
        """Test that function returns False when record not found."""
        result = find_exists_or_update_page("Nonexistent Article", "en", "GhostUser", "none.html")
        assert result is False

    def test_handles_exception_on_commit(self, monkeypatch):
        with get_session() as session:
            session.add(_PageRecord(title="Error_Page", lang="en", user="U", target=""))
            session.commit()
        with patch("src.sqlalchemy_app.shared.domain.services.page_service.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.all.return_value = [MagicMock(target="")]
            mock_session.commit.side_effect = Exception("DB Error")
            mock_get_session.return_value.__enter__.return_value = mock_session

            # Function returns True because record exists, but commit fails.
            result = find_exists_or_update_page("Error_Page", "en", "U", "T")
            assert result is True


class TestInsertPageTarget:
    """Tests for insert_page_target function."""

    def test_inserts_correctly(self, monkeypatch):
        """Test that function inserts correctly."""
        success = insert_page_target(
            "Global warming", "type", "Climate", "en", "Climatologist", "Global_warming_target.html"
        )
        assert success is True
        assert any(p.title == "Global warming" for p in list_pages())

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional parameters are passed correctly."""
        success = insert_page_target(
            "Astrophysics",
            "type",
            "Science",
            "en",
            "Astronomer",
            "Astrophysics_target.html",
            mdwiki_revid=987654,
            word=1200,
        )
        assert success is True
        p = next(p for p in list_pages() if p.title == "Astrophysics")
        assert p.mdwiki_revid == 987654
        assert p.word == 1200

    def test_handles_exception(self, monkeypatch):
        with patch("src.sqlalchemy_app.shared.domain.services.page_service.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.commit.side_effect = Exception("DB Error")
            mock_get_session.return_value.__enter__.return_value = mock_session

            success = insert_page_target("Error", "t", "c", "l", "u", "t")
            assert success is False
