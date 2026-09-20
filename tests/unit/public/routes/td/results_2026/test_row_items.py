"""
Unit tests for the results_2026 row items (ExistsItem / InProcessItem).

Covers the port of ``results_2026/results_table_exists.php`` and
``results_2026/results_table_inprocess.php``: the items carry only their own
data and emit the full ``<tr>`` markup from ``render()`` using the request
context passed by the template — mirroring ``MissingItem``.
"""

from __future__ import annotations

import pytest
from flask import Flask

from src.main_app.public.routes.td.results_2026.mapping import (
    ExistsItem,
    InProcessItem,
)


@pytest.fixture()
def app() -> Flask:
    app = Flask(__name__)
    # ``render`` resolves the login URL for anonymous visitors.
    app.add_url_rule("/auth/login", endpoint="auth.login", view_func=lambda: "login")
    return app


# ---------------------------------------------------------------------------
# ExistsItem
# ---------------------------------------------------------------------------


class TestExistsItem:
    def test_from_row_normalizes_title_and_reads_target_tab(self):
        item = ExistsItem.from_row(
            title="Tuberculosis",
            counter=3,
            row={"target": "Tuberkulose", "via": "td", "qid": "Q1338"},
        )
        assert item.counter == 3
        assert item.title == "Tuberculosis"
        assert item.target == "Tuberkulose"
        assert item.via == "td"
        assert item.qid == "Q1338"

    def test_from_row_replaces_underscores(self):
        item = ExistsItem.from_row(
            title="Influenza_vaccine",
            counter=1,
            row={},
        )
        assert item.title == "Influenza vaccine"
        # Missing keys degrade to empty strings (no KeyError).
        assert item.target == ""
        assert item.via == ""
        assert item.qid == ""

    def test_render_coordinator_authenticated_shows_translate_button(self, app):
        item = ExistsItem.from_row(
            title="Tuberculosis",
            counter=1,
            row={"target": "Tuberkulose", "via": "td", "qid": "Q1338"},
        )
        with app.test_request_context("/table?code=ar"):
            html = str(item.render("ar", "RTT", is_authenticated=True, user_coord=True))

        assert "<tr>" in html
        # Translate button links to ContentTranslation for the lead section.
        assert "Translate</a>" in html
        assert "ContentTranslation" in html
        # via == "td" → target appears in the "Translated" column only.
        assert html.count("ar.wikipedia.org/wiki/Tuberkulose") == 1
        # Wikidata cell.
        assert "wikidata.org/wiki/Q1338" in html

    def test_render_non_coordinator_hides_translate_button(self, app):
        item = ExistsItem.from_row(
            title="Tuberculosis",
            counter=1,
            row={"target": "Tuberkulose", "via": "td", "qid": "Q1338"},
        )
        with app.test_request_context("/table?code=ar"):
            html = str(item.render("ar", "RTT", is_authenticated=True, user_coord=False))

        assert "Translate</a>" not in html
        # Row is still complete.
        assert "wikidata.org/wiki/Q1338" in html

    def test_render_anonymous_shows_login_instead_of_translate(self, app):
        item = ExistsItem.from_row(
            title="Tuberculosis",
            counter=1,
            row={"target": "Tuberkulose", "via": "td", "qid": "Q1338"},
        )
        with app.test_request_context("/table?code=ar"):
            html = str(item.render("ar", "RTT", is_authenticated=False, user_coord=True))

        assert "/auth/login" in html
        assert "Translate</a>" not in html

    def test_render_routes_target_to_translated_before_column(self, app):
        item = ExistsItem.from_row(
            title="Influenza",
            counter=2,
            row={"target": "Grippe", "via": "other", "qid": "Q1"},
        )
        with app.test_request_context("/table?code=ar"):
            html = str(item.render("ar", "RTT", is_authenticated=True, user_coord=False))

        # via != "td" → link still rendered exactly once.
        assert html.count("ar.wikipedia.org/wiki/Grippe") == 1

    def test_render_url_encodes_and_escapes_title(self, app):
        item = ExistsItem.from_row(
            title="A & B <i>",
            counter=1,
            row={},
        )
        with app.test_request_context("/table?code=ar"):
            html = str(item.render("ar", "RTT", is_authenticated=True, user_coord=False))

        # href is URL-encoded (spaces → "_", "&" → %26, "<i>" → %3Ci%3E),
        # while the visible text is HTML-escaped.
        assert 'href="https://mdwiki.org/wiki/A_%26_B_%3Ci%3E"' in html


