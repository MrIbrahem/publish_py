"""Tests for helpers.format module."""

import pytest

from src.app.helpers.format import (
    SPECIAL_USERS,
    determine_hashtag,
    format_title,
    format_user,
    make_summary,
)


class TestFormatTitle:
    """Tests for format_title function."""

    def test_replaces_underscores_with_spaces(self):
        """Test that underscores are replaced with spaces."""
        assert format_title("Hello_World") == "Hello World"

    def test_normalizes_special_user_path(self):
        """Test that Mr. Ibrahem 1/ is replaced with Mr. Ibrahem/."""
        assert format_title("Mr. Ibrahem 1/test") == "Mr. Ibrahem/test"

    def test_handles_combined_transformations(self):
        """Test that both transformations are applied."""
        assert format_title("Mr._Ibrahem_1/test_page") == "Mr. Ibrahem/test page"

    def test_leaves_normal_titles_unchanged(self):
        """Test that normal titles without special patterns are unchanged."""
        assert format_title("Normal Title") == "Normal Title"


class TestFormatUser:
    """Tests for format_user function."""

    def test_maps_special_users(self):
        """Test that special users are mapped correctly."""
        assert format_user("Mr. Ibrahem 1") == "Mr. Ibrahem"
        assert format_user("Admin") == "Mr. Ibrahem"

    def test_replaces_underscores(self):
        """Test that underscores are replaced with spaces."""
        assert format_user("Test_User") == "Test User"

    def test_leaves_normal_users_unchanged(self):
        """Test that normal users are unchanged."""
        assert format_user("RegularUser") == "RegularUser"


class TestDetermineHashtag:
    """Tests for determine_hashtag function."""

    def test_returns_mdwikicx_by_default(self):
        """Test that #mdwikicx is returned by default."""
        assert determine_hashtag("Some Title", "Some User") == "#mdwikicx"

    def test_returns_empty_for_mr_ibrahem_own_pages(self):
        """Test that empty hashtag is returned for Mr. Ibrahem's own pages."""
        assert determine_hashtag("Mr. Ibrahem/test", "Mr. Ibrahem") == ""

    def test_returns_mdwikicx_for_other_users_on_mr_ibrahem_pages(self):
        """Test that hashtag is returned for other users on Mr. Ibrahem pages."""
        assert determine_hashtag("Mr. Ibrahem/test", "Other User") == "#mdwikicx"


class TestMakeSummary:
    """Tests for make_summary function."""

    def test_generates_correct_summary(self):
        """Test that edit summary is generated correctly."""
        summary = make_summary("12345", "Source Page", "ar", "#mdwikicx")
        expected = "Created by translating the page [[:mdwiki:Special:Redirect/revision/12345|Source Page]] to:ar #mdwikicx"
        assert summary == expected

    def test_generates_summary_without_hashtag(self):
        """Test that edit summary works without hashtag."""
        summary = make_summary("12345", "Source Page", "ar", "")
        expected = "Created by translating the page [[:mdwiki:Special:Redirect/revision/12345|Source Page]] to:ar "
        assert summary == expected


class TestSpecialUsers:
    """Tests for SPECIAL_USERS constant."""

    def test_special_users_mapping(self):
        """Test that special users mapping is correct."""
        assert SPECIAL_USERS["Mr. Ibrahem 1"] == "Mr. Ibrahem"
        assert SPECIAL_USERS["Admin"] == "Mr. Ibrahem"
