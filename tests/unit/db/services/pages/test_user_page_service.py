import pytest

from src.main_app.db.models import UserPageRecord
from src.main_app.db.services import (
    UserPagesService,
)

pytestmark = pytest.mark.unit


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = UserPagesService()

    def _make_page(self, title: str, lang: str, target: str, user: str = "u") -> UserPageRecord:
        return self.service.add_page(
            sourcetitle=title,
            translate_type="lead",
            cat="RTT",
            lang=lang,
            user=user,
            target=target,
        )


class TestPagesAndUserPagesService(TestSetup):
    """Tests for PagesService/UserPagesService class."""

    def test_page_workflow(self, sqlite_db):
        p = self.service.add_page(
            sourcetitle="COVID-19 pandemic",
            translate_type="lead",
            cat="History",
            lang="fr",
            user="Historian",
            target="COVID-19_pandemic.html",
            mdwiki_revid=4444,
            word=52,
        )
        assert p.title == "COVID-19 pandemic"

        assert any(x.title == "COVID-19 pandemic" for x in self.service.list_pages())

        updated = self.service.update_page(p.id, "COVID-19", "COVID-19.html")
        assert updated is not None
        assert updated.title == "COVID-19"

        orm_p = self.service.get(p.id)
        assert orm_p is not None
        orm_p.lang = "en"
        orm_p.user = "WikiUser"
        orm_p.target = ""
        sqlite_db.session.commit()

        success = self.service.insert_page_target(
            sourcetitle="Black Death",
            translate_type="lead",
            cat="History",
            lang="fr",
            user="Historian",
            target="Peste_noire.html",
            mdwiki_revid=525252,
            word=5000,
        )
        assert success is True

        self.service.delete(p.id)
        assert not any(x.id == p.id for x in self.service.list_pages())

    def test_returns_list_of_pages(self, monkeypatch):
        """Test that function returns list from store."""
        self.service.add_page("Evolution", "lead", "Biology", "en", "TestUser", "Evolution.html")
        self.service.add_page("Genetics", "lead", "Biology", "en", "TestUser", "Genetics.html")
        result = self.service.list_pages()
        assert len(result) >= 2
        assert any(p.title == "Evolution" for p in result)


class TestAddPage(TestSetup):
    """Tests for add_page function."""

    def test_adds_page(self, monkeypatch):
        """Test that function adds a page."""
        record = self.service.add_page(
            "Quantum mechanics", "lead", "Physics", "en", "TestUser", "Quantum_mechanics.html"
        )
        assert record.title == "Quantum mechanics"
        assert record.target == "Quantum_mechanics.html"

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_page("", "lead", "Test", "en", "TestUser", "test.html")


class TestUpdatePage(TestSetup):
    """Tests for update_page function."""

    def test_updates_the_record(self, monkeypatch):
        """Test that function updates the record."""
        p = self.service.add_page("Sociology", "lead", "Social", "en", "TestUser", "Sociology.html")
        updated = self.service.update_page(p.id, "Social Science", "Social_Science.html")
        assert updated is not None
        assert updated.title == "Social Science"
        assert updated.target == "Social_Science.html"


class TestDeletePage(TestSetup):
    """Tests for delete_page function."""

    def test_deletes_the_record(self, monkeypatch):
        """Test that function deletes the record."""
        p = self.service.add_page("Economics", "lead", "Social", "en", "TestUser", "Economics.html")
        self.service.delete(p.id)
        assert not any(x.id == p.id for x in self.service.list_pages())

    def test_raises_lookup_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestInsertPageTarget(TestSetup):
    """Tests for insert_page_target function."""

    def test_inserts_correctly(self, monkeypatch):
        """Test that function inserts correctly."""
        success = self.service.insert_page_target(
            "Global warming", "type", "Climate", "en", "Climatologist", "Global_warming_target.html"
        )
        assert success is True
        assert any(p.title == "Global warming" for p in self.service.list_pages())

    def test_passes_optional_params(self, monkeypatch):
        """Test that optional parameters are passed correctly."""
        success = self.service.insert_page_target(
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
        p = next(p for p in self.service.list_pages() if p.title == "Astrophysics")
        assert p.mdwiki_revid == 987654
        assert p.word == 1200


# ---------------------------------------------------------------------------
# Tests for new service functions added with the admin/translated work:
#   - self.service.list_translated(lang, limit, offset)
#   - self.service.count_translated(lang)
#   - self.service.get_by_id(page_id)
# ---------------------------------------------------------------------------


class TestListTranslated(TestSetup):
    """Tests for list_translated."""

    def test_excludes_rows_with_empty_or_null_target(self, sqlite_db):
        self._make_page("Has_target", "en", "T1.html")
        # Empty target row
        empty = self._make_page("Empty_target", "en", "x")
        empty.target = ""
        # NULL target row
        null = self._make_page("Null_target", "en", "x")
        null.target = None
        sqlite_db.session.commit()

        rows = self.service.list_translated(lang="All")
        titles = {p.title for p in rows}
        assert "Has_target" in titles
        assert "Empty_target" not in titles
        assert "Null_target" not in titles

    def test_filters_by_lang(self, monkeypatch):
        self._make_page("English_page", "en", "E.html")
        self._make_page("French_page", "fr", "F.html")
        rows = self.service.list_translated(lang="fr")
        titles = {p.title for p in rows}
        assert titles == {"French_page"}

    def test_lang_all_returns_every_language(self, monkeypatch):
        self._make_page("English_page", "en", "E.html")
        self._make_page("French_page", "fr", "F.html")
        rows = self.service.list_translated(lang="All")
        titles = {p.title for p in rows}
        assert titles == {"English_page", "French_page"}

    def test_respects_limit_and_offset(self, monkeypatch):
        for i in range(5):
            self._make_page(f"Page_{i}", "en", f"T_{i}.html")
        rows = self.service.list_translated(lang="en", limit=2, offset=0)
        assert len(rows) == 2
        rows_offset = self.service.list_translated(lang="en", limit=2, offset=2)
        assert len(rows_offset) == 2
        # Offset should yield a different set.
        first_ids = {p.id for p in rows}
        offset_ids = {p.id for p in rows_offset}
        assert first_ids.isdisjoint(offset_ids)

    def test_returns_empty_when_no_translated_rows(self, monkeypatch):
        assert self.service.list_translated(lang="All") == []


class TestCountTranslated(TestSetup):
    """Tests for count_translated."""

    def test_counts_only_rows_with_target(self, sqlite_db):
        self._make_page("With_target", "en", "X.html")
        empty = self._make_page("Empty", "en", "x")
        empty.target = ""
        sqlite_db.session.commit()

        assert self.service.count_translated(lang="All") == 1

    def test_counts_filtered_by_lang(self, monkeypatch):
        self._make_page("En1", "en", "E1.html")
        self._make_page("En2", "en", "E2.html")
        self._make_page("Fr1", "fr", "F1.html")
        assert self.service.count_translated(lang="en") == 2
        assert self.service.count_translated(lang="fr") == 1
        assert self.service.count_translated(lang="All") == 3

    def test_returns_zero_when_no_rows(self, monkeypatch):
        assert self.service.count_translated(lang="All") == 0


class TestGetById(TestSetup):
    """Tests for get_by_id."""

    def test_returns_record_when_found(self, monkeypatch):
        p = self._make_page("Findable", "en", "F.html")
        result = self.service.get_by_id(p.id)
        assert result is not None
        assert result.title == "Findable"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_by_id(99999) is None
