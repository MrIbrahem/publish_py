"""
Integration tests for src/main_app/public/routes/td/td_route.py.

Covers the four MethodView endpoints (index / table / missing / results_api)
that replaced the legacy ``TDRoutes`` function-based handlers. Endpoint names
are asserted so a future rename cannot silently break ``url_for`` calls in the
templates.
"""

from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.main_app.database.services import (
    CategoryService,
    LangService,
    SettingsService,
)

_TD_PREFIX = "/Translation_Dashboard"

_PATCH_TARGET = "src.main_app.public.routes.td.td_route.get_current_user"


@pytest.fixture
def seed_langs():
    """Seed two languages so the filter form and code lookups resolve."""
    service = LangService()
    service.add_lang(code="ar", autonym="العربية", name="Arabic")
    service.add_lang(code="en", autonym="English", name="English")
    return service


@pytest.fixture
def seed_category():
    """Seed a category bound to a campaign."""
    service = CategoryService()
    service.add_category(category="RTT", campaign="RTT", display="RTT")
    return service


@pytest.fixture
def logged_in(monkeypatch):
    """Authenticate the request as TestUser."""
    from src.main_app.services.auth.current_user import CurrentUser

    user = CurrentUser(user_id=12345, username="TestUser", access_token="", access_secret="")
    monkeypatch.setattr(_PATCH_TARGET, lambda: user)
    return user


@pytest.fixture
def anonymous(monkeypatch):
    """Force the anonymous branch."""
    monkeypatch.setattr(_PATCH_TARGET, lambda: None)


@pytest.mark.integration
class TestEndpointNames:
    """The templates call url_for('td.index') / url_for('td.table'); keep them."""

    def test_index_endpoint_resolves(self, mock_app: Flask):
        with mock_app.test_request_context():
            from flask import url_for

            assert url_for("td.index") == _TD_PREFIX + "/"

    def test_table_endpoint_resolves(self, mock_app: Flask):
        with mock_app.test_request_context():
            from flask import url_for

            assert url_for("td.table") == _TD_PREFIX + "/table"

    def test_missing_endpoint_resolves(self, mock_app: Flask):
        with mock_app.test_request_context():
            from flask import url_for

            assert url_for("td.missing") == _TD_PREFIX + "/missing"

    def test_results_api_endpoint_resolves(self, mock_app: Flask):
        with mock_app.test_request_context():
            from flask import url_for

            assert url_for("td.results_api") == _TD_PREFIX + "/results_api"


@pytest.mark.integration
class TestIndexView:
    """GET / — dashboard landing page with the filter form."""

    def test_returns_200_and_html(self, mock_client: FlaskClient, anonymous, seed_langs, seed_category):
        response = mock_client.get(f"{_TD_PREFIX}/")

        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

    def test_renders_seeded_campaigns(self, mock_client: FlaskClient, anonymous, seed_langs, seed_category):
        body = mock_client.get(f"{_TD_PREFIX}/").get_data(as_text=True)

        assert "RTT" in body
        assert "Arabic" in body

    def test_unknown_code_is_flashed_not_raised(
        self,
        mock_client: FlaskClient,
        anonymous,
        seed_langs,
        seed_category,
    ):
        # load_request.php flashes "code (xx) not valid wiki." instead of erroring.
        response = mock_client.get(f"{_TD_PREFIX}/", query_string={"code": "xx", "camp": "RTT"})

        assert response.status_code == 200
        assert "not valid wiki" in response.get_data(as_text=True)

    def test_invalid_campaign_is_flashed(
        self,
        mock_client: FlaskClient,
        anonymous,
        seed_langs,
        seed_category,
    ):
        response = mock_client.get(f"{_TD_PREFIX}/", query_string={"camp": "Nope"})

        assert response.status_code == 200
        assert "not valid" in response.get_data(as_text=True)


