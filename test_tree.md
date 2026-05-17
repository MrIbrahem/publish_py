```
tests/
├── __init__.py
├── conftest.py
├── integration/
│   ├── admin/
│   │   └── routes/
│   │       ├── test_admin_routes_integration.py
│   │       ├── test_coordinators_routes_integration.py
│   │       ├── test_full_translators_routes_integration.py
│   │       ├── test_language_settings_routes_integration.py
│   │       ├── test_settings_routes_integration.py
│   │       └── test_users_no_inprocess_routes_integration.py
│   ├── public/
│   │   └── routes/
│   │       ├── api/
│   │       │   └── test_api_routes.py
│   │       ├── auth/
│   │       │   └── test_auth_routes.py
│   │       ├── cxtoken/
│   │       │   ├── test_cxtoken_cors_disabled.py
│   │       │   ├── test_cxtoken_cors_on.py
│   │       │   └── test_cxtoken_routes.py
│   │       ├── main/
│   │       │   └── test_main_routes.py
│   │       ├── publish/
│   │       │   ├── test_publish_cors_disabled.py
│   │       │   ├── test_publish_cors_on.py
│   │       │   ├── test_publish_csrf_integration.py
│   │       │   └── test_publish_routes.py
│   │       └── refs/
│   │           └── test_refs_routes.py
│   └── shared/
│       ├── core/
│       │   └── cors/
│       │       ├── test_is_allowed_checker.py
│       │       └── test_main_routes_with_cors.py
│       └── services/
│           ├── test_pages_service_integration.py
│           └── test_user_token_service_integration.py
└── unit/
    ├── admin/
    │   └── routes/
    │       ├── test_admin_routes.py
    │       ├── test_coordinators_routes.py
    │       ├── test_full_translators_routes.py
    │       ├── test_language_settings_routes.py
    │       ├── test_settings_routes.py
    │       └── test_users_no_inprocess_routes.py
    ├── db/
    │   ├── models/
    │   │   ├── analytics/
    │   │   │   ├── test_assessment_model.py
    │   │   │   ├── test_enwiki_pageview_model.py
    │   │   │   ├── test_mdwiki_revid_model.py
    │   │   │   ├── test_refs_count_model.py
    │   │   │   ├── test_views_new_model.py
    │   │   │   └── test_word_model.py
    │   │   ├── config/
    │   │   │   ├── test_language_setting_model.py
    │   │   │   └── test_setting_model.py
    │   │   ├── content/
    │   │   │   ├── test_category_model.py
    │   │   │   ├── test_lang_model.py
    │   │   │   └── test_project_model.py
    │   │   ├── pages/
    │   │   │   ├── test_in_process_model.py
    │   │   │   ├── test_page_model.py
    │   │   │   └── test_translate_type_model.py
    │   │   ├── reports/
    │   │   │   ├── test_pages_users_to_main_model.py
    │   │   │   └── test_report_model.py
    │   │   ├── users/
    │   │   │   ├── test_coordinator_model.py
    │   │   │   ├── test_full_translator_model.py
    │   │   │   ├── test_user_model.py
    │   │   │   ├── test_user_token_model.py
    │   │   │   └── test_users_no_inprocess_model.py
    │   │   └── wikidata/
    │   │       └── test_qid_model.py
    │   └── services/
    │       ├── analytics/
    │       ├── config/
    │       ├── content/
    │       ├── pages/
    │       ├── reports/
    │       ├── users/
    │       └── wikidata/
    ├── public/
    │   └── routes/
    │       ├── api/
    │       ├── auth/
    │       │   ├── test_auth_oauth.py
    │       │   └── test_rate_limit.py
    │       ├── cxtoken/
    │       │   └── test_cxtoken_cache.py
    │       ├── main/
    │       ├── publish/
    │       │   └── test_publish_worker.py
    │       └── refs/
    └── shared/
        ├── auth/
        │   ├── test_decorators.py
        │   └── test_identity.py
        ├── clients/
        │   ├── test_mdwiki_api.py
        │   ├── test_mediawiki_api.py
        │   ├── test_oauth_client.py
        │   ├── test_revids_client.py
        │   ├── test_text_api.py
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
        │   ├── test_crypto.py
        │   └── test_extensions.py
        ├── services/
        │   ├── analytics/
        │   │   ├── test_assessment_service.py
        │   │   ├── test_enwiki_pageview_service.py
        │   │   ├── test_mdwiki_revid_service.py
        │   │   ├── test_refs_count_service.py
        │   │   ├── test_views_new_service.py
        │   │   └── test_word_service.py
        │   ├── config/
        │   │   ├── test_language_setting_service.py
        │   │   └── test_setting_service.py
        │   ├── content/
        │   │   ├── test_category_service.py
        │   │   ├── test_lang_service.py
        │   │   └── test_project_service.py
        │   ├── pages/
        │   │   ├── test_in_process_service.py
        │   │   ├── test_page_service.py
        │   │   ├── test_translate_type_service.py
        │   │   └── test_user_page_service.py
        │   ├── reports/
        │   │   ├── test_pages_users_to_main_service.py
        │   │   └── test_report_service.py
        │   ├── users/
        │   │   ├── test_coordinator_service.py
        │   │   ├── test_full_translator_service.py
        │   │   ├── test_user_service.py
        │   │   ├── test_user_token_service.py
        │   │   └── test_users_no_inprocess_service.py
        │   └── wikidata/
        │       ├── test_allqid_service.py
        │       └── test_qid_service.py
        └── utils/
            ├── helpers/
            │   ├── test_files.py
            │   ├── test_format.py
            │   ├── test_text_processor.py
            │   ├── test_words.py
            │   └── test_words_unit.py
            ├── test_decode_bytes.py
            └── test_web_utils.py

```