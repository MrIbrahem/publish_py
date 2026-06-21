"""
Tests that verify the new package-level __init__.py files correctly
re-export all documented symbols.

This PR introduced new __init__.py files for:
- src/main_app/db/services/analytics/
- src/main_app/db/services/config/
- src/main_app/db/services/content/
- src/main_app/db/services/pages/
- src/main_app/db/services/reports/
- src/main_app/db/services/users/

Each test class verifies that all symbols listed in __all__ are importable
from the package and are callable (functions) or are present (constants).
"""

import pytest

pytestmark = pytest.mark.unit


class TestAnalyticsPackageExports:
    """Verify analytics package __init__.py exports all documented symbols."""

    def test_all_symbols_in_dunder_all(self):
        import src.main_app.db.services.analytics as pkg
        assert hasattr(pkg, "__all__")
        assert len(pkg.__all__) > 0

    def test_assessment_functions_accessible(self):
        from src.main_app.db.services.analytics import (
            add_assessment,
            add_or_update_assessment,
            delete_assessment,
            get_assessment,
            get_assessment_by_title,
            list_assessments,
            update_assessment,
        )
        for fn in (list_assessments, get_assessment, get_assessment_by_title,
                   add_assessment, add_or_update_assessment, update_assessment,
                   delete_assessment):
            assert callable(fn)

    def test_enwiki_pageview_functions_accessible(self):
        from src.main_app.db.services.analytics import (
            add_enwiki_pageview,
            add_or_update_enwiki_pageview,
            delete_enwiki_pageview,
            get_enwiki_pageview,
            get_enwiki_pageview_by_title,
            get_top_enwiki_pageviews,
            list_enwiki_pageviews,
            update_enwiki_pageview,
        )
        for fn in (list_enwiki_pageviews, get_top_enwiki_pageviews, get_enwiki_pageview,
                   get_enwiki_pageview_by_title, add_enwiki_pageview,
                   add_or_update_enwiki_pageview, update_enwiki_pageview, delete_enwiki_pageview):
            assert callable(fn)

    def test_mdwiki_revid_functions_accessible(self):
        from src.main_app.db.services.analytics import (
            add_mdwiki_revid,
            add_or_update_mdwiki_revid,
            delete_mdwiki_revid,
            get_mdwiki_revid_by_title,
            get_revid_for_title,
            list_mdwiki_revids,
            update_mdwiki_revid,
        )
        for fn in (list_mdwiki_revids, get_mdwiki_revid_by_title, add_mdwiki_revid,
                   add_or_update_mdwiki_revid, update_mdwiki_revid, delete_mdwiki_revid,
                   get_revid_for_title):
            assert callable(fn)

    def test_refs_count_functions_accessible(self):
        from src.main_app.db.services.analytics import (
            add_or_update_refs_count,
            add_refs_count,
            delete_refs_count,
            get_ref_counts_for_title,
            get_refs_count,
            get_refs_count_by_title,
            list_refs_counts,
            update_refs_count,
        )
        for fn in (list_refs_counts, get_refs_count, get_refs_count_by_title, add_refs_count,
                   add_or_update_refs_count, update_refs_count, delete_refs_count,
                   get_ref_counts_for_title):
            assert callable(fn)

    def test_views_new_functions_accessible(self):
        from src.main_app.db.services.analytics import (
            add_or_update_views_new,
            add_views_new,
            delete_views_new,
            get_total_views_for_target,
            get_views_by_target_lang_year,
            get_views_new,
            list_views_by_lang,
            list_views_by_target,
            list_views_new,
            update_views_new,
        )
        for fn in (list_views_new, list_views_by_target, list_views_by_lang, get_views_new,
                   get_views_by_target_lang_year, add_views_new, add_or_update_views_new,
                   update_views_new, delete_views_new, get_total_views_for_target):
            assert callable(fn)

    def test_word_functions_accessible(self):
        from src.main_app.db.services.analytics import (
            add_or_update_word,
            add_word,
            delete_word,
            get_word,
            get_word_by_title,
            get_word_counts_for_title,
            list_words,
            update_word,
        )
        for fn in (list_words, get_word, get_word_by_title, add_word, add_or_update_word,
                   update_word, delete_word, get_word_counts_for_title):
            assert callable(fn)

    def test_all_symbols_importable(self):
        """Every symbol listed in __all__ is importable from the package."""
        import src.main_app.db.services.analytics as pkg
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"Missing symbol in analytics package: {name}"