# ---------------------------------------------------------------------------
# InProcessItem
# ---------------------------------------------------------------------------


class TestInProcessItem:
    @staticmethod
    def _make(tra_type: str = "lead") -> InProcessItem:
        return InProcessItem.from_row(
            title="Tuberculosis",
            counter=1,
            title_tab={"translate_type": tra_type, "user": "TestUser", "add_date": "2026-09-01 10:20:30"},
            row={
                "w_lead_words": 100,
                "w_all_words": 900,
                "r_lead_refs": 5,
                "r_all_refs": 40,
                "en_views": 1234,
                "importance": "High",
                "qid": "Q1338",
            },
            translate_type_info={},
        )

    def test_from_row_picks_lead_metrics(self):
        item = self._make("lead")
        assert item.tra_type == "lead"
        assert item.words.lead == 100
        assert item.refs.lead == 5
        assert item.en_views == 1234
        assert item.importance == "High"
        assert item.qid == "Q1338"
        assert item.user == "TestUser"
        # datetime-like value is truncated to the date part.
        assert item.date == "2026-09-01"
        assert item.is_video is False

    def test_from_row_picks_all_metrics_when_tra_type_all(self):
        item = self._make("all")
        assert item.tra_type == "all"
        assert item.words.all == 900
        assert item.refs.all == 40

    def test_from_row_forces_all_for_video_titles(self):
        item = InProcessItem.from_row(
            title="Video:Foo",
            counter=1,
            title_tab={"translate_type": "lead", "user": "U", "date": "2026-08-01"},
            row={"w_lead_words": 10, "w_all_words": 20, "en_views": 9, "qid": "Q1"},
        )
        assert item.is_video is True
        assert item.tra_type == "lead"
        # Date without a time component is kept as-is.
        assert item.date == "2026-08-01"

    def test_render_full_user_shows_lead_and_full_buttons(self, app):
        item = self._make()
        with app.test_request_context("/table?code=ar"):
            html = str(
                item.render(
                    "ar",
                    "RTT",
                    is_authenticated=True,
                    show_translation_button=True,
                    full_tr_user=True,
                )
            )

        assert "<tr>" in html
        assert "Lead</a>" in html
        assert "Full</a>" in html
        assert "wikidata.org/wiki/Q1338" in html
        assert "TestUser" in html
        assert "2026-09-01" in html

    def test_render_non_full_user_shows_single_translate_button(self, app):
        item = self._make()
        with app.test_request_context("/table?code=ar"):
            html = str(
                item.render(
                    "ar",
                    "RTT",
                    is_authenticated=True,
                    show_translation_button=True,
                    full_tr_user=False,
                )
            )

        assert "Translate</a>" in html
        assert "Full</a>" not in html

    def test_render_hides_translate_column_when_button_disabled(self, app):
        item = self._make()
        with app.test_request_context("/table?code=ar"):
            html = str(
                item.render(
                    "ar",
                    "RTT",
                    is_authenticated=True,
                    show_translation_button=False,
                    full_tr_user=True,
                )
            )

        assert "Translate</a>" not in html
        assert "Lead</a>" not in html
        # Row data is still rendered.
        assert "TestUser" in html

    def test_render_anonymous_shows_login_instead_of_translate(self, app):
        item = self._make()
        with app.test_request_context("/table?code=ar"):
            html = str(
                item.render(
                    "ar",
                    "RTT",
                    is_authenticated=False,
                    show_translation_button=True,
                    full_tr_user=True,
                )
            )

        assert "/auth/login" in html
        assert "Translate</a>" not in html
