"""Unit tests for ExistsItem and InProcessItem row builders and mapping."""

import pytest
from flask import Flask

from src.main_app.public.routes.td.results_2026.rows.mapping import ExistsItem, InProcessItem, Stats


@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"

    @app.route("/auth/login", endpoint="auth.login")
    def login():
        return "login"

    return app


def test_exists_item_from_row_and_render(test_app):
    item = ExistsItem.from_row(
        title="COVID-19_pandemic",
        counter=1,
        target_tab={"target": "جائحة_فيروس_كورونا", "via": "td", "qid": "Q842631"},
        user_coord=True,
        endpoint="https://mdwikicx.toolforge.org/w/index.php",
    )

    assert item.counter == 1
    assert item.display_title == "COVID-19 pandemic"
    assert item.target == "جائحة_فيروس_كورونا"
    assert item.via == "td"
    assert item.qid == "Q842631"

    with test_app.test_request_context():
        rendered = item.render(
            langcode="ar",
            cat="Medicine",
            camp="mdwiki",
            full_tr_user=False,
            is_authenticated=True,
        )
        rendered_str = str(rendered)
        assert "COVID-19 pandemic" in rendered_str
        assert "Translate" in rendered_str
        assert "Q842631" in rendered_str
        assert "ar.wikipedia.org" in rendered_str

        # Test unauthenticated render
        rendered_unauth = item.render(
            langcode="ar",
            cat="Medicine",
            camp="mdwiki",
            full_tr_user=False,
            is_authenticated=False,
        )
        assert "Login" in str(rendered_unauth)


def test_in_process_item_from_row_and_render(test_app):
    item = InProcessItem.from_row(
        title="COVID-19 pandemic",
        counter=2,
        title_tab={"translate_type": "lead", "user": "TestUser", "add_date": "2026-01-01 12:00:00"},
        title_data={
            "w_lead_words": 100,
            "w_all_words": 500,
            "r_lead_refs": 5,
            "r_all_refs": 20,
            "importance": "Top",
            "en_views": "1000",
            "qid": "Q842631",
        },
        inprocess_button="1",
        endpoint="https://mdwikicx.toolforge.org/w/index.php",
    )

    assert item.counter == 2
    assert item.title == "COVID-19 pandemic"
    assert item.importance == "Top"
    assert item.en_views == "1000"
    assert item.qid == "Q842631"
    assert item.user == "TestUser"
    assert item.date == "2026-01-01"

    with test_app.test_request_context():
        rendered = item.render(
            langcode="ar",
            cat="Medicine",
            camp="mdwiki",
            full_tr_user=True,
            is_authenticated=True,
        )
        rendered_str = str(rendered)
        assert "COVID-19 pandemic" in rendered_str
        assert "Lead" in rendered_str
        assert "Full" in rendered_str
        assert "TestUser" in rendered_str
        assert "2026-01-01" in rendered_str

        # Unauthenticated render
        rendered_unauth = item.render(
            langcode="ar",
            cat="Medicine",
            camp="mdwiki",
            full_tr_user=True,
            is_authenticated=False,
        )
        assert "Login" in str(rendered_unauth)