class TestConfigPackageExports:
    """Verify config package __init__.py exports all documented symbols."""

    def test_language_setting_functions_accessible(self):
        from src.main_app.db.services.config import (
            add_language_setting,
            add_or_update_language_setting,
            delete_language_setting,
            get_language_setting,
            get_language_setting_by_code,
            list_language_settings,
            update_language_setting,
        )
        for fn in (list_language_settings, get_language_setting, get_language_setting_by_code,
                   add_language_setting, add_or_update_language_setting, update_language_setting,
                   delete_language_setting):
            assert callable(fn)

    def test_setting_functions_accessible(self):
        from src.main_app.db.services.config import (
            add_setting,
            delete_setting,
            get_setting,
            get_setting_by_key,
            list_settings,
            update_value,
        )
        for fn in (list_settings, get_setting, get_setting_by_key, add_setting,
                   update_value, delete_setting):
            assert callable(fn)

    def test_all_symbols_importable(self):
        """Every symbol listed in __all__ is importable from the package."""
        import src.main_app.db.services.config as pkg
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"Missing symbol in config package: {name}"


class TestContentPackageExports:
    """Verify content package __init__.py exports all documented symbols."""

    def test_category_functions_accessible(self):
        from src.main_app.db.services.content import (
            add_category,
            delete_category,
            get_camp_to_cats,
            get_campaign_category,
            list_categories,
            update_category,
        )
        for fn in (add_category, delete_category, get_camp_to_cats,
                   get_campaign_category, list_categories, update_category):
            assert callable(fn)

    def test_lang_functions_accessible(self):
        from src.main_app.db.services.content import (
            add_lang,
            add_or_update_lang,
            delete_lang,
            get_lang,
            get_lang_by_code,
            list_langs,
        )
        for fn in (add_lang, add_or_update_lang, delete_lang, get_lang,
                   get_lang_by_code, list_langs):
            assert callable(fn)

    def test_project_functions_accessible(self):
        from src.main_app.db.services.content import (
            add_project,
            delete_project,
            get_project,
            get_project_by_title,
            list_projects,
            update_project,
            update_project_title,
        )
        for fn in (add_project, delete_project, get_project, get_project_by_title,
                   list_projects, update_project, update_project_title):
            assert callable(fn)

    def test_all_symbols_importable(self):
        """Every symbol listed in __all__ is importable from the package."""
        import src.main_app.db.services.content as pkg
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"Missing symbol in content package: {name}"


class TestPagesPackageExports:
    """Verify pages package __init__.py exports all documented symbols."""

    def test_in_process_functions_accessible(self):
        from src.main_app.db.services.pages import (
            add_in_process,
            delete_in_process,
            delete_in_process_by_title_user_lang,
            get_in_process,
            get_in_process_by_title_user_lang,
            get_in_process_counts_by_user,
            is_in_process,
            list_in_process,
            list_in_process_by_lang,
            list_in_process_by_user,
            update_in_process,
        )
        for fn in (add_in_process, delete_in_process, delete_in_process_by_title_user_lang,
                   get_in_process, get_in_process_by_title_user_lang, get_in_process_counts_by_user,
                   is_in_process, list_in_process, list_in_process_by_lang, list_in_process_by_user,
                   update_in_process):
            assert callable(fn)

    def test_leaderboard_functions_accessible(self):
        from src.main_app.db.services.pages import (
            get_leaderboard_chart_data,
            get_months_of_pages_years,
            get_pages,
            get_pages_years,
            list_of_users_by_translations_count,
            top_lang_of_users,
        )
        for fn in (get_leaderboard_chart_data, get_months_of_pages_years, get_pages,
                   get_pages_years, list_of_users_by_translations_count, top_lang_of_users):
            assert callable(fn)

    def test_page_service_functions_accessible(self):
        from src.main_app.db.services.pages import (
            add_page,
            add_translate_row_to_db,
            delete_page,
            find_exists_or_update_page,
            insert_page_target,
            list_pages,
            list_pages_by_lang_cat,
            update_page,
        )
        for fn in (add_page, add_translate_row_to_db, delete_page, find_exists_or_update_page,
                   insert_page_target, list_pages, list_pages_by_lang_cat, update_page):
            assert callable(fn)

    def test_all_symbols_importable(self):
        """Every symbol listed in __all__ is importable from the package."""
        import src.main_app.db.services.pages as pkg
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"Missing symbol in pages package: {name}"


