"""
Integration tests for src/main_app/public/routes/td/translate_med.py.

Mirrors the PHP flow (translate_med.php): anonymous visitors get a login card,
missing arguments get an error page, and a logged-in translator is 302'd to
Special:ContentTranslation with an idempotent in_process insert.
"""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from src.main_app.database.services import (
    CategoryService,
    InProcessService,
    UsersNoInprocessService,
)
from src.main_app.services.auth.current_user import CurrentUser

ROUTE = "/Translation_Dashboard/translate_med/"
ENDPOINT = "https://mdwikicx.toolforge.org/w/index.php"

_PATCH_TARGET = "src.main_app.public.routes.td.translate_med.get_current_user"


@pytest.fixture
def seed_category():
    """Seed a category with a campaign so the cat -> campaign lookup resolves."""
    service = CategoryService()
    service.add_category(category="RTT", campaign="RTT", display="RTT")
    return service


@pytest.fixture
def logged_in(monkeypatch):
    """Authenticate the request as TestUser."""
    user = CurrentUser(
        user_id=12345,
        username="TestUser",
        access_token="",
        access_secret="",
    )
    monkeypatch.setattr(_PATCH_TARGET, lambda: user)
    return user


@pytest.fixture
def anonymous(monkeypatch):
    """Force the anonymous branch."""
    monkeypatch.setattr(_PATCH_TARGET, lambda: None)


@pytest.fixture
def in_process_service():
    return InProcessService()


def _count_rows(in_process_service: InProcessService, title: str, user: str, lang: str) -> int:
    return 1 if in_process_service.get_in_process_by_title_user_lang(title, user, lang) else 0


@pytest.mark.integration
class TestAnonymousRequest:
    """PHP lines 169-184: no user -> login card, then exit."""

    def test_renders_login_card(self, mock_client: FlaskClient, anonymous):
        response = mock_client.get(ROUTE, query_string={"title": "COVID-19", "langcode": "ar"})

        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "/auth/login" in body
        assert "Login" in body

    def test_creates_no_in_process_row(
        self,
        mock_client: FlaskClient,
        anonymous,
        in_process_service: InProcessService,
    ):
        mock_client.get(ROUTE, query_string={"title": "COVID-19", "langcode": "ar"})

        assert _count_rows(in_process_service, "COVID-19", "", "ar") == 0
        assert in_process_service.list_in_process() == []


@pytest.mark.integration
class TestMissingArguments:
    """PHP line 186: both title and code are required, otherwise an empty page."""

    @pytest.mark.parametrize(
        "params",
        [
            {"title": "COVID-19"},
            {"langcode": "ar"},
            {},
            {"title": "   ", "langcode": "  "},
            {"title": "undefined", "langcode": "undefined"},
        ],
    )
    def test_no_redirect_and_no_row(
        self,
        mock_client: FlaskClient,
        logged_in,
        in_process_service: InProcessService,
        params: dict,
    ):
        response = mock_client.get(ROUTE, query_string=params)

        assert response.status_code == 200
        assert response.headers.get("Location") is None
        assert in_process_service.list_in_process() == []

    def test_renders_warning(self, mock_client: FlaskClient, logged_in):
        response = mock_client.get(ROUTE)

        assert response.status_code == 200
        assert "langcode" in response.get_data(as_text=True)


@pytest.mark.integration
class TestValidRequest:
    """PHP lines 186-229: happy path."""

    def test_redirects_to_content_translation(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
        in_process_service: InProcessService,
    ):
        response = mock_client.get(
            ROUTE,
            query_string={
                "title": "COVID-19",
                "langcode": "AR",
                "cat": "RTT",
                "camp": "RTT",
                "tra_type": "lead",
                "word": "1200",
            },
        )

        assert response.status_code == 302
        location = response.headers["Location"]
        assert location.startswith(ENDPOINT)
        assert "from=mdwiki" in location
        assert "to=ar" in location  # lowercased, PHP strtolower
        assert "tr_type=lead" in location
        assert "campaign=RTT" in location
        assert "page=COVID-19" in location

        rows = in_process_service.list_in_process_by_user("TestUser")
        assert len(rows) == 1
        row = rows[0]
        assert row.title == "COVID-19"
        assert row.lang == "ar"
        assert row.cat == "RTT"
        assert row.translate_type == "lead"
        assert row.word == 1200

    def test_defaults_tra_type_to_lead(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
        in_process_service: InProcessService,
    ):
        response = mock_client.get(
            ROUTE,
            query_string={"title": "Tuberculosis", "langcode": "ar", "cat": "RTT"},
        )

        assert response.status_code == 302
        assert "tr_type=lead" in response.headers["Location"]
        assert in_process_service.list_in_process_by_user("TestUser")[0].translate_type == "lead"

    def test_empty_campaign_still_redirects(
        self,
        mock_client: FlaskClient,
        logged_in,
        in_process_service: InProcessService,
    ):
        # No cat and no camp: PHP leaves $camp empty and still builds the URL.
        response = mock_client.get(
            ROUTE,
            query_string={"title": "Tuberculosis", "langcode": "ar"},
        )

        assert response.status_code == 302
        assert "campaign=" in response.headers["Location"]
        assert _count_rows(in_process_service, "Tuberculosis", "TestUser", "ar") == 1

    def test_repeated_request_is_idempotent(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
        in_process_service: InProcessService,
    ):
        params = {"title": "COVID-19", "langcode": "ar", "cat": "RTT"}

        first = mock_client.get(ROUTE, query_string=params)
        second = mock_client.get(ROUTE, query_string=params)

        assert first.status_code == 302
        assert second.status_code == 302
        assert len(in_process_service.list_in_process_by_user("TestUser")) == 1