@pytest.mark.integration
class TestTableView:
    """GET /table — dashboard plus the results card."""

    def test_returns_200_without_results(
        self,
        mock_client: FlaskClient,
        anonymous,
        seed_langs,
        seed_category,
    ):
        # No code/camp pair -> results bundle stays None and the page still renders.
        response = mock_client.get(f"{_TD_PREFIX}/table")

        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

    def test_renders_form_action_url(
        self,
        mock_client: FlaskClient,
        anonymous,
        seed_langs,
        seed_category,
    ):
        # templates/td/form.html posts to url_for('td.table').
        body = mock_client.get(f"{_TD_PREFIX}/table").get_data(as_text=True)

        assert f'action="{_TD_PREFIX}/table"' in body

    def test_results_loader_failure_is_flashed(
        self,
        mock_client: FlaskClient,
        anonymous,
        seed_langs,
        seed_category,
        mocker,
    ):
        # A loader crash must degrade to a flash, not a 500.
        mocker.patch(
            "src.main_app.public.routes.td.td_route.ResultsLoader.load",
            side_effect=RuntimeError("boom"),
        )

        response = mock_client.get(
            f"{_TD_PREFIX}/table",
            query_string={"code": "ar", "camp": "RTT"},
        )

        assert response.status_code == 200
        assert "Failed to load results" in response.get_data(as_text=True)


@pytest.mark.integration
class TestMissingView:
    """GET /missing — top languages by missing articles."""

    def test_returns_200(self, mock_client: FlaskClient, anonymous):
        response = mock_client.get(f"{_TD_PREFIX}/missing")

        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

    def test_defaults_category_to_rtt(self, mock_client: FlaskClient, anonymous):
        body = mock_client.get(f"{_TD_PREFIX}/missing").get_data(as_text=True)

        # PHP: $category = $_GET['cat'] ?? 'RTT'
        assert "RTT" in body

    def test_respects_category_argument(self, mock_client: FlaskClient, anonymous):
        body = mock_client.get(f"{_TD_PREFIX}/missing", query_string={"cat": "WikiProjectMed"}).get_data(as_text=True)

        assert "WikiProjectMed" in body

    def test_service_failure_still_renders(
        self,
        mock_client: FlaskClient,
        anonymous,
        mocker,
    ):
        mocker.patch(
            "src.main_app.public.routes.td.td_route.MissingStatsService.statics_by_category",
            side_effect=RuntimeError("boom"),
        )

        response = mock_client.get(f"{_TD_PREFIX}/missing")

        assert response.status_code == 200


@pytest.mark.integration
class TestResultsApiView:
    """GET /results_api — JSON payload for AJAX clients."""

    def test_returns_json(self, mock_client: FlaskClient, anonymous):
        response = mock_client.get(
            f"{_TD_PREFIX}/results_api",
            query_string={"code": "ar", "camp": "RTT", "depth": "0"},
        )

        assert response.status_code == 200
        assert response.content_type.startswith("application/json")
        payload = response.get_json()
        assert "execution_time" in payload
        assert "results" in payload

    def test_returns_500_on_failure(self, mock_client: FlaskClient, anonymous, mocker):
        mocker.patch(
            "src.main_app.public.routes.td.td_route.results_api_result",
            side_effect=RuntimeError("boom"),
        )

        response = mock_client.get(f"{_TD_PREFIX}/results_api")

        assert response.status_code == 500
        assert response.get_json() == {"error": "Failed to load results"}

    def test_missing_params_do_not_crash(self, mock_client: FlaskClient, anonymous):
        response = mock_client.get(f"{_TD_PREFIX}/results_api")

        assert response.status_code in (200, 500)


@pytest.mark.integration
class TestSettingsIntegration:
    """allow_type_of_translate toggles the tra_type widget (templates/td/form.html)."""

    def test_disabled_hides_type_widget(
        self,
        mock_client: FlaskClient,
        anonymous,
        seed_langs,
        seed_category,
    ):
        service = SettingsService()
        service.create_setting("allow_type_of_translate", "Allow type of translate", value_type="boolean", value="0")

        body = mock_client.get(f"{_TD_PREFIX}/table").get_data(as_text=True)

        # {% else %} branch: hidden input pins tra_type to "lead".
        assert 'name="tra_type" value="lead"' in body
        assert 'id="customRadio2"' not in body

    def test_enabled_shows_type_widget(
        self,
        mock_client: FlaskClient,
        anonymous,
        seed_langs,
        seed_category,
    ):
        service = SettingsService()
        service.create_setting("allow_type_of_translate", "Allow type of translate", value_type="boolean", value="1")

        body = mock_client.get(f"{_TD_PREFIX}/table").get_data(as_text=True)

        # {% if settings.allow_type_of_translate %} branch: radio group rendered.
        assert 'id="customRadio2"' in body
