```
tests/
├── __init__.py
├── conftest.py
├── integration/
│   ├── admin/
│   ├── public/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── cxtoken/
│   │       │   ├── test_cxtoken_cors_disabled.py
│   │       │   └── test_cxtoken_cors_on.py
│   │       ├── publish/
│   │       │   ├── test_publish_cors_disabled.py
│   │       │   ├── test_publish_cors_on.py
│   │       │   └── test_publish_csrf_integration.py
│   │       └── test_api_integration.py
│   └── shared/
│       ├── clients/
│       ├── core/
│       │   ├── cors/
│       │   │   └── test_is_allowed_checker.py
│       │   └── test_db_driver.py
│       ├── domain/
│       │   ├── db/
│       │   ├── services/
│       │   │   ├── test_pages_service.py
│       │   │   └── test_users_services.py
│       │   └── test_shared_db_ensure_tables.py
│       └── utils/
│           └── helpers/
└── unit/
    ├── admin/
    │   └── domain/
    │       ├── db/
    │       │   ├── test_db_coordinators.py
    │       │   ├── test_db_full_translators.py
    │       │   ├── test_db_language_settings.py
    │       │   ├── test_db_settings.py
    │       │   └── test_db_users_no_inprocess.py
    │       ├── models/
    │       │   ├── test_coordinator_model.py
    │       │   ├── test_full_translator_model.py
    │       │   ├── test_language_setting_model.py
    │       │   ├── test_setting_model.py
    │       │   └── test_users_no_inprocess_model.py
    │       ├── services/
    │       │   ├── test_coordinators_service.py
    │       │   ├── test_full_translators_service.py
    │       │   ├── test_language_settings_service.py
    │       │   ├── test_settings_service.py
    │       │   └── test_users_no_inprocess_service.py
    │       └── test_admin_db_ensure_tables.py
    ├── public/
    │   ├── domain/
    │   │   ├── db/
    │   │   │   ├── test_db_assessments.py
    │   │   │   ├── test_db_enwiki_pageviews.py
    │   │   │   ├── test_db_in_process.py
    │   │   │   ├── test_db_langs.py
    │   │   │   ├── test_db_mdwiki_revids.py
    │   │   │   ├── test_db_pages_users_to_main.py
    │   │   │   ├── test_db_projects.py
    │   │   │   ├── test_db_refs_counts.py
    │   │   │   ├── test_db_translate_type.py
    │   │   │   ├── test_db_users.py
    │   │   │   ├── test_db_views_new.py
    │   │   │   └── test_db_words.py
    │   │   ├── models/
    │   │   │   ├── test_assessment_model.py
    │   │   │   ├── test_enwiki_pageview_model.py
    │   │   │   ├── test_in_process_model.py
    │   │   │   ├── test_lang_model.py
    │   │   │   ├── test_mdwiki_revid_model.py
    │   │   │   ├── test_pages_users_to_main_model.py
    │   │   │   ├── test_project_model.py
    │   │   │   ├── test_refs_count_model.py
    │   │   │   ├── test_translate_type_model.py
    │   │   │   ├── test_user_model.py
    │   │   │   ├── test_views_new_model.py
    │   │   │   └── test_word_model.py
    │   │   ├── services/
    │   │   │   ├── test_assessments_service.py
    │   │   │   ├── test_enwiki_pageviews_service.py
    │   │   │   ├── test_in_process_service.py
    │   │   │   ├── test_langs_service.py
    │   │   │   ├── test_mdwiki_revids_service.py
    │   │   │   ├── test_pages_users_to_main_service.py
    │   │   │   ├── test_projects_service.py
    │   │   │   ├── test_refs_counts_service.py
    │   │   │   ├── test_translate_type_service.py
    │   │   │   ├── test_users_service.py
    │   │   │   ├── test_views_new_service.py
    │   │   │   └── test_words_service.py
    │   │   └── test_db_ensure_tables.py
    │   ├── routes/
    │   │   ├── test_cxtoken_cache.py
    │   │   └── test_cxtoken_cache_unit.py
    │   └── test_workers/
    │       └── test_post_worker.py
    └── shared/
        ├── auth/
        │   ├── test_decorators.py
        │   └── test_identity.py
        ├── clients/
        │   ├── test_mediawiki_api.py
        │   ├── test_oauth_client.py
        │   ├── test_revids_client.py
        │   └── test_wikidata_client.py
        ├── core/
        │   ├── cookies/
        │   │   └── test_cookie.py
        │   ├── cors/
        │   │   ├── test_check_cors_decorated.py
        │   │   ├── test_cors_request_unit.py
        │   │   ├── test_cors_wrappers.py
        │   │   ├── test_cors_wrappers_and_headers.py
        │   │   ├── test_is_allowed_checker_unit.py
        │   │   └── test_publish_secret_checks.py
        │   └── test_crypto.py
        ├── domain/
        │   ├── db/
        │   │   ├── __init__.py
        │   │   ├── test_db_categories.py
        │   │   ├── test_db_pages.py
        │   │   ├── test_db_publish_reports.py
        │   │   ├── test_db_qids.py
        │   │   └── test_db_user_tokens.py
        │   ├── models/
        │   │   ├── test_category_model.py
        │   │   ├── test_page_model.py
        │   │   ├── test_qid_model.py
        │   │   ├── test_report_model.py
        │   │   └── test_user_token_model.py
        │   └── services/
        │       ├── test_categories_service.py
        │       ├── test_db_service.py
        │       ├── test_pages_service_unit.py
        │       ├── test_qids_service.py
        │       └── test_users_services_unit.py
        └── utils/
            ├── helpers/
            │   ├── test_files.py
            │   ├── test_format.py
            │   ├── test_text_processor.py
            │   ├── test_words.py
            │   └── test_words_unit.py
            └── test_decode_bytes.py

```