@pytest.mark.integration
class TestCampaignResolution:
    """PHP lines 207-209: camp = cats_data[cat] when camp is empty."""

    def test_campaign_resolved_from_category(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
    ):
        response = mock_client.get(
            ROUTE,
            query_string={"title": "COVID-19", "langcode": "ar", "cat": "RTT"},
        )

        assert response.status_code == 302
        assert "campaign=RTT" in response.headers["Location"]

    def test_explicit_campaign_wins(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
    ):
        response = mock_client.get(
            ROUTE,
            query_string={
                "title": "COVID-19",
                "langcode": "ar",
                "cat": "RTT",
                "camp": "COVID",
            },
        )

        assert response.status_code == 302
        assert "campaign=COVID" in response.headers["Location"]

    def test_unknown_category_yields_empty_campaign(
        self,
        mock_client: FlaskClient,
        logged_in,
    ):
        # PHP: $cats_data[$cat] ?? "" — a missing category is not an error.
        response = mock_client.get(
            ROUTE,
            query_string={"title": "COVID-19", "langcode": "ar", "cat": "Nope"},
        )

        assert response.status_code == 302
        assert "campaign=" in response.headers["Location"]


@pytest.mark.integration
class TestWordParsing:
    """PHP FILTER_VALIDATE_INT with min_range 0 and default 0."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("-5", 0),
            ("abc", 0),
            ("", 0),
            ("9999", 9999),
        ],
    )
    def test_word_is_clamped(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
        in_process_service: InProcessService,
        raw: str,
        expected: int,
    ):
        response = mock_client.get(
            ROUTE,
            query_string={"title": "COVID-19", "langcode": "ar", "word": raw},
        )

        assert response.status_code == 302
        row = in_process_service.list_in_process_by_user("TestUser")[0]
        assert row.word == expected


@pytest.mark.integration
class TestUsersNoInprocess:
    """PHP lines 216-218: active members skip the in_process insert."""

    def test_active_member_gets_no_row(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
        in_process_service: InProcessService,
    ):
        UsersNoInprocessService().add_users_no_inprocess("TestUser", is_active=1)

        response = mock_client.get(
            ROUTE,
            query_string={"title": "COVID-19", "langcode": "ar", "cat": "RTT"},
        )

        assert response.status_code == 302
        assert "page=COVID-19" in response.headers["Location"]
        assert in_process_service.list_in_process_by_user("TestUser") == []

    def test_inactive_member_gets_row(
        self,
        mock_client: FlaskClient,
        logged_in,
        seed_category,
        in_process_service: InProcessService,
    ):
        UsersNoInprocessService().add_users_no_inprocess("TestUser", is_active=0)

        mock_client.get(
            ROUTE,
            query_string={"title": "COVID-19", "langcode": "ar", "cat": "RTT"},
        )

        assert _count_rows(in_process_service, "COVID-19", "TestUser", "ar") == 1


@pytest.mark.integration
class TestInjection:
    """The PHP page interpolates the URL into raw HTML; the 302 must not."""

    def test_markup_in_title_stays_encoded(self, mock_client: FlaskClient, logged_in):
        response = mock_client.get(
            ROUTE,
            query_string={"title": "'\"><script>alert(1)</script>", "langcode": "ar"},
        )

        assert response.status_code == 302
        location = response.headers["Location"]
        assert "<script>" not in location
        assert "page=%27%22%3E%3Cscript%3Ealert%281%29%3C%2Fscript%3E" in location

    def test_no_header_injection(self, mock_client: FlaskClient, logged_in):
        response = mock_client.get(
            ROUTE,
            query_string={"title": "Foo\r\nSet-Cookie:[REDACTED]"}
            )

        assert response.status_code == 302
        location = response.headers["Location"]
        assert "\r" not in location
        assert "\n" not in location
        assert "Set-Cookie" not in location

    def test_redirect_body_is_escaped(self, mock_client: FlaskClient, logged_in):
        response = mock_client.get(
            ROUTE,
            query_string={"title": "'\"><script>alert(1)</script>", "langcode": "ar"},
        )

        body = response.get_data(as_text=True)
        assert "<script>alert(1)</script>" not in body
