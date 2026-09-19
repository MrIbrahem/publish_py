"""Unit tests for BaseItem, MissingItem, ExistsItem, InProcessItem, and table renderers."""

import pytest
from flask import Flask

from src.main_app.public.routes.td.results_2026.rows.mapping import (
    BaseItem,
    ExistsItem,
    InProcessItem,
    MissingItem,
    Stats,
)
from src.main_app.public.routes.td.results_2026.tables import (
    ExistsTable,
    InProcessTable,
    MissingTable,
)


@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"

    @app.route("/auth/login", endpoint="auth.login")
    def login():
        return "login"

    return app


def test_base_item_properties():
    item = BaseItem(counter=1, title="COVID-19_pandemic_<script>", qid="Q842631")
    assert item.display_title == "COVID-19 pandemic <script>"
    assert item.encoded_title == "COVID-19_pandemic_&lt;script&gt;"
    assert not item.is_video

    video_item = BaseItem(counter=2, title="video:How_vaccines_work", qid="Q123")
    assert video_item.is_video


def test_missing_item_rendering(test_app):
    item = MissingItem.from_row(
        title="COVID-19 pandemic",
        counter=1,
        row={
            "w_lead_words": 100,
            "w_all_words": 500,
            "r_lead_refs": 5,
            "r_all_refs": 20,
            "en_views": "25000",
            "importance": "Top",
            "qid": "Q842631",
        },
        tra_type="lead",
        is_full_row=False,
    )

    assert item.n == "1"
    assert not item.is_video

    with test_app.test_request_context():
        # Unauthenticated user
        unauth_html = str(item.render("ar", "Medicine", "mdwiki", False, is_authenticated=False))
        assert "btn-sm" in unauth_html
        assert "Login" in unauth_html

        # Authenticated user, lead translation only
        auth_html = str(item.render("ar", "Medicine", "mdwiki", False, is_authenticated=True))
        assert "Translate" in auth_html
        assert "Q842631" in auth_html

        # Authenticated user, full_tr_user=True
        full_html = str(item.render("ar", "Medicine", "mdwiki", True, is_authenticated=True))
        assert "Lead" in full_html
        assert "Full" in full_html

    # Full row formatting
    full_item = MissingItem.from_row(
        title="COVID-19 pandemic",
        counter=1,
        row={"w_lead_words": 100, "w_all_words": 500, "r_lead_refs": 5, "r_all_refs": 20},
        tra_type="all",
        is_full_row=True,
    )
    assert full_item.n == "1.Full"


def test_missing_item_video_suppresses_full(test_app):
    item = MissingItem.from_row(
        title="Video:COVID-19_prevention",
        counter=3,
        row={"w_lead_words": 50, "w_all_words": 50, "r_lead_refs": 2, "r_all_refs": 2},
        tra_type="all",
        is_full_row=True,
    )
    assert item.is_video
    assert item.n == "3"  # No .Full suffix for videos

    with test_app.test_request_context():
        auth_html = str(item.render("ar", "Medicine", "mdwiki", True, is_authenticated=True))
        assert "Translate" in auth_html
        assert "Full" not in auth_html


def test_exists_item_rendering(test_app):
    item = ExistsItem.from_row(
        title="COVID-19_pandemic",
        counter=1,
        target_tab={"target": "جائحة_فيروس_كورونا", "via": "td", "qid": "Q842631"},
        user_coord=True,
        endpoint="https://mdwikicx.toolforge.org/w/index.php",
    )

    assert item.display_title == "COVID-19 pandemic"
    assert item.encoded_title == "COVID-19_pandemic"

    with test_app.test_request_context():
        # Unauthenticated
        unauth_html = str(item.render("ar", "Medicine", "mdwiki", False, is_authenticated=False))
        assert "Login" in unauth_html

        # Authenticated with user_coord=True
        coord_html = str(item.render("ar", "Medicine", "mdwiki", False, is_authenticated=True))
        assert "Translate" in coord_html
        assert "ar.wikipedia.org" in coord_html

        # Authenticated with user_coord=False
        no_coord_item = ExistsItem.from_row(
            title="COVID-19_pandemic",
            counter=1,
            target_tab={"target": "جائحة_فيروس_كورونا", "via": "other", "qid": "Q842631"},
            user_coord=False,
            endpoint="https://mdwikicx.toolforge.org/w/index.php",
        )
        no_coord_html = str(no_coord_item.render("ar", "Medicine", "mdwiki", False, is_authenticated=True))
        assert "Translate" not in no_coord_html