class TestReportsPackageExports:
    """Verify reports package __init__.py exports all documented symbols."""

    def test_pages_users_to_main_functions_accessible(self):
        from src.main_app.db.services.reports import (
            add_pages_users_to_main,
            delete_pages_users_to_main,
            get_pages_users_to_main,
            list_pages_users_to_main,
            update_pages_users_to_main,
        )
        for fn in (add_pages_users_to_main, delete_pages_users_to_main, get_pages_users_to_main,
                   list_pages_users_to_main, update_pages_users_to_main):
            assert callable(fn)

    def test_report_functions_accessible(self):
        from src.main_app.db.services.reports import (
            add_report,
            delete_report,
            list_reports,
            query_reports_with_filters,
        )
        for fn in (add_report, delete_report, list_reports, query_reports_with_filters):
            assert callable(fn)

    def test_all_symbols_importable(self):
        """Every symbol listed in __all__ is importable from the package."""
        import src.main_app.db.services.reports as pkg
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"Missing symbol in reports package: {name}"


class TestUsersPackageExports:
    """Verify users package __init__.py exports all documented symbols."""

    def test_coordinator_functions_accessible(self):
        from src.main_app.db.services.users import (
            active_coordinators,
            add_coordinator,
            add_or_update_coordinator,
            delete_coordinator,
            get_coordinator,
            get_coordinator_by_user,
            is_coordinator,
            list_coordinators,
            set_coordinator_active,
            update_coordinator,
        )
        for fn in (active_coordinators, add_coordinator, add_or_update_coordinator,
                   delete_coordinator, get_coordinator, get_coordinator_by_user,
                   is_coordinator, list_coordinators, set_coordinator_active,
                   update_coordinator):
            assert callable(fn)

    def test_full_translator_functions_accessible(self):
        from src.main_app.db.services.users import (
            add_full_translator,
            add_or_update_full_translator,
            delete_full_translator,
            get_full_translator,
            get_full_translator_by_user,
            is_full_translator,
            list_active_full_translators,
            list_full_translators,
            update_full_translator,
        )
        for fn in (add_full_translator, add_or_update_full_translator, delete_full_translator,
                   get_full_translator, get_full_translator_by_user, is_full_translator,
                   list_active_full_translators, list_full_translators, update_full_translator):
            assert callable(fn)

    def test_user_service_functions_accessible(self):
        from src.main_app.db.services.users import (
            add_user,
            delete_user,
            get_user,
            get_user_by_username,
            list_users,
            list_users_by_group,
            update_user,
            update_user_data,
            user_exists,
        )
        for fn in (add_user, delete_user, get_user, get_user_by_username, list_users,
                   list_users_by_group, update_user, update_user_data, user_exists):
            assert callable(fn)

    def test_user_token_functions_accessible(self):
        from src.main_app.db.services.users import (
            delete_user_token,
            delete_user_token_by_username,
            get_user_token,
            get_user_token_by_username,
            upsert_user_token,
        )
        for fn in (delete_user_token, delete_user_token_by_username, get_user_token,
                   get_user_token_by_username, upsert_user_token):
            assert callable(fn)

    def test_users_no_inprocess_functions_accessible(self):
        from src.main_app.db.services.users import (
            add_or_update_users_no_inprocess,
            add_users_no_inprocess,
            delete_users_no_inprocess,
            get_users_no_inprocess,
            get_users_no_inprocess_by_user,
            list_active_users_no_inprocess,
            list_users_no_inprocess,
            should_hide_from_inprocess,
            update_users_no_inprocess,
        )
        for fn in (add_or_update_users_no_inprocess, add_users_no_inprocess, delete_users_no_inprocess,
                   get_users_no_inprocess, get_users_no_inprocess_by_user, list_active_users_no_inprocess,
                   list_users_no_inprocess, should_hide_from_inprocess, update_users_no_inprocess):
            assert callable(fn)

    def test_all_symbols_importable(self):
        """Every symbol listed in __all__ is importable from the package."""
        import src.main_app.db.services.users as pkg
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"Missing symbol in users package: {name}"


class TestAdminDecoratorsImport:
    """Verify admin decorators use updated import path from users package."""

    def test_admin_required_decorator_importable(self):
        from src.main_app.admin.decorators import admin_required
        assert callable(admin_required)

    def test_active_coordinators_importable_from_users_package(self):
        """active_coordinators used in decorators.py is accessible from users package."""
        from src.main_app.db.services.users import active_coordinators
        assert callable(active_coordinators)