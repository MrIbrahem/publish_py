"""Unit tests for the ``pages_users_to_main_service`` admin helpers.

Mirrors the PHP ``coordinator/admin/pages_users_to_main/*.php`` flow:
- ``list_pending(lang)`` -> joined view of pages_users + pages_users_to_main
- ``get_user_page(id)``
- ``check_main_page_exists(title, lang)``
- ``delete_user_page_to_main(id)`` -> removes from BOTH pages_users_to_main and pages_users
"""

import pytest

from src.main_app.database.models import (
    PageRecord,
    PagesUsersToMainRecord,
    QidRecord,
    UserPageRecord,
)
from src.main_app.database.services import (
    PagesUsersToMainPagesService,
    UserPagesService,
)
from src.main_app.extensions import db

pytestmark = pytest.mark.unit


def _seed_pending(
    title: str,
    lang: str,
    user: str = "old_user",
    target: str = "Old_target.html",
    new_user: str = "new_user",
    new_target: str = "New_target.html",
    new_qid: str = "Q9",
    pupdate: str = "2026-01-01",
) -> UserPageRecord:
    """Insert a UserPageRecord plus its PagesUsersToMainRecord override."""
    user_page = UserPageRecord(
        title=title,
        translate_type="lead",
        cat="RTT",
        lang=lang,
        user=user,
        target=target,
        pupdate=pupdate,
    )
    db.session.add(user_page)
    db.session.flush()  # populate user_page.id

    db.session.add(
        PagesUsersToMainRecord(
            id=user_page.id,
            new_user=new_user,
            new_target=new_target,
            new_qid=new_qid,
        )
    )
    db.session.commit()
    return user_page


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = PagesUsersToMainPagesService()
        self.user_pages_service = UserPagesService()


class TestListPending(TestSetup):
    """Tests for self.service.list_pending."""

    def test_returns_joined_rows(self, sqlite_db):
        page = _seed_pending("Foo", "en")
        # Provide a qid so the outer-join fills the ``qid`` column.
        sqlite_db.session.add(QidRecord(title="Foo", qid="Q1"))
        sqlite_db.session.commit()

        rows = self.service.list_pending(lang="All")
        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == page.id
        assert row["title"] == "Foo"
        assert row["lang"] == "en"
        assert row["user"] == "old_user"
        assert row["target"] == "Old_target.html"
        assert row["new_user"] == "new_user"
        assert row["new_target"] == "New_target.html"
        assert row["new_qid"] == "Q9"
        assert row["qid"] == "Q1"
        assert row["pupdate"] == "2026-01-01"

    def test_excludes_user_pages_without_to_main_row(self, sqlite_db):
        # A pages_users row WITHOUT a matching pages_users_to_main row must
        # not appear (the inner join filters it out).
        sqlite_db.session.add(
            UserPageRecord(
                title="No_override",
                translate_type="lead",
                cat="RTT",
                lang="en",
                user="u",
                target="t",
            )
        )
        _seed_pending("Has_override", "en")
        sqlite_db.session.commit()

        titles = {r["title"] for r in self.service.list_pending(lang="All")}
        assert titles == {"Has_override"}

    def test_filters_by_lang(self):
        _seed_pending("English_one", "en")
        _seed_pending("French_one", "fr")
        rows = self.service.list_pending(lang="fr")
        assert {r["title"] for r in rows} == {"French_one"}

    def test_lang_all_returns_every_language(self):
        _seed_pending("English_one", "en")
        _seed_pending("French_one", "fr")
        titles = {r["title"] for r in self.service.list_pending(lang="All")}
        assert titles == {"English_one", "French_one"}

    def test_qid_is_empty_string_when_no_match(self):
        _seed_pending("Without_qid", "en")  # no QidRecord seeded
        rows = self.service.list_pending()
        assert rows[0]["qid"] == ""

    def test_returns_empty_when_no_pending_rows(self):
        assert self.service.list_pending() == []


class TestGetUserPage(TestSetup):
    """Tests for self.service.get_user_page."""

    def test_returns_user_page_record(self):
        page = _seed_pending("Foo", "en")
        result = self.service.get_user_page(page.id)
        assert result is not None
        assert isinstance(result, UserPageRecord)
        assert result.title == "Foo"

    def test_returns_none_when_id_missing(self):
        assert self.service.get_user_page(99999) is None

    def test_returns_none_when_id_is_falsy(self):
        assert self.service.get_user_page(0) is None
        assert self.service.get_user_page(None) is None  # type: ignore[arg-type]


class TestCheckMainPageExists(TestSetup):
    """Tests for self.service.check_main_page_exists."""

    def test_returns_record_when_main_page_with_target_exists(self, sqlite_db):
        sqlite_db.session.add(
            PageRecord(
                title="Foo",
                translate_type="lead",
                cat="RTT",
                lang="en",
                user="u",
                target="real_target.html",
            )
        )
        sqlite_db.session.commit()
        result = self.service.check_main_page_exists("Foo", "en")
        assert result is not None
        assert result.target == "real_target.html"

    def test_returns_none_when_target_is_empty(self, sqlite_db):
        sqlite_db.session.add(
            PageRecord(
                title="Empty",
                translate_type="lead",
                cat="RTT",
                lang="en",
                user="u",
                target="",
            )
        )
        sqlite_db.session.commit()
        assert self.service.check_main_page_exists("Empty", "en") is None

    def test_returns_none_when_target_is_null(self, sqlite_db):
        sqlite_db.session.add(
            PageRecord(
                title="Null_target",
                translate_type="lead",
                cat="RTT",
                lang="en",
                user="u",
                target=None,
            )
        )
        sqlite_db.session.commit()
        assert self.service.check_main_page_exists("Null_target", "en") is None

    def test_returns_none_when_no_match(self):
        assert self.service.check_main_page_exists("Ghost", "en") is None

    def test_returns_none_when_lang_or_title_blank(self):
        assert self.service.check_main_page_exists("", "en") is None
        assert self.service.check_main_page_exists("Foo", "") is None


class TestDeleteUserPage(TestSetup):
    """Tests for delete_user_page_to_main."""

    def test_removes_both_rows(self):
        page_record = UserPageRecord(
            title="title",
            translate_type="lead",
            cat="RTT",
            lang="ar",
            user="test",
            target="target",
        )
        page = self.user_pages_service.add_record(page_record)

        page_id = page.id

        record = PagesUsersToMainRecord(
            id=page_id,
            new_target="new_target",
            new_user="test",
            new_qid="Q88",
        )
        self.service.add_record(record)

        ok = self.service.delete_user_page_to_main(page_id)

        assert ok is True

        assert self.service.get_record_by_id(page_id) is None

        # TODO: need to check that the page record is deleted
        assert self.user_pages_service.get_record_by_id(page_id) is None

    def test_returns_true_when_user_page_only(self, sqlite_db):
        # PHP path: even if only the pages_users row is present, the deletion
        # should succeed (both queries are issued, idempotent).
        page = UserPageRecord(
            title="Lonely",
            translate_type="lead",
            cat="RTT",
            lang="en",
            user="u",
            target="t",
        )
        self.user_pages_service.add_record(page)

        page_id = page.id  # capture before delete; ORM proxy raises after.

        ok = self.user_pages_service.delete(page_id)
        assert ok is True
        assert self.user_pages_service.get_record_by_id(page_id) is None

    def test_returns_false_when_id_is_falsy(self):
        assert self.service.delete(0) is False
