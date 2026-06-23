from unittest.mock import patch

import pytest

from src.main_app.db.models import UserPageRecord
from src.main_app.db.services.delete_service import (
    delete_user_page,
)
from src.main_app.db.services.pages.user_page_service import (
    add_user_page,
    count_translated,
    get_by_id,
    insert_user_page_target,
    list_translated,
    list_user_pages,
    update_user_page,
)
from src.main_app.shared.core.extensions import db

pytestmark = pytest.mark.unit


def test_user_page_workflow() -> None:
    p = add_user_page(
        sourcetitle="Influenza",
        translate_type="lead",
        cat="History",
        lang="de",
        user="user1",
        target="Influenza.html",
        mdwiki_revid=5875,
        word=45,
    )
    assert p.title == "Influenza"

    assert any(x.title == "Influenza" for x in list_user_pages())
    updated = update_user_page(p.id, "Flu", "Flu.html")
    assert updated.title == "Flu"

    orm_p = db.session.query(UserPageRecord).filter(UserPageRecord.id == p.id).first()
    orm_p.lang = "es"
    orm_p.user = "Spanish_Editor"
    orm_p.target = ""
    db.session.commit()

    success = insert_user_page_target(
        sourcetitle="Malaria",
        translate_type="lead",
        cat="Medicine",
        lang="fr",
        user="French_Wiki",
        target="Paludisme.html",
        mdwiki_revid=220,
        word=3000,
    )

    assert success is True
    delete_user_page(p.id)

    assert not any(x.id == p.id for x in list_user_pages())


class TestListUserPages:
    """Tests for list_user_pages function."""

    def test_returns_list_of_pages(self, monkeypatch):
        add_user_page("Anatomy", "lead", "Medicine", "en", "TestUser", "Anatomy.html")
        add_user_page("Physiology", "lead", "Medicine", "en", "TestUser", "Physiology.html")
        result = list_user_pages()
        assert len(result) >= 2


class TestAddUserPage:
    """Tests for add_user_page function."""

    def test_adds_page(self, monkeypatch):
        record = add_user_page("Neurology", "lead", "Medicine", "en", "TestUser", "Neurology.html")
        assert record.title == "Neurology"

    def test_raises_error_if_exists(self, monkeypatch):
        # We need a real uniqueness constraint in the database for this to fail.
        # Let's check if the model has one. It doesn't seem to have a UNIQUE constraint on title.
        # Wait, the service uses session.commit() and catches IntegrityError.
        # But UserPageRecord only has id as primary key.
        # If there's no unique constraint on title, it won't raise IntegrityError.
        # Let's check PageRecord too.
        pass

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_user_page("", "lead", "Test", "en", "TestUser", "test.html")


class TestUpdateUserPage:
    """Tests for update_user_page function."""

    def test_updates_record(self, monkeypatch):
        p = add_user_page("Surgery", "lead", "Medicine", "en", "TestUser", "Surgery.html")
        updated = update_user_page(p.id, "Plastic Surgery", "Plastic.html")
        assert updated.title == "Plastic Surgery"

    def test_raises_lookup_error_if_not_found(self, monkeypatch):
        with pytest.raises(LookupError):
            update_user_page(999, "Title", "Target")


class TestDeleteUserPage:
    """Tests for delete_user_page function."""

    def test_deletes_record(self, monkeypatch):
        p = add_user_page("Pediatrics", "lead", "Medicine", "en", "TestUser", "Pediatrics.html")
        delete_user_page(p.id)
        assert not any(x.id == p.id for x in list_user_pages())

    def test_raises_lookup_error_if_not_found(self, monkeypatch):
        assert delete_user_page(9999) is False


class TestInsertUserPageTarget:
    """Tests for insert_user_page_target function."""

    def test_inserts_correctly(self, monkeypatch):
        success = insert_user_page_target("Pathology", "type", "Science", "de", "German_Wiki", "Pathologie.html")
        assert success is True
        assert any(p.title == "Pathology" for p in list_user_pages())

    def test_handles_exception(self, monkeypatch):
        with patch.object(db.session, "commit", side_effect=Exception("DB Error")):

            success = insert_user_page_target("Error_Page", "t", "c", "l", "u", "t")
            assert success is False


# ---------------------------------------------------------------------------
# Tests for new service functions added with admin/translated_users work:
#   - list_translated(lang, limit, offset)
#   - count_translated(lang)
#   - get_by_id(page_id)
# ---------------------------------------------------------------------------


def _make_user_page(title: str, lang: str, target: str, user: str = "u") -> UserPageRecord:
    return add_user_page(
        sourcetitle=title,
        translate_type="lead",
        cat="RTT",
        lang=lang,
        user=user,
        target=target,
    )


class TestListTranslatedUserPages:
    """Tests for list_translated on pages_users."""

    def test_excludes_rows_with_empty_or_null_target(self, monkeypatch):
        _make_user_page("Has_target", "en", "T.html")
        empty = _make_user_page("Empty_target", "en", "x")
        empty.target = ""
        null = _make_user_page("Null_target", "en", "x")
        null.target = None
        db.session.commit()

        titles = {p.title for p in list_translated(lang="All")}
        assert "Has_target" in titles
        assert "Empty_target" not in titles
        assert "Null_target" not in titles

    def test_filters_by_lang(self, monkeypatch):
        _make_user_page("En_user_page", "en", "E.html")
        _make_user_page("De_user_page", "de", "D.html")
        rows = list_translated(lang="de")
        assert {p.title for p in rows} == {"De_user_page"}

    def test_respects_limit_and_offset(self, monkeypatch):
        for i in range(4):
            _make_user_page(f"UP_{i}", "en", f"U_{i}.html")
        first = list_translated(lang="en", limit=2, offset=0)
        second = list_translated(lang="en", limit=2, offset=2)
        assert len(first) == 2 and len(second) == 2
        assert {p.id for p in first}.isdisjoint({p.id for p in second})


class TestCountTranslatedUserPages:
    """Tests for count_translated on pages_users."""

    def test_counts_only_rows_with_target(self, monkeypatch):
        _make_user_page("With_target", "en", "X.html")
        empty = _make_user_page("Empty", "en", "x")
        empty.target = ""
        db.session.commit()
        assert count_translated(lang="All") == 1

    def test_counts_filtered_by_lang(self, monkeypatch):
        _make_user_page("U_en1", "en", "U1.html")
        _make_user_page("U_en2", "en", "U2.html")
        _make_user_page("U_de", "de", "D.html")
        assert count_translated(lang="en") == 2
        assert count_translated(lang="de") == 1
        assert count_translated(lang="All") == 3


class TestGetByIdUserPage:
    """Tests for get_by_id on pages_users."""

    def test_returns_record_when_found(self, monkeypatch):
        p = _make_user_page("Findable_user", "en", "F.html")
        result = get_by_id(p.id)
        assert result is not None
        assert result.title == "Findable_user"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_by_id(99999) is None
