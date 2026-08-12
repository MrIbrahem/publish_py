import pytest

from src.main_app.database.models import PageRecord, QidRecord, TranslateTypeRecord
from src.main_app.database.services.pages.translate_type_service import TranslateTypeService
from src.main_app.db.exceptions import UniqueError


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = TranslateTypeService()


class TestTranslateTypeService(TestSetup):
    """Tests for TranslateTypeService class."""

    def test_translate_type_workflow(self):
        # Test add
        tt = self.service.add_translate_type("Medical history", 1, 0)
        assert tt.tt_title == "Medical history"
        assert tt.tt_lead == 1

        # Test get
        tt2 = self.service.get_translate_type(tt.tt_id)
        assert tt2 is not None
        assert tt2.tt_title == "Medical history"

        # Test get by title
        tt3 = self.service.get_translate_type_by_title("Medical history")
        assert tt3 is not None
        assert tt3.tt_id == tt.tt_id

        # Test list
        all_tt = self.service.list_translate_types()
        assert any(x.tt_title == "Medical history" for x in all_tt)

        # Test enabled lists
        leads = self.service.list_lead_enabled_types()
        assert any(x.tt_title == "Medical history" for x in leads)
        fulls = self.service.list_full_enabled_types()
        assert not any(x.tt_title == "Medical history" for x in fulls)

        # Test can_translate
        assert self.service.can_translate_lead("Medical history") is True
        assert self.service.can_translate_full("Medical history") is False

        # Test update
        updated = self.service.update_translate_type(tt.tt_id, tt_full=1)
        assert updated is not None
        assert updated.tt_full == 1
        assert self.service.can_translate_full("Medical history") is True

        # Test delete
        deleted = self.service.delete(tt.tt_id)
        assert deleted is True
        assert self.service.get_translate_type(tt.tt_id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.add_translate_type("Clinical trial")
        self.service.add_translate_type("Case study")
        result = self.service.list_translate_types()
        assert len(result) >= 2


class TestListLeadEnabledTypes(TestSetup):
    """Tests for list_lead_enabled_types method."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list of lead enabled types."""
        self.service.add_translate_type("Epidemiology study", tt_lead=1)
        self.service.add_translate_type("In vitro study", tt_lead=0)
        result = self.service.list_lead_enabled_types()
        assert len(result) == 1
        assert result[0].tt_title == "Epidemiology study"


class TestListFullEnabledTypes(TestSetup):
    """Tests for list_full_enabled_types method."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list of full enabled types."""
        self.service.add_translate_type("Systematic review", tt_full=1)
        self.service.add_translate_type("Meta-analysis", tt_full=0)
        result = self.service.list_full_enabled_types()
        assert len(result) == 1
        assert result[0].tt_title == "Systematic review"


class TestGetTranslateType(TestSetup):
    """Tests for get_translate_type method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        tt = self.service.add_translate_type("Cohort study")
        result = self.service.get_translate_type(tt.tt_id)
        assert isinstance(result, TranslateTypeRecord)
        assert result.tt_title == "Cohort study"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_translate_type(9999) is None


class TestGetTranslateTypeByTitle(TestSetup):
    """Tests for get_translate_type_by_title method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by title."""
        self.service.add_translate_type("Diagnostic test")
        result = self.service.get_translate_type_by_title("Diagnostic test")
        assert result is not None
        assert result.tt_title == "Diagnostic test"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_translate_type_by_title("Ghost") is None


class TestAddTranslateType(TestSetup):
    """Tests for add_translate_type method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_translate_type("Treatment guidelines", 1, 0)
        assert record.tt_title == "Treatment guidelines"
        assert record.tt_lead == 1

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_translate_type("Duplicate")
        with pytest.raises(UniqueError):
            self.service.add_translate_type("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_translate_type("")


class TestUpdateTranslateType(TestSetup):
    """Tests for update_translate_type method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns record."""
        tt = self.service.add_translate_type("Global health", 1, 0)
        updated = self.service.update_translate_type(tt.tt_id, tt_full=1)
        assert updated is not None
        assert updated.tt_full == 1

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        tt = self.service.add_translate_type("No_Change")
        result = self.service.update_translate_type(tt.tt_id)
        assert result is not None
        assert result.tt_title == "No_Change"


class TestDeleteTranslateType(TestSetup):
    """Tests for delete_translate_type method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        tt = self.service.add_translate_type("Pathology report")
        deleted = self.service.delete(tt.tt_id)
        assert deleted is True
        assert self.service.get_translate_type(tt.tt_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestCanTranslateLead(TestSetup):
    """Tests for can_translate_lead method."""

    def test_returns_true_when_tt_lead_is_1(self, monkeypatch):
        """Test that method returns True when tt_lead is 1."""
        self.service.add_translate_type("Pharmacology article", tt_lead=1)
        assert self.service.can_translate_lead("Pharmacology article") is True

    def test_returns_false_when_tt_lead_is_0(self, monkeypatch):
        """Test that method returns False when tt_lead is 0."""
        self.service.add_translate_type("In vivo study", tt_lead=0)
        assert self.service.can_translate_lead("In vivo study") is False

    def test_returns_true_when_no_record(self, monkeypatch):
        """Test that method returns True when no record found (default behavior)."""
        assert self.service.can_translate_lead("Unknown Title") is True


class TestCanTranslateFull(TestSetup):
    """Tests for can_translate_full method."""

    def test_returns_true_when_tt_full_is_1(self, monkeypatch):
        """Test that method returns True when tt_full is 1."""
        self.service.add_translate_type("Expert review", tt_full=1)
        assert self.service.can_translate_full("Expert review") is True

    def test_returns_false_when_tt_full_is_0(self, monkeypatch):
        """Test that method returns False when tt_full is 0."""
        self.service.add_translate_type("Draft article", tt_full=0)
        assert self.service.can_translate_full("Draft article") is False

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that method returns False when no record found (default behavior)."""
        assert self.service.can_translate_full("Unknown Title") is False


class TestListTranslateTypesByCategory(TestSetup):
    """Tests for the ``cat`` filter on list_translate_types."""

    def test_returns_all_when_cat_is_default(self, monkeypatch):
        self.service.add_translate_type("RTT_only_type")
        self.service.add_translate_type("Other_only_type")
        result = self.service.list_translate_types()
        titles = {tt.tt_title for tt in result}
        assert "RTT_only_type" in titles
        assert "Other_only_type" in titles

    def test_filters_by_category_membership(self, sqlite_db):
        self.service.add_translate_type("In_RTT")
        self.service.add_translate_type("Not_In_RTT")
        sqlite_db.session.add(
            PageRecord(
                title="In_RTT",
                translate_type="lead",
                cat="RTT",
                lang="en",
                user="u",
                target="t",
            )
        )
        sqlite_db.session.add(
            PageRecord(
                title="Not_In_RTT",
                translate_type="lead",
                cat="OTHER",
                lang="en",
                user="u",
                target="t",
            )
        )
        sqlite_db.session.commit()

        result = self.service.list_translate_types(cat="RTT")
        titles = {tt.tt_title for tt in result}
        assert "In_RTT" in titles
        assert "Not_In_RTT" not in titles

    def test_returns_empty_for_unknown_category(self, monkeypatch):
        self.service.add_translate_type("Some_type")
        result = self.service.list_translate_types(cat="NoSuchCat")
        assert result == []


class TestListNewTitles(TestSetup):
    """Tests for list_new_titles."""

    def test_returns_qids_titles_not_in_translate_type(self, sqlite_db):
        sqlite_db.session.add(QidRecord(title="Foo", qid="Q1"))
        sqlite_db.session.add(QidRecord(title="Bar", qid="Q2"))
        sqlite_db.session.commit()
        self.service.add_translate_type("Bar")

        result = self.service.list_new_titles()
        assert "Foo" in result
        assert "Bar" not in result

    def test_returns_empty_when_all_titles_already_in_translate_type(self, sqlite_db):
        sqlite_db.session.add(QidRecord(title="Already_There", qid="Q3"))
        sqlite_db.session.commit()
        self.service.add_translate_type("Already_There")

        assert self.service.list_new_titles() == []

    def test_returns_empty_when_qids_table_empty(self, sqlite_db):
        assert self.service.list_new_titles() == []

    def test_returns_distinct_titles(self, sqlite_db):
        sqlite_db.session.add(QidRecord(title="Distinct_one", qid="Q4"))
        sqlite_db.session.commit()
        result = self.service.list_new_titles()
        assert result.count("Distinct_one") == 1
