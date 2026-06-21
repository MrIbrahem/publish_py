"""
Unit tests for leaderboard_service.py (moved from page_service.py).

Functions tested:
- get_pages_years
- get_months_of_pages_years
- list_of_users_by_translations_count
- get_pages
- top_lang_of_users

Note: get_leaderboard_chart_data is already tested in test_chart_data.py.

Some functions use MySQL-specific SQL (YEAR(), MONTH()), which don't work
in SQLite. Those are tested via mocking.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.main_app.db.models import CategoryRecord, PageRecord, UserRecord
from src.main_app.db.services.pages.leaderboard_service import (
    get_leaderboard_chart_data,
    get_months_of_pages_years,
    get_pages,
    get_pages_years,
    list_of_users_by_translations_count,
    top_lang_of_users,
)
from src.main_app.shared.core.extensions import db

pytestmark = pytest.mark.unit


class TestGetPagesYears:
    """Tests for get_pages_years function (mocked - MySQL-specific YEAR() function)."""

    def test_returns_sorted_years_descending(self, app):
        """Returns years sorted in descending order."""
        with app.app_context():
            mock_row1 = MagicMock()
            mock_row1.year = 2023
            mock_row2 = MagicMock()
            mock_row2.year = 2022
            mock_row3 = MagicMock()
            mock_row3.year = 2024

            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = [mock_row1, mock_row2, mock_row3]

            with patch.object(db.session, "query", return_value=mock_query):
                result = get_pages_years()

            assert result == [2024, 2023, 2022]

    def test_filters_none_years(self, app):
        """Excludes rows where year is None."""
        with app.app_context():
            mock_row_valid = MagicMock()
            mock_row_valid.year = 2023
            mock_row_none = MagicMock()
            mock_row_none.year = None

            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = [mock_row_valid, mock_row_none]

            with patch.object(db.session, "query", return_value=mock_query):
                result = get_pages_years()

            assert None not in result
            assert 2023 in result

    def test_returns_empty_list_when_no_data(self, app):
        """Returns empty list when no pages exist."""
        with app.app_context():
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = []

            with patch.object(db.session, "query", return_value=mock_query):
                result = get_pages_years()

            assert result == []

    def test_applies_user_filter(self, app):
        """Applies user filter when user is provided."""
        with app.app_context():
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = []

            with patch.object(db.session, "query", return_value=mock_query):
                get_pages_years(user="TestUser")

            # filter should have been called multiple times (once for pupdate != '', once for user)
            assert mock_query.filter.call_count >= 2

    def test_applies_lang_filter(self, app):
        """Applies lang filter when lang is provided."""
        with app.app_context():
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = []

            with patch.object(db.session, "query", return_value=mock_query):
                get_pages_years(lang="en")

            assert mock_query.filter.call_count >= 2

    def test_no_filters_applied_when_none(self, app):
        """Only applies pupdate filter when user and lang are None."""
        with app.app_context():
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = []

            with patch.object(db.session, "query", return_value=mock_query):
                get_pages_years(user=None, lang=None)

            # Only one filter call for pupdate != ''
            assert mock_query.filter.call_count == 1


class TestGetMonthsOfPagesYears:
    """Tests for get_months_of_pages_years function (mocked - MySQL-specific SQL)."""

    def test_returns_sorted_months_descending(self, app):
        """Returns months sorted in descending order."""
        with app.app_context():
            mock_row1 = MagicMock()
            mock_row1.month = 3
            mock_row2 = MagicMock()
            mock_row2.month = 11
            mock_row3 = MagicMock()
            mock_row3.month = 7

            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = [mock_row1, mock_row2, mock_row3]

            with patch.object(db.session, "query", return_value=mock_query):
                result = get_months_of_pages_years(2023)

            assert result == [11, 7, 3]

    def test_filters_none_months(self, app):
        """Excludes rows where month is None."""
        with app.app_context():
            mock_row_valid = MagicMock()
            mock_row_valid.month = 5
            mock_row_none = MagicMock()
            mock_row_none.month = None

            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = [mock_row_valid, mock_row_none]

            with patch.object(db.session, "query", return_value=mock_query):
                result = get_months_of_pages_years(2023)

            assert None not in result
            assert 5 in result

    def test_returns_empty_list_for_year_with_no_data(self, app):
        """Returns empty list when no pages exist for the given year."""
        with app.app_context():
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = []

            with patch.object(db.session, "query", return_value=mock_query):
                result = get_months_of_pages_years(1900)

            assert result == []

    def test_passes_year_argument(self, app):
        """Verifies the year argument is used to filter."""
        with app.app_context():
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.distinct.return_value = mock_query
            mock_query.all.return_value = []

            with patch.object(db.session, "query", return_value=mock_query):
                get_months_of_pages_years(2024)

            # filter should have been called at least twice (pupdate != '' and year check)
            assert mock_query.filter.call_count >= 2


class TestListOfUsersByTranslationsCount:
    """Tests for list_of_users_by_translations_count function (SQLite-compatible)."""

    def test_returns_empty_dict_when_no_pages(self, app):
        """Returns empty dict when no pages exist."""
        with app.app_context():
            result = list_of_users_by_translations_count()
            assert result == {}

    def test_counts_users_with_targets(self, app):
        """Returns counts of translations per user where target is non-empty."""
        with app.app_context():
            p1 = PageRecord(title="Page1", user="Alice", lang="en", target="Target1")
            p2 = PageRecord(title="Page2", user="Alice", lang="en", target="Target2")
            p3 = PageRecord(title="Page3", user="Bob", lang="fr", target="Target3")
            db.session.add_all([p1, p2, p3])
            db.session.commit()

            result = list_of_users_by_translations_count()

            assert "Alice" in result
            assert "Bob" in result
            assert result["Alice"] == 2
            assert result["Bob"] == 1

    def test_excludes_pages_with_empty_target(self, app):
        """Excludes pages where target is empty string."""
        with app.app_context():
            p_with_target = PageRecord(title="P1", user="Alice", lang="en", target="T1")
            p_no_target = PageRecord(title="P2", user="Alice", lang="en", target="")
            db.session.add_all([p_with_target, p_no_target])
            db.session.commit()

            result = list_of_users_by_translations_count()

            assert result.get("Alice") == 1

    def test_excludes_pages_with_null_target(self, app):
        """Excludes pages where target is None."""
        with app.app_context():
            p_with_target = PageRecord(title="P1", user="Charlie", lang="en", target="T1")
            p_null_target = PageRecord(title="P2", user="Charlie", lang="en", target=None)
            db.session.add_all([p_with_target, p_null_target])
            db.session.commit()

            result = list_of_users_by_translations_count()

            assert result.get("Charlie") == 1

    def test_excludes_null_usernames(self, app):
        """Excludes rows where user is None."""
        with app.app_context():
            p = PageRecord(title="P1", user=None, lang="en", target="T1")
            db.session.add(p)
            db.session.commit()

            result = list_of_users_by_translations_count()

            assert None not in result

    def test_returns_dict_type(self, app):
        """Return type is always a dict."""
        with app.app_context():
            result = list_of_users_by_translations_count()
            assert isinstance(result, dict)

    def test_ordering_by_count_descending(self, app):
        """Users with higher translation counts appear first."""
        with app.app_context():
            # Alice: 3 translations, Bob: 1 translation
            for i in range(3):
                db.session.add(PageRecord(title=f"PA{i}", user="Alice", lang="en", target=f"TA{i}"))
            db.session.add(PageRecord(title="PB1", user="Bob", lang="en", target="TB1"))
            db.session.commit()

            result = list_of_users_by_translations_count()
            keys = list(result.keys())

            assert keys[0] == "Alice"
            assert keys[1] == "Bob"


class TestGetPages:
    """Tests for get_pages function (uses raw SQL with MySQL-specific YEAR() - mocked)."""

    def test_returns_list(self, app):
        """Returns a list result."""
        with app.app_context():
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = []
            with patch.object(db.session, "execute", return_value=mock_execute):
                result = get_pages()
            assert isinstance(result, list)

    def test_returns_empty_list_when_no_rows(self, app):
        """Returns empty list when no rows returned."""
        with app.app_context():
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = []
            with patch.object(db.session, "execute", return_value=mock_execute):
                result = get_pages()
            assert result == []

    def test_returns_dicts_for_each_row(self, app):
        """Converts each row to a dict."""
        with app.app_context():
            mock_row = MagicMock()
            mock_row._mapping = {"title": "TestPage", "lang": "en", "user": "Alice", "target": "T1"}
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = [mock_row]

            with patch.object(db.session, "execute", return_value=mock_execute):
                result = get_pages()

            assert len(result) == 1
            assert result[0]["title"] == "TestPage"
            assert result[0]["lang"] == "en"

    def test_passes_lang_filter_to_sql(self, app):
        """Passes lang parameter to SQL query."""
        with app.app_context():
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = []

            with patch.object(db.session, "execute", return_value=mock_execute) as mock_exec:
                get_pages(lang="fr")

            call_args = mock_exec.call_args
            params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("params", {})
            # The params dict should contain lang
            assert "lang" in str(mock_exec.call_args)

    def test_passes_user_filter_to_sql(self, app):
        """Passes user parameter to SQL query."""
        with app.app_context():
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = []

            with patch.object(db.session, "execute", return_value=mock_execute) as mock_exec:
                get_pages(user="Alice")

            assert "Alice" in str(mock_exec.call_args)

    def test_passes_year_filter_to_sql(self, app):
        """Passes year parameter to SQL query."""
        with app.app_context():
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = []

            with patch.object(db.session, "execute", return_value=mock_execute) as mock_exec:
                get_pages(year=2023)

            assert "2023" in str(mock_exec.call_args)

    def test_no_filter_uses_where_true(self, app):
        """When no filters, uses '1=1' in WHERE clause."""
        with app.app_context():
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = []

            with patch.object(db.session, "execute", return_value=mock_execute) as mock_exec:
                get_pages()

            sql_str = str(mock_exec.call_args[0][0])
            assert "1=1" in sql_str

    def test_multiple_filters_combined(self, app):
        """Multiple filters are combined with AND."""
        with app.app_context():
            mock_execute = MagicMock()
            mock_execute.fetchall.return_value = []

            with patch.object(db.session, "execute", return_value=mock_execute) as mock_exec:
                get_pages(user="Bob", lang="de")

            call_str = str(mock_exec.call_args)
            assert "Bob" in call_str
            assert "de" in call_str


class TestTopLangOfUsers:
    """Tests for top_lang_of_users function (SQLite-compatible)."""

    def test_returns_empty_dict_for_unknown_user(self, app):
        """Returns empty dict when user has no translations."""
        with app.app_context():
            result = top_lang_of_users("NonexistentUser")
            assert result == {}

    def test_returns_lang_counts_for_user(self, app):
        """Returns language counts for a given user."""
        with app.app_context():
            p1 = PageRecord(title="P1", user="Alice", lang="en", target="T1")
            p2 = PageRecord(title="P2", user="Alice", lang="en", target="T2")
            p3 = PageRecord(title="P3", user="Alice", lang="fr", target="T3")
            db.session.add_all([p1, p2, p3])
            db.session.commit()

            result = top_lang_of_users("Alice")

            assert "en" in result
            assert "fr" in result
            assert result["en"] == 2
            assert result["fr"] == 1

    def test_excludes_empty_target_pages(self, app):
        """Excludes pages where target is empty."""
        with app.app_context():
            p_with = PageRecord(title="P1", user="Bob", lang="de", target="T1")
            p_empty = PageRecord(title="P2", user="Bob", lang="de", target="")
            db.session.add_all([p_with, p_empty])
            db.session.commit()

            result = top_lang_of_users("Bob")

            assert result.get("de") == 1

    def test_excludes_null_target_pages(self, app):
        """Excludes pages where target is None."""
        with app.app_context():
            p_with = PageRecord(title="P1", user="Carol", lang="es", target="T1")
            p_null = PageRecord(title="P2", user="Carol", lang="es", target=None)
            db.session.add_all([p_with, p_null])
            db.session.commit()

            result = top_lang_of_users("Carol")

            assert result.get("es") == 1

    def test_does_not_include_other_users(self, app):
        """Only returns data for the specified user."""
        with app.app_context():
            p1 = PageRecord(title="P1", user="Alice", lang="en", target="T1")
            p2 = PageRecord(title="P2", user="Dave", lang="ja", target="T2")
            db.session.add_all([p1, p2])
            db.session.commit()

            result = top_lang_of_users("Alice")

            assert "ja" not in result
            assert "en" in result

    def test_returns_dict_type(self, app):
        """Return type is always a dict."""
        with app.app_context():
            result = top_lang_of_users("AnyUser")
            assert isinstance(result, dict)

    def test_multiple_languages_ordered_by_count(self, app):
        """Languages with more translations appear first."""
        with app.app_context():
            for i in range(5):
                db.session.add(PageRecord(title=f"E{i}", user="Eve", lang="en", target=f"TE{i}"))
            for i in range(2):
                db.session.add(PageRecord(title=f"F{i}", user="Eve", lang="fr", target=f"TF{i}"))
            db.session.commit()

            result = top_lang_of_users("Eve")
            langs = list(result.keys())

            assert langs[0] == "en"
            assert result["en"] == 5
            assert result["fr"] == 2


class TestLeaderboardServiceImports:
    """Verify that all exported symbols are accessible via the pages package."""

    def test_get_pages_years_importable_from_pages_package(self):
        from src.main_app.db.services.pages import get_pages_years as _f
        assert callable(_f)

    def test_get_months_of_pages_years_importable_from_pages_package(self):
        from src.main_app.db.services.pages import get_months_of_pages_years as _f
        assert callable(_f)

    def test_list_of_users_by_translations_count_importable_from_pages_package(self):
        from src.main_app.db.services.pages import list_of_users_by_translations_count as _f
        assert callable(_f)

    def test_get_pages_importable_from_pages_package(self):
        from src.main_app.db.services.pages import get_pages as _f
        assert callable(_f)

    def test_top_lang_of_users_importable_from_pages_package(self):
        from src.main_app.db.services.pages import top_lang_of_users as _f
        assert callable(_f)

    def test_get_leaderboard_chart_data_importable_from_pages_package(self):
        from src.main_app.db.services.pages import get_leaderboard_chart_data as _f
        assert callable(_f)