def test_exists_item_empty_fields(test_app):
    item = ExistsItem.from_row(
        title="",
        counter=1,
        target_tab={},
        user_coord=False,
        endpoint="",
    )
    assert item.display_title == ""
    assert item.qid == ""
    assert item.target == ""

    with test_app.test_request_context():
        rendered = str(item.render("ar", "cat", "camp", False, is_authenticated=True))
        assert "<tr>" in rendered


def test_in_process_item_rendering(test_app):
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

    assert item.user == "TestUser"
    assert item.date == "2026-01-01"

    with test_app.test_request_context():
        # Authenticated, full_tr_user=True
        auth_html = str(item.render("ar", "Medicine", "mdwiki", True, is_authenticated=True))
        assert "Lead" in auth_html
        assert "Full" in auth_html
        assert "TestUser" in auth_html

        # inprocess_button != "1"
        disabled_item = InProcessItem.from_row(
            title="COVID-19 pandemic",
            counter=2,
            title_tab={"translate_type": "lead", "user": "TestUser", "date": "2026-01-01"},
            title_data={},
            inprocess_button="0",
            endpoint="",
        )
        disabled_html = str(disabled_item.render("ar", "Medicine", "mdwiki", True, is_authenticated=True))
        assert "Translate" not in disabled_html
        assert "Lead" not in disabled_html


def test_table_renderers(test_app):
    missing_item = MissingItem.from_row(
        title="COVID-19 pandemic",
        counter=1,
        row={"w_lead_words": 100, "w_all_words": 500, "r_lead_refs": 5, "r_all_refs": 20, "qid": "Q842631"},
        tra_type="lead",
        is_full_row=False,
    )
    inprocess_item = InProcessItem.from_row(
        title="Asthma",
        counter=1,
        title_tab={"user": "UserA", "date": "2026-01-01"},
        title_data={"qid": "Q35865"},
        inprocess_button="1",
        endpoint="https://mdwikicx.toolforge.org/w/index.php",
    )
    exists_item = ExistsItem.from_row(
        title="Diabetes",
        counter=1,
        target_tab={"target": "السكري", "via": "td", "qid": "Q12206"},
        user_coord=True,
        endpoint="https://mdwikicx.toolforge.org/w/index.php",
    )

    with test_app.test_request_context():
        missing_table_html = str(
            MissingTable.render(
                rows=[missing_item],
                code="ar",
                cat="Medicine",
                camp="mdwiki",
                full_tr_user=False,
                is_authenticated=True,
            )
        )
        assert "<table" in missing_table_html
        assert "COVID-19 pandemic" in missing_table_html

        inprocess_table_html = str(
            InProcessTable.render(
                rows=[inprocess_item],
                code="ar",
                cat="Medicine",
                camp="mdwiki",
                full_tr_user=False,
                is_authenticated=True,
            )
        )
        assert "<table" in inprocess_table_html
        assert "Asthma" in inprocess_table_html

        exists_table_html = str(
            ExistsTable.render(
                rows=[exists_item],
                translated_count=1,
                translated_before_count=0,
                code="ar",
                cat="Medicine",
                camp="mdwiki",
                full_tr_user=False,
                is_authenticated=True,
            )
        )
        assert "<table" in exists_table_html
        assert "Diabetes" in exists_table_html
        assert "Translated (1)" in exists_table_html


def test_stats_from_row():
    row = {"w_lead_words": 10, "w_all_words": 50, "r_lead_refs": 2, "r_all_refs": 5}
    words = Stats.from_row(row, "words")
    refs = Stats.from_row(row, "refs")
    assert words.lead == 10
    assert words.all == 50
    assert refs.lead == 2
    assert refs.all == 5
